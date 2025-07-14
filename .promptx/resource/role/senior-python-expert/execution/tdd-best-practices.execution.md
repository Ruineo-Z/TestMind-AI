<execution>
  <constraint>
    ## TDD实践约束
    - **测试优先强制**：必须先写测试，再写实现代码
    - **测试独立性**：每个测试必须独立运行，不依赖其他测试
    - **测试确定性**：测试结果必须可重复，不受外部环境影响
    - **测试速度**：单元测试套件执行时间不超过30秒
    - **测试覆盖率**：核心业务逻辑测试覆盖率不低于90%
  </constraint>

  <rule>
    ## TDD强制规则
    - **红-绿-重构循环**：严格按照TDD三步骤执行
    - **最小实现原则**：只写让测试通过的最少代码
    - **重构安全网**：重构前必须有完整的测试覆盖
    - **测试命名规范**：测试名称必须清晰描述测试意图
    - **Mock使用原则**：只Mock外部依赖，不Mock被测试单元
  </rule>

  <guideline>
    ## TDD指导原则
    - **测试即文档**：测试用例是最好的使用文档
    - **简单设计**：通过TDD驱动简洁的设计
    - **快速反馈**：保持测试的快速执行
    - **持续重构**：在绿灯状态下持续改进代码
    - **团队协作**：通过测试促进团队协作
  </guideline>

  <process>
    ## TDD最佳实践流程
    
    ### Step 1: 测试设计与编写
    
    ```mermaid
    flowchart TD
        A[理解需求] --> B[设计测试用例]
        B --> C[编写失败测试]
        C --> D[验证测试失败]
        D --> E{测试合理?}
        E -->|否| B
        E -->|是| F[进入实现阶段]
    ```
    
    **测试用例设计原则**：
    - **AAA模式**：Arrange(准备) → Act(执行) → Assert(断言)
    - **边界测试**：正常值、边界值、异常值
    - **业务场景**：覆盖主要业务流程
    - **错误处理**：验证异常情况处理
    
    ### Step 2: FastAPI TDD实践
    
    ```python
    # 测试用例示例
    @pytest.mark.asyncio
    async def test_create_user_success():
        # Arrange
        user_data = {"name": "John", "email": "john@example.com"}
        
        # Act
        response = await client.post("/users", json=user_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == "John"
        assert "id" in response.json()
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_email():
        # Arrange
        user_data = {"name": "John", "email": "invalid-email"}
        
        # Act
        response = await client.post("/users", json=user_data)
        
        # Assert
        assert response.status_code == 422
        assert "email" in response.json()["detail"][0]["loc"]
    ```
    
    ### Step 3: 数据库测试策略
    
    ```mermaid
    graph TD
        A[测试数据库设置] --> B[事务开始]
        B --> C[执行测试]
        C --> D[断言验证]
        D --> E[事务回滚]
        E --> F[清理资源]
    ```
    
    **数据库测试最佳实践**：
    ```python
    @pytest.fixture
    async def db_session():
        # 创建测试事务
        async with async_session() as session:
            async with session.begin():
                yield session
                # 自动回滚事务
    
    @pytest.fixture
    def user_factory():
        def _create_user(**kwargs):
            defaults = {"name": "Test User", "email": "test@example.com"}
            defaults.update(kwargs)
            return User(**defaults)
        return _create_user
    ```
    
    ### Step 4: LangChain组件测试
    
    ```mermaid
    flowchart LR
        A[Mock LLM] --> B[测试Chain]
        B --> C[验证输出]
        C --> D[测试Memory]
        D --> E[验证状态]
    ```
    
    **LangChain测试策略**：
    ```python
    @pytest.fixture
    def mock_llm():
        return FakeLLM(responses=["Mocked response"])
    
    @pytest.mark.asyncio
    async def test_chain_execution(mock_llm):
        # Arrange
        chain = LLMChain(llm=mock_llm, prompt=test_prompt)
        
        # Act
        result = await chain.arun(input="test input")
        
        # Assert
        assert result == "Mocked response"
    ```
    
    ### Step 5: 重构与优化
    
    ```mermaid
    graph TD
        A[绿灯状态] --> B[识别代码异味]
        B --> C[设计重构方案]
        C --> D[执行重构]
        D --> E[运行测试]
        E --> F{测试通过?}
        F -->|是| G[提交代码]
        F -->|否| H[回滚重构]
        H --> C
    ```
    
    **重构检查清单**：
    - [ ] 消除代码重复
    - [ ] 提取公共方法
    - [ ] 简化复杂逻辑
    - [ ] 改善命名
    - [ ] 优化性能
  </process>

  <criteria>
    ## TDD质量标准
    
    ### 测试质量指标
    - ✅ 测试覆盖率：单元测试 ≥ 90%，集成测试 ≥ 70%
    - ✅ 测试执行速度：单元测试 < 30秒，集成测试 < 5分钟
    - ✅ 测试稳定性：测试通过率 ≥ 99%
    - ✅ 测试可读性：测试名称和结构清晰易懂
    
    ### 代码质量指标
    - ✅ 圈复杂度 < 10
    - ✅ 代码重复率 < 5%
    - ✅ 函数长度 < 50行
    - ✅ 类长度 < 500行
    
    ### TDD流程指标
    - ✅ 红-绿-重构循环时间 < 10分钟
    - ✅ 测试先行率 100%
    - ✅ 重构频率：每个功能至少1次重构
    - ✅ 测试维护成本 < 开发成本的30%
    
    ### 团队协作指标
    - ✅ 代码审查通过率 ≥ 95%
    - ✅ 测试用例可读性评分 ≥ 4.0/5.0
    - ✅ TDD实践一致性 ≥ 90%
    - ✅ 知识分享频率：每月至少1次TDD经验分享
  </criteria>
</execution>
