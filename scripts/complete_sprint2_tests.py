#!/usr/bin/env python3
"""
Sprint 2 完整测试套件
包含文档解析、AI模块、API接口的全面测试
"""
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CompleteSprint2TestSuite:
    """Sprint 2 完整测试套件"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.test_results = {}
        
    def run_complete_tests(self, open_browser=True, save_logs=True):
        """运行完整的Sprint 2测试"""
        print("🏭 TestMind AI - Sprint 2 完整测试套件")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试范围: 文档解析 + AI模块 + API接口 + 集成测试")
        print()

        start_time = time.time()

        # 1. 文档解析测试
        self._run_document_parsing_tests()

        # 2. AI模块测试
        self._run_ai_module_tests()

        # 3. API接口测试
        self._run_api_tests()

        # 4. 集成测试
        self._run_integration_tests()

        # 5. 生成综合报告和日志
        duration = time.time() - start_time

        if save_logs:
            self._save_comprehensive_logs(duration)

        self._generate_comprehensive_report(duration, open_browser)

        return self._calculate_overall_success()
    
    def _run_document_parsing_tests(self):
        """运行文档解析测试"""
        print("📝 1. 文档解析模块测试")
        print("-" * 50)
        
        # 运行文档解析器单元测试
        test_files = [
            "tests/unit/test_markdown_parser.py",
            "tests/unit/test_pdf_parser.py", 
            "tests/unit/test_word_parser.py"
        ]
        
        for test_file in test_files:
            parser_name = test_file.split('_')[2].replace('.py', '').upper()
            print(f"  🔍 测试 {parser_name} 解析器...")
            
            result = self._run_pytest(test_file)
            self.test_results[f"document_parsing_{parser_name.lower()}"] = result
            
            if result["success"]:
                print(f"  ✅ {parser_name} 解析器测试通过 ({result['duration']:.1f}s)")
            else:
                print(f"  ❌ {parser_name} 解析器测试失败")
        
        print()
    
    def _run_ai_module_tests(self):
        """运行AI模块测试"""
        print("🤖 2. AI模块测试")
        print("-" * 50)

        # 运行LangChain提取器测试
        print("  🔍 测试 LangChain 需求提取器...")
        result = self._run_pytest("tests/unit/test_langchain_extractor_simple.py")
        self.test_results["ai_langchain"] = result

        if result["success"]:
            print(f"  ✅ LangChain 提取器测试通过 ({result['duration']:.1f}s)")
        else:
            print(f"  ❌ LangChain 提取器测试失败")

        # 运行AI模块专项测试
        print("  🔍 测试 AI 模块专项功能...")
        ai_result = self._run_ai_module_script()
        self.test_results["ai_modules"] = ai_result

        if ai_result["success"]:
            print(f"  ✅ AI 模块专项测试通过 ({ai_result['duration']:.1f}s)")
        else:
            print(f"  ❌ AI 模块专项测试失败")

        # 运行AI模块详细测试报告
        print("  🔍 生成 AI 模块详细报告...")
        report_result = self._run_ai_module_report()
        self.test_results["ai_detailed_report"] = report_result

        if report_result["success"]:
            print(f"  ✅ AI 模块详细报告生成成功 ({report_result['duration']:.1f}s)")
        else:
            print(f"  ❌ AI 模块详细报告生成失败")

        print()
    
    def _run_api_tests(self):
        """运行API接口测试"""
        print("🔗 3. API接口测试")
        print("-" * 50)
        
        # 运行API单元测试
        print("  🔍 测试 API 接口...")
        result = self._run_pytest("tests/unit/test_requirements_api.py")
        self.test_results["api_units"] = result
        
        if result["success"]:
            print(f"  ✅ API 接口测试通过 ({result['duration']:.1f}s)")
        else:
            print(f"  ❌ API 接口测试失败")
        
        print()
    
    def _run_integration_tests(self):
        """运行集成测试"""
        print("🔄 4. 集成测试")
        print("-" * 50)
        
        # 运行生产级集成测试
        print("  🔍 测试 生产级集成功能...")
        result = self._run_pytest("tests/integration/test_production_simple.py")
        self.test_results["integration"] = result
        
        if result["success"]:
            print(f"  ✅ 集成测试通过 ({result['duration']:.1f}s)")
        else:
            print(f"  ❌ 集成测试失败")
        
        print()
    
    def _run_pytest(self, test_file):
        """运行pytest测试"""
        start_time = time.time()
        
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                test_file,
                "-v", "--tb=short"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            duration = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def _run_ai_module_script(self):
        """运行AI模块专项测试脚本"""
        start_time = time.time()

        try:
            cmd = [
                sys.executable,
                str(self.project_root / "scripts" / "test_ai_modules_no_mock.py"),
                "--level", "all"
            ]

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    def _run_ai_module_report(self):
        """运行AI模块详细报告生成"""
        start_time = time.time()

        try:
            cmd = [
                sys.executable,
                str(self.project_root / "scripts" / "ai_module_detailed_report.py"),
                "--no-browser"
            ]

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def _generate_comprehensive_report(self, total_duration, open_browser):
        """生成综合测试报告"""
        print("📊 5. 生成综合测试报告")
        print("-" * 50)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"sprint2_complete_report_{timestamp}.html"
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        # 生成HTML报告
        html_content = self._create_html_report(total_duration, total_tests, passed_tests, failed_tests)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  📄 报告已生成: {report_file.name}")
        print(f"  📏 报告大小: {report_file.stat().st_size / 1024:.1f} KB")
        
        if open_browser:
            print("  🌐 正在打开综合报告...")
            webbrowser.open(f"file://{report_file.absolute()}")
        
        print()
    
    def _create_html_report(self, total_duration, total_tests, passed_tests, failed_tests):
        """创建HTML报告"""
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 测试模块详情
        modules_html = ""
        for module_name, result in self.test_results.items():
            status_icon = "✅" if result["success"] else "❌"
            status_class = "success" if result["success"] else "failure"
            
            modules_html += f"""
            <div class="module-card {status_class}">
                <h3>{status_icon} {module_name.replace('_', ' ').title()}</h3>
                <p>执行时间: {result['duration']:.2f}秒</p>
                <p>状态: {'通过' if result['success'] else '失败'}</p>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sprint 2 完整测试报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .modules {{
            padding: 30px;
        }}
        .modules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .module-card {{
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        .module-card.success {{
            background: #d4edda;
            border-left: 5px solid #28a745;
        }}
        .module-card.failure {{
            background: #f8d7da;
            border-left: 5px solid #dc3545;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
        }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .total {{ color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Sprint 2 完整测试报告</h1>
            <p>TestMind AI - 文档解析与AI需求提取系统</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number total">{total_tests}</div>
                <div>测试模块</div>
            </div>
            <div class="stat-card">
                <div class="stat-number success">{passed_tests}</div>
                <div>通过模块</div>
            </div>
            <div class="stat-card">
                <div class="stat-number failure">{failed_tests}</div>
                <div>失败模块</div>
            </div>
            <div class="stat-card">
                <div class="stat-number total">{success_rate:.1f}%</div>
                <div>成功率</div>
            </div>
        </div>
        
        <div class="modules">
            <h2>📋 测试模块详情</h2>
            <div class="modules-grid">
                {modules_html}
            </div>
        </div>
        
        <div class="footer">
            <p>总执行时间: {total_duration:.2f}秒</p>
            <p>© 2025 TestMind AI - Sprint 2 完整测试套件</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _save_comprehensive_logs(self, total_duration):
        """保存综合测试日志"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = self.reports_dir / f"sprint2_complete_test_{timestamp}.log"

            # 收集所有日志信息
            log_content = []
            log_content.append("🏭 TestMind AI - Sprint 2 完整测试日志")
            log_content.append("=" * 70)
            log_content.append(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            log_content.append(f"测试范围: 文档解析 + AI模块 + API接口 + 集成测试")
            log_content.append(f"总执行时间: {total_duration:.2f}秒")
            log_content.append("")

            # 添加各模块测试结果
            log_content.append("📋 测试模块详情:")
            log_content.append("-" * 50)

            module_names = {
                "document_parsing_markdown": "Markdown解析器",
                "document_parsing_pdf": "PDF解析器",
                "document_parsing_word": "Word解析器",
                "ai_langchain": "LangChain提取器",
                "ai_modules": "AI模块专项",
                "api_units": "API接口",
                "integration": "集成测试"
            }

            for module_key, result in self.test_results.items():
                module_name = module_names.get(module_key, module_key)
                status = "✅ 通过" if result["success"] else "❌ 失败"
                log_content.append(f"{module_name}: {status} ({result['duration']:.2f}秒)")

                if not result["success"] and "error" in result:
                    log_content.append(f"  错误: {result['error']}")
                log_content.append("")

            # 添加统计信息
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results.values() if r["success"])
            failed_tests = total_tests - passed_tests

            log_content.append("📊 测试统计:")
            log_content.append("-" * 50)
            log_content.append(f"测试模块: {total_tests}")
            log_content.append(f"通过: {passed_tests}")
            log_content.append(f"失败: {failed_tests}")
            log_content.append(f"成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "成功率: 0%")

            if failed_tests > 0:
                log_content.append("")
                log_content.append("❌ 失败的模块:")
                for module_key, result in self.test_results.items():
                    if not result["success"]:
                        module_name = module_names.get(module_key, module_key)
                        log_content.append(f"  - {module_name}")

            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))

            print(f"  💾 综合测试日志已保存: {log_file.name}")

        except Exception as e:
            print(f"  ❌ 保存综合测试日志失败: {e}")

    def _calculate_overall_success(self):
        """计算总体成功率"""
        if not self.test_results:
            return False

        return all(result["success"] for result in self.test_results.values())
    
    def display_summary(self):
        """显示测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        print("📊 Sprint 2 测试总结")
        print("=" * 70)
        print(f"📈 测试模块: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"🎯 成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "🎯 成功率: 0%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的模块:")
            for module_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {module_name.replace('_', ' ').title()}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 Sprint 2 所有测试模块通过！")
            print(f"✨ 文档解析、AI模块、API接口、集成测试全部成功！")
        else:
            print(f"\n⚠️  {failed_tests} 个模块需要修复")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Sprint 2 完整测试套件")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="不自动打开浏览器"
    )
    parser.add_argument(
        "--no-logs",
        action="store_true",
        help="不保存日志文件"
    )
    parser.add_argument(
        "--view-logs",
        action="store_true",
        help="测试后查看日志文件"
    )

    args = parser.parse_args()

    suite = CompleteSprint2TestSuite()
    success = suite.run_complete_tests(
        open_browser=not args.no_browser,
        save_logs=not args.no_logs
    )
    suite.display_summary()

    # 如果需要查看日志
    if args.view_logs and not args.no_logs:
        log_files = list(suite.reports_dir.glob("sprint2_complete_test_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            print(f"\n📝 查看综合测试日志: {latest_log.name}")
            print("-" * 70)
            with open(latest_log, 'r', encoding='utf-8') as f:
                print(f.read())

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
