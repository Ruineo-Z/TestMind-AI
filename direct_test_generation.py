"""
直接测试API文档生成功能
绕过网络问题，直接调用内部API
"""
import asyncio
import json
from pathlib import Path

# 直接导入我们的服务
from app.requirements_parser.service import DocumentParsingService
from app.requirements_parser.models.document import DocumentType


async def test_api_document_generation():
    """直接测试API文档生成功能"""
    print("🚀 开始测试API文档生成功能")
    print("=" * 60)
    
    # 1. 读取OpenAPI文档
    openapi_file = "fastapi_demo_openapi.json"
    if not Path(openapi_file).exists():
        print(f"❌ 文件不存在: {openapi_file}")
        return
    
    print(f"📄 读取API文档: {openapi_file}")
    
    try:
        # 2. 解析文档
        print("🔍 解析API文档...")
        parsing_service = DocumentParsingService(ai_provider="gemini")
        
        result = await parsing_service.parse_document(
            file_path=openapi_file,
            document_type=DocumentType.OPENAPI,
            extract_requirements=False
        )
        
        print("✅ 文档解析成功!")
        print(f"   📋 文档标题: {result['document'].title}")
        print(f"   📊 文档分类: {result['document_category']}")
        
        # 3. 检查API文档数据
        if 'api_document' in result:
            api_doc = result['api_document']
            print(f"   🔗 API标题: {api_doc.info.title}")
            print(f"   🔗 API版本: {api_doc.info.version}")
            print(f"   🔗 端点数量: {len(api_doc.endpoints)}")
            
            print("\n📝 API端点列表:")
            for endpoint in api_doc.endpoints:
                print(f"   - {endpoint.method} {endpoint.path}: {endpoint.summary}")
                print(f"     参数数量: {len(endpoint.parameters)}")
                print(f"     响应数量: {len(endpoint.responses)}")
        
        # 4. 生成测试用例
        print("\n🧪 生成测试用例...")
        test_cases = await generate_test_cases_from_api_doc(result['api_document'])
        
        # 5. 保存测试文件
        print("\n💾 保存测试文件...")
        test_file_content = build_test_file(test_cases, result['api_document'])
        
        output_file = "test_fastapi_demo_generated.py"
        Path(output_file).write_text(test_file_content, encoding='utf-8')
        
        print(f"✅ 测试文件已保存: {output_file}")
        print(f"📏 文件大小: {len(test_file_content)} 字符")
        print(f"📊 测试用例数量: {len(test_cases)}")
        
        # 6. 显示生成的测试用例摘要
        print(f"\n📋 生成的测试用例:")
        for i, test_case in enumerate(test_cases, 1):
            print(f"   {i}. {test_case['name']} ({test_case['type']})")
            print(f"      {test_case['description']}")
        
        print(f"\n🎉 生成完成!")
        print(f"📝 下一步:")
        print(f"   1. 查看生成的测试文件: {output_file}")
        print(f"   2. 安装依赖: pip install pytest requests")
        print(f"   3. 运行测试: pytest {output_file} -v")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def generate_test_cases_from_api_doc(api_doc):
    """从API文档生成测试用例"""
    test_cases = []
    
    for endpoint in api_doc.endpoints:
        # 生成正向测试
        positive_test = generate_positive_test(endpoint)
        test_cases.append(positive_test)
        
        # 生成负向测试
        negative_test = generate_negative_test(endpoint)
        test_cases.append(negative_test)
        
        # 如果有路径参数，生成边界测试
        if endpoint.parameters:
            boundary_test = generate_boundary_test(endpoint)
            test_cases.append(boundary_test)
    
    return test_cases


def generate_positive_test(endpoint):
    """生成正向测试用例"""
    method = endpoint.method.lower()
    path = endpoint.path
    summary = endpoint.summary
    
    # 处理路径参数
    test_path = path
    if '{' in path:
        test_path = path.replace('{item_id}', '1')  # 使用示例值
    
    test_name = f"test_{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}_success"
    test_name = test_name.replace('__', '_').strip('_')
    
    # 根据方法生成不同的测试代码
    if method == 'get':
        code = f'''def {test_name}():
    """测试{summary} - 正向用例"""
    response = requests.get(f"{{BASE_URL}}{test_path}")
    assert response.status_code == 200
    
    # 验证响应格式
    data = response.json()
    assert data is not None
    
    # TODO: 添加更具体的断言
    print(f"✅ {summary} 测试通过")'''
    
    elif method == 'post':
        code = f'''def {test_name}():
    """测试{summary} - 正向用例"""
    test_data = {{
        "name": "测试项目",
        "description": "这是一个测试项目"
    }}
    
    response = requests.post(f"{{BASE_URL}}{test_path}", json=test_data)
    assert response.status_code == 201
    
    # 验证响应数据
    data = response.json()
    assert "id" in data
    assert data["name"] == test_data["name"]
    
    print(f"✅ {summary} 测试通过")'''
    
    elif method == 'delete':
        code = f'''def {test_name}():
    """测试{summary} - 正向用例"""
    # 先创建一个项目用于删除
    create_data = {{"name": "待删除项目", "description": "用于测试删除"}}
    create_response = requests.post(f"{{BASE_URL}}/items", json=create_data)
    assert create_response.status_code == 201
    
    item_id = create_response.json()["id"]
    
    # 删除项目
    response = requests.delete(f"{{BASE_URL}}/items/{{item_id}}")
    assert response.status_code == 200
    
    # 验证删除成功
    data = response.json()
    assert "message" in data
    
    print(f"✅ {summary} 测试通过")'''
    
    else:
        code = f'''def {test_name}():
    """测试{summary} - 正向用例"""
    response = requests.{method}(f"{{BASE_URL}}{test_path}")
    assert response.status_code in [200, 201, 204]
    
    print(f"✅ {summary} 测试通过")'''
    
    return {
        'name': test_name,
        'type': 'positive',
        'description': f"测试{summary} - 正向用例",
        'code': code
    }


def generate_negative_test(endpoint):
    """生成负向测试用例"""
    method = endpoint.method.lower()
    path = endpoint.path
    summary = endpoint.summary
    
    test_name = f"test_{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}_negative"
    test_name = test_name.replace('__', '_').strip('_')
    
    if method == 'post':
        code = f'''def {test_name}():
    """测试{summary} - 负向用例（无效数据）"""
    # 发送无效数据
    invalid_data = {{}}  # 缺少必填字段
    
    response = requests.post(f"{{BASE_URL}}{path}", json=invalid_data)
    assert response.status_code == 422
    
    print(f"✅ {summary} 负向测试通过")'''
    
    elif method == 'delete' and '{' in path:
        code = f'''def {test_name}():
    """测试{summary} - 负向用例（不存在的ID）"""
    # 使用不存在的ID
    non_existent_id = 99999
    
    response = requests.delete(f"{{BASE_URL}}/items/{{non_existent_id}}")
    assert response.status_code == 404
    
    # 验证错误信息
    data = response.json()
    assert "detail" in data
    
    print(f"✅ {summary} 负向测试通过")'''
    
    else:
        code = f'''def {test_name}():
    """测试{summary} - 负向用例"""
    # 测试无效请求
    response = requests.{method}(f"{{BASE_URL}}{path}")
    # 根据实际API行为调整期望的状态码
    assert response.status_code in [400, 404, 422, 500]
    
    print(f"✅ {summary} 负向测试通过")'''
    
    return {
        'name': test_name,
        'type': 'negative',
        'description': f"测试{summary} - 负向用例",
        'code': code
    }


def generate_boundary_test(endpoint):
    """生成边界测试用例"""
    method = endpoint.method.lower()
    path = endpoint.path
    summary = endpoint.summary
    
    test_name = f"test_{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}_boundary"
    test_name = test_name.replace('__', '_').strip('_')
    
    if '{item_id}' in path:
        code = f'''def {test_name}():
    """测试{summary} - 边界用例（边界ID值）"""
    # 测试边界值
    boundary_ids = [0, -1, 1]  # 包含边界值
    
    for test_id in boundary_ids:
        response = requests.{method}(f"{{BASE_URL}}/items/{{test_id}}")
        # 根据ID值验证不同的响应
        if test_id <= 0:
            assert response.status_code in [400, 404, 422]
        else:
            # 正常ID可能存在也可能不存在
            assert response.status_code in [200, 404]
    
    print(f"✅ {summary} 边界测试通过")'''
    
    else:
        code = f'''def {test_name}():
    """测试{summary} - 边界用例"""
    # 测试边界条件
    response = requests.{method}(f"{{BASE_URL}}{path}")
    assert response.status_code in [200, 201, 400, 404]
    
    print(f"✅ {summary} 边界测试通过")'''
    
    return {
        'name': test_name,
        'type': 'boundary',
        'description': f"测试{summary} - 边界用例",
        'code': code
    }


def build_test_file(test_cases, api_doc):
    """构建完整的测试文件"""
    api_title = api_doc.info.title
    api_version = api_doc.info.version
    
    header = f'''"""
{api_title} v{api_version} 自动生成测试用例
基于OpenAPI文档自动生成
生成时间: {Path(__file__).stat().st_mtime}

测试说明:
- 正向测试: 验证API正常功能
- 负向测试: 验证错误处理
- 边界测试: 验证边界条件

使用方法:
1. 确保API服务正在运行
2. 根据实际情况修改BASE_URL
3. 运行测试: pytest {Path(__file__).name} -v
"""
import requests
import pytest


class TestFastAPIDemo:
    """FastAPI演示接口测试类"""
    
    # 配置API基础URL - 请根据实际情况修改
    BASE_URL = "http://localhost:8002"
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 可以在这里添加测试前的准备工作
        pass
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 可以在这里添加测试后的清理工作
        pass

'''
    
    # 添加所有测试方法
    test_methods = []
    for test_case in test_cases:
        # 缩进测试方法
        indented_code = "    " + test_case['code'].replace("\n", "\n    ")
        test_methods.append(indented_code)
    
    footer = '''

if __name__ == "__main__":
    # 直接运行此文件进行测试
    pytest.main([__file__, "-v", "--tb=short"])
'''
    
    return header + "\n".join(test_methods) + footer


async def main():
    """主函数"""
    success = await test_api_document_generation()
    
    if success:
        print("\n🌟 API测试用例生成成功!")
        print("您现在可以:")
        print("1. 查看生成的测试文件")
        print("2. 根据实际API地址修改BASE_URL")
        print("3. 运行测试验证API功能")
    else:
        print("\n😞 生成失败，请检查错误信息")


if __name__ == "__main__":
    asyncio.run(main())
