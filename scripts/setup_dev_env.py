#!/usr/bin/env python3
"""
TestMind AI - 开发环境设置脚本
自动化设置开发环境的TDD验证脚本
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """运行命令并检查结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败")
        print(f"错误: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本不符合要求: {version.major}.{version.minor}.{version.micro} (需要3.11+)")
        return False

def setup_environment():
    """设置开发环境"""
    print("🚀 开始设置TestMind AI开发环境...")
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查项目结构
    project_root = Path.cwd()
    required_files = [
        "requirements/dev.txt",
        "pytest.ini", 
        "tests/conftest.py"
    ]
    
    for file_path in required_files:
        if not (project_root / file_path).exists():
            print(f"❌ 缺少必需文件: {file_path}")
            return False
    
    print("✅ 项目结构检查通过")
    
    # 安装依赖
    if not run_command("pip install -r requirements/dev.txt", "安装开发依赖"):
        return False
    
    # 运行环境测试
    if not run_command("python -m pytest tests/unit/test_environment.py -v", "运行环境测试"):
        return False
    
    # 启动应用测试
    print("🔄 测试应用启动...")
    try:
        # 导入测试
        from app.main import create_app
        app = create_app()
        print("✅ 应用创建成功")
        
        # 简单的健康检查测试
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ 健康检查端点正常")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 应用启动测试失败: {e}")
        return False
    
    print("\n🎉 开发环境设置完成！")
    print("\n📋 下一步操作:")
    print("1. 运行完整测试: pytest")
    print("2. 启动开发服务器: python -m app.main")
    print("3. 查看API文档: http://localhost:8000/docs")
    print("4. 开始Sprint 1的下一个任务")
    
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
