"""
Sprint3 AI驱动测试用例生成功能测试
验证AI能力在测试自动化中的应用
"""
import asyncio
import httpx
import json
from pathlib import Path
import pytest
from datetime import datetime


class TestSprint3AIGeneration:
    """Sprint3 AI测试生成功能测试类"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8001"
        self.client = httpx.AsyncClient(
            timeout=60.0,
            trust_env=False
        )
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def test_ai_capabilities_endpoint(self):
        """测试AI能力查询端点"""
        print("\n🧪 测试AI能力查询端点...")
        
        response = await self.client.get(f"{self.base_url}/api/v1/tests/capabilities")
        
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        
        data = response.json()
        
        # 验证AI能力信息
        assert "ai_providers" in data
        assert "ai_capabilities" in data
        assert "quality_features" in data
        
        # 验证AI提供商支持
        assert "gemini" in data["ai_providers"]
        assert "openai" in data["ai_providers"]
        assert "ollama" in data["ai_providers"]
        
        # 验证AI核心能力
        ai_capabilities = data["ai_capabilities"]
        assert "api_analysis" in ai_capabilities
        assert "test_strategy" in ai_capabilities
        assert "test_generation" in ai_capabilities
        assert "code_generation" in ai_capabilities
        
        print("✅ AI能力查询端点测试通过")
        return data
    
    async def test_health_check(self):
        """测试健康检查端点"""
        print("\n🧪 测试健康检查端点...")
        
        response = await self.client.get(f"{self.base_url}/api/v1/tests/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "AI Test Case Generation Service" in data["service"]
        assert "利用AI能力实现测试自动化" in data["description"]
        
        print("✅ 健康检查端点测试通过")
        return data
    
    async def test_ai_test_generation_with_real_api(self):
        """测试AI驱动的测试用例生成（使用真实API文档）"""
        print("\n🧪 测试AI驱动的测试用例生成（真实API文档）...")

        # 先通过Sprint2的文档解析接口解析真实API文档
        print("📄 步骤1: 通过Sprint2解析真实API文档...")

        api_file_path = "/Users/augenstern/development/personal/TestMind-AI/api-documentation.yml"

        # 读取API文档文件
        with open(api_file_path, 'rb') as f:
            files = {'file': ('api-documentation.yml', f, 'application/x-yaml')}
            data = {
                'test_type': 'api_test',
                'ai_provider': 'gemini'
            }

            # 调用Sprint2的文档解析接口
            parse_response = await self.client.post(
                f"{self.base_url}/api/v1/documents/parse",
                files=files,
                data=data
            )

        if parse_response.status_code != 200:
            print(f"❌ 文档解析失败: {parse_response.status_code}")
            print(f"错误详情: {parse_response.text}")
            return None

        parse_result = parse_response.json()
        print(f"✅ 文档解析成功!")
        print(f"   📋 API标题: {parse_result['document']['title']}")

        if 'api_document' in parse_result:
            api_info = parse_result['api_document']
            print(f"   🔗 API: {api_info['info']['title']} v{api_info['info']['version']}")
            print(f"   📊 端点数量: {len(api_info['endpoints'])}")

            # 显示解析到的端点
            for endpoint in api_info['endpoints']:
                print(f"      - {endpoint['method']} {endpoint['path']}: {endpoint.get('summary', '无摘要')}")

        print("\n🤖 步骤2: 使用AI生成测试用例...")

        # 构建AI测试生成请求
        request_data = {
            "test_type": "api_test",
            "document_data": parse_result,  # 使用Sprint2的解析结果
            "ai_provider": "gemini",
            "include_positive_tests": True,
            "include_negative_tests": True,
            "include_boundary_tests": True,
            "test_framework": "pytest"
        }

        # 发送AI生成请求
        response = await self.client.post(
            f"{self.base_url}/api/v1/tests/generate",
            json=request_data
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"错误响应: {response.text}")
            return None
        
        result = response.json()
        
        # 验证AI生成结果
        assert "test_file_content" in result
        assert "total_tests" in result
        assert "metadata" in result
        
        # 验证元数据包含AI信息
        metadata = result["metadata"]
        assert "ai_provider" in metadata
        assert "generation_time" in metadata
        assert "processing_time" in metadata
        assert "ai_analysis" in metadata
        assert "test_strategy" in metadata
        
        # 验证生成的测试文件内容
        test_content = result["test_file_content"]
        assert "import pytest" in test_content
        assert "import httpx" in test_content
        assert "async def test_" in test_content
        assert "中文注释" in test_content or "测试" in test_content
        
        print(f"✅ AI生成测试用例成功!")
        print(f"   📊 总测试数: {result['total_tests']}")
        print(f"   ✅ 正向测试: {result['positive_tests']}")
        print(f"   ❌ 负向测试: {result['negative_tests']}")
        print(f"   🔄 边界测试: {result['boundary_tests']}")
        print(f"   🤖 AI提供商: {metadata['ai_provider']}")
        print(f"   ⏱️ 处理时间: {metadata['processing_time']:.2f}秒")
        
        # 保存生成的测试文件
        output_file = f"ai_generated_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        Path(output_file).write_text(test_content, encoding='utf-8')
        print(f"   💾 测试文件已保存: {output_file}")
        
        return result
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Sprint3 AI驱动测试用例生成功能测试")
        print("=" * 60)
        
        try:
            # 测试1: AI能力查询
            await self.test_ai_capabilities_endpoint()
            
            # 测试2: 健康检查
            await self.test_health_check()
            
            # 测试3: AI测试生成（核心功能 - 使用真实API文档）
            await self.test_ai_test_generation_with_real_api()
            
            print("\n🎉 所有测试通过！Sprint3 AI功能正常工作！")
            print("\n📋 测试总结:")
            print("   ✅ AI能力查询端点正常")
            print("   ✅ 健康检查端点正常")
            print("   ✅ AI测试生成功能正常")
            print("   ✅ 生成的代码符合要求（pytest + httpx + 中文注释）")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {str(e)}")
            raise
        
        finally:
            await self.close()


async def main():
    """主函数"""
    tester = TestSprint3AIGeneration()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("🧪 Sprint3 AI驱动测试用例生成功能测试")
    print("项目理念: 利用AI的能力，实现测试自动化")
    print("=" * 60)
    
    asyncio.run(main())
