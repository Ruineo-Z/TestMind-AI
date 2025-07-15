#!/usr/bin/env python3
"""
一键可视化测试运行器
整合HTML报告、仪表板和实时监控的完整解决方案
"""
import sys
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_visual_tests(test_level="all", open_browser=True):
    """运行可视化测试"""
    print("🎨 TestMind AI - 一键可视化测试")
    print("=" * 50)
    print(f"测试级别: {test_level}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建报告目录
    reports_dir = project_root / "test_reports"
    reports_dir.mkdir(exist_ok=True)
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_report = reports_dir / f"visual_test_report_{timestamp}.html"
    
    # 确定测试文件
    if test_level == "1":
        test_files = ["tests/integration/test_production_simple.py::TestLevel1QuickValidation"]
        test_name = "Level 1 快速验证"
    elif test_level == "2":
        test_files = ["tests/integration/test_production_simple.py::TestLevel2ComprehensiveFunctionality"]
        test_name = "Level 2 全面功能"
    else:
        test_files = ["tests/integration/test_production_simple.py"]
        test_name = "完整测试套件"
    
    print(f"📋 执行测试: {test_name}")
    print(f"📁 测试文件: {', '.join(test_files)}")
    print()
    
    # 构建pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        *test_files,
        "-v", "-s",  # -s 显示print输出
        "--tb=long",  # 详细的错误堆栈
        "--capture=no",  # 不捕获输出，显示所有日志
        f"--html={html_report}",
        "--self-contained-html",
        "--log-cli-level=INFO",  # 显示INFO级别的日志
        "--log-cli-format=%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    ]
    
    print("🚀 正在执行测试...")
    
    try:
        # 执行测试
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # 显示结果
        print(f"✅ 测试执行完成")
        print(f"📊 返回码: {result.returncode}")
        
        if result.returncode == 0:
            print("🎉 所有测试通过!")
        else:
            print("⚠️  部分测试失败")
        
        # 解析测试输出获取统计信息
        output_lines = result.stdout.split('\n')
        stats_line = [line for line in output_lines if 'passed' in line and ('failed' in line or 'error' in line or line.endswith('passed'))]
        
        if stats_line:
            print(f"📈 测试统计: {stats_line[-1].strip()}")
        
        # 显示报告位置
        print(f"\n📁 测试报告:")
        print(f"  HTML报告: {html_report}")
        
        if html_report.exists():
            print(f"  文件大小: {html_report.stat().st_size / 1024:.1f} KB")
            
            if open_browser:
                print(f"\n🌐 正在打开测试报告...")
                webbrowser.open(f"file://{html_report.absolute()}")
            else:
                print(f"\n💡 手动打开报告: file://{html_report.absolute()}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ 测试执行超时")
        return False
    except Exception as e:
        print(f"💥 测试执行异常: {e}")
        return False


def show_usage():
    """显示使用说明"""
    print("""
🎨 TestMind AI - 可视化测试使用指南

📋 可用命令:
  python scripts/run_visual_tests.py              # 运行所有测试
  python scripts/run_visual_tests.py --level 1    # 快速验证测试
  python scripts/run_visual_tests.py --level 2    # 全面功能测试
  python scripts/run_visual_tests.py --no-browser # 不自动打开浏览器

🎯 测试级别说明:
  Level 1: 快速验证 (3个测试, < 5秒)
    - API健康检查
    - 支持格式验证  
    - 基础Markdown解析

  Level 2: 全面功能 (3个测试, < 10秒)
    - 错误处理测试
    - 复杂文档解析
    - 边界条件验证

  All: 完整测试 (6个测试, < 15秒)
    - 包含Level 1和Level 2的所有测试

📊 报告特性:
  ✅ 美观的HTML测试报告
  ✅ 详细的测试统计信息
  ✅ 失败测试的错误详情
  ✅ 自动打开浏览器查看
  ✅ 自包含HTML文件，便于分享

💡 使用建议:
  - 开发过程中使用 --level 1 进行快速验证
  - 提交代码前使用 --level 2 进行全面测试
  - 发布前运行完整测试套件
""")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TestMind AI 可视化测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--level",
        choices=["1", "2", "all"],
        default="all",
        help="测试级别 (1=快速验证, 2=全面功能, all=完整测试)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="不自动打开浏览器"
    )
    parser.add_argument(
        "--help-usage",
        action="store_true",
        help="显示详细使用说明"
    )
    
    args = parser.parse_args()
    
    if args.help_usage:
        show_usage()
        return 0
    
    success = run_visual_tests(
        test_level=args.level,
        open_browser=not args.no_browser
    )
    
    if success:
        print("\n🎉 测试执行成功！")
        print("💡 提示: 可以将HTML报告分享给团队成员查看")
        return 0
    else:
        print("\n⚠️  测试执行失败，请查看报告了解详情")
        return 1


if __name__ == "__main__":
    sys.exit(main())
