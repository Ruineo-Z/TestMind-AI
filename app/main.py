"""
TestMind AI - 主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.core.config import get_settings
from app.core.database import get_database_manager, close_database_connections
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    yield
    # 关闭时的清理
    await close_database_connections()

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app_settings = get_settings()

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.version,
        debug=app_settings.debug,
        description="AI-powered automated testing platform",
        lifespan=lifespan
    )

    # 注册API路由
    app.include_router(api_router)

    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "app_name": app_settings.app_name,
            "version": app_settings.version
        }

    @app.get("/health/database")
    async def database_health_check():
        """数据库健康检查端点"""
        try:
            db_manager = await get_database_manager()
            is_healthy = await db_manager.health_check()

            return {
                "database": {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "connected": db_manager.is_connected()
                }
            }
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database health check failed: {str(e)}"
            )



    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
