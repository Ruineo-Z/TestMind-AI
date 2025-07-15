#!/usr/bin/env python3
"""
详细日志测试运行器
提供完整的测试执行日志和可视化报告
"""
import sys
import subprocess
import logging
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from io import StringIO

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DetailedTestRunner:
    """详细日志测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.log_buffer = StringIO()
        
        # 设置日志
        self.setup_logging()
    
    def setup_logging(self):
        """设置详细日志"""
        # 创建日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # 字符串缓冲处理器（用于保存日志）
        buffer_handler = logging.StreamHandler(self.log_buffer)
        buffer_handler.setLevel(logging.DEBUG)
        buffer_handler.setFormatter(formatter)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(buffer_handler)
        
        # 创建测试专用日志器
        self.logger = logging.getLogger('TestRunner')
    
    def run_detailed_tests(self, test_level="all", open_browser=True, save_logs=True):
        """运行带详细日志的测试"""
        self.logger.info("🔍 TestMind AI - 详细日志测试运行器")
        self.logger.info("=" * 60)
        self.logger.info(f"测试级别: {test_level}")
        self.logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"工作目录: {self.project_root}")
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_report = self.reports_dir / f"detailed_test_report_{timestamp}.html"
        log_file = self.reports_dir / f"test_execution_{timestamp}.log"
        
        # 确定测试文件
        test_files, test_name = self._get_test_files(test_level)
        
        self.logger.info(f"📋 执行测试: {test_name}")
        self.logger.info(f"📁 测试文件: {', '.join(test_files)}")
        self.logger.info(f"📊 HTML报告: {html_report.name}")
        self.logger.info(f"📝 日志文件: {log_file.name}")
        
        # 构建pytest命令
        cmd = self._build_pytest_command(test_files, html_report)
        
        self.logger.info("🚀 开始执行测试...")
        self.logger.debug(f"执行命令: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            # 执行测试并实时显示输出
            result = self._run_pytest_with_logging(cmd)
            
            duration = time.time() - start_time
            
            # 记录执行结果
            self._log_execution_results(result, duration)
            
            # 保存日志文件
            if save_logs:
                self._save_log_file(log_file)
            
            # 生成增强的HTML报告
            self._enhance_html_report(html_report, log_file)
            
            # 显示报告信息
            self._display_report_info(html_report, log_file, open_browser)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"💥 测试执行异常: {e}")
            return False
    
    def _get_test_files(self, test_level):
        """获取测试文件列表"""
        if test_level == "1":
            return (
                ["tests/integration/test_production_simple.py::TestLevel1QuickValidation"],
                "Level 1 快速验证测试"
            )
        elif test_level == "2":
            return (
                ["tests/integration/test_production_simple.py::TestLevel2ComprehensiveFunctionality"],
                "Level 2 全面功能测试"
            )
        else:
            return (
                ["tests/integration/test_production_simple.py"],
                "完整测试套件"
            )
    
    def _build_pytest_command(self, test_files, html_report):
        """构建pytest命令"""
        return [
            sys.executable, "-m", "pytest",
            *test_files,
            "-v", "-s",  # 详细输出和显示print
            "--tb=long",  # 详细错误堆栈
            "--capture=no",  # 不捕获输出
            f"--html={html_report}",
            "--self-contained-html",
            "--log-cli-level=DEBUG",  # 显示DEBUG级别日志
            "--log-cli-format=%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            "--log-cli-date-format=%Y-%m-%d %H:%M:%S"
        ]
    
    def _run_pytest_with_logging(self, cmd):
        """运行pytest并记录详细日志"""
        self.logger.info("📋 开始收集测试...")
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时读取和记录输出
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                line = line.rstrip()
                output_lines.append(line)
                
                # 解析并记录不同类型的输出
                self._parse_and_log_line(line)
        
        # 等待进程完成
        return_code = process.wait()
        
        # 创建结果对象
        class Result:
            def __init__(self, returncode, stdout):
                self.returncode = returncode
                self.stdout = stdout
        
        return Result(return_code, '\n'.join(output_lines))
    
    def _parse_and_log_line(self, line):
        """解析并记录pytest输出行"""
        line = line.strip()
        if not line:
            return
        
        # 测试收集阶段
        if "collecting" in line.lower():
            self.logger.info(f"🔍 {line}")
        elif "collected" in line and "item" in line:
            self.logger.info(f"📊 {line}")
        
        # 测试执行阶段
        elif "::" in line and any(status in line for status in ["PASSED", "FAILED", "SKIPPED"]):
            if "PASSED" in line:
                self.logger.info(f"✅ {line}")
            elif "FAILED" in line:
                self.logger.error(f"❌ {line}")
            elif "SKIPPED" in line:
                self.logger.warning(f"⏭️  {line}")
        
        # 错误和异常
        elif "ERROR" in line or "Exception" in line:
            self.logger.error(f"💥 {line}")
        elif "WARNING" in line or "warning" in line:
            self.logger.warning(f"⚠️  {line}")
        
        # 测试统计
        elif "passed" in line and ("failed" in line or "error" in line or line.endswith("passed")):
            self.logger.info(f"📈 {line}")
        
        # 其他重要信息
        elif any(keyword in line.lower() for keyword in ["setup", "teardown", "fixture"]):
            self.logger.debug(f"🔧 {line}")
        else:
            # 一般输出
            self.logger.debug(f"📝 {line}")
    
    def _log_execution_results(self, result, duration):
        """记录执行结果"""
        self.logger.info("=" * 60)
        self.logger.info("📊 测试执行完成")
        self.logger.info("=" * 60)
        self.logger.info(f"⏱️  执行时间: {duration:.2f}秒")
        self.logger.info(f"📊 返回码: {result.returncode}")
        
        if result.returncode == 0:
            self.logger.info("🎉 所有测试通过!")
        else:
            self.logger.warning("⚠️  部分测试失败")
        
        # 解析测试统计
        output_lines = result.stdout.split('\n')
        stats_line = [line for line in output_lines if 'passed' in line and ('failed' in line or 'error' in line or line.endswith('passed'))]
        
        if stats_line:
            self.logger.info(f"📈 测试统计: {stats_line[-1].strip()}")
    
    def _save_log_file(self, log_file):
        """保存日志文件"""
        try:
            log_content = self.log_buffer.getvalue()
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            self.logger.info(f"💾 日志已保存: {log_file}")
        except Exception as e:
            self.logger.error(f"❌ 保存日志失败: {e}")
    
    def _enhance_html_report(self, html_report, log_file):
        """增强HTML报告，添加日志链接"""
        try:
            if not html_report.exists():
                return
            
            with open(html_report, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 添加日志链接
            log_section = f"""
<div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
    <h3>📝 详细执行日志</h3>
    <p>完整的测试执行日志已保存到: <a href="{log_file.name}" target="_blank">{log_file.name}</a></p>
    <p>日志包含详细的测试执行过程、调试信息和错误详情。</p>
</div>
"""
            
            # 插入日志部分
            html_content = html_content.replace('<body>', f'<body>{log_section}')
            
            with open(html_report, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            self.logger.error(f"⚠️ 增强HTML报告失败: {e}")
    
    def _display_report_info(self, html_report, log_file, open_browser):
        """显示报告信息"""
        self.logger.info("📁 生成的文件:")
        self.logger.info(f"  📊 HTML报告: {html_report}")
        self.logger.info(f"  📝 执行日志: {log_file}")
        
        if html_report.exists():
            self.logger.info(f"  📏 HTML大小: {html_report.stat().st_size / 1024:.1f} KB")
        
        if log_file.exists():
            self.logger.info(f"  📏 日志大小: {log_file.stat().st_size / 1024:.1f} KB")
        
        if open_browser and html_report.exists():
            self.logger.info("🌐 正在打开HTML报告...")
            webbrowser.open(f"file://{html_report.absolute()}")
        else:
            self.logger.info(f"💡 手动打开报告: file://{html_report.absolute()}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="详细日志测试运行器")
    parser.add_argument(
        "--level",
        choices=["1", "2", "all"],
        default="all",
        help="测试级别"
    )
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
    
    args = parser.parse_args()
    
    runner = DetailedTestRunner()
    success = runner.run_detailed_tests(
        test_level=args.level,
        open_browser=not args.no_browser,
        save_logs=not args.no_logs
    )
    
    if success:
        print("\n🎉 测试执行成功！")
        print("💡 提示: 查看日志文件了解详细执行过程")
        return 0
    else:
        print("\n⚠️  测试执行失败，请查看日志了解详情")
        return 1


if __name__ == "__main__":
    sys.exit(main())
