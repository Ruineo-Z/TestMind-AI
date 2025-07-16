"""
API v1版本路由配置
"""
from fastapi import APIRouter

from app.api.v1.requirements import router as requirements_router
from app.api.v1.documents import router as documents_router
from app.api.v1.tests import router as tests_router


# 创建v1版本的主路由
api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(requirements_router)  # 保持向后兼容
api_router.include_router(documents_router)     # 新的文档解析接口
api_router.include_router(tests_router)         # 新的测试生成接口
