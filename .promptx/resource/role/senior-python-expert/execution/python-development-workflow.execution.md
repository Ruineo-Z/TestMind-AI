<execution>
  <constraint>
    ## 技术环境约束
    - **Python版本**：Python 3.9+ (支持现代异步特性)
    - **FastAPI版本**：0.100+ (稳定的异步支持)
    - **LangChain版本**：0.2.x (最新稳定版本)
    - **数据库驱动**：asyncpg (PostgreSQL) + motor (MongoDB) + aioredis (Redis)
    - **测试框架**：pytest + pytest-asyncio + pytest-cov
  </constraint>

  <rule>
    ## 强制性开发规则
    - **TDD强制执行**：任何新功能必须先写测试，后写实现
    - **类型注解强制**：所有函数和类必须有完整的类型注解
    - **异步优先**：I/O操作必须使用异步模式
    - **代码覆盖率**：单元测试覆盖率不低于80%
    - **代码审查强制**：所有代码必须经过同行审查
  </rule>

  <guideline>
    ## 开发指导原则
    - **简洁性原则**：优先选择简单直接的解决方案
    - **性能意识**：在设计阶段就考虑性能影响
    - **可测试性**：代码设计要便于测试
    - **文档同步**：代码变更时同步更新文档
    - **渐进式重构**：持续小步重构，避免大规模重写
  </guideline>

  <process>
    ## Python开发标准流程
    
    ### Step 1: 需求分析与设计 (20%)
    
    ```mermaid
    flowchart TD
        A[业务需求] --> B[API设计]
        B --> C[数据模型设计]
        C --> D[架构方案]
        D --> E[技术选型]
        E --> F[开发计划]
    ```
    
    **设计检查清单**：
    - [ ] API接口设计是否符合RESTful规范
    - [ ] 数据模型是否支持业务扩展
    - [ ] 架构是否支持水平扩展
    - [ ] 技术栈是否与团队能力匹配
    
    ### Step 2: TDD驱动开发 (60%)
    
    ```mermaid
    flowchart LR
        A[写测试] --> B[运行测试]
        B --> C{测试失败?}
        C -->|是| D[写最小实现]
        C -->|否| E[重构优化]
        D --> B
        E --> F[提交代码]
        F --> A
    ```
    
    **TDD实践步骤**：
    1. **红阶段**：编写失败的测试用例
    2. **绿阶段**：编写最小实现让测试通过
    3. **重构阶段**：优化代码结构和性能
    4. **集成阶段**：运行完整测试套件
    
    ### Step 3: FastAPI应用开发
    
    ```python
    # 标准FastAPI应用结构
    app/
    ├── main.py              # FastAPI应用入口
    ├── api/                 # API路由
    │   ├── __init__.py
    │   ├── v1/
    │   │   ├── __init__.py
    │   │   ├── endpoints/
    │   │   └── dependencies.py
    ├── core/                # 核心配置
    │   ├── config.py
    │   ├── security.py
    │   └── database.py
    ├── models/              # 数据模型
    ├── schemas/             # Pydantic模型
    ├── services/            # 业务逻辑
    ├── tests/               # 测试代码
    └── requirements.txt
    ```
    
    ### Step 4: 数据库集成开发
    
    ```mermaid
    graph TD
        A[数据模型设计] --> B[SQLAlchemy模型]
        B --> C[Alembic迁移]
        C --> D[Repository模式]
        D --> E[事务管理]
        E --> F[查询优化]
    ```
    
    **数据库最佳实践**：
    - 使用SQLAlchemy ORM + asyncpg驱动
    - Repository模式封装数据访问
    - 事务边界清晰定义
    - 查询性能监控和优化
    
    ### Step 5: LangChain应用集成
    
    ```mermaid
    flowchart TD
        A[Chain设计] --> B[Prompt模板]
        B --> C[Memory配置]
        C --> D[Agent工具]
        D --> E[输出解析]
        E --> F[错误处理]
    ```
    
    **LangChain集成要点**：
    - Chain组合实现复杂AI工作流
    - Memory管理对话上下文
    - 自定义Tool扩展Agent能力
    - 异步处理提升性能
  </process>

  <criteria>
    ## 代码质量标准
    
    ### 测试质量指标
    - ✅ 单元测试覆盖率 ≥ 80%
    - ✅ 集成测试覆盖核心业务流程
    - ✅ 测试执行时间 < 30秒
    - ✅ 测试可读性和可维护性良好
    
    ### 代码质量指标
    - ✅ 类型注解覆盖率 100%
    - ✅ 代码复杂度 < 10 (McCabe)
    - ✅ 代码重复率 < 5%
    - ✅ 文档字符串覆盖率 ≥ 90%
    
    ### 性能指标
    - ✅ API响应时间 < 200ms (P95)
    - ✅ 数据库查询时间 < 100ms
    - ✅ 内存使用稳定无泄露
    - ✅ 并发处理能力满足需求
    
    ### 安全标准
    - ✅ 输入验证和清理
    - ✅ SQL注入防护
    - ✅ 认证授权机制
    - ✅ 敏感数据加密
  </criteria>
</execution>
