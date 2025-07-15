#!/usr/bin/env python3
"""
测试仪表板生成器
创建一个美观的测试结果仪表板，包含图表和详细统计
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDashboard:
    """测试仪表板生成器"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_dashboard(self, test_results: Dict[str, Any]) -> str:
        """生成测试仪表板HTML"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TestMind AI - 测试仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
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
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .total {{ color: #007bff; }}
        
        .charts-section {{
            padding: 30px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .chart-title {{
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.3em;
            color: #2c3e50;
        }}
        
        .details-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .test-list {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .test-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .test-item:last-child {{
            border-bottom: none;
        }}
        
        .test-name {{
            font-weight: 500;
            color: #2c3e50;
        }}
        
        .test-status {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .status-passed {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .status-skipped {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 TestMind AI</h1>
            <p>测试结果仪表板</p>
            <p>生成时间: {timestamp}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number total">{test_results.get('total', 0)}</div>
                <div class="stat-label">总测试数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number passed">{test_results.get('passed', 0)}</div>
                <div class="stat-label">通过</div>
            </div>
            <div class="stat-card">
                <div class="stat-number failed">{test_results.get('failed', 0)}</div>
                <div class="stat-label">失败</div>
            </div>
            <div class="stat-card">
                <div class="stat-number skipped">{test_results.get('skipped', 0)}</div>
                <div class="stat-label">跳过</div>
            </div>
        </div>
        
        <div class="charts-section">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">📊 测试结果分析</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">测试结果分布</div>
                    <canvas id="resultChart" width="400" height="300"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">成功率趋势</div>
                    <canvas id="trendChart" width="400" height="300"></canvas>
                </div>
            </div>
        </div>
        
        <div class="details-section">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">📋 测试详情</h2>
            <div class="test-list">
                {self._generate_test_list(test_results.get('tests', []))}
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 TestMind AI - 自动化测试平台</p>
            <p>执行耗时: {test_results.get('duration', 0):.2f}秒</p>
        </div>
    </div>
    
    <script>
        // 测试结果饼图
        const resultCtx = document.getElementById('resultChart').getContext('2d');
        new Chart(resultCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['通过', '失败', '跳过'],
                datasets: [{{
                    data: [{test_results.get('passed', 0)}, {test_results.get('failed', 0)}, {test_results.get('skipped', 0)}],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 成功率趋势图
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        const successRate = {(test_results.get('passed', 0) / max(test_results.get('total', 1), 1) * 100):.1f};
        new Chart(trendCtx, {{
            type: 'line',
            data: {{
                labels: ['当前测试'],
                datasets: [{{
                    label: '成功率 (%)',
                    data: [successRate],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html_template
    
    def _generate_test_list(self, tests: List[Dict[str, Any]]) -> str:
        """生成测试列表HTML"""
        if not tests:
            return '<div class="test-item"><span class="test-name">暂无测试数据</span></div>'
        
        html_items = []
        for test in tests[:20]:  # 只显示前20个测试
            name = test.get('nodeid', 'Unknown Test').split('::')[-1]
            outcome = test.get('outcome', 'unknown')
            
            status_class = f"status-{outcome}" if outcome in ['passed', 'failed', 'skipped'] else "status-unknown"
            status_text = {'passed': '通过', 'failed': '失败', 'skipped': '跳过'}.get(outcome, outcome)
            
            html_items.append(f'''
                <div class="test-item">
                    <span class="test-name">{name}</span>
                    <span class="test-status {status_class}">{status_text}</span>
                </div>
            ''')
        
        return ''.join(html_items)


def create_sample_dashboard():
    """创建示例仪表板"""
    dashboard = TestDashboard()
    
    # 模拟测试结果数据
    sample_results = {
        'total': 6,
        'passed': 6,
        'failed': 0,
        'skipped': 0,
        'duration': 0.42,
        'tests': [
            {'nodeid': 'test_api_health_check', 'outcome': 'passed'},
            {'nodeid': 'test_supported_formats', 'outcome': 'passed'},
            {'nodeid': 'test_simple_markdown_parsing', 'outcome': 'passed'},
            {'nodeid': 'test_error_handling_unsupported_format', 'outcome': 'passed'},
            {'nodeid': 'test_error_handling_empty_file', 'outcome': 'passed'},
            {'nodeid': 'test_complex_markdown_parsing', 'outcome': 'passed'},
        ]
    }
    
    # 生成仪表板HTML
    html_content = dashboard.generate_dashboard(sample_results)
    
    # 保存到文件
    dashboard_file = dashboard.reports_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📊 测试仪表板已生成: {dashboard_file}")
    return dashboard_file


if __name__ == "__main__":
    dashboard_file = create_sample_dashboard()
    
    # 自动打开浏览器
    import webbrowser
    webbrowser.open(f"file://{dashboard_file.absolute()}")
    print("🌐 正在打开测试仪表板...")
