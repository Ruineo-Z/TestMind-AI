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
你是一位资深的API测试专家，请基于API分析和测试策略生成完整的测试用例。

API分析结果：
{json.dumps(api_analysis, ensure_ascii=False, indent=2)}

测试策略：
{json.dumps(test_strategy, ensure_ascii=False, indent=2)}

**重要要求**：
1. 必须生成正向、负向、边界三种类型的测试用例
2. 每种类型至少生成2个测试用例
3. 测试用例必须覆盖API的所有主要端点
4. 使用真实的测试数据，避免使用mock数据

**测试用例生成规则**：

**正向测试用例 (positive)**：
- 测试正常的成功场景
- 使用有效的参数和数据
- 期望返回2xx状态码
- 验证响应数据的正确性

**负向测试用例 (negative)**：
- 测试错误和异常场景
- 使用无效参数、缺失参数、错误格式
- 期望返回4xx或5xx状态码
- 验证错误处理的正确性

**边界测试用例 (boundary)**：
- 测试边界条件和极限值
- 空值、最大值、最小值、特殊字符
- 测试参数长度限制
- 验证边界处理的正确性

请严格按照以下JSON格式返回测试用例，确保JSON格式正确：

```json
{{
    "test_cases": [
        {{
            "name": "test_get_welcome_success",
            "description": "测试获取欢迎消息成功场景",
            "type": "positive",
            "endpoint": "/",
            "method": "GET",
            "headers": {{}},
            "params": {{}},
            "body": null,
            "expected_status": 200,
            "expected_response": {{"message": "string"}},
            "validations": ["response.status_code == 200", "response.message is not None"]
        }},
        {{
            "name": "test_get_items_success",
            "description": "测试获取项目列表成功场景",
            "type": "positive",
            "endpoint": "/items",
            "method": "GET",
            "headers": {{}},
            "params": {{}},
            "body": null,
            "expected_status": 200,
            "expected_response": [],
            "validations": ["response.status_code == 200", "isinstance(response.json(), list)"]
        }},
        {{
            "name": "test_create_item_invalid_data",
            "description": "测试创建项目时使用无效数据",
            "type": "negative",
            "endpoint": "/items",
            "method": "POST",
            "headers": {{"Content-Type": "application/json"}},
            "params": {{}},
            "body": {{"invalid": "data"}},
            "expected_status": 422,
            "expected_response": {{"detail": "string"}},
            "validations": ["response.status_code == 422"]
        }},
        {{
            "name": "test_delete_nonexistent_item",
            "description": "测试删除不存在的项目",
            "type": "negative",
            "endpoint": "/items/99999",
            "method": "DELETE",
            "headers": {{}},
            "params": {{"item_id": "99999"}},
            "body": null,
            "expected_status": 404,
            "expected_response": {{"detail": "string"}},
            "validations": ["response.status_code == 404"]
        }},
        {{
            "name": "test_create_item_empty_body",
            "description": "测试创建项目时使用空请求体",
            "type": "boundary",
            "endpoint": "/items",
            "method": "POST",
            "headers": {{"Content-Type": "application/json"}},
            "params": {{}},
            "body": {{}},
            "expected_status": 422,
            "expected_response": {{"detail": "string"}},
            "validations": ["response.status_code in [400, 422]"]
        }},
        {{
            "name": "test_invalid_http_method",
            "description": "测试使用不支持的HTTP方法",
            "type": "boundary",
            "endpoint": "/",
            "method": "PATCH",
            "headers": {{}},
            "params": {{}},
            "body": null,
            "expected_status": 405,
            "expected_response": {{}},
            "validations": ["response.status_code == 405"]
        }}
    ]
}}
```

**注意事项**：
1. 确保JSON格式完全正确，没有语法错误
2. 每个测试用例都必须包含所有必需字段
3. 测试名称必须以"test_"开头，符合pytest规范
4. 测试类型必须是"positive"、"negative"或"boundary"之一
5. 根据实际API端点调整endpoint和method字段
6. 确保生成至少6个测试用例，覆盖三种类型
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
