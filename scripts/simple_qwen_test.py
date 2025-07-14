#!/usr/bin/env python3
"""
简单的qwen3:4b需求提取测试
使用简化的文档和提示词
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType

async def test_simple_extraction():
    """测试简单需求提取"""
    print("🧪 简单需求提取测试")
    print("=" * 40)
    
    # 创建简单的测试文档
    simple_doc = Document(
        title="简单需求测试",
        content="""# 用户登录系统

## 功能需求
1. 用户可以通过邮箱和密码登录
2. 支持记住登录状态
3. 登录失败3次后锁定账户

## 非功能需求
1. 登录响应时间小于2秒
2. 支持1000并发用户
""",
        document_type=DocumentType.MARKDOWN
    )
    
    print(f"📄 测试文档: {simple_doc.title}")
    print(f"📝 内容长度: {len(simple_doc.content)} 字符")
    
    # 创建提取器
    extractor = LangChainExtractor(
        provider=AIProvider.OLLAMA,
        model="qwen3:4b"
    )
    
    print("\n🤖 开始AI提取...")
    
    try:
        requirements = await extractor.extract_async(simple_doc)
        
        print(f"✅ 提取成功！共 {len(requirements)} 个需求")
        
        for i, req in enumerate(requirements, 1):
            print(f"\n📋 需求 {i}:")
            print(f"   ID: {req.id}")
            print(f"   标题: {req.title}")
            print(f"   类型: {req.type}")
            print(f"   优先级: {req.priority}")
            print(f"   描述: {req.description}")
            if req.acceptance_criteria:
                print(f"   验收标准: {len(req.acceptance_criteria)} 个")
        
        return len(requirements) > 0
        
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        return False

async def test_user_story_extraction():
    """测试用户故事提取"""
    print("\n🧪 用户故事提取测试")
    print("=" * 40)
    
    # 用户故事文档
    story_doc = Document(
        title="用户故事",
        content="""# 电商系统用户故事

## 作为买家，我希望能够搜索商品
验收标准：
- 支持关键词搜索
- 搜索结果准确
- 搜索速度快

## 作为卖家，我希望能够上传商品
验收标准：
- 支持图片上传
- 商品信息完整
- 审核流程清晰
""",
        document_type=DocumentType.MARKDOWN
    )
    
    extractor = LangChainExtractor(
        provider=AIProvider.OLLAMA,
        model="qwen3:4b"
    )
    
    try:
        requirements = await extractor.extract_async(story_doc)
        
        print(f"✅ 用户故事提取成功！共 {len(requirements)} 个")
        
        user_stories = [r for r in requirements if r.type == "user_story"]
        print(f"👤 用户故事: {len(user_stories)} 个")
        
        return len(user_stories) > 0
        
    except Exception as e:
        print(f"❌ 用户故事提取失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 qwen3:4b 简化测试")
    print("=" * 50)
    
    results = []
    
    # 测试1：简单需求提取
    result1 = await test_simple_extraction()
    results.append(("简单需求提取", result1))
    
    # 测试2：用户故事提取
    result2 = await test_user_story_extraction()
    results.append(("用户故事提取", result2))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:15} : {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 qwen3:4b 工作正常！")
        print("💡 建议：")
        print("   1. 使用简化的文档格式")
        print("   2. 避免过于复杂的需求文档")
        print("   3. 分段处理大型文档")
    else:
        print("\n⚠️  部分测试失败")
        print("💡 建议：")
        print("   1. 检查Ollama服务状态")
        print("   2. 尝试其他模型（如llama2）")
        print("   3. 调整提示词格式")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
