"""
简化的API测试用例生成脚本
交互式界面，方便用户使用
"""
import asyncio
import httpx
from pathlib import Path
import json


class SimpleAPITestGenerator:
    """简化的API测试生成器"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8001"
        # 禁用代理，直接连接本地服务
        self.client = httpx.AsyncClient(
            timeout=60.0,
            trust_env=False  # 禁用环境变量中的代理设置
        )
    
    async def close(self):
        await self.client.aclose()
    
    async def check_server(self):
        """检查服务器状态"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/documents/formats")
            return response.status_code == 200
        except:
            return False
    
    async def process_api_file(self, file_path: str):
        """处理API文件的完整流程"""
        print(f"\n🚀 开始处理API文档: {file_path}")
        print("=" * 60)
        
        try:
            # 1. 解析文档
            print("📄 步骤1: 解析API文档...")
            parse_result = await self._parse_document(file_path)
            
            # 2. 生成测试用例
            print("\n🧪 步骤2: 生成测试用例...")
            test_result = await self._generate_tests(parse_result)
            print(test_result)

            # 3. 保存测试文件
            print("\n💾 步骤3: 保存测试文件...")
            output_file = await self._save_test_file(test_result, file_path)
            
            print(f"\n🎉 完成! 测试文件已生成: {output_file}")
            print("\n📝 使用方法:")
            print(f"   1. 安装依赖: pip install pytest requests")
            print(f"   2. 运行测试: pytest {output_file} -v")
            print(f"   3. 查看详细报告: pytest {output_file} --tb=short")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 处理失败: {str(e)}")
            return False
    
    async def _parse_document(self, file_path: str):
        """解析文档"""
        # 检测文件类型
        file_ext = Path(file_path).suffix.lower()
        if file_ext == '.json':
            content_type = 'application/json'
        elif file_ext in ['.yaml', '.yml']:
            content_type = 'application/x-yaml'
        else:
            content_type = 'text/plain'
        
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, content_type)}
            data = {
                'test_type': 'api_test',
                'ai_provider': 'gemini'
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/documents/parse",
                files=files,
                data=data
            )
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get('detail', error_detail)
            except:
                pass
            raise Exception(f"解析失败 ({response.status_code}): {error_detail}")
        
        result = response.json()
        
        # 显示解析结果
        print(f"   ✅ 解析成功!")
        print(f"   📋 文档标题: {result['document']['title']}")
        
        if 'api_document' in result:
            api_info = result['api_document']
            print(f"   🔗 API: {api_info['info']['title']} v{api_info['info']['version']}")
            print(f"   📊 端点数量: {len(api_info['endpoints'])}")
            
            # 显示前几个端点
            endpoints = api_info['endpoints'][:3]
            for endpoint in endpoints:
                print(f"      - {endpoint['method']} {endpoint['path']}")
            if len(api_info['endpoints']) > 3:
                print(f"      ... 还有 {len(api_info['endpoints']) - 3} 个端点")
        
        return result
    
    async def _generate_tests(self, document_data):
        """生成测试用例"""
        request_data = {
            "test_type": "api_test",
            "document_data": document_data,
            "ai_provider": "gemini",
            "include_positive_tests": True,
            "include_negative_tests": True,
            "include_boundary_tests": True,
            "test_framework": "pytest"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/tests/generate",
            json=request_data
        )
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get('detail', error_detail)
            except:
                pass
            raise Exception(f"生成失败 ({response.status_code}): {error_detail}")
        
        result = response.json()
        
        # 显示生成结果
        print(f"   ✅ 生成成功!")
        print(f"   📊 总测试: {result['total_tests']} 个")
        print(f"   ✅ 正向测试: {result['positive_tests']} 个")
        print(f"   ❌ 负向测试: {result['negative_tests']} 个")
        print(f"   🔄 边界测试: {result['boundary_tests']} 个")
        
        return result
    
    async def _save_test_file(self, test_result, original_file_path):
        """保存测试文件"""
        # 生成输出文件名
        original_file = Path(original_file_path)
        output_file = f"test_{original_file.stem}_api.py"
        
        # 保存文件
        test_content = test_result['test_file_content']
        Path(output_file).write_text(test_content, encoding='utf-8')
        
        print(f"   ✅ 已保存到: {output_file}")
        print(f"   📏 文件大小: {len(test_content)} 字符")
        
        return output_file


def show_welcome():
    """显示欢迎信息"""
    print("🎯 API测试用例自动生成工具")
    print("=" * 60)
    print("功能: 上传API文档 → 解析结构 → 生成pytest测试用例")
    print("支持: OpenAPI 3.0, Swagger 2.0 (JSON/YAML格式)")
    print("=" * 60)


def get_api_file():
    """获取API文档文件路径"""
    while True:
        print("\n📁 请提供API文档文件:")
        print("   支持格式: .json, .yaml, .yml")
        print("   示例: openapi.json, swagger.yaml")
        
        file_path = input("\n请输入文件路径 (或输入 'q' 退出): ").strip()
        
        if file_path.lower() == 'q':
            return None
        
        if not file_path:
            print("❌ 请输入文件路径")
            continue
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            continue
        
        if file_path.suffix.lower() not in ['.json', '.yaml', '.yml']:
            print(f"❌ 不支持的文件格式: {file_path.suffix}")
            print("💡 请使用 .json, .yaml 或 .yml 格式")
            continue
        
        return str(file_path)


async def main():
    """主函数"""
    show_welcome()
    
    # 获取API文件
    api_file = get_api_file()
    if not api_file:
        print("👋 再见!")
        return
    
    # 创建生成器
    generator = SimpleAPITestGenerator()
    
    try:
        # 检查服务器
        print("\n🔍 检查服务器连接...")
        if not await generator.check_server():
            print("❌ 无法连接到服务器")
            print("\n💡 请先启动FastAPI服务:")
            print("   cd /Users/augenstern/development/personal/TestMind-AI")
            print("   uvicorn app.main:app --reload")
            print("\n然后重新运行此脚本")
            return
        
        print("✅ 服务器连接正常")
        
        # 处理API文件
        success = await generator.process_api_file(api_file)
        
        if success:
            print("\n🌟 生成完成! 您的API测试用例已准备就绪!")
        else:
            print("\n😞 生成失败，请检查错误信息并重试")
    
    finally:
        await generator.close()


if __name__ == "__main__":
    print("启动API测试生成工具...")
    asyncio.run(main())
