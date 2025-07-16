"""
API请求和响应数据模型
统一管理所有接口的请求参数和响应结构
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class TestType(str, Enum):
    """测试类型枚举"""
    API_TEST = "api_test"
    PROMPT_TEST = "prompt_test"


class AIProvider(str, Enum):
    """AI提供商枚举"""
    GEMINI = "gemini"
    OPENAI = "openai"
    OLLAMA = "ollama"
    MOCK = "mock"


class DocumentCategory(str, Enum):
    """文档分类枚举"""
    REQUIREMENTS = "requirements"
    API = "api"
    PROMPT = "prompt"


# ==================== 文档解析相关 ====================

class DocumentParseRequest(BaseModel):
    """文档解析请求"""
    test_type: TestType = Field(..., description="测试类型")
    ai_provider: AIProvider = Field(default=AIProvider.GEMINI, description="AI提供商")
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_type": "api_test",
                "ai_provider": "gemini"
            }
        }


class DocumentInfo(BaseModel):
    """文档基础信息"""
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    document_type: str = Field(..., description="文档类型")
    sections: List[str] = Field(default_factory=list, description="章节列表")
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="表格数据")
    links: List[str] = Field(default_factory=list, description="链接列表")
    user_stories: List[str] = Field(default_factory=list, description="用户故事")


class APIEndpointInfo(BaseModel):
    """API端点信息"""
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="HTTP方法")
    summary: str = Field(..., description="接口摘要")
    description: Optional[str] = Field(None, description="接口描述")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="参数列表")
    responses: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="响应定义")


class APIDocumentInfo(BaseModel):
    """API文档信息"""
    info: Dict[str, str] = Field(..., description="API基本信息")
    servers: List[Dict[str, str]] = Field(default_factory=list, description="服务器列表")
    endpoints: List[APIEndpointInfo] = Field(default_factory=list, description="端点列表")


class PromptTemplateInfo(BaseModel):
    """Prompt模板信息"""
    name: str = Field(..., description="模板名称")
    content: str = Field(..., description="模板内容")
    variables: List[str] = Field(default_factory=list, description="变量列表")
    description: Optional[str] = Field(None, description="模板描述")


class PromptTestCaseInfo(BaseModel):
    """Prompt测试用例信息"""
    name: str = Field(..., description="测试用例名称")
    input: Dict[str, Any] = Field(..., description="输入数据")
    expected_output: str = Field(..., description="期望输出")
    description: Optional[str] = Field(None, description="用例描述")


class PromptDocumentInfo(BaseModel):
    """Prompt文档信息"""
    title: str = Field(..., description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    templates: List[PromptTemplateInfo] = Field(default_factory=list, description="模板列表")
    test_cases: List[PromptTestCaseInfo] = Field(default_factory=list, description="测试用例列表")


class DocumentParseResponse(BaseModel):
    """文档解析响应"""
    test_type: TestType = Field(..., description="测试类型")
    document: DocumentInfo = Field(..., description="文档基础信息")
    document_category: DocumentCategory = Field(..., description="文档分类")
    
    # 可选的特定文档信息
    api_document: Optional[APIDocumentInfo] = Field(None, description="API文档信息")
    prompt_document: Optional[PromptDocumentInfo] = Field(None, description="Prompt文档信息")
    
    metadata: Dict[str, Any] = Field(..., description="元数据信息")


# ==================== 测试用例生成相关 ====================

class TestGenerateRequest(BaseModel):
    """测试用例生成请求"""
    test_type: TestType = Field(..., description="测试类型")
    document_data: Dict[str, Any] = Field(..., description="文档解析数据")
    ai_provider: AIProvider = Field(default=AIProvider.GEMINI, description="AI提供商")
    
    # 生成选项
    include_positive_tests: bool = Field(default=True, description="包含正向测试")
    include_negative_tests: bool = Field(default=True, description="包含负向测试")
    include_boundary_tests: bool = Field(default=True, description="包含边界测试")
    test_framework: str = Field(default="pytest", description="测试框架")
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_type": "api_test",
                "document_data": {"api_document": {}},
                "ai_provider": "gemini",
                "include_positive_tests": True,
                "include_negative_tests": True,
                "include_boundary_tests": True,
                "test_framework": "pytest"
            }
        }


class GeneratedTestCase(BaseModel):
    """生成的测试用例"""
    name: str = Field(..., description="测试用例名称")
    description: str = Field(..., description="测试用例描述")
    test_type: str = Field(..., description="测试类型：positive/negative/boundary")
    code: str = Field(..., description="测试代码")
    dependencies: List[str] = Field(default_factory=list, description="依赖包列表")


class TestGenerateResponse(BaseModel):
    """测试用例生成响应"""
    test_type: TestType = Field(..., description="测试类型")
    test_cases: List[GeneratedTestCase] = Field(..., description="生成的测试用例列表")
    test_file_content: str = Field(..., description="完整的测试文件内容")
    
    # 统计信息
    total_tests: int = Field(..., description="测试用例总数")
    positive_tests: int = Field(default=0, description="正向测试数量")
    negative_tests: int = Field(default=0, description="负向测试数量")
    boundary_tests: int = Field(default=0, description="边界测试数量")
    
    metadata: Dict[str, Any] = Field(..., description="生成元数据")


# ==================== 任务状态相关 ====================

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: float = Field(default=0.0, description="进度百分比 0-100")
    message: str = Field(default="", description="状态消息")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123456",
                "status": "completed",
                "progress": 100.0,
                "message": "测试用例生成完成",
                "result": {"test_cases": []},
                "created_at": "2025-01-16T10:00:00Z",
                "updated_at": "2025-01-16T10:05:00Z"
            }
        }


# ==================== 错误响应 ====================

class ErrorResponse(BaseModel):
    """错误响应"""
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: str = Field(..., description="错误时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_TEST_TYPE",
                "error_message": "不支持的测试类型",
                "details": {"valid_types": ["api_test", "prompt_test"]},
                "timestamp": "2025-01-16T10:00:00Z"
            }
        }
