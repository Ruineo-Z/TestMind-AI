"""
测试模板数据模型
定义测试用例模板的结构
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TemplateType(str, Enum):
    """模板类型枚举"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    REQUESTS = "requests"


class TestTemplate(BaseModel):
    """测试模板模型"""
    
    # 基本信息
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    template_type: TemplateType = Field(..., description="模板类型")
    version: str = Field(default="1.0.0", description="模板版本")
    
    # 模板内容
    header_template: str = Field(..., description="文件头部模板")
    import_template: str = Field(..., description="导入语句模板")
    setup_template: str = Field(..., description="测试前置模板")
    test_case_template: str = Field(..., description="测试用例模板")
    teardown_template: str = Field(..., description="测试后置模板")
    
    # 配置参数
    required_imports: List[str] = Field(default_factory=list, description="必需的导入模块")
    optional_imports: List[str] = Field(default_factory=list, description="可选的导入模块")
    template_variables: Dict[str, Any] = Field(default_factory=dict, description="模板变量")
    
    # 元数据
    author: str = Field(default="TestMind AI", description="模板作者")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "pytest_api_template",
                "description": "用于API测试的pytest模板",
                "template_type": "pytest",
                "version": "1.0.0",
                "required_imports": ["pytest", "httpx", "json"],
                "optional_imports": ["asyncio", "time"],
                "template_variables": {
                    "base_url": "https://api.example.com",
                    "timeout": 30,
                    "headers": {"Content-Type": "application/json"}
                }
            }
        }


# 预定义的pytest模板
PYTEST_API_TEMPLATE = TestTemplate(
    name="pytest_api_template",
    description="用于API接口测试的pytest模板",
    template_type=TemplateType.PYTEST,
    version="1.0.0",
    
    header_template='''"""
{api_title} - 自动生成的API测试用例
生成时间: {generation_time}
API版本: {api_version}
测试框架: pytest + httpx
"""''',
    
    import_template='''import pytest
import httpx
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime''',
    
    setup_template='''
@pytest.fixture
async def api_client():
    """创建API客户端"""
    async with httpx.AsyncClient(
        base_url="{base_url}",
        timeout=30.0,
        headers={{"Content-Type": "application/json"}}
    ) as client:
        yield client


@pytest.fixture
def test_data():
    """测试数据"""
    return {{
        "timestamp": datetime.now().isoformat(),
        "test_run_id": "test_{{}}".format(int(datetime.now().timestamp()))
    }}
''',
    
    test_case_template='''
@pytest.mark.asyncio
async def {test_function_name}(api_client, test_data):
    """
    {test_description}
    
    测试类型: {test_type}
    端点: {http_method} {endpoint_path}
    期望状态码: {expected_status_code}
    """
    # 准备请求数据
    url = "{endpoint_path}"
    method = "{http_method}"
    headers = {request_headers}
    params = {request_params}
    json_data = {request_body}
    
    # 发送请求
    response = await api_client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json_data
    )
    
    # 验证响应
    assert response.status_code == {expected_status_code}, f"期望状态码 {expected_status_code}, 实际 {{response.status_code}}"
    
    # 验证响应内容
    if response.status_code == 200:
        response_data = response.json()
        {validation_code}
    
    # 记录测试结果
    print(f"✅ {{test_data['test_run_id']}}: {test_function_name} - 通过")
''',
    
    teardown_template='''
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "api: API接口测试标记"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项配置"""
    for item in items:
        item.add_marker(pytest.mark.api)
''',
    
    required_imports=["pytest", "httpx", "json", "asyncio"],
    optional_imports=["datetime", "typing"],
    template_variables={
        "base_url": "https://api.example.com",
        "timeout": 30,
        "content_type": "application/json"
    }
)
