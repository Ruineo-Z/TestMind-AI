"""
TestMind AI - 测试配置文件
提供全局测试fixtures和配置
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# 确保事件循环策略正确设置
@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.get_event_loop_policy()

@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    """创建事件循环用于整个测试会话"""
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def app():
    """创建FastAPI应用实例"""
    from app.main import create_app
    return create_app()

@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    with TestClient(app) as test_client:
        yield test_client

@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def mock_settings():
    """模拟配置设置"""
    from app.core.config import Settings
    return Settings(
        app_name="TestMind AI Test",
        debug=True,
        database_url="postgresql://test:test@localhost:5432/testmind_test",
        redis_url="redis://localhost:6379/1",
        secret_key="test-secret-key-for-testing-only",
        openai_api_key="sk-test1234567890abcdef1234567890abcdef12345678"
    )

@pytest_asyncio.fixture
async def db_session():
    """创建测试数据库会话"""
    # 这里将在实现数据库模块后完善
    # 目前返回None，避免测试失败
    yield None

@pytest.fixture
def sample_requirements_doc():
    """示例需求文档"""
    return """
    # 用户管理系统需求

    ## 功能需求
    1. 用户注册功能
       - 支持邮箱注册
       - 密码强度验证
       - 邮箱验证

    2. 用户登录功能
       - 邮箱密码登录
       - 记住登录状态
       - 登录失败限制

    ## 非功能需求
    - 响应时间 < 2秒
    - 支持1000并发用户
    - 99.9%可用性
    """

@pytest.fixture
def sample_api_spec():
    """示例API规范"""
    return {
        "openapi": "3.0.0",
        "info": {"title": "User API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "post": {
                    "summary": "Create user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8}
                                    },
                                    "required": ["email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "User created"},
                        "400": {"description": "Invalid input"}
                    }
                }
            }
        }
    }
