"""
Sprint 2 - LangChain需求提取器测试
测试AI驱动的需求提取功能
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import Requirement, RequirementType, Priority

@pytest.fixture
def test_api_key():
    """测试用的API密钥"""
    return "mock-test-key"

@pytest.fixture
def extractor(test_api_key):
    """LangChain提取器fixture - 使用MOCK提供商"""
    return LangChainExtractor(provider=AIProvider.MOCK, api_key=test_api_key)

class TestLangChainExtractor:
    """测试LangChain需求提取器"""
    
    def test_extractor_initialization(self, extractor):
        """测试提取器初始化 - 这个测试现在会失败"""
        assert extractor is not None
        assert hasattr(extractor, 'extract')
        assert hasattr(extractor, 'extract_async')

    @pytest.mark.asyncio
    async def test_extract_functional_requirements(self, extractor):
        """测试提取功能需求 - 使用MOCK提供商"""
        document = Document(
            title="用户管理系统需求",
            content="""# 用户管理系统需求

## 功能需求

### 1. 用户注册
- 用户可以通过邮箱注册
- 密码必须包含大小写字母和数字
- 注册后发送验证邮件
""",
            document_type=DocumentType.MARKDOWN
        )

        # 执行提取（使用MOCK提供商）
        requirements = await extractor.extract_async(document)

        # 验证结果
        assert len(requirements) >= 1

        # 验证需求基本信息
        req = requirements[0]
        assert req.id == "REQ-001"
        assert req.title == "模拟需求"
        assert req.type == RequirementType.FUNCTIONAL
        assert req.priority == Priority.MEDIUM
        assert len(req.acceptance_criteria) >= 1
    
    @pytest.mark.asyncio
    async def test_extract_non_functional_requirements(self):
        """测试提取非功能需求 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        document = Document(
            title="系统性能需求",
            content="""# 系统性能需求

## 非功能需求

### 性能要求
- 响应时间 < 2秒
- 支持1000并发用户
- 99.9%可用性

### 安全要求
- 密码加密存储
- 支持HTTPS
- 数据备份每日执行
""",
            document_type=DocumentType.MARKDOWN
        )
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''[
                {
                    "id": "REQ-003",
                    "title": "系统性能要求",
                    "description": "系统必须满足性能指标",
                    "type": "non_functional",
                    "priority": "high",
                    "acceptance_criteria": [
                        "响应时间 < 2秒",
                        "支持1000并发用户",
                        "99.9%可用性"
                    ]
                }
            ]'''
            
            mock_client.chat.completions.create.return_value = mock_response
            
            requirements = await extractor.extract_async(document)
            
            assert len(requirements) == 1
            req = requirements[0]
            assert req.type == RequirementType.NON_FUNCTIONAL
            assert req.priority == Priority.HIGH
    
    @pytest.mark.asyncio
    async def test_extract_user_stories(self):
        """测试提取用户故事 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        document = Document(
            title="用户故事",
            content="""# 用户故事

## 作为用户，我希望能够注册账户
**验收标准：**
- 用户可以输入邮箱和密码
- 密码强度验证
- 注册成功后跳转到登录页面

**优先级：** 高

## 作为管理员，我希望能够管理用户
**验收标准：**
- 查看用户列表
- 禁用/启用用户账户
- 重置用户密码

**优先级：** 中
""",
            document_type=DocumentType.MARKDOWN
        )
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''[
                {
                    "id": "US-001",
                    "title": "用户账户注册",
                    "description": "作为用户，我希望能够注册账户",
                    "type": "user_story",
                    "priority": "high",
                    "acceptance_criteria": [
                        "用户可以输入邮箱和密码",
                        "密码强度验证",
                        "注册成功后跳转到登录页面"
                    ]
                }
            ]'''
            
            mock_client.chat.completions.create.return_value = mock_response
            
            requirements = await extractor.extract_async(document)
            
            assert len(requirements) == 1
            req = requirements[0]
            assert req.type == RequirementType.USER_STORY
            assert "作为用户" in req.description
    
    def test_extract_sync_method(self):
        """测试同步提取方法 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        document = Document(
            title="简单需求",
            content="用户需要登录功能",
            document_type=DocumentType.MARKDOWN
        )
        
        with patch.object(extractor, 'extract_async') as mock_async:
            mock_async.return_value = [
                Requirement(
                    id="REQ-001",
                    title="用户登录",
                    description="用户需要登录功能",
                    type=RequirementType.FUNCTIONAL,
                    priority=Priority.MEDIUM
                )
            ]
            
            requirements = extractor.extract(document)
            
            assert len(requirements) == 1
            assert requirements[0].title == "用户登录"
    
    @pytest.mark.asyncio
    async def test_extract_with_custom_prompt(self):
        """测试使用自定义提示词提取 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        document = Document(
            title="API需求",
            content="需要创建用户API",
            document_type=DocumentType.MARKDOWN
        )
        
        custom_prompt = "请专注于API设计需求的提取"
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''[
                {
                    "id": "API-001",
                    "title": "用户API创建",
                    "description": "创建用户管理相关的API接口",
                    "type": "functional",
                    "priority": "high",
                    "acceptance_criteria": ["API接口设计", "数据验证", "错误处理"]
                }
            ]'''
            
            mock_client.chat.completions.create.return_value = mock_response
            
            requirements = await extractor.extract_async(document, custom_prompt=custom_prompt)
            
            # 验证自定义提示词被使用
            call_args = mock_client.chat.completions.create.call_args
            assert custom_prompt in str(call_args)
            
            assert len(requirements) == 1
            assert "API" in requirements[0].title
    
    @pytest.mark.asyncio
    async def test_extract_accuracy_validation(self):
        """测试提取准确率验证 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        document = Document(
            title="测试需求",
            content="""
            需求1: 用户登录
            需求2: 用户注册  
            需求3: 密码重置
            """,
            document_type=DocumentType.MARKDOWN
        )
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''[
                {
                    "id": "REQ-001",
                    "title": "用户登录",
                    "description": "用户登录功能",
                    "type": "functional",
                    "priority": "high",
                    "acceptance_criteria": []
                },
                {
                    "id": "REQ-002",
                    "title": "用户注册",
                    "description": "用户注册功能",
                    "type": "functional", 
                    "priority": "high",
                    "acceptance_criteria": []
                }
            ]'''
            
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await extractor.extract_with_accuracy(document)
            
            # 验证返回结果包含准确率信息
            assert 'requirements' in result
            assert 'accuracy' in result
            assert 'confidence' in result
            
            # 验证准确率计算（2个提取出来，3个预期，准确率约67%）
            assert result['accuracy'] >= 0.6
            assert len(result['requirements']) == 2
    
    @pytest.mark.asyncio
    async def test_extract_error_handling(self):
        """测试错误处理 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        document = Document(
            title="测试文档",
            content="测试内容",
            document_type=DocumentType.MARKDOWN
        )
        
        # 测试API错误
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="需求提取失败"):
                await extractor.extract_async(document)
    
    @pytest.mark.asyncio
    async def test_extract_performance(self):
        """测试提取性能 - 这个测试现在会失败"""
        extractor = LangChainExtractor()
        
        # 创建大型文档
        large_content = "# 大型需求文档\n\n" + "\n\n".join([
            f"## 需求 {i}\n用户需要功能{i}"
            for i in range(50)
        ])
        
        document = Document(
            title="大型需求文档",
            content=large_content,
            document_type=DocumentType.MARKDOWN
        )
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '[]'  # 空结果
            
            mock_client.chat.completions.create.return_value = mock_response
            
            import time
            start_time = time.time()
            requirements = await extractor.extract_async(document)
            end_time = time.time()
            
            # 验证性能要求（应该在5秒内完成）
            extract_time = end_time - start_time
            assert extract_time < 5.0, f"提取时间过长: {extract_time:.2f}秒"
