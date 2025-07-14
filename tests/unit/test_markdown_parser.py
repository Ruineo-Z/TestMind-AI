"""
Sprint 2 - Markdown解析器测试
测试Markdown文档解析功能
"""
import pytest
from pathlib import Path
from app.requirements_parser.parsers.markdown_parser import MarkdownParser
from app.requirements_parser.models.document import Document, DocumentType

class TestMarkdownParser:
    """测试Markdown解析器"""
    
    def test_parser_initialization(self):
        """测试解析器初始化 - 这个测试现在会失败"""
        parser = MarkdownParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
    
    def test_parse_simple_markdown(self):
        """测试解析简单Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        markdown_content = """# 用户管理系统需求

## 功能需求

### 1. 用户注册
- 用户可以通过邮箱注册
- 密码必须包含大小写字母和数字
- 注册后发送验证邮件

### 2. 用户登录
- 支持邮箱登录
- 支持记住登录状态
- 登录失败3次锁定账户

## 非功能需求

### 性能要求
- 响应时间 < 2秒
- 支持1000并发用户

### 安全要求
- 密码加密存储
- 支持HTTPS
"""
        
        document = parser.parse(markdown_content)
        
        # 验证解析结果
        assert isinstance(document, Document)
        assert document.document_type == DocumentType.MARKDOWN
        assert document.title == "用户管理系统需求"
        assert len(document.content) > 0
        
        # 验证解析的结构化信息
        assert hasattr(document, 'sections')
        assert len(document.sections) >= 2  # 功能需求 + 非功能需求
    
    def test_parse_markdown_with_metadata(self):
        """测试解析带元数据的Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        markdown_content = """---
title: API设计文档
author: 开发团队
version: 1.0
date: 2024-01-15
---

# API设计文档

## 接口列表

### 1. 用户接口
- GET /api/users - 获取用户列表
- POST /api/users - 创建用户
- PUT /api/users/{id} - 更新用户
- DELETE /api/users/{id} - 删除用户
"""
        
        document = parser.parse(markdown_content)
        
        # 验证基本信息
        assert document.title == "API设计文档"
        assert document.document_type == DocumentType.MARKDOWN
        
        # 验证元数据解析
        assert hasattr(document, 'frontmatter')
        assert document.frontmatter['author'] == "开发团队"
        assert document.frontmatter['version'] == 1.0  # YAML解析为浮点数
    
    def test_parse_markdown_with_code_blocks(self):
        """测试解析包含代码块的Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        markdown_content = """# 技术规范

## 数据库设计

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API示例

```python
@app.post("/api/users")
async def create_user(user: UserCreate):
    return await user_service.create(user)
```
"""
        
        document = parser.parse(markdown_content)
        
        # 验证代码块被正确解析
        assert "CREATE TABLE users" in document.content
        assert "@app.post" in document.content
        assert hasattr(document, 'code_blocks')
        assert len(document.code_blocks) == 2
    
    def test_parse_markdown_with_tables(self):
        """测试解析包含表格的Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        markdown_content = """# 接口文档

## 用户接口

| 方法 | 路径 | 描述 | 参数 |
|------|------|------|------|
| GET | /api/users | 获取用户列表 | page, size |
| POST | /api/users | 创建用户 | email, password |
| PUT | /api/users/{id} | 更新用户 | id, email |
| DELETE | /api/users/{id} | 删除用户 | id |
"""
        
        document = parser.parse(markdown_content)
        
        # 验证表格被正确解析
        assert hasattr(document, 'tables')
        assert len(document.tables) == 1
        assert len(document.tables[0]['rows']) == 4  # 4个接口
    
    def test_parse_markdown_with_links(self):
        """测试解析包含链接的Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        markdown_content = """# 参考文档

## 相关链接

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)

## 内部链接

参见 [用户管理](#用户管理) 章节。
"""
        
        document = parser.parse(markdown_content)
        
        # 验证链接被正确解析
        assert hasattr(document, 'links')
        assert len(document.links) >= 3
        
        # 验证外部链接
        external_links = [link for link in document.links if link['type'] == 'external']
        assert len(external_links) == 3
        
        # 验证内部链接
        internal_links = [link for link in document.links if link['type'] == 'internal']
        assert len(internal_links) == 1
    
    def test_parse_empty_markdown(self):
        """测试解析空Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        
        with pytest.raises(ValueError, match="文档内容不能为空"):
            parser.parse("")
    
    def test_parse_invalid_markdown(self):
        """测试解析无效Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        
        # 测试None输入
        with pytest.raises(ValueError):
            parser.parse(None)
    
    def test_parse_markdown_from_file(self):
        """测试从文件解析Markdown - 这个测试现在会失败"""
        parser = MarkdownParser()
        
        # 创建临时Markdown文件内容
        markdown_content = """# 测试文档

这是一个测试文档。

## 章节1

内容1

## 章节2

内容2
"""
        
        document = parser.parse_from_string(markdown_content, file_path="test.md")
        
        assert document.title == "测试文档"
        assert document.file_path == "test.md"
        assert document.document_type == DocumentType.MARKDOWN
    
    def test_extract_requirements_from_markdown(self):
        """测试从Markdown提取需求信息 - 这个测试现在会失败"""
        parser = MarkdownParser()
        markdown_content = """# 用户故事

## 作为用户，我希望能够注册账户

**验收标准：**
- 用户可以输入邮箱和密码
- 密码强度验证
- 注册成功后跳转到登录页面

**优先级：** 高

## 作为管理员，我希望能够管理用户

**验收标准：**
- 查看用户列表
- 禁用/启用用户账户
- 重置用户密码

**优先级：** 中
"""
        
        document = parser.parse(markdown_content)
        
        # 验证需求提取
        assert hasattr(document, 'user_stories')
        assert len(document.user_stories) == 2
        
        # 验证第一个用户故事
        story1 = document.user_stories[0]
        assert "注册账户" in story1['title']
        assert story1['priority'] == "高"
        assert len(story1['acceptance_criteria']) == 3
    
    def test_parser_performance(self):
        """测试解析器性能 - 这个测试现在会失败"""
        parser = MarkdownParser()
        
        # 创建大型Markdown文档
        large_content = "# 大型文档\n\n" + "\n\n".join([
            f"## 章节 {i}\n\n这是第{i}个章节的内容。" + "内容 " * 100
            for i in range(100)
        ])
        
        import time
        start_time = time.time()
        document = parser.parse(large_content)
        end_time = time.time()
        
        # 验证性能要求（应该在1秒内完成）
        parse_time = end_time - start_time
        assert parse_time < 1.0, f"解析时间过长: {parse_time:.2f}秒"
        
        # 验证解析结果
        assert document.title == "大型文档"
        assert len(document.sections) == 101  # 包含主标题 + 100个子章节
