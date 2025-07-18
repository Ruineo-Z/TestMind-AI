"""
统一日志配置模块
使用loguru进行日志管理，支持按天和脚本分别保存日志文件
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import Optional


class LoggerConfig:
    """日志配置管理器"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 按日期创建子目录
        self.daily_dir = self.log_dir / datetime.now().strftime("%Y-%m-%d")
        self.daily_dir.mkdir(exist_ok=True)
        
        # 移除默认的控制台处理器
        logger.remove()
        
        # 添加控制台输出（带颜色）
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # 添加全局日志文件（按天）
        logger.add(
            self.daily_dir / "all.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            encoding="utf-8"
        )
    
    def setup_script_logger(self, script_name: str, level: str = "INFO") -> None:
        """
        为特定脚本设置专用日志文件
        
        Args:
            script_name: 脚本名称（不含扩展名）
            level: 日志级别
        """
        # 清理脚本名称
        clean_name = script_name.replace(".py", "").replace("/", "_").replace("\\", "_")
        
        # 创建脚本专用日志文件
        script_log_file = self.daily_dir / f"{clean_name}.log"
        
        logger.add(
            script_log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            rotation="100 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8",
            filter=lambda record: record["extra"].get("script") == clean_name
        )
        
        # 绑定脚本标识
        return logger.bind(script=clean_name)
    
    def get_script_logger(self, script_name: str, level: str = "INFO"):
        """
        获取脚本专用的logger实例
        
        Args:
            script_name: 脚本名称
            level: 日志级别
            
        Returns:
            绑定了脚本标识的logger实例
        """
        clean_name = script_name.replace(".py", "").replace("/", "_").replace("\\", "_")
        
        # 如果还没有为这个脚本设置日志，则设置
        script_log_file = self.daily_dir / f"{clean_name}.log"
        if not script_log_file.exists():
            self.setup_script_logger(script_name, level)
        
        return logger.bind(script=clean_name)


# 全局日志配置实例
_logger_config = None


def get_logger(script_name: Optional[str] = None, level: str = "INFO"):
    """
    获取logger实例
    
    Args:
        script_name: 脚本名称，如果提供则创建脚本专用日志
        level: 日志级别
        
    Returns:
        logger实例
    """
    global _logger_config
    
    if _logger_config is None:
        _logger_config = LoggerConfig()
    
    if script_name:
        return _logger_config.get_script_logger(script_name, level)
    else:
        return logger


def setup_test_logger(test_name: str, level: str = "INFO"):
    """
    为测试脚本设置专用logger
    
    Args:
        test_name: 测试名称
        level: 日志级别
        
    Returns:
        配置好的logger实例
    """
    return get_logger(f"test_{test_name}", level)


def setup_service_logger(service_name: str, level: str = "INFO"):
    """
    为服务设置专用logger
    
    Args:
        service_name: 服务名称
        level: 日志级别
        
    Returns:
        配置好的logger实例
    """
    return get_logger(f"service_{service_name}", level)


# 便捷的日志函数
def log_info(message: str, script_name: Optional[str] = None):
    """记录信息日志"""
    get_logger(script_name).info(message)


def log_error(message: str, script_name: Optional[str] = None):
    """记录错误日志"""
    get_logger(script_name).error(message)


def log_warning(message: str, script_name: Optional[str] = None):
    """记录警告日志"""
    get_logger(script_name).warning(message)


def log_debug(message: str, script_name: Optional[str] = None):
    """记录调试日志"""
    get_logger(script_name).debug(message)


def log_success(message: str, script_name: Optional[str] = None):
    """记录成功日志"""
    get_logger(script_name).success(message)


# 测试日志功能
if __name__ == "__main__":
    # 测试基本日志功能
    test_logger = get_logger("test_logger_module")
    
    test_logger.info("这是一条信息日志")
    test_logger.warning("这是一条警告日志")
    test_logger.error("这是一条错误日志")
    test_logger.success("这是一条成功日志")
    test_logger.debug("这是一条调试日志")
    
    # 测试脚本专用日志
    script_logger = setup_test_logger("comprehensive_gen001")
    script_logger.info("GEN-001测试开始")
    script_logger.success("测试步骤1完成")
    script_logger.warning("发现潜在问题")
    script_logger.info("GEN-001测试结束")
    
    print("✅ 日志配置测试完成，请检查 logs/ 目录下的日志文件")
