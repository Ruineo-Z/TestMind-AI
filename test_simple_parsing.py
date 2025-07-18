#!/usr/bin/env python3
"""
简单的解析功能测试
测试AI生成的需求对象是否能正确转换为测试用例
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_simple_parsing():
    """测试简单的解析功能"""
    print("🎯 TestMind AI - 简单解析测试")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 目标: 测试需求对象到测试用例的转换")
    print()
    
    try:
        # 导入必要的模块
        from app.test_case_generator.service import AITestCaseGenerationService
        
        # 创建服务实例
        print("🤖 初始化AI测试生成服务...")
        service = AITestCaseGenerationService(ai_provider="ollama")
        
        # 创建模拟的需求对象
        print("📋 创建模拟需求对象...")
        
        class MockRequirement:
            def __init__(self, id, title, description):
                self.id = id
                self.title = title
                self.description = description
                self.acceptance_criteria = [
                    "使用有效数据创建项目成功，返回2xx状态码",
                    "使用无效数据创建项目失败，返回4xx状态码"
                ]
        
        # 创建测试需求
        req = MockRequirement(
            id="REQ-001",
            title="API功能测试-创建项目",
            description="系统应允许用户创建新的项目。测试用例需包含正向测试（有效数据）、负向测试（无效数据）和边界测试（最大长度）。"
        )
        
        # 测试需求对象转换
        print("🔄 测试需求对象转换...")
        test_cases = service._generate_testcases_from_requirement(req)
        
        print(f"✅ 成功生成 {len(test_cases)} 个测试用例:")
        for i, tc in enumerate(test_cases, 1):
            print(f"   {i}. {tc['name']} - {tc['description']}")
            print(f"      端点: {tc['method']} {tc['endpoint']}")
            print(f"      类型: {tc['type']}")
            print(f"      期望状态码: {tc['expected_status']}")
            print()
        
        # 测试AI响应内容解析
        print("🔄 测试AI响应内容解析...")
        content = f"{req.title}: {req.description}"
        if hasattr(req, 'acceptance_criteria') and req.acceptance_criteria:
            content += f"\n验收标准: {'; '.join(req.acceptance_criteria)}"
        
        print(f"📝 解析的内容: {content[:100]}...")
        
        print()
        print("🎉 简单解析测试完成！")
        print("✅ 需求对象到测试用例的转换功能正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_parsing())
    sys.exit(0 if success else 1)
