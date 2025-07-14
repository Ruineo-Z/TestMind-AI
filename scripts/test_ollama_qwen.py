#!/usr/bin/env python3
"""
测试Ollama + qwen3:4b配置
验证模型是否正常工作
"""
import asyncio
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType

async def test_ollama_connection():
    """测试Ollama连接"""
    print("🔍 测试Ollama连接...")
    
    try:
        import aiohttp
        
        payload = {
            "model": "qwen3:4b",
            "prompt": "你好，请用中文简单介绍一下你自己。",
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:11434/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Ollama连接成功")
                    print(f"📝 qwen3:4b响应: {result.get('response', '无响应')}")
                    return True
                else:
                    print(f"❌ Ollama连接失败: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Ollama连接失败: {e}")
        return False

async def test_requirements_extraction():
    """测试需求提取功能"""
    print("\n🔍 测试需求提取功能...")
    
    try:
        # 创建提取器，使用qwen3:4b模型
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="qwen3:4b",
            ollama_url="http://localhost:11434"
        )
        
        # 创建测试文档
        document = Document(
            title="用户管理系统需求",
            content="""# 用户管理系统需求文档

## 功能需求

### 1. 用户注册功能
- 用户可以通过邮箱注册账户
- 密码必须包含大小写字母和数字，长度至少8位
- 注册成功后发送验证邮件
- 验收标准：注册成功率 > 95%

### 2. 用户登录功能  
- 支持邮箱和密码登录
- 支持记住登录状态（7天）
- 登录失败3次后锁定账户30分钟
- 验收标准：登录响应时间 < 2秒

### 3. 密码重置功能
- 用户可以通过邮箱重置密码
- 重置链接24小时内有效
- 重置后强制重新登录所有设备

## 非功能需求

### 性能要求
- 系统响应时间 < 3秒
- 支持1000并发用户
- 99.9%系统可用性

### 安全要求
- 密码必须加密存储
- 支持HTTPS传输
- 定期安全审计
""",
            document_type=DocumentType.MARKDOWN
        )
        
        print("📄 测试文档创建完成")
        print("🤖 开始AI需求提取...")
        
        # 执行需求提取
        requirements = await extractor.extract_async(document)
        
        print(f"✅ 需求提取成功！提取到 {len(requirements)} 个需求")
        
        # 显示提取结果
        for i, req in enumerate(requirements, 1):
            print(f"\n📋 需求 {i}:")
            print(f"   ID: {req.id}")
            print(f"   标题: {req.title}")
            print(f"   类型: {req.type}")
            print(f"   优先级: {req.priority}")
            print(f"   描述: {req.description[:100]}...")
            print(f"   验收标准数量: {len(req.acceptance_criteria)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 需求提取失败: {e}")
        return False

async def test_extraction_quality():
    """测试提取质量"""
    print("\n🔍 测试提取质量评估...")
    
    try:
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="qwen3:4b"
        )
        
        # 简单测试文档
        document = Document(
            title="简单需求测试",
            content="""# 简单需求

## 功能需求
1. 用户登录
2. 数据查询
3. 报表生成

## 非功能需求
1. 性能要求：响应时间 < 2秒
2. 安全要求：数据加密
""",
            document_type=DocumentType.MARKDOWN
        )
        
        # 提取需求并评估质量
        result = await extractor.extract_with_accuracy(document, expected_count=5)
        
        print(f"✅ 质量评估完成")
        print(f"   提取数量: {result['extracted_count']}")
        print(f"   预期数量: {result['expected_count']}")
        print(f"   准确率: {result['accuracy']:.2%}")
        print(f"   置信度: {result['confidence']:.2%}")
        
        # 详细质量分析
        quality = extractor.validate_extraction_quality(result['requirements'])
        print(f"   质量分数: {quality['quality_score']:.2f}")
        print(f"   发现问题: {len(quality['issues'])} 个")
        print(f"   改进建议: {len(quality['recommendations'])} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 质量评估失败: {e}")
        return False

async def test_chinese_optimization():
    """测试中文优化效果"""
    print("\n🔍 测试中文需求提取...")
    
    try:
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="qwen3:4b"
        )
        
        # 中文需求文档
        document = Document(
            title="电商系统需求",
            content="""# 电商平台需求规格说明书

## 用户故事

### 作为买家，我希望能够浏览商品
**验收标准：**
- 可以按分类浏览商品
- 支持关键词搜索
- 商品信息展示完整
- 页面加载速度 < 3秒

### 作为买家，我希望能够下单购买
**验收标准：**
- 支持多种支付方式
- 订单确认流程清晰
- 支持优惠券使用
- 库存实时更新

### 作为卖家，我希望能够管理商品
**验收标准：**
- 可以添加、编辑、删除商品
- 支持批量操作
- 库存管理功能
- 销售数据统计

## 系统约束
- 支持10万并发用户
- 数据库响应时间 < 100ms
- 99.99%系统可用性
- 符合国家电商法规要求
""",
            document_type=DocumentType.MARKDOWN
        )
        
        requirements = await extractor.extract_async(document)
        
        print(f"✅ 中文需求提取成功！提取到 {len(requirements)} 个需求")
        
        # 检查中文处理质量
        chinese_quality = 0
        for req in requirements:
            if any(char >= '\u4e00' and char <= '\u9fff' for char in req.title):
                chinese_quality += 1
        
        print(f"   中文标题比例: {chinese_quality/len(requirements):.1%}")
        
        # 显示部分结果
        for req in requirements[:3]:
            print(f"\n📋 {req.title}")
            print(f"   类型: {req.type}")
            print(f"   描述: {req.description[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 中文需求提取失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试Ollama + qwen3:4b配置...\n")
    
    # 测试结果
    results = []
    
    # 1. 测试Ollama连接
    ollama_result = await test_ollama_connection()
    results.append(("Ollama连接", ollama_result))
    
    if not ollama_result:
        print("\n❌ Ollama连接失败，请检查：")
        print("   1. Ollama服务是否启动: ollama serve")
        print("   2. qwen3:4b模型是否下载: ollama list")
        print("   3. 端口11434是否可访问")
        return 1
    
    # 2. 测试需求提取
    extraction_result = await test_requirements_extraction()
    results.append(("需求提取", extraction_result))
    
    # 3. 测试质量评估
    quality_result = await test_extraction_quality()
    results.append(("质量评估", quality_result))
    
    # 4. 测试中文优化
    chinese_result = await test_chinese_optimization()
    results.append(("中文优化", chinese_result))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:15} : {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("🎉 所有测试通过！qwen3:4b配置成功！")
        print("\n📋 您现在可以：")
        print("   1. 使用免费的本地AI进行需求提取")
        print("   2. 处理中文需求文档")
        print("   3. 获得高质量的结构化需求输出")
        print("   4. 开始Sprint 3的开发")
        print("\n🚀 建议下一步：")
        print("   python scripts/demo_requirements_extraction.py")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
