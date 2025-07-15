#!/usr/bin/env python3
"""
生产级文档解析测试执行脚本
支持不同级别的测试执行和详细的测试报告
"""
import argparse
import time
import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import psutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ProductionTestRunner:
    """生产级测试执行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = []
        self.start_time = None
        
    def run_tests(self, level: str = "all", verbose: bool = True):
        """执行测试"""
        self.start_time = time.time()
        
        print("🏭 TestMind AI - 生产级文档解析功能测试")
        print("=" * 60)
        print(f"测试级别: {level}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python版本: {sys.version}")
        print(f"工作目录: {self.project_root}")
        
        # 检查环境
        self._check_environment()
        
        # 执行测试
        if level == "all":
            self._run_all_levels()
        else:
            self._run_specific_level(level)
        
        # 生成报告
        self._generate_report()
    
    def _check_environment(self):
        """检查测试环境"""
        print("\n🔍 环境检查")
        print("-" * 30)
        
        # 检查依赖
        try:
            import fastapi
            import pytest
            import psutil
            print("✅ 核心依赖包已安装")
        except ImportError as e:
            print(f"❌ 缺少依赖包: {e}")
            sys.exit(1)
        
        # 检查测试数据
        test_data_dir = self.project_root / "tests" / "integration" / "test_data"
        if not test_data_dir.exists():
            print("⚠️  测试数据目录不存在，将创建基础测试数据")
            self._create_test_data()
        else:
            print("✅ 测试数据目录存在")
        
        # 检查系统资源
        memory = psutil.virtual_memory()
        print(f"💾 可用内存: {memory.available / 1024 / 1024 / 1024:.1f} GB")
        print(f"🖥️  CPU核心数: {psutil.cpu_count()}")
    
    def _create_test_data(self):
        """创建基础测试数据"""
        test_data_dir = self.project_root / "tests" / "integration" / "test_data"
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建markdown测试目录
        markdown_dir = test_data_dir / "markdown"
        markdown_dir.mkdir(exist_ok=True)
        
        print("📝 创建基础测试数据完成")
    
    def _run_all_levels(self):
        """运行所有级别的测试"""
        levels = [
            ("1", "快速验证测试", "< 30秒"),
            ("2", "全面功能测试", "2-5分钟"),
            ("3", "性能压力测试", "5-10分钟"),
            ("4", "用户验收测试", "端到端场景")
        ]
        
        for level, name, duration in levels:
            print(f"\n📋 Level {level}: {name} (预计耗时: {duration})")
            print("-" * 50)
            self._run_specific_level(level)
    
    def _run_specific_level(self, level: str):
        """运行特定级别的测试"""
        test_file = self.project_root / "tests" / "integration" / "test_document_parsing_production.py"
        
        if not test_file.exists():
            print(f"❌ 测试文件不存在: {test_file}")
            return
        
        # 构建pytest命令
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v",
            "--tb=short"
        ]

        if level == "1":
            cmd.append("-k TestLevel1QuickValidation")
        elif level == "2":
            cmd.append("-k TestLevel2ComprehensiveFunctionality")
        elif level == "3":
            cmd.append("-k TestLevel3PerformanceStress")
        elif level == "4":
            cmd.append("-k TestLevel4UserAcceptance")
        
        start_time = time.time()
        
        try:
            # 执行测试
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            duration = time.time() - start_time
            
            # 记录结果
            test_result = {
                "level": level,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            self.test_results.append(test_result)
            
            # 显示结果
            if result.returncode == 0:
                print(f"✅ Level {level} 测试通过 (耗时: {duration:.1f}秒)")
            else:
                print(f"❌ Level {level} 测试失败 (耗时: {duration:.1f}秒)")
                print("错误输出:")
                print(result.stderr)
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Level {level} 测试超时")
            self.test_results.append({
                "level": level,
                "duration": 600,
                "return_code": -1,
                "success": False,
                "error": "测试超时"
            })
        
        except Exception as e:
            print(f"💥 Level {level} 测试执行异常: {e}")
            self.test_results.append({
                "level": level,
                "duration": 0,
                "return_code": -1,
                "success": False,
                "error": str(e)
            })
    
    def _generate_report(self):
        """生成测试报告"""
        total_duration = time.time() - self.start_time
        
        print("\n📊 测试报告")
        print("=" * 60)
        print(f"总耗时: {total_duration:.1f}秒")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 测试统计:")
        print(f"  总测试级别: {total_tests}")
        print(f"  通过: {passed_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "  成功率: 0%")
        
        # 详细结果
        print(f"\n📋 详细结果:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  Level {result['level']}: {status} ({result['duration']:.1f}s)")
        
        # 保存报告到文件
        report_file = self.project_root / "test_reports" / f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests/total_tests if total_tests > 0 else 0
            },
            "results": self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细报告已保存到: {report_file}")
        
        # 给出建议
        self._provide_recommendations()
    
    def _provide_recommendations(self):
        """提供测试建议"""
        print(f"\n💡 建议:")
        
        failed_levels = [r["level"] for r in self.test_results if not r["success"]]
        
        if not failed_levels:
            print("  🎉 所有测试都通过了！系统已准备好生产部署。")
        else:
            print(f"  ⚠️  以下级别的测试失败: {', '.join(failed_levels)}")
            
            if "1" in failed_levels:
                print("  🔧 Level 1失败表示基础功能有问题，请检查API和核心解析器")
            if "2" in failed_levels:
                print("  🔧 Level 2失败表示复杂场景处理有问题，请检查错误处理和边界情况")
            if "3" in failed_levels:
                print("  🔧 Level 3失败表示性能不达标，请优化算法和资源使用")
            if "4" in failed_levels:
                print("  🔧 Level 4失败表示用户体验有问题，请检查端到端流程")
        
        # 性能建议
        slow_tests = [r for r in self.test_results if r.get("duration", 0) > 60]
        if slow_tests:
            print(f"  ⏰ 以下测试耗时较长，考虑优化: {[r['level'] for r in slow_tests]}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生产级文档解析功能测试")
    parser.add_argument(
        "--level",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="测试级别 (1=快速验证, 2=全面功能, 3=性能压力, 4=用户验收, all=全部)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    runner = ProductionTestRunner()
    runner.run_tests(level=args.level, verbose=args.verbose)


if __name__ == "__main__":
    main()
