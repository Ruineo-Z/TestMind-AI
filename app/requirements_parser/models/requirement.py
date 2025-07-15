"""
需求数据模型
定义需求的结构、类型和属性
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer

class RequirementType(str, Enum):
    """需求类型枚举"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    USER_STORY = "user_story"
    BUSINESS_RULE = "business_rule"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"

class Priority(str, Enum):
    """优先级枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RequirementStatus(str, Enum):
    """需求状态枚举"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    REJECTED = "rejected"

class AcceptanceCriteria(BaseModel):
    """验收标准模型"""
    id: str = Field(..., description="验收标准ID")
    description: str = Field(..., description="验收标准描述", min_length=1)
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")
    testable: bool = Field(default=True, description="是否可测试")
    
    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow"
    )

class Requirement(BaseModel):
    """需求模型"""
    id: str = Field(..., description="需求ID", min_length=1)
    title: str = Field(..., description="需求标题", min_length=1)
    description: str = Field(..., description="需求描述", min_length=1)
    type: RequirementType = Field(..., description="需求类型")
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")
    status: RequirementStatus = Field(default=RequirementStatus.DRAFT, description="需求状态")
    
    # 验收标准
    acceptance_criteria: List[str] = Field(default_factory=list, description="验收标准列表")
    
    # 关联信息
    parent_id: Optional[str] = Field(None, description="父需求ID")
    dependencies: List[str] = Field(default_factory=list, description="依赖的需求ID列表")
    
    # 业务信息
    business_value: Optional[str] = Field(None, description="业务价值")
    user_role: Optional[str] = Field(None, description="用户角色（用于用户故事）")
    
    # 技术信息
    complexity: Optional[str] = Field(None, description="复杂度评估")
    effort_estimate: Optional[float] = Field(None, description="工作量估算（小时）", ge=0)
    
    # 追踪信息
    source_document: Optional[str] = Field(None, description="来源文档")
    source_section: Optional[str] = Field(None, description="来源章节")
    extracted_by: Optional[str] = Field(None, description="提取方式")
    confidence_score: Optional[float] = Field(None, description="置信度分数", ge=0, le=1)
    
    # 时间信息
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    # 额外属性
    tags: List[str] = Field(default_factory=list, description="标签列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow"
    )

    @field_serializer('created_at', 'updated_at', when_used='json')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """序列化datetime字段为ISO格式字符串"""
        return value.isoformat() if value else None
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """验证需求ID格式"""
        if not v or not v.strip():
            raise ValueError("需求ID不能为空")
        
        # 基本格式验证
        v = v.strip()
        if len(v) < 3:
            raise ValueError("需求ID长度至少3个字符")
        
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证需求标题"""
        if not v or not v.strip():
            raise ValueError("需求标题不能为空")
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """验证需求描述"""
        if not v or not v.strip():
            raise ValueError("需求描述不能为空")
        return v.strip()
    
    @field_validator('effort_estimate')
    @classmethod
    def validate_effort_estimate(cls, v: Optional[float]) -> Optional[float]:
        """验证工作量估算"""
        if v is not None and v < 0:
            raise ValueError("工作量估算不能为负数")
        return v
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v: Optional[float]) -> Optional[float]:
        """验证置信度分数"""
        if v is not None and (v < 0 or v > 1):
            raise ValueError("置信度分数必须在0-1之间")
        return v
    
    def add_acceptance_criterion(self, criterion: str) -> None:
        """添加验收标准"""
        if criterion and criterion.strip():
            self.acceptance_criteria.append(criterion.strip())
    
    def add_dependency(self, requirement_id: str) -> None:
        """添加依赖需求"""
        if requirement_id and requirement_id not in self.dependencies:
            self.dependencies.append(requirement_id)
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag and tag.strip() and tag not in self.tags:
            self.tags.append(tag.strip())
    
    def is_user_story(self) -> bool:
        """判断是否为用户故事"""
        return self.type == RequirementType.USER_STORY
    
    def is_functional(self) -> bool:
        """判断是否为功能需求"""
        return self.type == RequirementType.FUNCTIONAL
    
    def is_non_functional(self) -> bool:
        """判断是否为非功能需求"""
        return self.type == RequirementType.NON_FUNCTIONAL
    
    def get_priority_weight(self) -> int:
        """获取优先级权重（用于排序）"""
        priority_weights = {
            Priority.CRITICAL: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1
        }
        return priority_weights.get(self.priority, 0)
    
    def to_user_story_format(self) -> str:
        """转换为用户故事格式"""
        if self.user_role:
            return f"作为{self.user_role}，我希望{self.description}"
        else:
            return f"作为用户，我希望{self.description}"

class RequirementCollection(BaseModel):
    """需求集合模型"""
    requirements: List[Requirement] = Field(default_factory=list, description="需求列表")
    total_count: int = Field(default=0, description="总需求数量")
    functional_count: int = Field(default=0, description="功能需求数量")
    non_functional_count: int = Field(default=0, description="非功能需求数量")
    user_story_count: int = Field(default=0, description="用户故事数量")
    
    # 统计信息
    priority_distribution: Dict[str, int] = Field(default_factory=dict, description="优先级分布")
    status_distribution: Dict[str, int] = Field(default_factory=dict, description="状态分布")
    
    # 质量指标
    average_confidence: Optional[float] = Field(None, description="平均置信度")
    extraction_accuracy: Optional[float] = Field(None, description="提取准确率")
    
    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow"
    )
    
    def add_requirement(self, requirement: Requirement) -> None:
        """添加需求"""
        self.requirements.append(requirement)
        self._update_statistics()
    
    def remove_requirement(self, requirement_id: str) -> bool:
        """移除需求"""
        for i, req in enumerate(self.requirements):
            if req.id == requirement_id:
                del self.requirements[i]
                self._update_statistics()
                return True
        return False
    
    def get_requirement_by_id(self, requirement_id: str) -> Optional[Requirement]:
        """根据ID获取需求"""
        for req in self.requirements:
            if req.id == requirement_id:
                return req
        return None
    
    def get_requirements_by_type(self, req_type: RequirementType) -> List[Requirement]:
        """根据类型获取需求"""
        return [req for req in self.requirements if req.type == req_type]
    
    def get_requirements_by_priority(self, priority: Priority) -> List[Requirement]:
        """根据优先级获取需求"""
        return [req for req in self.requirements if req.priority == priority]
    
    def sort_by_priority(self) -> None:
        """按优先级排序"""
        self.requirements.sort(key=lambda x: x.get_priority_weight(), reverse=True)
    
    def _update_statistics(self) -> None:
        """更新统计信息"""
        self.total_count = len(self.requirements)
        
        # 类型统计
        self.functional_count = len(self.get_requirements_by_type(RequirementType.FUNCTIONAL))
        self.non_functional_count = len(self.get_requirements_by_type(RequirementType.NON_FUNCTIONAL))
        self.user_story_count = len(self.get_requirements_by_type(RequirementType.USER_STORY))
        
        # 优先级分布
        self.priority_distribution = {}
        for priority in Priority:
            count = len(self.get_requirements_by_priority(priority))
            if count > 0:
                self.priority_distribution[priority.value] = count
        
        # 状态分布
        self.status_distribution = {}
        for req in self.requirements:
            status = req.status.value
            self.status_distribution[status] = self.status_distribution.get(status, 0) + 1
        
        # 平均置信度
        confidence_scores = [req.confidence_score for req in self.requirements if req.confidence_score is not None]
        if confidence_scores:
            self.average_confidence = sum(confidence_scores) / len(confidence_scores)
