#!/usr/bin/env python3
"""
实时测试监控器
在终端中显示美观的实时测试进度和结果
"""
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import threading
import re

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class LiveTestMonitor:
    """实时测试监控器"""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_completed = 0
        self.tests_total = 0
        self.current_test = ""
        self.results = []
        
    def run_with_monitor(self, test_level: str = "all"):
        """运行带监控的测试"""
        print("🔴 TestMind AI - 实时测试监控")
        print("=" * 60)
        
        # 确定测试文件
        if test_level == "1":
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
            "--no-header",
            "--no-summary"
        ]
        
        print(f"🚀 开始执行测试...")
        print(f"📁 测试文件: {', '.join(test_files)}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        start_time = time.time()
        
        try:
            # 启动pytest进程
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时监控输出
            self._monitor_output(process)
            
            # 等待进程完成
            return_code = process.wait()
            duration = time.time() - start_time
            
            # 显示最终结果
            self._display_final_results(return_code, duration)
            
            return return_code == 0
            
        except Exception as e:
            print(f"💥 测试执行异常: {e}")
            return False
    
    def _monitor_output(self, process):
        """监控pytest输出"""
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
            
            # 解析测试进度
            if "::" in line and ("PASSED" in line or "FAILED" in line or "SKIPPED" in line):
                self._parse_test_result(line)
            elif "collecting" in line.lower():
                print("🔍 正在收集测试...")
            elif "collected" in line and "item" in line:
                # 提取测试总数
                match = re.search(r'collected (\d+) item', line)
                if match:
                    self.tests_total = int(match.group(1))
                    print(f"📊 发现 {self.tests_total} 个测试")
                    print()
    
    def _parse_test_result(self, line):
        """解析单个测试结果"""
        self.tests_completed += 1
        
        # 提取测试名称和结果
        if "PASSED" in line:
            status = "✅ PASSED"
            color = "\033[92m"  # 绿色
        elif "FAILED" in line:
            status = "❌ FAILED"
            color = "\033[91m"  # 红色
        elif "SKIPPED" in line:
            status = "⏭️  SKIPPED"
            color = "\033[93m"  # 黄色
        else:
            status = "❓ UNKNOWN"
            color = "\033[94m"  # 蓝色
        
        # 提取测试名称
        test_name = line.split("::")[1].split()[0] if "::" in line else "Unknown"
        
        # 计算进度
        progress = (self.tests_completed / max(self.tests_total, 1)) * 100
        progress_bar = self._create_progress_bar(progress)
        
        # 显示结果
        reset_color = "\033[0m"
        print(f"{color}{status}{reset_color} {test_name}")
        print(f"📈 进度: {progress_bar} {self.tests_completed}/{self.tests_total} ({progress:.1f}%)")
        print()
        
        # 记录结果
        self.results.append({
            'name': test_name,
            'status': status,
            'timestamp': datetime.now()
        })
    
    def _create_progress_bar(self, percentage, width=30):
        """创建进度条"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _display_final_results(self, return_code, duration):
        """显示最终结果"""
        print("=" * 60)
        print("📊 测试执行完成")
        print("=" * 60)
        
        # 统计结果
        passed = sum(1 for r in self.results if "PASSED" in r['status'])
        failed = sum(1 for r in self.results if "FAILED" in r['status'])
        skipped = sum(1 for r in self.results if "SKIPPED" in r['status'])
        
        # 显示统计
        print(f"⏱️  执行时间: {duration:.2f}秒")
        print(f"📈 总测试数: {len(self.results)}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⏭️  跳过: {skipped}")
        print(f"🎯 成功率: {(passed / max(len(self.results), 1) * 100):.1f}%")
        
        # 显示最终状态
        if return_code == 0:
            print("\n🎉 所有测试通过！")
        else:
            print("\n⚠️  部分测试失败，请检查详细信息。")
        
        # 显示失败的测试
        if failed > 0:
            print("\n❌ 失败的测试:")
            for result in self.results:
                if "FAILED" in result['status']:
                    print(f"  - {result['name']}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="实时测试监控器")
    parser.add_argument(
        "--level",
        choices=["1", "2", "all"],
        default="all",
        help="测试级别"
    )
    
    args = parser.parse_args()
    
    monitor = LiveTestMonitor()
    success = monitor.run_with_monitor(test_level=args.level)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
