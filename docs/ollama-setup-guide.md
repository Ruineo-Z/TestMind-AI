# 🦙 Ollama本地AI部署指南

## 🎯 为什么选择Ollama？

✅ **完全免费** - 无API费用  
✅ **数据安全** - 本地运行，数据不出本地  
✅ **高性能** - 针对本地硬件优化  
✅ **多模型支持** - 支持Llama2、Mistral、CodeLlama等  
✅ **易于集成** - 与LangChain完美兼容  

## 🚀 快速安装

### Windows安装
```bash
# 下载并安装Ollama
# 访问 https://ollama.ai/download/windows
# 或使用winget
winget install Ollama.Ollama
```

### macOS安装
```bash
# 使用Homebrew
brew install ollama

# 或下载安装包
# https://ollama.ai/download/mac
```

### Linux安装
```bash
# 一键安装脚本
curl -fsSL https://ollama.ai/install.sh | sh
```

## 📦 推荐模型下载

### 1. Llama2 (推荐用于需求分析)
```bash
# 7B模型 (4GB内存)
ollama pull llama2

# 13B模型 (8GB内存) - 更准确
ollama pull llama2:13b

# 70B模型 (40GB内存) - 最准确
ollama pull llama2:70b
```

### 2. Mistral (快速响应)
```bash
# 7B模型 - 速度快
ollama pull mistral

# Mistral Instruct - 指令优化
ollama pull mistral:instruct
```

### 3. CodeLlama (代码理解)
```bash
# 代码专用模型
ollama pull codellama

# Python专用
ollama pull codellama:python
```

### 4. 中文优化模型
```bash
# 中文支持更好的模型
ollama pull qwen:7b
ollama pull baichuan2:7b
```

## ⚙️ TestMind AI配置

### 1. 环境变量配置
```bash
# .env文件
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
AI_PROVIDER=ollama
```

### 2. 代码使用示例
```python
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider

# 使用Ollama提取需求
extractor = LangChainExtractor(
    provider=AIProvider.OLLAMA,
    model="llama2",  # 或 "mistral", "codellama"
    ollama_url="http://localhost:11434"
)

# 提取需求
requirements = await extractor.extract_async(document)
```

### 3. 性能优化配置
```python
# 针对不同硬件的优化配置
configs = {
    "低配置": {
        "model": "llama2:7b",
        "temperature": 0.1,
        "max_tokens": 1000
    },
    "中配置": {
        "model": "llama2:13b", 
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "高配置": {
        "model": "llama2:70b",
        "temperature": 0.05,
        "max_tokens": 4000
    }
}
```

## 🔧 启动和管理

### 启动Ollama服务
```bash
# 启动服务
ollama serve

# 后台运行
nohup ollama serve > ollama.log 2>&1 &
```

### 模型管理
```bash
# 查看已安装模型
ollama list

# 删除模型
ollama rm llama2

# 更新模型
ollama pull llama2
```

### 性能监控
```bash
# 查看运行状态
ollama ps

# 查看模型信息
ollama show llama2
```

## 📊 性能对比

| 模型 | 大小 | 内存需求 | 速度 | 准确率 | 推荐用途 |
|------|------|----------|------|--------|----------|
| llama2:7b | 4GB | 8GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 快速原型 |
| llama2:13b | 7GB | 16GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 生产环境 |
| mistral:7b | 4GB | 8GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 平衡选择 |
| codellama:7b | 4GB | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 代码分析 |

## 🎯 TestMind AI集成测试

### 1. 基础功能测试
```python
# 测试Ollama连接
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama2",
    "prompt": "Hello, world!",
    "stream": False
})

print(response.json())
```

### 2. 需求提取测试
```python
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType

# 创建提取器
extractor = LangChainExtractor(provider=AIProvider.OLLAMA, model="llama2")

# 测试文档
document = Document(
    title="用户登录需求",
    content="用户需要能够通过邮箱和密码登录系统",
    document_type=DocumentType.MARKDOWN
)

# 提取需求
requirements = await extractor.extract_async(document)
print(f"提取到 {len(requirements)} 个需求")
```

## 🔍 故障排除

### 常见问题

#### 1. 端口占用
```bash
# 检查端口
netstat -an | grep 11434

# 更改端口
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

#### 2. 内存不足
```bash
# 使用更小的模型
ollama pull llama2:7b-q4_0  # 量化版本，更省内存
```

#### 3. 响应慢
```bash
# 检查GPU支持
ollama run llama2 --verbose

# 使用CPU优化
OLLAMA_NUM_PARALLEL=4 ollama serve
```

#### 4. 中文支持问题
```python
# 使用中文优化的提示词
system_prompt = """你是一个专业的中文需求分析师。
请用中文分析文档并提取需求信息。
返回格式必须是有效的JSON。"""
```

## 🚀 生产环境部署

### Docker部署
```dockerfile
# Dockerfile.ollama
FROM ollama/ollama:latest

# 预下载模型
RUN ollama pull llama2

EXPOSE 11434
CMD ["ollama", "serve"]
```

### docker-compose集成
```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      
  testmind-ai:
    build: .
    environment:
      - AI_PROVIDER=ollama
      - OLLAMA_URL=http://ollama:11434
      - OLLAMA_MODEL=llama2
    depends_on:
      - ollama

volumes:
  ollama_data:
```

## 📈 性能优化建议

### 硬件要求
- **最低配置**: 8GB RAM, 4核CPU
- **推荐配置**: 16GB RAM, 8核CPU  
- **最佳配置**: 32GB RAM, 16核CPU + GPU

### 软件优化
```bash
# 启用GPU加速 (NVIDIA)
OLLAMA_GPU=1 ollama serve

# 调整并发数
OLLAMA_NUM_PARALLEL=2 ollama serve

# 设置模型保持时间
OLLAMA_KEEP_ALIVE=10m ollama serve
```

## 🎉 开始使用

1. **安装Ollama**: 选择适合你系统的安装方式
2. **下载模型**: 推荐从`llama2`开始
3. **启动服务**: `ollama serve`
4. **配置TestMind AI**: 设置环境变量
5. **开始提取需求**: 享受免费的AI需求分析！

现在您可以完全免费地使用AI进行需求提取，无需担心API费用！🎊
