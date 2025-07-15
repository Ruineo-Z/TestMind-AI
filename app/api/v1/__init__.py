"""
API v1版本路由配置
"""
from fastapi import APIRouter

from app.api.v1.requirements import router as requirements_router


# 创建v1版本的主路由
api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(requirements_router)
