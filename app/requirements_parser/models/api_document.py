"""
API文档数据模型
定义API文档的结构化数据模型，支持OpenAPI、Swagger等格式
"""
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class HTTPMethod(str, Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ParameterLocation(str, Enum):
    """参数位置枚举"""
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"
    BODY = "body"


class APIParameter(BaseModel):
    """API参数模型"""
    name: str = Field(..., description="参数名称")
    location: ParameterLocation = Field(..., description="参数位置")
    type: str = Field(..., description="参数类型")
    required: bool = Field(default=False, description="是否必需")
    description: Optional[str] = Field(None, description="参数描述")
    example: Optional[Any] = Field(None, description="参数示例")
    default: Optional[Any] = Field(None, description="默认值")
    enum: Optional[List[Any]] = Field(None, description="枚举值")
    format: Optional[str] = Field(None, description="参数格式")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证参数名称"""
        if not v or not v.strip():
            raise ValueError("参数名称不能为空")
        return v.strip()


class APIRequestBody(BaseModel):
    """API请求体模型"""
    content_type: str = Field(default="application/json", description="内容类型")
    body_schema: Dict[str, Any] = Field(..., description="请求体结构")
    required: bool = Field(default=True, description="是否必需")
    description: Optional[str] = Field(None, description="请求体描述")
    examples: Optional[Dict[str, Any]] = Field(None, description="请求体示例")


class APIResponse(BaseModel):
    """API响应模型"""
    status_code: str = Field(..., description="状态码")
    description: str = Field(..., description="响应描述")
    content_type: str = Field(default="application/json", description="响应内容类型")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="响应结构")
    examples: Optional[Dict[str, Any]] = Field(None, description="响应示例")
    headers: Optional[Dict[str, APIParameter]] = Field(None, description="响应头")


class APIEndpoint(BaseModel):
    """API端点模型"""
    path: str = Field(..., description="API路径")
    method: HTTPMethod = Field(..., description="HTTP方法")
    summary: str = Field(..., description="接口摘要")
    description: Optional[str] = Field(None, description="接口详细描述")
    operation_id: Optional[str] = Field(None, description="操作ID")
    tags: Optional[List[str]] = Field(None, description="标签")
    parameters: List[APIParameter] = Field(default_factory=list, description="参数列表")
    request_body: Optional[APIRequestBody] = Field(None, description="请求体")
    responses: Dict[str, APIResponse] = Field(..., description="响应定义")
    deprecated: bool = Field(default=False, description="是否已废弃")
    security: Optional[List[Dict[str, List[str]]]] = Field(None, description="安全要求")
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v):
        """验证API路径"""
        if not v or not v.strip():
            raise ValueError("API路径不能为空")
        if not v.startswith('/'):
            v = '/' + v
        return v
    
    @field_validator('summary')
    @classmethod
    def validate_summary(cls, v):
        """验证接口摘要"""
        if not v or not v.strip():
            raise ValueError("接口摘要不能为空")
        return v.strip()


class APISecurityScheme(BaseModel):
    """API安全方案模型"""
    type: str = Field(..., description="安全类型")
    description: Optional[str] = Field(None, description="安全方案描述")
    name: Optional[str] = Field(None, description="参数名称")
    location: Optional[str] = Field(None, description="参数位置")
    scheme: Optional[str] = Field(None, description="HTTP认证方案")
    bearer_format: Optional[str] = Field(None, description="Bearer格式")


class APIInfo(BaseModel):
    """API信息模型"""
    title: str = Field(..., description="API标题")
    version: str = Field(..., description="API版本")
    description: Optional[str] = Field(None, description="API描述")
    terms_of_service: Optional[str] = Field(None, description="服务条款")
    contact: Optional[Dict[str, str]] = Field(None, description="联系信息")
    license: Optional[Dict[str, str]] = Field(None, description="许可证信息")


class APIServer(BaseModel):
    """API服务器模型"""
    url: str = Field(..., description="服务器URL")
    description: Optional[str] = Field(None, description="服务器描述")
    variables: Optional[Dict[str, Any]] = Field(None, description="服务器变量")


class APIDocument(BaseModel):
    """API文档模型"""
    info: APIInfo = Field(..., description="API基本信息")
    servers: List[APIServer] = Field(default_factory=list, description="服务器列表")
    endpoints: List[APIEndpoint] = Field(default_factory=list, description="API端点列表")
    components: Optional[Dict[str, Any]] = Field(None, description="可重用组件")
    security: Optional[List[Dict[str, List[str]]]] = Field(None, description="全局安全要求")
    security_schemes: Optional[Dict[str, APISecurityScheme]] = Field(None, description="安全方案定义")
    tags: Optional[List[Dict[str, str]]] = Field(None, description="标签定义")
    external_docs: Optional[Dict[str, str]] = Field(None, description="外部文档")
    
    # 解析相关的元数据
    source_format: str = Field(..., description="源文档格式")  # openapi, swagger, markdown
    source_version: Optional[str] = Field(None, description="源文档版本")
    parsing_accuracy: Optional[float] = Field(None, description="解析准确率")
    parsing_warnings: List[str] = Field(default_factory=list, description="解析警告")
    
    @field_validator('endpoints')
    @classmethod
    def validate_endpoints(cls, v):
        """验证端点列表"""
        if not v:
            raise ValueError("API文档必须包含至少一个端点")
        return v
    
    def get_endpoint_by_path_method(self, path: str, method: HTTPMethod) -> Optional[APIEndpoint]:
        """根据路径和方法获取端点"""
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method == method:
                return endpoint
        return None
    
    def get_endpoints_by_tag(self, tag: str) -> List[APIEndpoint]:
        """根据标签获取端点列表"""
        return [
            endpoint for endpoint in self.endpoints
            if endpoint.tags and tag in endpoint.tags
        ]
    
    def get_all_paths(self) -> List[str]:
        """获取所有API路径"""
        return list(set(endpoint.path for endpoint in self.endpoints))
    
    def get_methods_for_path(self, path: str) -> List[HTTPMethod]:
        """获取指定路径支持的HTTP方法"""
        return [
            endpoint.method for endpoint in self.endpoints
            if endpoint.path == path
        ]
