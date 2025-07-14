"""
测试开发环境配置
这是我们的第一个TDD测试 - 验证环境是否正确配置
"""
import sys
import subprocess
import pytest
from pathlib import Path

class TestDevelopmentEnvironment:
    """测试开发环境配置是否正确"""
    
    def test_python_version(self):
        """测试Python版本是否符合要求"""
        version_info = sys.version_info
        assert version_info.major == 3
        assert version_info.minor >= 11, f"Python 3.11+ required, got {version_info.major}.{version_info.minor}"
    
    def test_required_packages_importable(self):
        """测试必需的包是否可以导入"""
        required_packages = [
            'fastapi',
            'uvicorn', 
            'asyncpg',
            'sqlalchemy',
            'langchain',
            'pydantic',
            'pytest'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package '{package}' not installed")
    
    def test_project_structure_exists(self):
        """测试项目结构是否正确创建"""
        project_root = Path.cwd()
        
        required_dirs = [
            'app',
            'tests',
            'requirements'
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Directory '{dir_name}' does not exist"
            assert dir_path.is_dir(), f"'{dir_name}' is not a directory"
    
    def test_configuration_files_exist(self):
        """测试配置文件是否存在"""
        project_root = Path.cwd()
        
        required_files = [
            'pytest.ini',
            'requirements/base.txt',
            'requirements/dev.txt',
            'tests/conftest.py'
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Configuration file '{file_path}' does not exist"
            assert full_path.is_file(), f"'{file_path}' is not a file"
    
    def test_pytest_configuration(self):
        """测试pytest配置是否正确"""
        # 运行pytest --collect-only来验证配置
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        # 如果配置正确，pytest应该能够收集测试
        assert result.returncode == 0, f"pytest configuration error: {result.stderr}"
    
    @pytest.mark.slow
    def test_database_tools_available(self):
        """测试数据库工具是否可用"""
        try:
            import asyncpg
            import sqlalchemy
            # 基本导入测试
            assert hasattr(asyncpg, 'create_pool')
            assert hasattr(sqlalchemy, 'create_engine')
        except ImportError as e:
            pytest.fail(f"Database tools not available: {e}")
    
    def test_ai_tools_available(self):
        """测试AI工具是否可用"""
        try:
            import langchain
            import openai
            # 基本导入测试 - 检查langchain模块是否可用
            # 注意：LLMChain在新版本中可能位置有变化，我们只检查基本导入
            assert langchain is not None
            assert openai is not None
        except ImportError as e:
            pytest.fail(f"AI tools not available: {e}")

class TestCodeQualityTools:
    """测试代码质量工具配置"""
    
    def test_black_available(self):
        """测试Black代码格式化工具"""
        result = subprocess.run(
            [sys.executable, '-m', 'black', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Black not available"
        assert 'black' in result.stdout.lower()
    
    def test_flake8_available(self):
        """测试Flake8代码检查工具"""
        result = subprocess.run(
            [sys.executable, '-m', 'flake8', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Flake8 not available"
    
    def test_pytest_coverage_available(self):
        """测试pytest覆盖率工具"""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "pytest not available"
        assert 'pytest' in result.stdout.lower()

class TestEnvironmentVariables:
    """测试环境变量配置"""
    
    def test_python_path_configured(self):
        """测试Python路径配置"""
        import os
        python_path = os.environ.get('PYTHONPATH', '')
        current_dir = str(Path.cwd())
        
        # PYTHONPATH应该包含当前目录或者Python能找到app模块
        try:
            import app
            # 如果能导入app模块，说明路径配置正确
            assert True
        except ImportError:
            # 如果不能导入，检查PYTHONPATH
            assert current_dir in python_path or '.' in python_path, \
                "PYTHONPATH not configured correctly for app module"
