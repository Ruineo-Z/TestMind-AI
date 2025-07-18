#!/usr/bin/env python3
"""
测试用例覆盖修复验证脚本
验证修复后的AI测试用例生成是否能正确生成正向、负向、边界测试用例
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

async def test_coverage_fix():
    """测试覆盖修复验证"""
    print("🎯 测试用例覆盖修复验证")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 目标: 验证修复后能生成正向、负向、边界测试用例")
    
    try:
        from app.test_case_generator.service import AITestCaseGenerationService
        from app.requirements_parser.models.api_document import APIDocument, APIInfo, APIServer, APIEndpoint
        from app.requirements_parser.models.api_document import HTTPMethod, APIParameter
        
        # 创建测试用的API文档
        api_doc = APIDocument(
            source_format="openapi",
            info=APIInfo(
                title="测试API",
                version="1.0.0",
                description="用于测试覆盖修复的API"
            ),
            servers=[
                APIServer(url="http://localhost:8000", description="测试服务器")
            ],
            endpoints=[
                APIEndpoint(
                    path="/test",
                    method=HTTPMethod.GET,
                    summary="测试端点",
                    description="用于测试的端点",
                    tags=["测试"],
                    parameters=[],
                    responses={}
                ),
                APIEndpoint(
                    path="/items",
                    method=HTTPMethod.POST,
                    summary="创建项目",
                    description="创建新项目",
                    tags=["项目"],
                    parameters=[],
                    responses={}
                )
            ]
        )
        
        # 使用mock provider避免API配额问题
        print("🤖 初始化AI测试生成服务 (mock provider)...")
        service = AITestCaseGenerationService(ai_provider="mock")
        
        # 生成测试套件
        print("🔄 开始生成测试用例...")
        print(f"   - API: {api_doc.info.title} v{api_doc.info.version}")
        print(f"   - 端点数量: {len(api_doc.endpoints)}")
        print(f"   - AI提供商: mock")
        
        start_time = datetime.now()
        
        result = await service.generate_test_suite(
            api_document=api_doc,
            include_positive=True,
            include_negative=True,
            include_boundary=True,
            test_framework="pytest"
        )
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"✅ 测试用例生成完成，耗时: {generation_time:.2f}秒")
        
        # 分析结果
        test_suite = result.get("test_suite")
        test_file_content = result.get("test_file_content", "")
        
        if test_suite:
            print("\n📊 测试套件统计:")
            print(f"   - 总测试数: {test_suite.total_tests}")
            print(f"   - 正向测试: {test_suite.positive_tests}")
            print(f"   - 负向测试: {test_suite.negative_tests}")
            print(f"   - 边界测试: {test_suite.boundary_tests}")
            print(f"   - 测试用例数量: {len(test_suite.test_cases)}")
            
            # 验证覆盖率
            coverage_ok = True
            if test_suite.positive_tests == 0:
                print("❌ 缺少正向测试用例")
                coverage_ok = False
            if test_suite.negative_tests == 0:
                print("❌ 缺少负向测试用例")
                coverage_ok = False
            if test_suite.boundary_tests == 0:
                print("❌ 缺少边界测试用例")
                coverage_ok = False
            
            if coverage_ok:
                print("✅ 测试用例覆盖率验证通过！")
            else:
                print("❌ 测试用例覆盖率验证失败！")
            
            # 显示测试用例详情
            print("\n📋 测试用例详情:")
            for i, tc in enumerate(test_suite.test_cases, 1):
                print(f"   {i}. {tc.name}")
                print(f"      类型: {tc.test_type}")
                print(f"      端点: {tc.http_method} {tc.endpoint_path}")
                print(f"      期望状态: {tc.expected_status_code}")
                print(f"      描述: {tc.description}")
                print()
        
        # 分析生成的代码
        if test_file_content:
            lines = test_file_content.splitlines()
            test_functions = [line for line in lines if line.strip().startswith("async def test_")]
            
            print(f"📝 生成的pytest代码:")
            print(f"   - 代码长度: {len(test_file_content)}字符")
            print(f"   - 代码行数: {len(lines)}行")
            print(f"   - 测试函数: {len(test_functions)}个")
            
            if test_functions:
                print("   测试函数列表:")
                for func in test_functions:
                    func_name = func.strip().split('(')[0].replace('async def ', '')
                    print(f"     - {func_name}")
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(f"coverage_fix_test_{timestamp}")
        output_dir.mkdir(exist_ok=True)
        
        # 保存测试套件
        suite_file = output_dir / "test_suite.json"
        with open(suite_file, 'w', encoding='utf-8') as f:
            json.dump(test_suite.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"✅ 已保存测试套件: {suite_file}")
        
        # 保存测试代码
        if test_file_content:
            code_file = output_dir / "test_code.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(test_file_content)
            print(f"✅ 已保存测试代码: {code_file}")
        
        # 保存完整结果
        result_file = output_dir / "complete_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            # 转换TestSuite对象为字典
            result_copy = result.copy()
            if 'test_suite' in result_copy:
                result_copy['test_suite'] = test_suite.model_dump()
            json.dump(result_copy, f, indent=2, ensure_ascii=False)
        print(f"✅ 已保存完整结果: {result_file}")
        
        print(f"\n📁 所有结果已保存到: {output_dir}")
        
        # 最终验证
        success = (
            test_suite and 
            test_suite.total_tests >= 3 and
            test_suite.positive_tests >= 1 and
            test_suite.negative_tests >= 1 and
            test_suite.boundary_tests >= 1 and
            len(test_suite.test_cases) >= 3
        )
        
        if success:
            print("\n🎉 覆盖修复验证成功！")
            print("✅ 已成功修复测试用例覆盖不全的问题")
            print("✅ 现在能正确生成正向、负向、边界三种类型的测试用例")
            return True
        else:
            print("\n❌ 覆盖修复验证失败！")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_coverage_fix())
    exit(0 if success else 1)
