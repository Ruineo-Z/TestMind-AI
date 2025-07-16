#!/usr/bin/env python3
"""
简单的LangChain需求提取器演示
展示如何使用清理后的LangChain多供应商需求提取器
"""
import asyncio
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType


def create_sample_document() -> Document:
    """创建示例文档"""
    content = """# 移动应用需求文档

## 功能需求

### 用户认证
- 用户注册功能
- 用户登录功能
- 忘记密码功能

### 内容管理
- 文章浏览功能
- 文章搜索功能
- 收藏功能

## 非功能性需求

### 性能要求
- 应用启动时间不超过3秒
- 页面加载时间不超过2秒

### 兼容性要求
- 支持iOS 14+
- 支持Android 8+
"""
    
    return Document(
        title="移动应用需求文档",
        content=content,
        document_type=DocumentType.MARKDOWN
    )


async def demo_ollama_extraction():
    """演示使用Ollama进行需求提取"""
    print("🚀 LangChain需求提取器演示")
    print("=" * 50)
    
    # 创建文档
    document = create_sample_document()
    print(f"📄 文档: {document.title}")
    print(f"📝 内容长度: {len(document.content)} 字符")
    
    # 使用Ollama提取器（使用您本地的qwen3:4b模型）
    print(f"\n🔧 初始化LangChain提取器...")
    extractor = LangChainExtractor(
        provider=AIProvider.OLLAMA,
        model="qwen3:4b",
        temperature=0.1
    )
    
    print(f"✅ 提取器配置:")
    print(f"   供应商: {extractor.provider.value}")
    print(f"   模型: {extractor.model}")
    print(f"   温度: {extractor.temperature}")
    
    try:
        # 执行需求提取
        print(f"\n🔄 开始提取需求...")
        requirements = await extractor.extract_async(document)
        
        # 显示结果
        print(f"✅ 提取完成！")
        print(f"📊 提取到 {len(requirements)} 个需求")
        
        # 显示需求详情
        print(f"\n📋 需求列表:")
        for i, req in enumerate(requirements[:5], 1):  # 只显示前5个
            print(f"\n{i}. {req.title}")
            print(f"   ID: {req.id}")
            print(f"   类型: {req.type}")
            print(f"   优先级: {req.priority}")
            print(f"   描述: {req.description[:80]}...")
            print(f"   验收标准: {len(req.acceptance_criteria)} 项")
        
        if len(requirements) > 5:
            print(f"\n... 还有 {len(requirements) - 5} 个需求")
        
        # 统计信息
        functional_count = sum(1 for req in requirements if req.type == "functional")
        non_functional_count = sum(1 for req in requirements if req.type == "non_functional")
        
        print(f"\n📈 统计信息:")
        print(f"   功能性需求: {functional_count} 个")
        print(f"   非功能性需求: {non_functional_count} 个")
        print(f"   总计: {len(requirements)} 个")
        
        return requirements
        
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        print(f"💡 请确保:")
        print(f"   1. Ollama服务正在运行 (http://localhost:11434)")
        print(f"   2. qwen3:4b模型已安装")
        print(f"   3. 网络连接正常")
        return []


def demo_provider_switching():
    """演示供应商切换功能"""
    print(f"\n🔄 供应商切换演示")
    print("=" * 30)
    
    # 演示不同供应商的初始化
    providers_config = [
        {
            "name": "Ollama (本地)",
            "provider": AIProvider.OLLAMA,
            "model": "qwen3:4b",
            "available": True
        },
        {
            "name": "OpenAI",
            "provider": AIProvider.OPENAI,
            "model": "gpt-3.5-turbo",
            "available": False  # 需要API密钥
        },
        {
            "name": "Google Gemini",
            "provider": AIProvider.GEMINI,
            "model": "gemini-1.5-pro",
            "available": False  # 需要API密钥
        }
    ]
    
    for config in providers_config:
        print(f"\n📱 {config['name']}:")
        print(f"   供应商: {config['provider'].value}")
        print(f"   推荐模型: {config['model']}")
        print(f"   状态: {'✅ 可用' if config['available'] else '❌ 需要API密钥'}")
        
        if config['available']:
            try:
                extractor = LangChainExtractor(
                    provider=config['provider'],
                    model=config['model']
                )
                print(f"   初始化: ✅ 成功")
            except Exception as e:
                print(f"   初始化: ❌ 失败 - {e}")


async def main():
    """主函数"""
    try:
        # 演示需求提取
        requirements = await demo_ollama_extraction()
        
        # 演示供应商切换
        demo_provider_switching()
        
        print(f"\n✨ 演示完成！")
        
        if requirements:
            print(f"\n💡 下一步建议:")
            print(f"   1. 尝试不同的模型参数（温度、模型名称）")
            print(f"   2. 测试不同类型的文档")
            print(f"   3. 配置OpenAI或Gemini API密钥体验云端模型")
            print(f"   4. 使用批量处理功能处理多个文档")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())
