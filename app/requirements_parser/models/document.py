"""
文档数据模型
定义文档的结构、类型和元数据
"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer

class DocumentType(str, Enum):
    """文档类型枚举"""
    MARKDOWN = "markdown"
    PDF = "pdf"
    WORD = "word"
    TXT = "txt"
    # 新增API文档类型
    OPENAPI = "openapi"
    SWAGGER = "swagger"
    API_MARKDOWN = "api_markdown"
    # 新增Prompt文档类型
    PROMPT = "prompt"

class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    file_size: int = Field(..., description="文件大小（字节）", ge=0)
    created_at: Optional[datetime] = Field(None, description="创建时间")
    modified_at: Optional[datetime] = Field(None, description="修改时间")
    encoding: Optional[str] = Field(None, description="文件编码")
    language: Optional[str] = Field(None, description="文档语言")

    @field_serializer('created_at', 'modified_at', when_used='json')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """序列化datetime字段为ISO格式字符串"""
        return value.isoformat() if value else None

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        if v < 0:
            raise ValueError("文件大小不能为负数")
        return v

    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v):
        if v is not None:
            valid_encodings = ["utf-8", "gbk", "ascii", "latin-1"]
            if v not in valid_encodings:
                raise ValueError(f"不支持的编码格式: {v}")
        return v

    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v is not None:
            valid_languages = ["zh-CN", "en-US", "ja-JP", "ko-KR"]
            if v not in valid_languages:
                raise ValueError(f"不支持的语言代码: {v}")
        return v

class Document(BaseModel):
    """文档模型"""
    title: str = Field(..., description="文档标题", min_length=1)
    content: str = Field(..., description="文档内容", min_length=1)
    document_type: DocumentType = Field(..., description="文档类型")
    file_path: Optional[str] = Field(None, description="文件路径")
    metadata: Optional[DocumentMetadata] = Field(None, description="文档元数据")
    
    # 文件扩展名映射
    _extension_mapping: ClassVar[dict] = {
        ".md": DocumentType.MARKDOWN,
        ".markdown": DocumentType.MARKDOWN,
        ".pdf": DocumentType.PDF,
        ".doc": DocumentType.WORD,
        ".docx": DocumentType.WORD,
        ".txt": DocumentType.TXT,
        # API文档格式
        ".json": DocumentType.OPENAPI,  # 默认JSON为OpenAPI
        ".yaml": DocumentType.OPENAPI,
        ".yml": DocumentType.OPENAPI,
    }
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("文档标题不能为空")
        return v.strip()

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("文档内容不能为空")
        return v
    
    @classmethod
    def from_file_path(cls, file_path: str, title: str, content: str, **kwargs):
        """从文件路径创建文档，自动推断文档类型"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # 从扩展名推断文档类型
        document_type = cls._extension_mapping.get(extension, DocumentType.TXT)
        
        return cls(
            title=title,
            content=content,
            document_type=document_type,
            file_path=file_path,
            **kwargs
        )
    
    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow"  # 允许额外字段
    )
