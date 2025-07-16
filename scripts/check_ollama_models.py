#!/usr/bin/env python3
"""
检查本地Ollama模型
"""
import httpx
import json
import asyncio


async def check_ollama_models():
    """检查本地Ollama模型"""
    ollama_url = "http://localhost:11434"
    
    try:
        async with httpx.AsyncClient() as client:
            # 检查Ollama服务是否运行
            print("🔍 检查Ollama服务状态...")
            try:
                response = await client.get(f"{ollama_url}/api/version")
                if response.status_code == 200:
                    version_info = response.json()
                    print(f"✅ Ollama服务正在运行")
                    print(f"   版本: {version_info.get('version', 'unknown')}")
                else:
                    print(f"❌ Ollama服务响应异常: {response.status_code}")
                    return
            except Exception as e:
                print(f"❌ 无法连接到Ollama服务: {e}")
                print(f"   请确保Ollama在 {ollama_url} 运行")
                return
            
            # 获取可用模型列表
            print(f"\n📋 获取本地模型列表...")
            try:
                response = await client.get(f"{ollama_url}/api/tags")
                if response.status_code == 200:
                    models_data = response.json()
                    models = models_data.get('models', [])
                    
                    if models:
                        print(f"✅ 找到 {len(models)} 个本地模型:")
                        print("-" * 50)
                        for i, model in enumerate(models, 1):
                            name = model.get('name', 'unknown')
                            size = model.get('size', 0)
                            modified = model.get('modified_at', 'unknown')
                            
                            # 转换大小为可读格式
                            if size > 1024**3:
                                size_str = f"{size / (1024**3):.1f} GB"
                            elif size > 1024**2:
                                size_str = f"{size / (1024**2):.1f} MB"
                            else:
                                size_str = f"{size} bytes"
                            
                            print(f"{i}. {name}")
                            print(f"   大小: {size_str}")
                            print(f"   修改时间: {modified}")
                            print()
                        
                        # 推荐模型
                        print("💡 推荐使用的模型:")
                        for model in models:
                            name = model.get('name', '')
                            if 'qwen' in name.lower():
                                print(f"   - {name} (Qwen系列)")
                            elif 'llama' in name.lower():
                                print(f"   - {name} (Llama系列)")
                            elif 'gemma' in name.lower():
                                print(f"   - {name} (Gemma系列)")
                    else:
                        print("❌ 没有找到本地模型")
                        print("   请使用 'ollama pull <model_name>' 下载模型")
                else:
                    print(f"❌ 获取模型列表失败: {response.status_code}")
            except Exception as e:
                print(f"❌ 获取模型列表时出错: {e}")
                
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")


def update_extractor_config(model_name: str):
    """更新提取器配置文件中的模型名称"""
    print(f"\n🔧 如何使用模型 '{model_name}':")
    print("1. 在代码中使用:")
    print(f"""
from app.requirements_parser.extractors.langchain_extractor_real import LangChainExtractorReal, AIProvider

extractor = LangChainExtractorReal(
    provider=AIProvider.OLLAMA,
    model="{model_name}",
    ollama_url="http://localhost:11434"
)
""")
    
    print("2. 或者修改默认配置:")
    print(f"   在 langchain_extractor_real.py 中将默认模型改为: {model_name}")


async def main():
    """主函数"""
    print("🚀 Ollama模型检查工具")
    print("=" * 50)
    
    await check_ollama_models()
    
    print("\n" + "=" * 50)
    print("📝 使用说明:")
    print("1. 如果没有模型，请使用 'ollama pull <model_name>' 下载")
    print("2. 推荐的轻量级模型:")
    print("   - ollama pull qwen2.5:4b")
    print("   - ollama pull llama3.2:3b")
    print("   - ollama pull gemma2:2b")
    print("3. 找到可用模型后，更新代码中的模型名称")


if __name__ == "__main__":
    asyncio.run(main())
