#!/usr/bin/env python3
"""
LangChain多供应商需求提取器演示
展示如何使用OpenAI、Gemini、Ollama三个供应商进行需求提取
"""
import asyncio
import os
from typing import Dict, Any

from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType


def create_sample_document() -> Document:
    """创建示例文档"""
    content = """# 在线学习平台需求文档

## 项目概述
开发一个现代化的在线学习平台，支持多种学习方式和互动功能。

## 功能需求

### 1. 用户管理系统
- 用户注册和登录
- 用户资料管理
- 角色权限管理（学生、教师、管理员）
- 密码重置功能

### 2. 课程管理
- 课程创建和编辑
- 课程分类和标签
- 课程发布和下架
- 课程评价系统

### 3. 学习功能
- 视频播放器
- 在线测验系统
- 学习进度跟踪
- 笔记功能
- 讨论区

### 4. 支付系统
- 课程购买
- 多种支付方式
- 订单管理
- 退款处理

## 非功能性需求

### 性能要求
- 系统响应时间不超过2秒
- 支持1000并发用户
- 视频加载时间不超过5秒

### 安全要求
- 用户数据加密存储
- HTTPS通信
- 防SQL注入
- 定期安全审计

### 可用性要求
- 系统可用性99.9%
- 支持移动端访问
- 多语言支持
"""
    
    return Document(
        title="在线学习平台需求文档",
        content=content,
        document_type=DocumentType.MARKDOWN
    )


async def demo_provider_extraction(provider: AIProvider, document: Document) -> Dict[str, Any]:
    """演示特定供应商的需求提取"""
    print(f"\n{'='*60}")
    print(f"使用 {provider.value.upper()} 供应商进行需求提取")
    print(f"{'='*60}")
    
    try:
        # 根据供应商创建提取器
        if provider == AIProvider.OPENAI:
            # 注意：需要设置 OPENAI_API_KEY 环境变量
            extractor = LangChainExtractor(
                provider=AIProvider.OPENAI,
                model="gpt-3.5-turbo",
                temperature=0.1
            )
        elif provider == AIProvider.GEMINI:
            # 注意：需要设置 GOOGLE_API_KEY 环境变量
            extractor = LangChainExtractor(
                provider=AIProvider.GEMINI,
                model="gemini-1.5-pro",
                temperature=0.1
            )
        elif provider == AIProvider.OLLAMA:
            # Ollama 不需要API密钥，但需要本地运行Ollama服务
            extractor = LangChainExtractor(
                provider=AIProvider.OLLAMA,
                model="qwen2.5:3b",
                ollama_url="http://localhost:11434",
                temperature=0.1
            )
        else:
            raise ValueError(f"不支持的供应商: {provider}")
        
        print(f"✅ 成功初始化 {provider.value} 提取器")
        print(f"   模型: {extractor.model}")
        print(f"   温度: {extractor.temperature}")
        
        # 执行需求提取
        print(f"\n🔄 开始提取需求...")
        result = await extractor.extract_with_accuracy(document, expected_count=10)
        
        # 显示结果
        requirements = result['requirements']
        print(f"✅ 提取完成！")
        print(f"   提取数量: {result['extracted_count']}")
        print(f"   准确率: {result['accuracy']:.2%}")
        print(f"   置信度: {result['confidence']:.2%}")
        
        # 显示前3个需求的详细信息
        print(f"\n📋 需求详情（前3个）:")
        for i, req in enumerate(requirements[:3], 1):
            print(f"\n{i}. {req.title}")
            print(f"   ID: {req.id}")
            print(f"   类型: {req.type}")
            print(f"   优先级: {req.priority}")
            print(f"   描述: {req.description[:100]}...")
            print(f"   验收标准: {len(req.acceptance_criteria)} 项")
            print(f"   提取器: {req.extracted_by}")
        
        # 质量验证
        quality_result = extractor.validate_extraction_quality(requirements)
        print(f"\n📊 质量评估:")
        print(f"   质量分数: {quality_result['quality_score']:.2%}")
        print(f"   发现问题: {len(quality_result['issues'])} 个")
        print(f"   改进建议: {len(quality_result['recommendations'])} 个")
        
        return {
            'provider': provider.value,
            'success': True,
            'requirements_count': len(requirements),
            'accuracy': result['accuracy'],
            'confidence': result['confidence'],
            'quality_score': quality_result['quality_score']
        }
        
    except Exception as e:
        print(f"❌ {provider.value} 提取失败: {e}")
        return {
            'provider': provider.value,
            'success': False,
            'error': str(e)
        }


async def compare_providers():
    """比较不同供应商的提取效果"""
    print("🚀 LangChain多供应商需求提取器演示")
    print("支持的供应商: OpenAI, Google Gemini, Ollama")
    
    # 创建示例文档
    document = create_sample_document()
    print(f"\n📄 文档信息:")
    print(f"   标题: {document.title}")
    print(f"   类型: {document.document_type}")
    print(f"   内容长度: {len(document.content)} 字符")
    
    # 检查环境变量
    print(f"\n🔧 环境检查:")
    openai_key = os.environ.get('OPENAI_API_KEY')
    google_key = os.environ.get('GOOGLE_API_KEY')
    print(f"   OPENAI_API_KEY: {'✅ 已设置' if openai_key else '❌ 未设置'}")
    print(f"   GOOGLE_API_KEY: {'✅ 已设置' if google_key else '❌ 未设置'}")
    print(f"   Ollama服务: 假设在 localhost:11434 运行")
    
    # 测试所有可用的供应商
    results = []
    
    # 测试 Ollama（通常最容易设置）
    print(f"\n🎯 开始测试供应商...")
    ollama_result = await demo_provider_extraction(AIProvider.OLLAMA, document)
    results.append(ollama_result)
    
    # 测试 OpenAI（如果有API密钥）
    if openai_key:
        openai_result = await demo_provider_extraction(AIProvider.OPENAI, document)
        results.append(openai_result)
    else:
        print(f"\n⚠️  跳过 OpenAI 测试（未设置API密钥）")
    
    # 测试 Gemini（如果有API密钥）
    if google_key:
        gemini_result = await demo_provider_extraction(AIProvider.GEMINI, document)
        results.append(gemini_result)
    else:
        print(f"\n⚠️  跳过 Gemini 测试（未设置API密钥）")
    
    # 汇总比较结果
    print(f"\n{'='*60}")
    print("📊 供应商比较结果")
    print(f"{'='*60}")
    
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        print(f"{'供应商':<12} {'需求数量':<8} {'准确率':<8} {'置信度':<8} {'质量分数':<10}")
        print("-" * 60)
        
        for result in successful_results:
            print(f"{result['provider']:<12} "
                  f"{result['requirements_count']:<8} "
                  f"{result['accuracy']:.1%}    "
                  f"{result['confidence']:.1%}    "
                  f"{result['quality_score']:.1%}")
        
        # 找出最佳供应商
        best_provider = max(successful_results, 
                          key=lambda x: (x['accuracy'] + x['confidence'] + x['quality_score']) / 3)
        print(f"\n🏆 推荐供应商: {best_provider['provider'].upper()}")
        print(f"   综合评分最高，适合当前需求提取任务")
    else:
        print("❌ 没有供应商测试成功")
        print("请检查:")
        print("1. Ollama服务是否在运行 (http://localhost:11434)")
        print("2. API密钥是否正确设置")
        print("3. 网络连接是否正常")


async def main():
    """主函数"""
    try:
        await compare_providers()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
    finally:
        print(f"\n✨ 演示结束")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())
