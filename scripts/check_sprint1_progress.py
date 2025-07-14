#!/usr/bin/env python3
"""
Sprint 1 进度检查脚本
基于TDD验证Sprint 1的完成情况
"""
import subprocess
import sys
from pathlib import Path
import json

class Sprint1ProgressChecker:
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {}
        
    def check_task(self, task_id, description, check_function):
        """检查单个任务"""
        print(f"🔍 检查 {task_id}: {description}")
        try:
            result = check_function()
            status = "✅ 完成" if result else "❌ 未完成"
            print(f"   {status}")
            self.results[task_id] = {"description": description, "completed": result}
            return result
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
            self.results[task_id] = {"description": description, "completed": False, "error": str(e)}
            return False
    
    def check_env_001(self):
        """ENV-001: 开发环境配置"""
        checks = []
        
        # Python环境检查
        version = sys.version_info
        checks.append(version.major == 3 and version.minor >= 11)
        
        # 数据库工具检查
        try:
            import asyncpg
            checks.append(True)
        except ImportError:
            checks.append(False)
        
        # Redis工具检查
        try:
            import redis
            checks.append(True)
        except ImportError:
            checks.append(False)
        
        # Docker检查（可选）
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            checks.append(result.returncode == 0)
        except FileNotFoundError:
            checks.append(False)  # Docker不是必需的，但建议有
        
        return sum(checks) >= 3  # 至少3/4通过
    
    def check_env_002(self):
        """ENV-002: 项目结构初始化"""
        required_structure = [
            "app/__init__.py",
            "app/main.py", 
            "app/core/__init__.py",
            "app/core/config.py",
            "tests/__init__.py",
            "tests/conftest.py",
            "requirements/base.txt",
            "requirements/dev.txt",
            "pytest.ini"
        ]
        
        for path in required_structure:
            if not (self.project_root / path).exists():
                return False
        
        # 检查FastAPI应用是否可以创建
        try:
            from app.main import create_app
            app = create_app()
            return True
        except Exception:
            return False
    
    def check_env_003(self):
        """ENV-003: 数据库设计（基础版本）"""
        # 目前只检查数据库连接模块是否存在
        # 实际的数据库设计将在后续任务中完成
        try:
            from app.core.config import get_settings
            settings = get_settings()
            return hasattr(settings, 'database_url')
        except Exception:
            return False
    
    def check_env_004(self):
        """ENV-004: CI/CD流水线（基础版本）"""
        # 检查测试是否可以运行
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_acceptance_criteria(self):
        """检查Sprint 1验收标准"""
        criteria = []
        
        # 1. 开发环境可正常启动
        try:
            from app.main import create_app
            app = create_app()
            criteria.append(True)
        except Exception:
            criteria.append(False)
        
        # 2. 数据库连接正常（配置层面）
        try:
            from app.core.config import get_settings
            settings = get_settings()
            criteria.append(bool(settings.database_url))
        except Exception:
            criteria.append(False)
        
        # 3. CI/CD流水线运行成功（测试层面）
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/test_environment.py", "-v"],
                capture_output=True,
                text=True
            )
            criteria.append(result.returncode == 0)
        except Exception:
            criteria.append(False)
        
        # 4. 团队成员都能正常开发（工具链检查）
        tools_available = []
        for tool in ["black", "flake8", "pytest"]:
            try:
                result = subprocess.run([sys.executable, "-m", tool, "--version"], 
                                      capture_output=True)
                tools_available.append(result.returncode == 0)
            except Exception:
                tools_available.append(False)
        
        criteria.append(all(tools_available))
        
        return all(criteria)
    
    def run_full_check(self):
        """运行完整的Sprint 1检查"""
        print("🎯 Sprint 1 进度检查开始...\n")
        
        # 检查各个任务
        tasks = [
            ("ENV-001", "开发环境配置", self.check_env_001),
            ("ENV-002", "项目结构初始化", self.check_env_002), 
            ("ENV-003", "数据库设计（基础）", self.check_env_003),
            ("ENV-004", "CI/CD流水线（基础）", self.check_env_004)
        ]
        
        completed_tasks = 0
        for task_id, description, check_func in tasks:
            if self.check_task(task_id, description, check_func):
                completed_tasks += 1
        
        print(f"\n📊 任务完成情况: {completed_tasks}/{len(tasks)}")
        
        # 检查验收标准
        print(f"\n🎯 验收标准检查:")
        acceptance_passed = self.check_task(
            "ACCEPTANCE", 
            "Sprint 1 验收标准", 
            self.check_acceptance_criteria
        )
        
        # 生成报告
        self.generate_report(completed_tasks, len(tasks), acceptance_passed)
        
        return completed_tasks == len(tasks) and acceptance_passed
    
    def generate_report(self, completed, total, acceptance_passed):
        """生成进度报告"""
        progress_percentage = (completed / total) * 100
        
        print(f"\n📋 Sprint 1 进度报告")
        print(f"=" * 50)
        print(f"总体进度: {progress_percentage:.1f}% ({completed}/{total})")
        print(f"验收状态: {'✅ 通过' if acceptance_passed else '❌ 未通过'}")
        
        if progress_percentage == 100 and acceptance_passed:
            print(f"\n🎉 Sprint 1 完成！可以开始Sprint 2")
            print(f"📋 下一步:")
            print(f"   1. 开始需求解析模块开发")
            print(f"   2. 集成LangChain")
            print(f"   3. 实现文档解析器")
        else:
            print(f"\n⚠️  Sprint 1 尚未完成")
            print(f"📋 待完成任务:")
            for task_id, result in self.results.items():
                if not result["completed"]:
                    print(f"   - {task_id}: {result['description']}")
        
        # 保存结果到文件
        with open("sprint1_progress.json", "w") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细结果已保存到: sprint1_progress.json")

if __name__ == "__main__":
    checker = Sprint1ProgressChecker()
    success = checker.run_full_check()
    sys.exit(0 if success else 1)
