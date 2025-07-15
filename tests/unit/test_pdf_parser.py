"""
PDF解析器单元测试
"""
import pytest
import tempfile
import os
from pathlib import Path

from app.requirements_parser.parsers.pdf_parser import PDFParser
from app.requirements_parser.models.document import Document, DocumentType


class TestPDFParser:
    """PDF解析器测试类"""
    
    def test_parser_initialization(self):
        """测试解析器初始化"""
        parser = PDFParser()
        assert parser is not None
        assert '.pdf' in parser.supported_extensions
    
    def test_parse_simple_pdf_content(self):
        """测试解析简单PDF内容"""
        parser = PDFParser()
        
        # 模拟PDF文本内容
        pdf_text = """
        # 用户管理系统需求文档
        
        ## 功能需求
        1. 用户注册
        2. 用户登录
        3. 密码重置
        
        ## 非功能需求
        - 性能要求：响应时间 < 2秒
        - 安全要求：密码加密存储
        """
        
        # 由于我们无法在测试中创建真实PDF，这里测试文本解析逻辑
        document = parser._parse_text_content(pdf_text, "test.pdf")
        
        assert document.title == "用户管理系统需求文档"
        assert document.document_type == DocumentType.PDF
        assert "用户注册" in document.content
        assert "性能要求" in document.content
    
    def test_parse_empty_pdf(self):
        """测试解析空PDF"""
        parser = PDFParser()
        
        with pytest.raises(ValueError, match="PDF内容为空"):
            parser._parse_text_content("", "empty.pdf")
    
    def test_parse_invalid_pdf_content(self):
        """测试解析无效PDF内容"""
        parser = PDFParser()
        
        # 测试只有空白字符的内容
        with pytest.raises(ValueError, match="PDF内容为空"):
            parser._parse_text_content("   \n\t  ", "whitespace.pdf")
    
    def test_extract_metadata_from_pdf(self):
        """测试从PDF提取元数据"""
        parser = PDFParser()
        
        pdf_text = """
        # API设计文档
        
        版本: 1.0
        作者: 开发团队
        日期: 2024-01-15
        
        ## 接口列表
        - GET /users
        - POST /users
        - PUT /users/{id}
        """
        
        document = parser._parse_text_content(pdf_text, "api_doc.pdf")
        
        assert document.title == "API设计文档"
        assert "版本: 1.0" in document.content
        assert "GET /users" in document.content
    
    def test_can_parse_pdf_files(self):
        """测试是否可以解析PDF文件"""
        parser = PDFParser()
        
        assert parser.can_parse("document.pdf") is True
        assert parser.can_parse("document.PDF") is True
        assert parser.can_parse("document.txt") is False
        assert parser.can_parse("document.docx") is False
    
    def test_parse_pdf_with_tables(self):
        """测试解析包含表格的PDF"""
        parser = PDFParser()
        
        pdf_text = """
        # 测试用例文档
        
        ## 测试用例表格
        
        | 用例ID | 用例名称 | 预期结果 |
        |--------|----------|----------|
        | TC001  | 用户登录 | 登录成功 |
        | TC002  | 密码错误 | 登录失败 |
        """
        
        document = parser._parse_text_content(pdf_text, "test_cases.pdf")
        
        assert document.title == "测试用例文档"
        assert "TC001" in document.content
        assert "用户登录" in document.content
    
    def test_parse_pdf_performance(self):
        """测试PDF解析性能"""
        parser = PDFParser()
        
        # 创建较大的文本内容
        large_content = "# 大型需求文档\n\n"
        for i in range(100):
            large_content += f"## 需求 {i+1}\n这是第{i+1}个需求的详细描述。\n\n"
        
        import time
        start_time = time.time()
        document = parser._parse_text_content(large_content, "large_doc.pdf")
        end_time = time.time()
        
        # 解析时间应该在合理范围内（< 1秒）
        assert (end_time - start_time) < 1.0
        assert document.title == "大型需求文档"
        assert len(document.content) > 1000
