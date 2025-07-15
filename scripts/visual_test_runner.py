#!/usr/bin/env python3
"""
可视化测试运行器
生成HTML测试报告和JSON数据，提供丰富的可视化测试结果
"""
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
import webbrowser

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class VisualTestRunner:
    """可视化测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_visual_tests(self, test_level: str = "all", open_browser: bool = True):
        """运行可视化测试"""
        print("🎨 TestMind AI - 可视化测试运行器")
        print("=" * 50)
        print(f"测试级别: {test_level}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 设置报告文件路径
        html_report = self.reports_dir / f"test_report_{timestamp}.html"
        json_report = self.reports_dir / f"test_report_{timestamp}.json"
        coverage_report = self.reports_dir / f"coverage_{timestamp}"
        
        # 确定测试文件
        if test_level == "all":
            test_files = [
                "tests/integration/test_production_simple.py",
                "tests/unit/test_requirements_api.py",
                "tests/unit/test_markdown_parser.py",
                "tests/unit/test_pdf_parser.py",
                "tests/unit/test_word_parser.py"
            ]
        elif test_level == "1":
            test_files = ["tests/integration/test_production_simple.py::TestLevel1QuickValidation"]
        elif test_level == "2":
            test_files = ["tests/integration/test_production_simple.py::TestLevel2ComprehensiveFunctionality"]
        else:
            test_files = ["tests/integration/test_production_simple.py"]
        
        # 构建pytest命令
        cmd = [
            sys.executable, "-m", "pytest",
            *test_files,
            "-v",
            "--tb=short",
            f"--html={html_report}",
            "--self-contained-html",
            f"--json-report={json_report}",
            "--json-report-summary",
            f"--cov=app",
            f"--cov-report=html:{coverage_report}",
            "--cov-report=term-missing"
        ]
        
        print(f"\n🔍 执行测试命令:")
        print(f"uv run pytest {' '.join(test_files)} --html={html_report.name}")
        
        start_time = time.time()
        
        try:
            # 执行测试
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            duration = time.time() - start_time
            
            # 显示结果
            print(f"\n📊 测试执行完成 (耗时: {duration:.1f}秒)")
            print(f"返回码: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ 所有测试通过!")
            else:
                print("❌ 部分测试失败")
            
            # 解析JSON报告
            if json_report.exists():
                self._display_test_summary(json_report)
            
            # 生成自定义可视化报告
            self._generate_custom_report(html_report, json_report, duration)
            
            # 打开浏览器
            if open_browser and html_report.exists():
                print(f"\n🌐 正在打开测试报告...")
                webbrowser.open(f"file://{html_report.absolute()}")
            
            print(f"\n📁 报告文件位置:")
            print(f"  HTML报告: {html_report}")
            print(f"  JSON数据: {json_report}")
            print(f"  覆盖率报告: {coverage_report}/index.html")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("⏰ 测试执行超时")
            return False
        except Exception as e:
            print(f"💥 测试执行异常: {e}")
            return False
    
    def _display_test_summary(self, json_report_path: Path):
        """显示测试摘要"""
        try:
            with open(json_report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            
            print(f"\n📈 测试统计:")
            print(f"  总测试数: {summary.get('total', 0)}")
            print(f"  通过: {summary.get('passed', 0)}")
            print(f"  失败: {summary.get('failed', 0)}")
            print(f"  跳过: {summary.get('skipped', 0)}")
            print(f"  错误: {summary.get('error', 0)}")
            print(f"  成功率: {(summary.get('passed', 0) / max(summary.get('total', 1), 1) * 100):.1f}%")
            
            # 显示失败的测试
            if summary.get('failed', 0) > 0:
                print(f"\n❌ 失败的测试:")
                for test in data.get('tests', []):
                    if test.get('outcome') == 'failed':
                        print(f"  - {test.get('nodeid', 'Unknown')}")
            
        except Exception as e:
            print(f"⚠️ 无法解析JSON报告: {e}")
    
    def _generate_custom_report(self, html_report: Path, json_report: Path, duration: float):
        """生成自定义可视化报告"""
        try:
            # 读取原始HTML报告
            if not html_report.exists():
                return
            
            with open(html_report, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 添加自定义样式和脚本
            custom_header = f"""
<style>
.custom-header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    text-align: center;
}}
.custom-stats {{
    display: flex;
    justify-content: space-around;
    margin: 20px 0;
}}
.stat-card {{
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    min-width: 120px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
.stat-number {{
    font-size: 2em;
    font-weight: bold;
    color: #2c3e50;
}}
.stat-label {{
    color: #7f8c8d;
    font-size: 0.9em;
}}
</style>
<div class="custom-header">
    <h1>🏭 TestMind AI - 测试报告</h1>
    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>执行耗时: {duration:.2f}秒</p>
</div>
"""
            
            # 插入自定义头部
            html_content = html_content.replace('<body>', f'<body>{custom_header}')
            
            # 保存增强的HTML报告
            with open(html_report, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"⚠️ 生成自定义报告失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="可视化测试运行器")
    parser.add_argument(
        "--level",
        choices=["1", "2", "all"],
        default="all",
        help="测试级别 (1=快速验证, 2=全面功能, all=全部)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="不自动打开浏览器"
    )
    
    args = parser.parse_args()
    
    runner = VisualTestRunner()
    success = runner.run_visual_tests(
        test_level=args.level,
        open_browser=not args.no_browser
    )
    
    if success:
        print("\n🎉 测试执行成功！请查看HTML报告获取详细结果。")
        return 0
    else:
        print("\n⚠️ 测试执行失败，请查看报告了解详情。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
