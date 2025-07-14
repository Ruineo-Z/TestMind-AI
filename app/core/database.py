"""
TestMind AI - 数据库管理模块
"""
import asyncpg
import asyncio
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from .config import get_settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or get_settings().database_url
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """建立数据库连接池"""
        try:
            self._pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    async def disconnect(self) -> None:
        """关闭数据库连接池"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._pool is not None and not self._pool._closed
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """获取数据库连接"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        
        async with self._pool.acquire() as connection:
            yield connection
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None

async def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.connect()
    return _db_manager

async def get_database_connection(database_url: Optional[str] = None) -> DatabaseManager:
    """获取数据库连接（兼容性函数）"""
    if database_url:
        # 如果提供了特定的URL，创建新的管理器
        manager = DatabaseManager(database_url)
        await manager.connect()
        return manager
    else:
        # 使用全局管理器
        return await get_database_manager()

def validate_database_url(url: str) -> bool:
    """验证数据库URL格式"""
    if not url:
        return False
    
    valid_schemes = ["postgresql", "postgresql+asyncpg"]
    
    for scheme in valid_schemes:
        if url.startswith(f"{scheme}://"):
            return True
    
    return False

async def close_database_connections():
    """关闭所有数据库连接"""
    global _db_manager
    if _db_manager:
        await _db_manager.disconnect()
        _db_manager = None
