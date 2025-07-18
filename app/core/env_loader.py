"""
环境变量加载器
从.env文件加载环境变量，支持AI Provider配置
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any


class EnvLoader:
    """环境变量加载器"""
    
    def __init__(self, env_file: str = ".env"):
        """
        初始化环境变量加载器
        
        Args:
            env_file: .env文件路径
        """
        self.env_file = Path(env_file)
        self.loaded = False
        
    def load_env(self) -> bool:
        """
        加载.env文件中的环境变量
        
        Returns:
            bool: 是否成功加载
        """
        if not self.env_file.exists():
            print(f"⚠️  .env文件不存在: {self.env_file}")
            return False
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # 设置环境变量（如果尚未设置）
                        if key not in os.environ:
                            os.environ[key] = value
                    else:
                        print(f"⚠️  .env文件第{line_num}行格式错误: {line}")
            
            self.loaded = True
            print(f"✅ 成功加载.env文件: {self.env_file}")
            return True
            
        except Exception as e:
            print(f"❌ 加载.env文件失败: {e}")
            return False
    
    def get_ai_config(self) -> Dict[str, Any]:
        """
        获取AI相关配置
        
        Returns:
            Dict: AI配置信息
        """
        if not self.loaded:
            self.load_env()
        
        config = {
            # API Keys
            "google_api_key": os.environ.get("GOOGLE_API_KEY"),
            "openai_api_key": os.environ.get("OPENAI_API_KEY"),

            # Gemini配置
            "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite-preview-06-17"),

            # OpenAI配置
            "openai_model": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            
            # Ollama配置
            "ollama_base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            "ollama_model": os.environ.get("OLLAMA_MODEL", "qwen2.5:3b"),

            # 默认提供商
            "default_provider": os.environ.get("DEFAULT_AI_PROVIDER", "gemini"),

            # LangChain配置
            "langchain_verbose": os.environ.get("LANGCHAIN_VERBOSE", "false").lower() == "true",
            "langchain_tracing": os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        }
        
        return config
    
    def check_api_keys(self) -> Dict[str, bool]:
        """
        检查API Key是否配置
        
        Returns:
            Dict: 各个API Key的配置状态
        """
        config = self.get_ai_config()
        
        status = {
            "gemini": bool(config["google_api_key"] and config["google_api_key"] != "your-gemini-api-key-here"),
            "openai": bool(config["openai_api_key"] and config["openai_api_key"] != "your-openai-api-key-here"),
            "ollama": True  # Ollama不需要API Key
        }
        
        return status
    
    def print_config_status(self):
        """打印配置状态"""
        print("\n🔧 AI Provider配置状态:")
        print("=" * 40)
        
        config = self.get_ai_config()
        status = self.check_api_keys()
        
        # Gemini配置
        if status["gemini"]:
            masked_key = self._mask_api_key(config["google_api_key"])
            print(f"✅ Gemini API Key: {masked_key}")
        else:
            print(f"❌ Gemini API Key: 未配置")
        
        # OpenAI配置
        if status["openai"]:
            masked_key = self._mask_api_key(config["openai_api_key"])
            print(f"✅ OpenAI API Key: {masked_key}")
        else:
            print(f"❌ OpenAI API Key: 未配置")
        
        # Ollama配置
        print(f"✅ Ollama URL: {config['ollama_base_url']}")
        print(f"✅ Ollama Model: {config['ollama_model']}")
        
        # 默认提供商
        print(f"🎯 默认AI提供商: {config['default_provider']}")
        
        # 配置建议
        if not any(status.values()):
            print("\n💡 建议:")
            print("请在.env文件中配置至少一个AI Provider的API Key")
        elif not status[config['default_provider']]:
            print(f"\n⚠️  警告: 默认提供商 '{config['default_provider']}' 未配置API Key")
    
    def _mask_api_key(self, api_key: Optional[str]) -> str:
        """
        遮蔽API Key，只显示前后几位
        
        Args:
            api_key: API Key
            
        Returns:
            str: 遮蔽后的API Key
        """
        if not api_key or len(api_key) < 16:
            return "***"
        
        return f"{api_key[:8]}...{api_key[-8:]}"


# 全局实例
env_loader = EnvLoader()


def load_env_config() -> bool:
    """
    加载环境配置的便捷函数
    
    Returns:
        bool: 是否成功加载
    """
    return env_loader.load_env()


def get_ai_config() -> Dict[str, Any]:
    """
    获取AI配置的便捷函数
    
    Returns:
        Dict: AI配置
    """
    return env_loader.get_ai_config()


def check_api_keys() -> Dict[str, bool]:
    """
    检查API Key配置的便捷函数
    
    Returns:
        Dict: API Key配置状态
    """
    return env_loader.check_api_keys()


if __name__ == "__main__":
    # 测试环境变量加载
    loader = EnvLoader()
    loader.load_env()
    loader.print_config_status()
