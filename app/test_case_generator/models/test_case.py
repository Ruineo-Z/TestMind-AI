"""
测试用例数据模型
定义测试用例的结构和类型
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TestType(str, Enum):
    """测试用例类型枚举"""
    POSITIVE = "positive"  # 正向测试
    NEGATIVE = "negative"  # 负向测试
    BOUNDARY = "boundary"  # 边界测试


class TestResult(str, Enum):
    """测试结果枚举"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class TestCase(BaseModel):
    """单个测试用例模型"""
    
    # 基本信息
    name: str = Field(..., description="测试用例名称")
    description: str = Field(..., description="测试用例描述")
    test_type: TestType = Field(..., description="测试类型")
    
    # API相关信息
    endpoint_path: str = Field(..., description="API端点路径")
    http_method: str = Field(..., description="HTTP方法")
    
    # 测试数据
    request_headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    request_params: Dict[str, Any] = Field(default_factory=dict, description="请求参数")
    request_body: Optional[Dict[str, Any]] = Field(None, description="请求体")
    
    # 期望结果
    expected_status_code: int = Field(..., description="期望的HTTP状态码")
    expected_response_schema: Optional[Dict[str, Any]] = Field(None, description="期望的响应结构")
    expected_error_message: Optional[str] = Field(None, description="期望的错误信息")
    
    # 验证规则
    validation_rules: List[str] = Field(default_factory=list, description="验证规则列表")
    
    # 元数据
    tags: List[str] = Field(default_factory=list, description="测试标签")
    priority: int = Field(default=1, description="优先级 1-5")
    timeout: int = Field(default=30, description="超时时间(秒)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "test_get_user_success",
                "description": "测试获取用户信息成功场景",
                "test_type": "positive",
                "endpoint_path": "/api/v1/users/{user_id}",
                "http_method": "GET",
                "request_params": {"user_id": "123"},
                "expected_status_code": 200,
                "validation_rules": ["response.user_id == '123'"],
                "tags": ["user", "get"],
                "priority": 1
            }
        }


class TestSuite(BaseModel):
    """测试套件模型"""
    
    # 基本信息
    name: str = Field(..., description="测试套件名称")
    description: str = Field(..., description="测试套件描述")
    
    # API信息
    api_title: str = Field(..., description="API标题")
    api_version: str = Field(..., description="API版本")
    base_url: str = Field(..., description="API基础URL")
    
    # 测试用例
    test_cases: List[TestCase] = Field(default_factory=list, description="测试用例列表")
    
    # 统计信息
    total_tests: int = Field(default=0, description="总测试数量")
    positive_tests: int = Field(default=0, description="正向测试数量")
    negative_tests: int = Field(default=0, description="负向测试数量")
    boundary_tests: int = Field(default=0, description="边界测试数量")
    
    # 配置信息
    setup_code: Optional[str] = Field(None, description="测试前置代码")
    teardown_code: Optional[str] = Field(None, description="测试后置代码")
    
    def add_test_case(self, test_case: TestCase) -> None:
        """添加测试用例"""
        self.test_cases.append(test_case)
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """更新统计信息"""
        self.total_tests = len(self.test_cases)
        self.positive_tests = len([tc for tc in self.test_cases if tc.test_type == TestType.POSITIVE])
        self.negative_tests = len([tc for tc in self.test_cases if tc.test_type == TestType.NEGATIVE])
        self.boundary_tests = len([tc for tc in self.test_cases if tc.test_type == TestType.BOUNDARY])
    
    def get_tests_by_type(self, test_type: TestType) -> List[TestCase]:
        """根据类型获取测试用例"""
        return [tc for tc in self.test_cases if tc.test_type == test_type]
    
    def get_tests_by_endpoint(self, endpoint_path: str) -> List[TestCase]:
        """根据端点获取测试用例"""
        return [tc for tc in self.test_cases if tc.endpoint_path == endpoint_path]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "UserAPI测试套件",
                "description": "用户管理API的完整测试套件",
                "api_title": "User Management API",
                "api_version": "1.0.0",
                "base_url": "https://api.example.com",
                "total_tests": 15,
                "positive_tests": 8,
                "negative_tests": 5,
                "boundary_tests": 2
            }
        }
