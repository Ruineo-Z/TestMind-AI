"""
AI测试用例生成的专业提示词模板
针对不同阶段的AI任务设计专门的提示词
"""
from typing import Dict, List, Any
import json


class TestGenerationPrompts:
    """AI测试生成提示词管理器"""
    
    def get_api_analysis_prompt(self, api_description: str) -> str:
        """
        获取API文档分析提示词
        
        Args:
            api_description: API文档描述
            
        Returns:
            str: API分析提示词
        """
        return f"""
你是一位资深的API测试专家，请分析以下API文档并提供专业的测试分析。

API文档内容：
{api_description}

请从以下维度分析这个API：

1. **复杂度评估** (simple/medium/complex)：
   - 端点数量和复杂程度
   - 参数类型的多样性
   - 数据关联的复杂度

2. **认证需求分析**：
   - 是否需要认证
   - 认证方式推测
   - 权限控制复杂度

3. **数据类型分析**：
   - 涉及的主要数据类型
   - 特殊格式要求
   - 数据验证规则

4. **关键端点识别**：
   - 核心业务端点
   - 高风险操作端点
   - 依赖关系复杂的端点

5. **测试挑战预测**：
   - 可能的测试难点
   - 边界条件复杂的场景
   - 错误处理的复杂度

6. **推荐测试场景**：
   - 必须覆盖的核心场景
   - 重要的异常场景
   - 性能敏感的场景

请以JSON格式返回分析结果：
{{
    "complexity": "medium",
    "auth_required": true,
    "data_types": ["string", "integer", "object"],
    "critical_endpoints": ["/api/v1/users", "/api/v1/orders"],
    "challenges": ["复杂的数据验证", "多层级权限控制"],
    "scenarios": ["用户注册流程", "订单创建验证", "权限边界测试"]
}}
"""

    def get_test_strategy_prompt(
        self, 
        api_analysis: Dict[str, Any],
        include_positive: bool,
        include_negative: bool,
        include_boundary: bool
    ) -> str:
        """
        获取测试策略生成提示词
        
        Args:
            api_analysis: API分析结果
            include_positive: 是否包含正向测试
            include_negative: 是否包含负向测试
            include_boundary: 是否包含边界测试
            
        Returns:
            str: 测试策略提示词
        """
        test_types = []
        if include_positive:
            test_types.append("正向测试")
        if include_negative:
            test_types.append("负向测试")
        if include_boundary:
            test_types.append("边界测试")
        
        return f"""
基于以下API分析结果，请设计全面的测试策略：

API分析结果：
{json.dumps(api_analysis, ensure_ascii=False, indent=2)}

需要包含的测试类型：{', '.join(test_types)}

请设计详细的测试策略，包括：

1. **正向测试场景** (如果需要)：
   - 标准成功流程测试
   - 各种有效参数组合
   - 正常业务场景覆盖

2. **负向测试场景** (如果需要)：
   - 参数缺失测试
   - 无效参数类型测试
   - 权限不足测试
   - 业务规则违反测试

3. **边界测试场景** (如果需要)：
   - 参数最值测试
   - 空值处理测试
   - 特殊字符测试
   - 长度限制测试

4. **测试优先级**：
   - P0: 核心功能必须测试
   - P1: 重要功能应该测试
   - P2: 边缘情况可以测试

5. **覆盖目标**：
   - 功能覆盖率目标
   - 代码路径覆盖目标
   - 错误场景覆盖目标

6. **特殊考虑**：
   - 性能测试需求
   - 安全测试重点
   - 兼容性测试要求

请以JSON格式返回策略：
{{
    "positive_scenarios": ["场景1", "场景2"],
    "negative_scenarios": ["错误场景1", "错误场景2"],
    "boundary_scenarios": ["边界场景1", "边界场景2"],
    "priorities": {{"P0": ["核心测试"], "P1": ["重要测试"], "P2": ["边缘测试"]}},
    "coverage": {{"function": 90, "error": 80, "boundary": 70}},
    "considerations": ["性能考虑", "安全考虑"]
}}
"""

    def get_test_cases_prompt(
        self, 
        api_analysis: Dict[str, Any], 
        test_strategy: Dict[str, Any]
    ) -> str:
        """
        获取具体测试用例生成提示词
        
        Args:
            api_analysis: API分析结果
            test_strategy: 测试策略
            
        Returns:
            str: 测试用例生成提示词
        """
        return f"""
基于API分析和测试策略，请生成具体的测试用例：

API分析：
{json.dumps(api_analysis, ensure_ascii=False, indent=2)}

测试策略：
{json.dumps(test_strategy, ensure_ascii=False, indent=2)}

请为每个测试场景生成详细的测试用例，包括：

1. **测试用例基本信息**：
   - 测试名称（英文，符合pytest命名规范）
   - 测试描述（中文，清晰说明测试目的）
   - 测试类型（positive/negative/boundary）

2. **请求信息**：
   - HTTP方法和路径
   - 请求头（如果需要）
   - 请求参数（路径参数、查询参数）
   - 请求体（如果需要）

3. **期望结果**：
   - 期望的HTTP状态码
   - 期望的响应结构
   - 关键字段验证规则

4. **测试数据**：
   - 使用真实可能的测试数据
   - 避免使用mock或假数据
   - 考虑数据的业务合理性

请以JSON格式返回测试用例列表：
{{
    "test_cases": [
        {{
            "name": "test_get_user_success",
            "description": "测试获取用户信息成功场景",
            "type": "positive",
            "endpoint": "/api/v1/users/{{user_id}}",
            "method": "GET",
            "headers": {{"Authorization": "Bearer {{token}}"}},
            "params": {{"user_id": "12345"}},
            "body": null,
            "expected_status": 200,
            "expected_response": {{"user_id": "12345", "name": "string"}},
            "validations": ["response.user_id == params.user_id", "response.name is not None"]
        }}
    ]
}}
"""

    def get_code_generation_prompt(
        self, 
        api_document,
        test_cases: List[Dict[str, Any]], 
        test_framework: str
    ) -> str:
        """
        获取测试代码生成提示词
        
        Args:
            api_document: API文档对象
            test_cases: 测试用例列表
            test_framework: 测试框架
            
        Returns:
            str: 代码生成提示词
        """
        return f"""
请基于以下测试用例生成完整的{test_framework}测试代码：

API信息：
- 标题: {api_document.info.title}
- 版本: {api_document.info.version}
- 基础URL: {api_document.servers[0].url if api_document.servers else 'https://api.example.com'}

测试用例：
{json.dumps(test_cases, ensure_ascii=False, indent=2)}

代码生成要求：

1. **技术要求**：
   - 使用{test_framework}框架
   - 使用httpx作为HTTP客户端（禁用aiohttp）
   - 支持异步测试
   - 包含完整的错误处理

2. **代码结构**：
   - 文件头部注释（中文）
   - 必要的import语句
   - pytest fixtures设置
   - 每个测试用例对应一个测试函数
   - 清晰的断言和验证

3. **代码质量**：
   - 遵循PEP 8规范
   - 函数和重要逻辑添加中文注释
   - 使用有意义的变量名
   - 包含详细的断言信息

4. **测试数据**：
   - 使用真实的测试数据
   - 避免硬编码，使用参数化
   - 考虑数据的可维护性

5. **执行要求**：
   - 生成的代码必须可以直接执行
   - 包含必要的依赖检查
   - 提供清晰的执行说明

请生成完整的Python测试文件代码，以JSON格式返回：
{{
    "test_code": "完整的Python测试代码字符串"
}}
"""
