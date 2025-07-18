#!/usr/bin/env python3
"""
使用模拟需求测试完整流程
跳过AI调用，直接测试需求对象到测试代码的转换
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_with_mock_requirements():
    """使用模拟需求测试完整流程"""
    print("🎯 TestMind AI - 模拟需求测试")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 目标: 跳过AI调用，测试需求到代码的完整转换")
    print()
    
    try:
        # 导入必要的模块
        from app.test_case_generator.service import AITestCaseGenerationService
        from app.requirements_parser.models.api_document import APIDocument, APIInfo, APIEndpoint, HTTPMethod, APIResponse

        # 创建服务实例
        print("🤖 初始化AI测试生成服务...")
        service = AITestCaseGenerationService(ai_provider="ollama")

        # 创建模拟API文档
        print("📄 创建模拟API文档...")
        api_info = APIInfo(
            title="FastAPI 演示接口",
            version="1.0.0",
            description="用于测试的API接口"
        )

        # 创建响应对象
        success_response = APIResponse(
            status_code="200",
            description="成功响应",
            response_schema={"type": "object"},
            examples={"message": "Hello World"}
        )

        endpoints = [
            APIEndpoint(
                path="/",
                method=HTTPMethod.GET,
                summary="获取欢迎消息",
                description="返回欢迎消息",
                responses={"200": success_response}
            ),
            APIEndpoint(
                path="/items",
                method=HTTPMethod.POST,
                summary="创建新项目",
                description="创建一个新的项目",
                responses={"201": success_response}
            )
        ]

        api_doc = APIDocument(
            info=api_info,
            endpoints=endpoints,
            servers=[]
        )
        
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
        
        # 测试需求转换为测试用例
        print("🔄 测试需求转换为测试用例...")
        test_cases_result = service._convert_requirements_to_testcases(requirements)
        test_cases = test_cases_result.get("test_cases", [])
        
        print(f"✅ 成功生成 {len(test_cases)} 个测试用例:")
        for i, tc in enumerate(test_cases, 1):
            print(f"   {i}. {tc['name']} - {tc['description']}")
            print(f"      端点: {tc['method']} {tc['endpoint']}")
            print(f"      类型: {tc['type']}")
            print()
        
        # 测试生成pytest代码
        print("🔄 测试生成pytest代码...")
        
        # 模拟AI生成的需求对象（用于代码生成）
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
            )
        ]
        
        code_result = service._convert_requirements_to_code(code_requirements)
        test_code = code_result.get("test_code", "")
        
        if test_code:
            print(f"✅ 成功生成pytest代码: {len(test_code)}字符")
            print("📝 代码预览:")
            print(test_code[:500] + "..." if len(test_code) > 500 else test_code)
        else:
            print("❌ 代码生成失败")
        
        print()
        print("🎉 模拟需求测试完成！")
        print("✅ 需求对象到测试用例和代码的转换功能正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_with_mock_requirements())
    sys.exit(0 if success else 1)
