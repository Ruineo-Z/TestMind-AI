"""
需求解析API端点测试
"""
import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import create_app


class TestRequirementsAPI:
    """需求解析API测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        return create_app()
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_parse_requirements_endpoint_exists(self, client):
        """测试需求解析端点存在"""
        # 测试端点是否存在（即使没有文件也应该返回422而不是404）
        response = client.post("/api/v1/requirements/parse")
        assert response.status_code != 404
    
    def test_parse_requirements_without_file(self, client):
        """测试没有文件的请求"""
        response = client.post("/api/v1/requirements/parse")
        assert response.status_code == 422  # 缺少必需参数
    
    def test_parse_markdown_file(self, client):
        """测试解析Markdown文件"""
        # 创建临时Markdown文件
        markdown_content = """
        # 用户管理系统需求
        
        ## 功能需求
        1. 用户注册功能
        2. 用户登录功能
        
        ## 非功能需求
        - 性能要求：响应时间 < 2秒
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(markdown_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("test.md", f, "text/markdown")}
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构
            assert "document" in data
            assert "requirements" in data
            assert "metadata" in data
            
            # 验证文档信息
            document = data["document"]
            assert document["title"] == "用户管理系统需求"
            assert document["document_type"] == "markdown"
            assert "用户注册功能" in document["content"]
            
            # 验证需求提取
            requirements = data["requirements"]
            assert len(requirements) > 0
            
        finally:
            os.unlink(temp_file_path)
    
    def test_parse_unsupported_file_type(self, client):
        """测试不支持的文件类型"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("这是一个文本文件")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "不支持的文件类型" in data["detail"]
            
        finally:
            os.unlink(temp_file_path)
    
    def test_parse_empty_file(self, client):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("empty.md", f, "text/markdown")}
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "文件内容为空" in data["detail"]
            
        finally:
            os.unlink(temp_file_path)
    
    def test_parse_requirements_with_options(self, client):
        """测试带选项的需求解析"""
        markdown_content = """
        # API设计文档
        
        ## 接口需求
        1. 用户管理接口
        2. 权限管理接口
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(markdown_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("api_doc.md", f, "text/markdown")},
                    data={
                        "extract_user_stories": "true",
                        "ai_provider": "mock"
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证选项生效
            assert "requirements" in data
            assert "metadata" in data
            
            metadata = data["metadata"]
            assert metadata["ai_provider"] == "mock"
            
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_parse_requirements_async(self, app):
        """测试异步需求解析"""
        from httpx import ASGITransport
        transport = ASGITransport(app=app)
        
        markdown_content = """
        # 测试需求文档
        
        ## 功能需求
        1. 测试功能A
        2. 测试功能B
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(markdown_content)
            temp_file_path = f.name
        
        try:
            async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
                with open(temp_file_path, 'rb') as f:
                    response = await ac.post(
                        "/api/v1/requirements/parse",
                        files={"file": ("test.md", f, "text/markdown")}
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "document" in data
                assert "requirements" in data
                
        finally:
            os.unlink(temp_file_path)
    
    def test_get_parse_status(self, client):
        """测试获取解析状态"""
        # 这个端点用于查询异步解析任务的状态
        response = client.get("/api/v1/requirements/parse/status/test-task-id")
        
        # 如果任务不存在，应该返回404
        assert response.status_code == 404
    
    def test_list_supported_formats(self, client):
        """测试获取支持的文件格式"""
        response = client.get("/api/v1/requirements/formats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "supported_formats" in data
        formats = data["supported_formats"]
        
        # 验证支持的格式
        assert "markdown" in formats
        assert "pdf" in formats
        assert "word" in formats
        
        # 验证格式信息
        assert ".md" in formats["markdown"]["extensions"]
        assert ".markdown" in formats["markdown"]["extensions"]
        assert ".pdf" in formats["pdf"]["extensions"]
        assert ".docx" in formats["word"]["extensions"]
        assert ".doc" in formats["word"]["extensions"]
