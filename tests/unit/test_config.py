"""
配置管理测试
测试环境变量配置和默认值
"""
import os
import pytest
from unittest.mock import patch
from app.core.config import Settings, get_settings

class TestSettings:
    """测试配置设置"""
    
    def test_default_settings(self):
        """测试默认配置值"""
        settings = Settings()
        
        # 应用基础配置
        assert settings.app_name == "TestMind AI"
        assert settings.debug is False
        assert settings.version == "0.1.0"
        
        # 数据库配置应该有默认值但可以被环境变量覆盖
        assert settings.database_url is not None
        assert settings.redis_url is not None
        
        # 安全配置
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
        
        # AI配置
        assert settings.langchain_verbose is False
        
        # 测试配置
        assert settings.testing is False
    
    def test_environment_variable_override(self):
        """测试环境变量覆盖配置"""
        env_vars = {
            "APP_NAME": "TestMind AI Test",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
            "REDIS_URL": "redis://localhost:6380/1",
            "SECRET_KEY": "test-secret-key-123",
            "OPENAI_API_KEY": "sk-test-key-123",
            "LANGCHAIN_VERBOSE": "true",
            "TESTING": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            
            assert settings.app_name == "TestMind AI Test"
            assert settings.debug is True
            assert settings.database_url == "postgresql://test:test@localhost:5432/test_db"
            assert settings.redis_url == "redis://localhost:6380/1"
            assert settings.secret_key == "test-secret-key-123"
            assert settings.openai_api_key == "sk-test-key-123"
            assert settings.langchain_verbose is True
            assert settings.testing is True
    
    def test_production_secret_key_validation(self):
        """测试生产环境密钥验证"""
        # 生产环境必须设置安全的SECRET_KEY
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "dev-secret-key-change-in-production",  # 默认值在生产环境应该失败
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with pytest.raises(ValueError, match="生产环境必须设置安全的SECRET_KEY"):
                Settings()
    
    def test_openai_api_key_validation(self):
        """测试OpenAI API密钥验证"""
        # 有效的API密钥格式
        valid_keys = [
            "sk-1234567890abcdef1234567890abcdef12345678",
            "sk-proj-1234567890abcdef1234567890abcdef12345678"
        ]
        
        for key in valid_keys:
            with patch.dict(os.environ, {"OPENAI_API_KEY": key}, clear=False):
                settings = Settings()
                assert settings.openai_api_key == key
    
    def test_database_url_validation(self):
        """测试数据库URL验证"""
        # 有效的数据库URL格式
        valid_urls = [
            "postgresql://user:pass@localhost:5432/db",
            "postgresql+asyncpg://user:pass@localhost:5432/db",
            "sqlite:///./test.db"
        ]
        
        for url in valid_urls:
            with patch.dict(os.environ, {"DATABASE_URL": url}, clear=False):
                settings = Settings()
                assert settings.database_url == url
    
    def test_redis_url_validation(self):
        """测试Redis URL验证"""
        # 有效的Redis URL格式
        valid_urls = [
            "redis://localhost:6379/0",
            "redis://user:pass@localhost:6379/1",
            "rediss://localhost:6380/0"  # SSL Redis
        ]
        
        for url in valid_urls:
            with patch.dict(os.environ, {"REDIS_URL": url}, clear=False):
                settings = Settings()
                assert settings.redis_url == url
    
    def test_boolean_environment_variables(self):
        """测试布尔类型环境变量的解析"""
        # 测试各种布尔值表示
        true_values = ["true", "True", "TRUE", "1", "yes", "on"]
        false_values = ["false", "False", "FALSE", "0", "no", "off"]
        
        for value in true_values:
            with patch.dict(os.environ, {"DEBUG": value}, clear=False):
                settings = Settings()
                assert settings.debug is True
        
        for value in false_values:
            with patch.dict(os.environ, {"DEBUG": value}, clear=False):
                settings = Settings()
                assert settings.debug is False
    
    def test_integer_environment_variables(self):
        """测试整数类型环境变量的解析"""
        with patch.dict(os.environ, {"ACCESS_TOKEN_EXPIRE_MINUTES": "60"}, clear=False):
            settings = Settings()
            assert settings.access_token_expire_minutes == 60
    
    def test_get_settings_singleton(self):
        """测试get_settings单例模式"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # 应该返回同一个实例
        assert settings1 is settings2
    
    def test_development_environment(self):
        """测试开发环境配置"""
        env_vars = {
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "TESTING": "false"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.environment == "development"
            assert settings.debug is True
            assert settings.testing is False
    
    def test_production_environment(self):
        """测试生产环境配置"""
        env_vars = {
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "SECRET_KEY": "super-secure-production-key-123456789012345678901234567890",  # 32+字符
            "DATABASE_URL": "postgresql://prod_user:prod_pass@prod_host:5432/prod_db"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.environment == "production"
            assert settings.debug is False
            assert settings.secret_key == "super-secure-production-key-123456789012345678901234567890"
    
    def test_testing_environment(self):
        """测试测试环境配置"""
        env_vars = {
            "ENVIRONMENT": "testing",
            "TESTING": "true",
            "DATABASE_URL": "sqlite:///./test.db"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.environment == "testing"
            assert settings.testing is True
