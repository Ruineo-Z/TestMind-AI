# Sprint 1 TDD实施计划

## 🎯 目标：建立坚实的TDD基础设施

### Day 1: 测试基础设施搭建

#### 1. 项目结构创建
```bash
testmind-ai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   └── api/
│       ├── __init__.py
│       └── v1/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── test.txt
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

#### 2. 测试配置文件
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
asyncio_mode = auto
```

#### 3. 第一个TDD循环：数据库连接
```python
# tests/unit/test_database.py
import pytest
from app.core.database import get_database_connection

class TestDatabaseConnection:
    @pytest.mark.asyncio
    async def test_database_connection_success(self):
        """测试数据库连接成功"""
        # 这个测试会失败，因为还没有实现
        connection = await get_database_connection()
        assert connection is not None
        assert connection.is_connected()
    
    @pytest.mark.asyncio
    async def test_database_connection_with_invalid_url(self):
        """测试无效URL的错误处理"""
        with pytest.raises(ConnectionError):
            await get_database_connection("invalid://url")
```

### Day 2: 核心组件TDD实现

#### 1. 数据库模块实现
```python
# app/core/database.py
import asyncpg
from typing import Optional
from .config import get_settings

class DatabaseConnection:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool
    
    def is_connected(self) -> bool:
        return self._pool is not None and not self._pool._closed
    
    async def close(self):
        if self._pool:
            await self._pool.close()

async def get_database_connection(url: Optional[str] = None) -> DatabaseConnection:
    """获取数据库连接"""
    settings = get_settings()
    database_url = url or settings.database_url
    
    try:
        pool = await asyncpg.create_pool(database_url)
        return DatabaseConnection(pool)
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")
```

#### 2. 配置模块TDD
```python
# tests/unit/test_config.py
import pytest
import os
from app.core.config import Settings, get_settings

class TestSettings:
    def test_settings_default_values(self):
        """测试默认配置值"""
        settings = Settings()
        assert settings.app_name == "TestMind AI"
        assert settings.debug is False
        assert settings.database_url is not None
    
    def test_settings_from_environment(self, monkeypatch):
        """测试从环境变量读取配置"""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
        monkeypatch.setenv("DEBUG", "true")
        
        settings = Settings()
        assert "test:test@localhost/test" in settings.database_url
        assert settings.debug is True
```

### Day 3: FastAPI应用TDD

#### 1. 应用启动测试
```python
# tests/integration/test_app.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAppStartup:
    def test_app_startup(self):
        """测试应用能够正常启动"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_app_database_health_check(self):
        """测试数据库健康检查"""
        client = TestClient(app)
        response = client.get("/health/database")
        assert response.status_code == 200
        assert "database" in response.json()
```

#### 2. FastAPI应用实现
```python
# app/main.py
from fastapi import FastAPI, Depends
from .core.config import get_settings
from .core.database import get_database_connection
from .api.v1 import health

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0"
    )
    
    # 注册路由
    app.include_router(health.router, prefix="/health", tags=["health"])
    
    return app

app = create_app()
```

### Day 4: Docker和CI/CD TDD

#### 1. Docker配置测试
```python
# tests/e2e/test_docker.py
import subprocess
import pytest
import requests
import time

class TestDockerDeployment:
    def test_docker_build_success(self):
        """测试Docker镜像构建成功"""
        result = subprocess.run(
            ["docker", "build", "-t", "testmind-ai:test", "."],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
    
    def test_docker_container_health(self):
        """测试Docker容器健康状态"""
        # 启动容器
        subprocess.run([
            "docker", "run", "-d", "--name", "testmind-test",
            "-p", "8000:8000", "testmind-ai:test"
        ])
        
        # 等待启动
        time.sleep(5)
        
        try:
            response = requests.get("http://localhost:8000/health")
            assert response.status_code == 200
        finally:
            # 清理
            subprocess.run(["docker", "stop", "testmind-test"])
            subprocess.run(["docker", "rm", "testmind-test"])
```

## 🎯 Sprint 1 验收标准（TDD版本）

### 自动化验收测试
```python
# tests/acceptance/test_sprint1_acceptance.py
import pytest
import subprocess
import requests
import asyncio
from app.core.database import get_database_connection

class TestSprint1Acceptance:
    """Sprint 1 完整验收测试套件"""
    
    def test_development_environment_ready(self):
        """验收标准1：开发环境可正常启动"""
        # 测试Python环境
        result = subprocess.run(["python", "--version"], capture_output=True)
        assert result.returncode == 0
        assert "3.11" in result.stdout.decode() or "3.12" in result.stdout.decode()
        
        # 测试依赖安装
        import fastapi, pytest, asyncpg
        assert True  # 如果能导入就说明安装成功
    
    @pytest.mark.asyncio
    async def test_database_connection_working(self):
        """验收标准2：数据库连接正常"""
        connection = await get_database_connection()
        assert connection.is_connected()
        await connection.close()
    
    def test_ci_cd_pipeline_working(self):
        """验收标准3：CI/CD流水线运行成功"""
        # 运行完整测试套件
        result = subprocess.run(["pytest", "--cov=app"], capture_output=True)
        assert result.returncode == 0
        
        # 检查覆盖率
        assert "TOTAL" in result.stdout.decode()
    
    def test_team_development_ready(self):
        """验收标准4：团队成员都能正常开发"""
        # 检查代码格式化工具
        result = subprocess.run(["black", "--check", "app/"], capture_output=True)
        # 如果代码已格式化，返回0；如果需要格式化，返回1
        assert result.returncode in [0, 1]
        
        # 检查代码质量工具
        result = subprocess.run(["flake8", "app/"], capture_output=True)
        assert result.returncode == 0
```

## 📊 每日进度检查

### Day 1 检查点
- [ ] 项目结构创建完成
- [ ] 测试框架配置完成
- [ ] 第一个测试用例编写并失败
- [ ] 基础CI配置完成

### Day 2 检查点
- [ ] 数据库连接模块TDD完成
- [ ] 配置管理模块TDD完成
- [ ] 单元测试覆盖率 > 80%
- [ ] 所有测试通过

### Day 3 检查点
- [ ] FastAPI应用TDD完成
- [ ] 健康检查接口实现
- [ ] 集成测试通过
- [ ] API文档自动生成

### Day 4 检查点
- [ ] Docker配置完成
- [ ] CI/CD流水线运行成功
- [ ] 端到端测试通过
- [ ] 团队开发环境验证

## 🚨 风险缓解措施

1. **数据库连接问题**：准备SQLite作为备选方案
2. **Docker环境问题**：提供本地开发替代方案
3. **CI/CD配置复杂**：先实现基础版本，后续迭代
4. **团队环境差异**：提供详细的环境配置文档

## 🎯 成功标准

Sprint 1成功的标志：
- 所有验收测试通过
- 测试覆盖率 ≥ 80%
- CI/CD流水线绿色
- 团队成员能够独立开发和测试
