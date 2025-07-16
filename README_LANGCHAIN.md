# LangChain多供应商需求提取器

基于LangChain框架实现的AI驱动需求提取器，支持OpenAI、Google Gemini、Ollama三个主要AI供应商。

## 🌟 特性

- **多供应商支持**: 无缝切换OpenAI、Google Gemini、Ollama
- **真正的LangChain集成**: 使用LangChain的统一抽象而非直接调用各供应商SDK
- **异步处理**: 支持异步API调用和批量处理
- **灵活配置**: 支持自定义模型、温度参数等
- **质量评估**: 内置准确率和置信度评估
- **本地优先**: 默认使用本地Ollama模型，无需API密钥

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装LangChain相关包
uv add langchain-ollama langchain-openai langchain-google-genai langchain-core langchain-community
```

### 2. 基本使用

```python
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType

# 创建文档
document = Document(
    title="需求文档",
    content="# 用户管理系统\n- 用户注册\n- 用户登录",
    document_type=DocumentType.MARKDOWN
)

# 使用Ollama（本地模型，无需API密钥）
extractor = LangChainExtractor(
    provider=AIProvider.OLLAMA,
    model="qwen3:4b"  # 使用您本地的模型
)

# 提取需求
requirements = extractor.extract(document)
print(f"提取到 {len(requirements)} 个需求")
```

### 3. 异步使用

```python
import asyncio

async def extract_requirements():
    # 异步提取
    requirements = await extractor.extract_async(document)
    
    # 带准确率评估
    result = await extractor.extract_with_accuracy(document, expected_count=5)
    print(f"准确率: {result['accuracy']:.2%}")
    print(f"置信度: {result['confidence']:.2%}")

asyncio.run(extract_requirements())
```

## 🔧 供应商配置

### Ollama (推荐，本地运行)

```python
extractor = LangChainExtractor(
    provider=AIProvider.OLLAMA,
    model="qwen3:4b",  # 或其他本地模型
    ollama_url="http://localhost:11434"
)
```

**优势**: 无需API密钥，数据隐私，成本低
**要求**: 本地安装Ollama和模型

### OpenAI

```python
extractor = LangChainExtractor(
    provider=AIProvider.OPENAI,
    model="gpt-3.5-turbo",
    openai_api_key="your-api-key"  # 或设置环境变量OPENAI_API_KEY
)
```

**优势**: 高质量输出，稳定可靠
**要求**: OpenAI API密钥

### Google Gemini

```python
extractor = LangChainExtractor(
    provider=AIProvider.GEMINI,
    model="gemini-1.5-pro",
    google_api_key="your-api-key"  # 或设置环境变量GOOGLE_API_KEY
)
```

**优势**: 多模态支持，成本效益
**要求**: Google API密钥

## 📁 项目结构

```
app/requirements_parser/extractors/
├── langchain_extractor.py          # 主要的LangChain需求提取器
└── __init__.py

tests/unit/
├── test_langchain_extractor.py     # 完整的多供应商测试套件
└── ...

examples/
├── simple_langchain_demo.py        # 简单演示脚本
├── langchain_multi_provider_demo.py # 多供应商比较演示
└── ...

scripts/
├── check_ollama_models.py          # Ollama模型检查工具
└── ...
```

## 🧪 运行测试

```bash
# 运行所有LangChain测试
uv run pytest tests/unit/test_langchain_extractor.py -v

# 运行特定测试
uv run pytest tests/unit/test_langchain_extractor.py::TestLangChainMultiProvider::test_ollama_extract_async -v
```

## 🎯 演示脚本

### 简单演示
```bash
uv run python examples/simple_langchain_demo.py
```

### 多供应商比较
```bash
uv run python examples/langchain_multi_provider_demo.py
```

### 检查本地模型
```bash
uv run python scripts/check_ollama_models.py
```

## 🔍 高级功能

### 批量处理

```python
documents = [doc1, doc2, doc3]
results = await extractor.extract_batch(documents)
# 返回: {"文档1": [需求列表], "文档2": [需求列表], ...}
```

### 质量验证

```python
quality_result = extractor.validate_extraction_quality(requirements)
print(f"质量分数: {quality_result['quality_score']:.2%}")
print(f"发现问题: {len(quality_result['issues'])} 个")
```

### 需求集合管理

```python
collection = extractor.create_requirement_collection(requirements)
print(f"功能性需求: {collection.functional_count}")
print(f"非功能性需求: {collection.non_functional_count}")
```

## 🛠️ 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `provider` | AIProvider | OLLAMA | AI供应商 |
| `model` | str | qwen3:4b | 模型名称 |
| `temperature` | float | 0.1 | 温度参数 |
| `ollama_url` | str | http://localhost:11434 | Ollama服务地址 |
| `openai_api_key` | str | None | OpenAI API密钥 |
| `google_api_key` | str | None | Google API密钥 |

## 🐛 故障排除

### Ollama相关问题

1. **模型未找到**
   ```bash
   # 检查可用模型
   uv run python scripts/check_ollama_models.py
   
   # 下载模型
   ollama pull qwen3:4b
   ```

2. **服务未运行**
   ```bash
   # 启动Ollama服务
   ollama serve
   ```

### API密钥问题

1. **设置环境变量**
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export GOOGLE_API_KEY="your-google-key"
   ```

2. **代码中直接设置**
   ```python
   extractor = LangChainExtractor(
       provider=AIProvider.OPENAI,
       openai_api_key="your-key"
   )
   ```

## 📚 相关文档

- [LangChain官方文档](https://python.langchain.com/)
- [Ollama官方文档](https://ollama.ai/)
- [项目Sprint 2报告](project-management/sprint2-langchain-integration.md)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证。
