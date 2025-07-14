"""
Sprint 2 - LangChain需求提取器简化测试
测试多AI提供商的需求提取功能
"""
import pytest
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import RequirementType, Priority

@pytest.fixture
def mock_extractor():
    """MOCK提取器fixture"""
    return LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

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

class TestLangChainExtractor:
    """测试LangChain需求提取器"""
    
    def test_extractor_initialization(self, mock_extractor):
        """测试提取器初始化"""
        assert mock_extractor is not None
        assert hasattr(mock_extractor, 'extract')
        assert hasattr(mock_extractor, 'extract_async')
        assert mock_extractor.provider == AIProvider.MOCK
    
    @pytest.mark.asyncio
    async def test_extract_with_mock_provider(self, mock_extractor, sample_document):
        """测试使用MOCK提供商提取需求"""
        requirements = await mock_extractor.extract_async(sample_document)
        
        # 验证基本结果
        assert len(requirements) >= 1
        
        # 验证需求结构
        req = requirements[0]
        assert req.id == "REQ-001"
        assert req.title == "模拟需求"
        assert req.type == RequirementType.FUNCTIONAL
        assert req.priority == Priority.MEDIUM
        assert len(req.acceptance_criteria) >= 1
        assert req.source_document == sample_document.title
        assert "mock" in req.extracted_by.lower()
    
    def test_extract_sync_method(self, mock_extractor, sample_document):
        """测试同步提取方法"""
        requirements = mock_extractor.extract(sample_document)
        
        assert len(requirements) >= 1
        assert requirements[0].title == "模拟需求"
    
    @pytest.mark.asyncio
    async def test_extract_with_custom_prompt(self, mock_extractor, sample_document):
        """测试使用自定义提示词"""
        custom_prompt = "请专注于API设计需求的提取"
        
        requirements = await mock_extractor.extract_async(sample_document, custom_prompt=custom_prompt)
        
        # MOCK提供商会返回固定结果，但应该能正常处理自定义提示词
        assert len(requirements) >= 1
    
    @pytest.mark.asyncio
    async def test_extract_accuracy_validation(self, mock_extractor, sample_document):
        """测试提取准确率验证"""
        result = await mock_extractor.extract_with_accuracy(sample_document, expected_count=2)
        
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
    
    def test_create_requirement_collection(self, mock_extractor, sample_document):
        """测试创建需求集合"""
        requirements = mock_extractor.extract(sample_document)
        collection = mock_extractor.create_requirement_collection(requirements)
        
        assert collection.total_count == len(requirements)
        assert collection.functional_count >= 0
        assert collection.requirements == requirements
    
    def test_validate_extraction_quality(self, mock_extractor, sample_document):
        """测试提取质量验证"""
        requirements = mock_extractor.extract(sample_document)
        quality_result = mock_extractor.validate_extraction_quality(requirements)
        
        # 验证质量评估结果
        assert 'quality_score' in quality_result
        assert 'issues' in quality_result
        assert 'recommendations' in quality_result
        assert 'type_distribution' in quality_result
        assert 'priority_distribution' in quality_result
        
        # 验证数据类型
        assert isinstance(quality_result['quality_score'], float)
        assert isinstance(quality_result['issues'], list)
        assert isinstance(quality_result['recommendations'], list)
        assert isinstance(quality_result['type_distribution'], dict)
        assert isinstance(quality_result['priority_distribution'], dict)

class TestAIProviders:
    """测试不同AI提供商"""
    
    def test_mock_provider_initialization(self):
        """测试MOCK提供商初始化"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK)
        assert extractor.provider == AIProvider.MOCK
        assert extractor.model == "mock-model"
    
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
    
    @pytest.mark.asyncio
    async def test_unsupported_provider_error(self):
        """测试不支持的提供商错误"""
        # 创建一个无效的提供商
        extractor = LangChainExtractor(provider=AIProvider.MOCK)
        extractor.provider = "invalid_provider"  # 手动设置无效提供商
        
        document = Document(
            title="测试",
            content="测试内容",
            document_type=DocumentType.MARKDOWN
        )
        
        with pytest.raises(Exception, match="需求提取失败"):
            await extractor.extract_async(document)
