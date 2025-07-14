# TestMind AI

AI驱动的自动化测试平台，支持传统软件测试和AI应用测试的统一解决方案。

## 项目概述

TestMind AI 通过智能化的需求分析、测试用例生成、质量审查和执行管理，显著提升测试效率和质量。

## 核心功能

- **智能需求解析** - 自动解析PRD文档，提取关键测试点
- **测试用例生成** - 支持接口测试、功能测试、Prompt测试
- **AI质量审查** - 多维度测试用例质量评估
- **测试执行引擎** - 统一的测试执行和监控
- **智能结果分析** - 深度分析测试结果，提供改进建议

## 技术栈

- **Backend**: FastAPI + Pydantic
- **AI Framework**: LangChain + OpenAI/Claude API
- **Testing**: pytest + requests + selenium
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Queue**: Celery + Redis
- **Frontend**: Streamlit (MVP) → React (Production)

## 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 12+
- Redis 6+

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/your-org/testmind-ai.git
cd testmind-ai
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和API密钥
```

5. 启动服务
```bash
uvicorn src.main:app --reload
```

## 项目结构

```
testmind-ai/
├── src/
│   ├── core/           # 核心业务逻辑
│   ├── api/            # API接口
│   ├── models/         # 数据模型
│   ├── services/       # 业务服务
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── docs/               # 文档
├── requirements.txt    # 依赖列表
└── README.md          # 项目说明
```

## 开发路线图

### MVP版本
- [x] 项目架构搭建
- [ ] 需求解析功能
- [ ] 接口测试用例生成
- [ ] 基础测试执行
- [ ] 简单报告生成

### V1.0版本
- [ ] 功能测试支持
- [ ] AI质量审查
- [ ] 用户界面优化
- [ ] 团队协作功能

### V2.0版本
- [ ] Prompt测试能力
- [ ] 高级分析功能
- [ ] CI/CD集成
- [ ] 企业级功能

## 文档

- [产品需求文档 (PRD)](PRD.md)
- [API文档](docs/api.md)
- [开发指南](docs/development.md)
- [部署指南](docs/deployment.md)

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

