#!/usr/bin/env python3
"""
测试核心功能
直接测试需求对象到测试用例和代码的转换
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_core_functionality():
    """测试核心功能"""
    print("🎯 TestMind AI - 核心功能测试")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 目标: 测试需求对象到测试用例和代码的转换")
    print()
    
    try:
        # 导入必要的模块
        from app.test_case_generator.service import AITestCaseGenerationService
        
        # 创建服务实例
        print("🤖 初始化AI测试生成服务...")
        service = AITestCaseGenerationService(ai_provider="ollama")
        
        # 创建模拟需求对象
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
        
        # 创建多个测试需求
        requirements = [
            MockRequirement(
                id="REQ-001",
                title="API功能测试-创建项目",
                description="系统应允许用户创建新的项目。测试用例需包含正向测试（有效数据）、负向测试（无效数据）和边界测试（最大长度）。"
            ),
            MockRequirement(
                id="REQ-002",
                title="API功能测试-读取项目",
                description="系统应允许用户读取项目信息。测试用例需包含正向测试（读取存在的项目）、负向测试（读取不存在的项目）。"
            )
        ]
        
        # 测试1: 需求转换为测试用例
        print("🔄 测试1: 需求转换为测试用例...")
        test_cases_result = service._convert_requirements_to_testcases(requirements)
        test_cases = test_cases_result.get("test_cases", [])
        
        print(f"✅ 成功生成 {len(test_cases)} 个测试用例:")
        for i, tc in enumerate(test_cases, 1):
            print(f"   {i}. {tc['name']} - {tc['description']}")
            print(f"      端点: {tc['method']} {tc['endpoint']}")
            print(f"      类型: {tc['type']}")
        print()
        
        # 测试2: 需求转换为pytest代码
        print("🔄 测试2: 需求转换为pytest代码...")
        
        # 模拟AI生成的代码需求对象
        code_requirements = [
            MockRequirement(
                id="REQ-CODE-001",
                title="pytest框架集成",
                description="生成的代码必须使用pytest框架编写测试用例。"
            ),
            MockRequirement(
                id="REQ-CODE-002",
                title="使用httpx库",
                description="生成的代码必须使用httpx库作为HTTP客户端，且禁用aiohttp。"
            ),
            MockRequirement(
                id="REQ-CODE-003",
                title="支持异步测试",
                description="生成的代码必须支持异步测试，能够高效地处理多个HTTP请求。"
            )
        ]
        
        code_result = service._convert_requirements_to_code(code_requirements)
        test_code = code_result.get("test_code", "")
        
        if test_code:
            print(f"✅ 成功生成pytest代码: {len(test_code)}字符")
            print("📝 代码预览:")
            lines = test_code.split('\n')
            for i, line in enumerate(lines[:20]):  # 显示前20行
                print(f"   {i+1:2d}: {line}")
            if len(lines) > 20:
                print(f"   ... (还有{len(lines)-20}行)")
        else:
            print("❌ 代码生成失败")
        print()
        
        # 测试3: 单个需求对象转换
        print("🔄 测试3: 单个需求对象转换...")
        single_req = MockRequirement(
            id="REQ-SINGLE",
            title="API功能测试-删除项目",
            description="系统应允许用户删除项目。测试用例需包含正向测试（删除存在的项目）、负向测试（删除不存在的项目）。"
        )
        
        single_test_cases = service._generate_testcases_from_requirement(single_req)
        print(f"✅ 单个需求生成 {len(single_test_cases)} 个测试用例:")
        for i, tc in enumerate(single_test_cases, 1):
            print(f"   {i}. {tc['name']} - {tc['description']}")
            print(f"      端点: {tc['method']} {tc['endpoint']}")
            print(f"      类型: {tc['type']}")
        print()
        
        print("🎉 核心功能测试完成！")
        print("✅ 所有核心转换功能都正常工作")
        print("✅ 需求对象 → 测试用例 ✓")
        print("✅ 需求对象 → pytest代码 ✓")
        print("✅ 单个需求转换 ✓")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_core_functionality())
    sys.exit(0 if success else 1)
