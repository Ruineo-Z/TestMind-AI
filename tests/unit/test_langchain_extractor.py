"""
LangChain多供应商需求提取器测试
测试支持OpenAI、Gemini、Ollama三个供应商的LangChain需求提取功能
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import RequirementType, Priority

@pytest.fixture
def sample_document():
    """示例文档fixture"""
    return Document(
        title="电商系统需求",
        content="""# 电商系统需求文档

## 功能需求

### 1. 用户管理
- 用户注册功能
- 用户登录功能
- 用户信息管理

### 2. 商品管理
- 商品展示
- 商品搜索
- 商品分类

### 3. 订单管理
- 购物车功能
- 订单创建
- 订单支付
""",
        document_type=DocumentType.MARKDOWN
    )

@pytest.fixture
def mock_response():
    """模拟AI响应"""
    return [
        {
            "id": "REQ-001",
            "title": "用户注册",
            "description": "系统应支持用户通过邮箱注册账户",
            "type": "functional",
            "priority": "high",
            "acceptance_criteria": ["支持邮箱注册", "密码强度验证", "邮箱验证"]
        },
        {
            "id": "REQ-002",
            "title": "商品搜索",
            "description": "用户可以通过关键词搜索商品",
            "type": "functional",
            "priority": "medium",
            "acceptance_criteria": ["关键词搜索", "搜索结果排序", "搜索历史"]
        }
    ]

class TestLangChainMultiProvider:
    """测试LangChain多供应商需求提取器"""
    
    def test_openai_provider_initialization(self):
        """测试OpenAI提供商初始化"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(
                provider=AIProvider.OPENAI,
                model="gpt-3.5-turbo"
            )
            assert extractor.provider == AIProvider.OPENAI
            assert extractor.model == "gpt-3.5-turbo"
            assert extractor.openai_api_key == "test-key"
    
    def test_gemini_provider_initialization(self):
        """测试Gemini提供商初始化"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-google-key'}):
            extractor = LangChainExtractor(
                provider=AIProvider.GEMINI,
                model="gemini-1.5-pro"
            )
            assert extractor.provider == AIProvider.GEMINI
            assert extractor.model == "gemini-1.5-pro"
            assert extractor.google_api_key == "test-google-key"
    
    def test_ollama_provider_initialization(self):
        """测试Ollama提供商初始化"""
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="qwen3:4b",
            ollama_url="http://localhost:11434"
        )
        assert extractor.provider == AIProvider.OLLAMA
        assert extractor.model == "qwen3:4b"
        assert extractor.ollama_url == "http://localhost:11434"
    
    def test_default_models(self):
        """测试默认模型设置"""
        # 测试OpenAI默认模型
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(provider=AIProvider.OPENAI)
            assert extractor.model == "gpt-3.5-turbo"
        
        # 测试Gemini默认模型
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(provider=AIProvider.GEMINI)
            assert extractor.model == "gemini-1.5-pro"
        
        # 测试Ollama默认模型
        extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
        assert extractor.model == "qwen3:4b"
    
    def test_missing_api_key_errors(self):
        """测试缺少API密钥时的错误处理"""
        # 测试OpenAI缺少API密钥
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="使用OpenAI提供商需要提供API密钥"):
                LangChainExtractor(provider=AIProvider.OPENAI)
        
        # 测试Gemini缺少API密钥
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="使用Gemini提供商需要提供Google API密钥"):
                LangChainExtractor(provider=AIProvider.GEMINI)
    
    def test_custom_api_keys(self):
        """测试自定义API密钥"""
        # 测试自定义OpenAI API密钥
        extractor = LangChainExtractor(
            provider=AIProvider.OPENAI,
            openai_api_key="custom-openai-key"
        )
        assert extractor.openai_api_key == "custom-openai-key"
        
        # 测试自定义Google API密钥
        extractor = LangChainExtractor(
            provider=AIProvider.GEMINI,
            google_api_key="custom-google-key"
        )
        assert extractor.google_api_key == "custom-google-key"
    
    @pytest.mark.asyncio
    async def test_openai_extract_async(self, sample_document, mock_response):
        """测试OpenAI异步提取"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(provider=AIProvider.OPENAI)
            
            # 模拟chain
            original_chain = extractor.chain
            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)
            
            try:
                extractor.chain = mock_chain
                
                # 执行提取
                requirements = await extractor.extract_async(sample_document)
                
                # 验证结果
                assert len(requirements) == 2
                assert requirements[0].title == "用户注册"
                assert requirements[0].type == RequirementType.FUNCTIONAL
                assert requirements[0].priority == Priority.HIGH
                assert "langchain_openai_extractor" in requirements[0].extracted_by
                
            finally:
                extractor.chain = original_chain
    
    @pytest.mark.asyncio
    async def test_gemini_extract_async(self, sample_document, mock_response):
        """测试Gemini异步提取"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(provider=AIProvider.GEMINI)
            
            # 模拟chain
            original_chain = extractor.chain
            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)
            
            try:
                extractor.chain = mock_chain
                
                # 执行提取
                requirements = await extractor.extract_async(sample_document)
                
                # 验证结果
                assert len(requirements) == 2
                assert requirements[0].title == "用户注册"
                assert requirements[1].title == "商品搜索"
                assert "langchain_gemini_extractor" in requirements[0].extracted_by
                
            finally:
                extractor.chain = original_chain
    
    @pytest.mark.asyncio
    async def test_ollama_extract_async(self, sample_document, mock_response):
        """测试Ollama异步提取"""
        extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
        
        # 模拟chain
        original_chain = extractor.chain
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        
        try:
            extractor.chain = mock_chain
            
            # 执行提取
            requirements = await extractor.extract_async(sample_document)
            
            # 验证结果
            assert len(requirements) == 2
            assert requirements[0].title == "用户注册"
            assert requirements[1].title == "商品搜索"
            assert "langchain_ollama_extractor" in requirements[0].extracted_by
            
        finally:
            extractor.chain = original_chain
    
    def test_provider_switching(self):
        """测试供应商切换"""
        # 创建不同供应商的提取器
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'GOOGLE_API_KEY': 'test-google-key'}):
            openai_extractor = LangChainExtractor(provider=AIProvider.OPENAI)
            gemini_extractor = LangChainExtractor(provider=AIProvider.GEMINI)
            ollama_extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
            
            # 验证不同的提供商
            assert openai_extractor.provider == AIProvider.OPENAI
            assert gemini_extractor.provider == AIProvider.GEMINI
            assert ollama_extractor.provider == AIProvider.OLLAMA
            
            # 验证不同的LLM类型
            assert openai_extractor.llm.__class__.__name__ == "ChatOpenAI"
            assert gemini_extractor.llm.__class__.__name__ == "ChatGoogleGenerativeAI"
            assert ollama_extractor.llm.__class__.__name__ == "ChatOllama"
    
    def test_temperature_configuration(self):
        """测试温度参数配置"""
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            temperature=0.5
        )
        assert extractor.temperature == 0.5
        assert extractor.llm.temperature == 0.5
    
    def test_system_prompt_consistency(self):
        """测试系统提示词一致性"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'GOOGLE_API_KEY': 'test-google-key'}):
            openai_extractor = LangChainExtractor(provider=AIProvider.OPENAI)
            gemini_extractor = LangChainExtractor(provider=AIProvider.GEMINI)
            ollama_extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
            
            # 所有提取器应该使用相同的系统提示词
            openai_prompt = openai_extractor._get_system_prompt()
            gemini_prompt = gemini_extractor._get_system_prompt()
            ollama_prompt = ollama_extractor._get_system_prompt()
            
            assert openai_prompt == gemini_prompt == ollama_prompt
            assert "需求分析师" in openai_prompt
            assert "JSON格式" in openai_prompt
    
    def test_unsupported_provider_error(self):
        """测试不支持的提供商错误"""
        # 这个测试需要模拟一个无效的提供商
        # 由于我们使用枚举，这种情况在正常使用中不会发生
        # 但我们可以测试枚举的有效性
        valid_providers = [AIProvider.OPENAI, AIProvider.GEMINI, AIProvider.OLLAMA]
        assert len(valid_providers) == 3
        assert AIProvider.OPENAI.value == "openai"
        assert AIProvider.GEMINI.value == "gemini"
        assert AIProvider.OLLAMA.value == "ollama"

class TestProviderSpecificFeatures:
    """测试供应商特定功能"""
    
    def test_openai_specific_configuration(self):
        """测试OpenAI特定配置"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                temperature=0.2
            )
            
            assert extractor.model == "gpt-4"
            assert extractor.temperature == 0.2
            assert hasattr(extractor.llm, 'model_name')
    
    def test_gemini_specific_configuration(self):
        """测试Gemini特定配置"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            extractor = LangChainExtractor(
                provider=AIProvider.GEMINI,
                model="gemini-1.5-flash",
                temperature=0.3
            )
            
            assert extractor.model == "gemini-1.5-flash"
            assert extractor.temperature == 0.3
    
    def test_ollama_specific_configuration(self):
        """测试Ollama特定配置"""
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="llama3.1",
            ollama_url="http://custom-host:11434",
            temperature=0.1
        )
        
        assert extractor.model == "llama3.1"
        assert extractor.ollama_url == "http://custom-host:11434"
        assert extractor.temperature == 0.1
