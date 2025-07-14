"""
TestMind AI - 配置管理
基于环境变量的配置系统
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置设置 - 通过环境变量配置"""

    # 环境配置
    environment: str = Field(default="development", description="运行环境")

    # 应用基础配置
    app_name: str = Field(default="TestMind AI", description="应用名称")
    debug: bool = Field(default=False, description="调试模式")
    version: str = Field(default="0.1.0", description="应用版本")

    # 数据库配置 - 通过环境变量配置
    database_url: str = Field(
        default="postgresql://testmind:testmind@localhost:5432/testmind",
        description="数据库连接URL"
    )

    # Redis配置 - 通过环境变量配置
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )

    # 安全配置 - 必须通过环境变量设置
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT密钥"
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="Token过期时间(分钟)")

    # AI配置 - 通过环境变量配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    langchain_verbose: bool = Field(default=False, description="LangChain详细日志")

    # 测试配置
    testing: bool = Field(default=False, description="测试模式")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """验证密钥安全性"""
        if info.data.get('environment') == 'production':
            if not v or v == "dev-secret-key-change-in-production":
                raise ValueError("生产环境必须设置安全的SECRET_KEY")
            if len(v) < 32:
                raise ValueError("生产环境SECRET_KEY长度至少32字符")
        return v

    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_api_key(cls, v: Optional[str]) -> Optional[str]:
        """验证OpenAI API密钥格式"""
        if v is not None:
            if not v.startswith(('sk-', 'sk-proj-')):
                raise ValueError("OpenAI API密钥格式无效")
        return v

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """验证数据库URL格式"""
        valid_schemes = ['postgresql', 'postgresql+asyncpg', 'sqlite']
        if not any(v.startswith(f'{scheme}://') for scheme in valid_schemes):
            raise ValueError(f"数据库URL必须以以下之一开头: {valid_schemes}")
        return v

    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """验证Redis URL格式"""
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError("Redis URL必须以redis://或rediss://开头")
        return v

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()
