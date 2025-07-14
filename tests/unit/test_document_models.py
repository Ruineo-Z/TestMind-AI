"""
Sprint 2 - 文档模型测试
测试文档数据模型的创建、验证和序列化
"""
import pytest
from datetime import datetime
from pathlib import Path
from app.requirements_parser.models.document import Document, DocumentType, DocumentMetadata

class TestDocumentModel:
    """测试文档模型"""
    
    def test_document_creation_basic(self):
        """测试基本文档创建 - 这个测试现在会失败"""
        # 基本文档信息
        doc = Document(
            title="用户管理系统需求",
            content="# 用户管理系统\n## 功能需求\n1. 用户注册",
            document_type=DocumentType.MARKDOWN,
            file_path="requirements.md"
        )
        
        assert doc.title == "用户管理系统需求"
        assert doc.document_type == DocumentType.MARKDOWN
        assert doc.file_path == "requirements.md"
        assert len(doc.content) > 0
    
    def test_document_type_enum(self):
        """测试文档类型枚举 - 这个测试现在会失败"""
        # 验证支持的文档类型
        assert DocumentType.MARKDOWN == "markdown"
        assert DocumentType.PDF == "pdf"
        assert DocumentType.WORD == "word"
        assert DocumentType.TXT == "txt"
    
    def test_document_metadata_creation(self):
        """测试文档元数据创建 - 这个测试现在会失败"""
        metadata = DocumentMetadata(
            file_size=1024,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            encoding="utf-8",
            language="zh-CN"
        )
        
        assert metadata.file_size == 1024
        assert metadata.encoding == "utf-8"
        assert metadata.language == "zh-CN"
        assert isinstance(metadata.created_at, datetime)
    
    def test_document_with_metadata(self):
        """测试带元数据的文档创建 - 这个测试现在会失败"""
        metadata = DocumentMetadata(
            file_size=2048,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            encoding="utf-8"
        )
        
        doc = Document(
            title="API设计文档",
            content="# API设计\n## 接口列表",
            document_type=DocumentType.MARKDOWN,
            file_path="api_design.md",
            metadata=metadata
        )
        
        assert doc.metadata.file_size == 2048
        assert doc.metadata.encoding == "utf-8"
    
    def test_document_validation_required_fields(self):
        """测试文档必填字段验证 - 这个测试现在会失败"""
        # 缺少必填字段应该抛出验证错误
        with pytest.raises(ValueError):
            Document(
                title="",  # 空标题应该失败
                content="some content",
                document_type=DocumentType.MARKDOWN
            )
    
    def test_document_content_validation(self):
        """测试文档内容验证 - 这个测试现在会失败"""
        # 内容不能为空
        with pytest.raises(ValueError):
            Document(
                title="测试文档",
                content="",  # 空内容应该失败
                document_type=DocumentType.MARKDOWN
            )
    
    def test_document_file_path_validation(self):
        """测试文件路径验证 - 这个测试现在会失败"""
        doc = Document(
            title="测试文档",
            content="测试内容",
            document_type=DocumentType.PDF,
            file_path="documents/test.pdf"
        )

        # 验证文件路径设置正确
        assert doc.file_path == "documents/test.pdf"
        assert doc.document_type == DocumentType.PDF
    
    def test_document_serialization(self):
        """测试文档序列化 - 这个测试现在会失败"""
        doc = Document(
            title="序列化测试",
            content="# 测试内容",
            document_type=DocumentType.MARKDOWN,
            file_path="test.md"
        )
        
        # 测试转换为字典
        doc_dict = doc.model_dump()
        assert doc_dict["title"] == "序列化测试"
        assert doc_dict["document_type"] == "markdown"

        # 测试JSON序列化
        doc_json = doc.model_dump_json()
        assert "序列化测试" in doc_json.decode() if isinstance(doc_json, bytes) else doc_json
    
    def test_document_from_file_path(self):
        """测试从文件路径推断文档类型 - 这个测试现在会失败"""
        # 测试自动推断文档类型
        doc = Document.from_file_path(
            file_path="requirements.md",
            title="自动推断测试",
            content="# 测试"
        )
        
        assert doc.document_type == DocumentType.MARKDOWN
        
        doc_pdf = Document.from_file_path(
            file_path="spec.pdf",
            title="PDF测试",
            content="PDF内容"
        )
        
        assert doc_pdf.document_type == DocumentType.PDF

class TestDocumentMetadata:
    """测试文档元数据模型"""
    
    def test_metadata_optional_fields(self):
        """测试元数据可选字段 - 这个测试现在会失败"""
        # 只提供必填字段
        metadata = DocumentMetadata(
            file_size=1024
        )
        
        assert metadata.file_size == 1024
        assert metadata.encoding is None  # 可选字段
        assert metadata.language is None  # 可选字段
    
    def test_metadata_file_size_validation(self):
        """测试文件大小验证 - 这个测试现在会失败"""
        # 文件大小不能为负数
        with pytest.raises(ValueError):
            DocumentMetadata(file_size=-1)
    
    def test_metadata_encoding_validation(self):
        """测试编码格式验证 - 这个测试现在会失败"""
        # 支持的编码格式
        valid_encodings = ["utf-8", "gbk", "ascii", "latin-1"]
        
        for encoding in valid_encodings:
            metadata = DocumentMetadata(
                file_size=1024,
                encoding=encoding
            )
            assert metadata.encoding == encoding
    
    def test_metadata_language_validation(self):
        """测试语言代码验证 - 这个测试现在会失败"""
        # 支持的语言代码
        valid_languages = ["zh-CN", "en-US", "ja-JP", "ko-KR"]
        
        for language in valid_languages:
            metadata = DocumentMetadata(
                file_size=1024,
                language=language
            )
            assert metadata.language == language
