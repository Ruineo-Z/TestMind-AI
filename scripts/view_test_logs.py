#!/usr/bin/env python3
"""
测试日志查看器
美观地显示测试执行日志
"""
import sys
import re
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestLogViewer:
    """测试日志查看器"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "test_reports"
    
    def view_latest_log(self):
        """查看最新的测试日志"""
        log_files = list(self.reports_dir.glob("test_execution_*.log"))
        
        if not log_files:
            print("❌ 没有找到测试日志文件")
            print("💡 请先运行: uv run python scripts/detailed_test_runner.py")
            return
        
        # 获取最新的日志文件
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        
        print(f"📝 查看测试日志: {latest_log.name}")
        print("=" * 80)
        
        self._display_log_content(latest_log)
    
    def view_specific_log(self, log_file_path):
        """查看指定的日志文件"""
        log_file = Path(log_file_path)
        
        if not log_file.exists():
            print(f"❌ 日志文件不存在: {log_file}")
            return
        
        print(f"📝 查看测试日志: {log_file.name}")
        print("=" * 80)
        
        self._display_log_content(log_file)
    
    def _display_log_content(self, log_file):
        """显示日志内容"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"📊 日志统计:")
            print(f"  📏 总行数: {len(lines)}")
            print(f"  📅 文件大小: {log_file.stat().st_size / 1024:.1f} KB")
            print()
            
            # 分类显示日志
            self._display_categorized_logs(lines)
            
        except Exception as e:
            print(f"❌ 读取日志文件失败: {e}")
    
    def _display_categorized_logs(self, lines):
        """分类显示日志"""
        # 分类日志
        categories = {
            'setup': [],
            'test_execution': [],
            'api_calls': [],
            'results': [],
            'errors': []
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 分类日志行
            if any(keyword in line.lower() for keyword in ['开始', '执行测试', '工作目录']):
                categories['setup'].append(line)
            elif any(keyword in line for keyword in ['🔍 开始', '📡 检查', '📊 响应状态', '✅']):
                categories['test_execution'].append(line)
            elif 'HTTP Request:' in line or 'httpx:' in line:
                categories['api_calls'].append(line)
            elif any(keyword in line for keyword in ['测试执行完成', '通过', '失败', '📈 测试统计']):
                categories['results'].append(line)
            elif any(keyword in line.lower() for keyword in ['error', 'exception', '❌', 'failed']):
                categories['errors'].append(line)
        
        # 显示各类日志
        self._show_category("🚀 测试环境设置", categories['setup'])
        self._show_category("🧪 测试执行过程", categories['test_execution'])
        self._show_category("📡 API调用记录", categories['api_calls'])
        self._show_category("📊 测试结果", categories['results'])
        
        if categories['errors']:
            self._show_category("❌ 错误和异常", categories['errors'])
    
    def _show_category(self, title, logs):
        """显示特定类别的日志"""
        if not logs:
            return
        
        print(f"\n{title}")
        print("-" * 60)
        
        for log in logs:
            # 提取时间戳和消息
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', log)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                message = log[timestamp_match.end():].strip()
                
                # 移除日志级别标记
                message = re.sub(r'\[.*?\].*?:', '', message).strip()
                
                print(f"  {timestamp} {message}")
            else:
                print(f"  {log}")
    
    def list_available_logs(self):
        """列出可用的日志文件"""
        log_files = list(self.reports_dir.glob("test_execution_*.log"))
        
        if not log_files:
            print("❌ 没有找到测试日志文件")
            return
        
        print("📁 可用的测试日志文件:")
        print("-" * 50)
        
        # 按时间排序
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        for i, log_file in enumerate(log_files, 1):
            # 提取时间戳
            timestamp_match = re.search(r'(\d{8}_\d{6})', log_file.name)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = timestamp_str
            else:
                formatted_time = "未知时间"
            
            file_size = log_file.stat().st_size / 1024
            print(f"  {i}. {log_file.name}")
            print(f"     时间: {formatted_time}")
            print(f"     大小: {file_size:.1f} KB")
            print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试日志查看器")
    parser.add_argument(
        "--file",
        help="指定要查看的日志文件路径"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用的日志文件"
    )
    
    args = parser.parse_args()
    
    viewer = TestLogViewer()
    
    if args.list:
        viewer.list_available_logs()
    elif args.file:
        viewer.view_specific_log(args.file)
    else:
        viewer.view_latest_log()


if __name__ == "__main__":
    main()
