"""
Prompt文档数据模型
定义Prompt文档的结构化数据模型，用于AI应用的提示词管理和测试
"""
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class PromptType(str, Enum):
    """Prompt类型枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TEMPLATE = "template"


class PromptRole(str, Enum):
    """Prompt角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class TestCaseType(str, Enum):
    """测试用例类型枚举"""
    FUNCTIONAL = "functional"  # 功能测试
    PERFORMANCE = "performance"  # 性能测试
    SAFETY = "safety"  # 安全测试
    BIAS = "bias"  # 偏见测试
    ROBUSTNESS = "robustness"  # 鲁棒性测试


class PromptVariable(BaseModel):
    """Prompt变量模型"""
    name: str = Field(..., description="变量名称")
    type: str = Field(..., description="变量类型")
    description: Optional[str] = Field(None, description="变量描述")
    required: bool = Field(default=True, description="是否必需")
    default: Optional[Any] = Field(None, description="默认值")
    examples: Optional[List[Any]] = Field(None, description="示例值")
    constraints: Optional[Dict[str, Any]] = Field(None, description="约束条件")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证变量名称"""
        if not v or not v.strip():
            raise ValueError("变量名称不能为空")
        return v.strip()


class PromptTemplate(BaseModel):
    """Prompt模板模型"""
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    type: PromptType = Field(..., description="Prompt类型")
    role: Optional[PromptRole] = Field(None, description="Prompt角色")
    content: str = Field(..., description="Prompt内容")
    variables: List[PromptVariable] = Field(default_factory=list, description="变量列表")
    tags: Optional[List[str]] = Field(None, description="标签")
    version: str = Field(default="1.0", description="模板版本")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """验证模板ID"""
        if not v or not v.strip():
            raise ValueError("模板ID不能为空")
        return v.strip()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证模板名称"""
        if not v or not v.strip():
            raise ValueError("模板名称不能为空")
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """验证Prompt内容"""
        if not v or not v.strip():
            raise ValueError("Prompt内容不能为空")
        return v


class PromptTestCase(BaseModel):
    """Prompt测试用例模型"""
    id: str = Field(..., description="测试用例ID")
    name: str = Field(..., description="测试用例名称")
    description: Optional[str] = Field(None, description="测试用例描述")
    type: TestCaseType = Field(..., description="测试类型")
    prompt_template_id: str = Field(..., description="关联的Prompt模板ID")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    expected_output: Optional[Dict[str, Any]] = Field(None, description="期望输出")
    evaluation_criteria: List[str] = Field(default_factory=list, description="评估标准")
    tags: Optional[List[str]] = Field(None, description="标签")
    priority: str = Field(default="medium", description="优先级")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """验证测试用例ID"""
        if not v or not v.strip():
            raise ValueError("测试用例ID不能为空")
        return v.strip()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证测试用例名称"""
        if not v or not v.strip():
            raise ValueError("测试用例名称不能为空")
        return v.strip()


class PromptScenario(BaseModel):
    """Prompt使用场景模型"""
    id: str = Field(..., description="场景ID")
    name: str = Field(..., description="场景名称")
    description: Optional[str] = Field(None, description="场景描述")
    context: Optional[str] = Field(None, description="使用上下文")
    user_personas: Optional[List[str]] = Field(None, description="用户画像")
    success_criteria: List[str] = Field(default_factory=list, description="成功标准")
    failure_scenarios: Optional[List[str]] = Field(None, description="失败场景")
    related_prompts: List[str] = Field(default_factory=list, description="相关Prompt ID列表")


class PromptEvaluation(BaseModel):
    """Prompt评估模型"""
    criteria: str = Field(..., description="评估标准")
    description: Optional[str] = Field(None, description="标准描述")
    weight: float = Field(default=1.0, description="权重", ge=0.0, le=1.0)
    measurement_method: str = Field(..., description="测量方法")
    threshold: Optional[float] = Field(None, description="阈值")


class PromptDocument(BaseModel):
    """Prompt文档模型"""
    title: str = Field(..., description="文档标题")
    version: str = Field(default="1.0", description="文档版本")
    description: Optional[str] = Field(None, description="文档描述")
    author: Optional[str] = Field(None, description="作者")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    # 核心内容
    prompts: List[PromptTemplate] = Field(default_factory=list, description="Prompt模板列表")
    test_cases: List[PromptTestCase] = Field(default_factory=list, description="测试用例列表")
    scenarios: List[PromptScenario] = Field(default_factory=list, description="使用场景列表")
    evaluations: List[PromptEvaluation] = Field(default_factory=list, description="评估标准列表")
    
    # 元数据
    tags: Optional[List[str]] = Field(None, description="文档标签")
    categories: Optional[List[str]] = Field(None, description="文档分类")
    dependencies: Optional[List[str]] = Field(None, description="依赖关系")
    
    # 解析相关的元数据
    source_format: str = Field(..., description="源文档格式")  # markdown, json, yaml
    parsing_accuracy: Optional[float] = Field(None, description="解析准确率")
    parsing_warnings: List[str] = Field(default_factory=list, description="解析警告")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """验证文档标题"""
        if not v or not v.strip():
            raise ValueError("文档标题不能为空")
        return v.strip()
    
    @field_validator('prompts')
    @classmethod
    def validate_prompts(cls, v):
        """验证Prompt列表"""
        if not v:
            raise ValueError("Prompt文档必须包含至少一个Prompt模板")
        return v
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[PromptTemplate]:
        """根据ID获取Prompt模板"""
        for prompt in self.prompts:
            if prompt.id == prompt_id:
                return prompt
        return None
    
    def get_test_cases_by_prompt_id(self, prompt_id: str) -> List[PromptTestCase]:
        """根据Prompt ID获取相关测试用例"""
        return [
            test_case for test_case in self.test_cases
            if test_case.prompt_template_id == prompt_id
        ]
    
    def get_prompts_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """根据类型获取Prompt列表"""
        return [
            prompt for prompt in self.prompts
            if prompt.type == prompt_type
        ]
    
    def get_test_cases_by_type(self, test_type: TestCaseType) -> List[PromptTestCase]:
        """根据类型获取测试用例列表"""
        return [
            test_case for test_case in self.test_cases
            if test_case.type == test_type
        ]
