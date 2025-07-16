"""
Sprint 2 - LangChain需求提取器测试
使用Ollama提供商测试AI驱动的需求提取功能
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import RequirementType, Priority

@pytest.fixture
def ollama_extractor():
    """Ollama提取器fixture"""
    return LangChainExtractor(
        provider=AIProvider.OLLAMA,
        model="llama2",
        ollama_url="http://localhost:11434"
    )

@pytest.fixture
def sample_document():
    """示例文档fixture"""
    return Document(
        title="用户管理系统需求",
        content="""# 用户管理系统需求

## 功能需求

### 1. 用户注册
- 用户可以通过邮箱注册
- 密码必须包含大小写字母和数字
- 注册后发送验证邮件

### 2. 用户登录
- 支持邮箱登录
- 支持记住登录状态
""",
        document_type=DocumentType.MARKDOWN
    )

# 模拟Ollama API响应
@pytest.fixture
def mock_ollama_response():
    """模拟Ollama API响应"""
    return {
        "response": '''[
            {
                "id": "REQ-001",
                "title": "用户注册",
                "description": "用户可以通过邮箱注册系统",
                "type": "functional",
                "priority": "high",
                "acceptance_criteria": ["支持邮箱注册", "密码必须包含大小写字母和数字", "注册后发送验证邮件"]
            },
            {
                "id": "REQ-002",
                "title": "用户登录",
                "description": "用户可以登录系统",
                "type": "functional",
                "priority": "high",
                "acceptance_criteria": ["支持邮箱登录", "支持记住登录状态"]
            }
        ]'''
    }

class TestLangChainExtractor:
    """测试LangChain需求提取器"""
    
    def test_extractor_initialization(self, ollama_extractor):
        """测试提取器初始化"""
        assert ollama_extractor is not None
        assert hasattr(ollama_extractor, 'extract')
        assert hasattr(ollama_extractor, 'extract_async')
        assert ollama_extractor.provider == AIProvider.OLLAMA
        assert ollama_extractor.model == "llama2"
        assert ollama_extractor.ollama_url == "http://localhost:11434"
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_extract_with_ollama_provider(self, mock_session, ollama_extractor, sample_document, mock_ollama_response):
        """测试使用Ollama提供商提取需求"""
        # 设置模拟响应
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_ollama_response
        
        # 设置模拟会话
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 执行提取
        requirements = await ollama_extractor.extract_async(sample_document)
        
        # 验证基本结果
        assert len(requirements) == 2
        
        # 验证第一个需求
        req1 = requirements[0]
        assert req1.id == "REQ-001"
        assert req1.title == "用户注册"
        assert req1.type == RequirementType.FUNCTIONAL
        assert req1.priority == Priority.HIGH
        assert len(req1.acceptance_criteria) == 3
        assert req1.source_document == sample_document.title
        
        # 验证第二个需求
        req2 = requirements[1]
        assert req2.id == "REQ-002"
        assert req2.title == "用户登录"
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_extract_with_custom_prompt(self, mock_session, ollama_extractor, sample_document, mock_ollama_response):
        """测试使用自定义提示词"""
        # 设置模拟响应
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_ollama_response
        
        # 设置模拟会话
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 使用自定义提示词
        custom_prompt = "请专注于API设计需求的提取"
        requirements = await ollama_extractor.extract_async(sample_document, custom_prompt=custom_prompt)
        
        # 验证结果
        assert len(requirements) == 2
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_extract_accuracy_validation(self, mock_session, ollama_extractor, sample_document, mock_ollama_response):
        """测试提取准确率验证"""
        # 设置模拟响应
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_ollama_response
        
        # 设置模拟会话
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 执行准确率验证
        result = await ollama_extractor.extract_with_accuracy(sample_document, expected_count=2)
        
        # 验证返回结果包含准确率信息
        assert 'requirements' in result
        assert 'accuracy' in result
        assert 'confidence' in result
        assert 'extracted_count' in result
        assert 'expected_count' in result
        
        # 验证数据类型
        assert isinstance(result['requirements'], list)
        assert isinstance(result['accuracy'], float)
        assert isinstance(result['confidence'], float)
        assert result['expected_count'] == 2
        assert result['extracted_count'] == 2
        assert result['accuracy'] == 1.0  # 预期2个，提取2个，准确率100%
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_create_requirement_collection(self, mock_session, ollama_extractor, sample_document, mock_ollama_response):
        """测试创建需求集合"""
        # 设置模拟响应
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_ollama_response
        
        # 设置模拟会话
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 提取需求
        requirements = await ollama_extractor.extract_async(sample_document)
        
        # 创建需求集合
        collection = ollama_extractor.create_requirement_collection(requirements)
        
        # 验证集合
        assert collection.total_count == 2
        assert collection.functional_count == 2
        assert collection.requirements == requirements

class TestAIProviders:
    """测试不同AI提供商"""
    
    def test_ollama_provider_initialization(self):
        """测试Ollama提供商初始化"""
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="llama2",
            ollama_url="http://localhost:11434"
        )
        assert extractor.provider == AIProvider.OLLAMA
        assert extractor.model == "llama2"
        assert extractor.ollama_url == "http://localhost:11434"
    
    def test_openai_provider_initialization_without_key(self):
        """测试OpenAI提供商初始化（无密钥）"""
        with pytest.raises(ValueError, match="未设置OpenAI API密钥"):
            LangChainExtractor(provider=AIProvider.OPENAI)
    
    def test_openai_provider_initialization_with_key(self):
        """测试OpenAI提供商初始化（有密钥）"""
        extractor = LangChainExtractor(
            provider=AIProvider.OPENAI,
            api_key="sk-test1234567890abcdef1234567890abcdef12345678"
        )
        assert extractor.provider == AIProvider.OPENAI
        assert extractor.api_key.startswith("sk-")
    
    def test_gemini_provider_initialization(self):
        """测试Gemini提供商初始化"""
        extractor = LangChainExtractor(
            provider=AIProvider.GEMINI,
            api_key="test-gemini-key",
            model="gemini-pro"
        )
        assert extractor.provider == AIProvider.GEMINI
        assert extractor.model == "gemini-pro"
        assert extractor.api_key == "test-gemini-key"
    
    @pytest.mark.asyncio
    async def test_unsupported_provider_error(self):
        """测试不支持的提供商错误"""
        # 创建一个无效的提供商
        extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
        extractor.provider = "invalid_provider"  # 手动设置无效提供商
        
        document = Document(
            title="测试",
            content="测试内容",
            document_type=DocumentType.MARKDOWN
        )
        
        with pytest.raises(ValueError, match="不支持的AI提供商"):
            await extractor.extract_async(document)
