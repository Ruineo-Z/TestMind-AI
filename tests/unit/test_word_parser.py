"""
Word解析器单元测试
"""
import pytest
import tempfile
import os
from pathlib import Path

from app.requirements_parser.parsers.word_parser import WordParser
from app.requirements_parser.models.document import Document, DocumentType


class TestWordParser:
    """Word解析器测试类"""
    
    def test_parser_initialization(self):
        """测试解析器初始化"""
        parser = WordParser()
        assert parser is not None
        assert '.docx' in parser.supported_extensions
        assert '.doc' in parser.supported_extensions
    
    def test_parse_simple_word_content(self):
        """测试解析简单Word内容"""
        parser = WordParser()
        
        # 模拟Word文档段落内容
        paragraphs = [
            "用户管理系统需求文档",
            "",
            "功能需求",
            "1. 用户注册功能",
            "   - 支持邮箱注册",
            "   - 密码强度验证",
            "2. 用户登录功能",
            "   - 邮箱密码登录",
            "   - 记住登录状态",
            "",
            "非功能需求",
            "- 性能要求：响应时间 < 2秒",
            "- 安全要求：密码加密存储"
        ]
        
        document = parser._parse_paragraphs(paragraphs, "test.docx")
        
        assert document.title == "用户管理系统需求文档"
        assert document.document_type == DocumentType.WORD
        assert "用户注册功能" in document.content
        assert "性能要求" in document.content
    
    def test_parse_empty_word(self):
        """测试解析空Word文档"""
        parser = WordParser()
        
        with pytest.raises(ValueError, match="Word文档内容为空"):
            parser._parse_paragraphs([], "empty.docx")
    
    def test_parse_word_with_only_empty_paragraphs(self):
        """测试解析只有空段落的Word文档"""
        parser = WordParser()
        
        empty_paragraphs = ["", "   ", "\t", "\n"]
        
        with pytest.raises(ValueError, match="Word文档内容为空"):
            parser._parse_paragraphs(empty_paragraphs, "empty.docx")
    
    def test_extract_title_from_word(self):
        """测试从Word文档提取标题"""
        parser = WordParser()
        
        paragraphs = [
            "API设计规范文档",
            "",
            "版本: 2.0",
            "作者: 技术团队",
            "",
            "概述",
            "本文档描述了系统API的设计规范和实现要求。",
            "",
            "接口列表",
            "1. 用户管理接口",
            "2. 权限管理接口"
        ]
        
        document = parser._parse_paragraphs(paragraphs, "api_spec.docx")
        
        assert document.title == "API设计规范文档"
        assert "版本: 2.0" in document.content
        assert "用户管理接口" in document.content
    
    def test_can_parse_word_files(self):
        """测试是否可以解析Word文件"""
        parser = WordParser()
        
        assert parser.can_parse("document.docx") is True
        assert parser.can_parse("document.doc") is True
        assert parser.can_parse("document.DOCX") is True
        assert parser.can_parse("document.txt") is False
        assert parser.can_parse("document.pdf") is False
    
    def test_parse_word_with_headings(self):
        """测试解析包含标题的Word文档"""
        parser = WordParser()
        
        paragraphs = [
            "测试计划文档",
            "",
            "1. 测试目标",
            "确保系统功能正常运行。",
            "",
            "2. 测试范围",
            "包括功能测试、性能测试和安全测试。",
            "",
            "2.1 功能测试",
            "验证所有功能需求。",
            "",
            "2.2 性能测试",
            "验证系统性能指标。"
        ]
        
        document = parser._parse_paragraphs(paragraphs, "test_plan.docx")
        
        assert document.title == "测试计划文档"
        assert "测试目标" in document.content
        assert "功能测试" in document.content
        assert len(document.sections) > 0
    
    def test_parse_word_with_lists(self):
        """测试解析包含列表的Word文档"""
        parser = WordParser()
        
        paragraphs = [
            "需求清单",
            "",
            "功能需求：",
            "• 用户注册",
            "• 用户登录",
            "• 密码重置",
            "",
            "非功能需求：",
            "- 高可用性",
            "- 高性能",
            "- 安全性"
        ]
        
        document = parser._parse_paragraphs(paragraphs, "requirements.docx")
        
        assert document.title == "需求清单"
        assert "用户注册" in document.content
        assert "高可用性" in document.content
    
    def test_parse_word_performance(self):
        """测试Word解析性能"""
        parser = WordParser()
        
        # 创建大量段落
        large_paragraphs = ["大型需求文档"]
        for i in range(200):
            large_paragraphs.extend([
                f"需求 {i+1}",
                f"这是第{i+1}个需求的详细描述。",
                ""
            ])
        
        import time
        start_time = time.time()
        document = parser._parse_paragraphs(large_paragraphs, "large_doc.docx")
        end_time = time.time()
        
        # 解析时间应该在合理范围内（< 1秒）
        assert (end_time - start_time) < 1.0
        assert document.title == "大型需求文档"
        assert len(document.content) > 1000
    
    def test_extract_sections_from_word(self):
        """测试从Word文档提取章节"""
        parser = WordParser()
        
        paragraphs = [
            "系统设计文档",
            "",
            "1. 系统架构",
            "系统采用微服务架构。",
            "",
            "1.1 前端架构",
            "使用React框架。",
            "",
            "1.2 后端架构",
            "使用FastAPI框架。",
            "",
            "2. 数据库设计",
            "使用PostgreSQL数据库。"
        ]
        
        document = parser._parse_paragraphs(paragraphs, "design.docx")
        
        assert len(document.sections) >= 4  # 至少包含主要章节
        section_titles = [section['title'] for section in document.sections]
        assert "系统架构" in section_titles
        assert "数据库设计" in section_titles
    
    def test_extract_user_stories_from_word(self):
        """测试从Word文档提取用户故事"""
        parser = WordParser()
        
        paragraphs = [
            "用户故事文档",
            "",
            "作为一个普通用户，我希望能够注册账号，以便使用系统功能。",
            "",
            "作为一个管理员，我希望能够管理用户权限，以便控制系统访问。",
            "",
            "其他需求：",
            "系统应该支持多语言。"
        ]
        
        document = parser._parse_paragraphs(paragraphs, "user_stories.docx")
        
        assert len(document.user_stories) >= 2
        story_texts = [story['story'] for story in document.user_stories]
        assert any("普通用户" in story for story in story_texts)
        assert any("管理员" in story for story in story_texts)
