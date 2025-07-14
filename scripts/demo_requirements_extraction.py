#!/usr/bin/env python3
"""
TestMind AI - 需求提取演示
展示完整的文档解析 → AI需求提取流程
使用您的Ollama + qwen3:4b配置
"""
import asyncio
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.requirements_parser.parsers.markdown_parser import MarkdownParser
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType

async def demo_complete_workflow():
    """演示完整的需求提取工作流程"""
    print("🚀 TestMind AI - 需求提取演示")
    print("=" * 60)
    print("使用技术栈：")
    print("📄 文档解析：Markdown Parser")
    print("🤖 AI模型：Ollama + qwen3:4b (免费本地)")
    print("🔧 框架：LangChain + FastAPI")
    print("=" * 60)
    
    # 1. 创建示例需求文档
    print("\n📝 步骤1：创建示例需求文档")
    
    sample_markdown = """# 在线教育平台需求规格说明书

## 项目概述
开发一个面向K12教育的在线学习平台，支持直播课程、作业管理和学习进度跟踪。

## 用户故事

### 作为学生，我希望能够观看直播课程
**验收标准：**
- 支持高清视频直播（1080p）
- 延迟小于3秒
- 支持课程回放功能
- 可以在课程中提问和互动
- 支持多设备同步观看

**优先级：** 高

### 作为老师，我希望能够创建和管理课程
**验收标准：**
- 可以创建课程大纲和课程表
- 支持上传课件和教学资源
- 可以布置和批改作业
- 能够查看学生学习进度
- 支持课堂互动工具

**优先级：** 高

### 作为家长，我希望能够监控孩子的学习情况
**验收标准：**
- 可以查看孩子的课程安排
- 能够看到作业完成情况
- 可以查看学习时长统计
- 接收学习进度报告
- 可以与老师沟通

**优先级：** 中

## 功能需求

### 1. 用户管理系统
- 支持学生、老师、家长三种角色注册
- 实名认证功能
- 权限管理和角色切换
- 个人信息管理

### 2. 课程管理系统
- 课程创建和编辑
- 课程分类和搜索
- 课程评价和推荐
- 课程资源管理

### 3. 直播教学系统
- 实时音视频传输
- 屏幕共享功能
- 白板工具
- 课堂互动（举手、投票）
- 课程录制和回放

### 4. 作业管理系统
- 作业发布和收集
- 在线批改工具
- 成绩统计和分析
- 作业提醒功能

### 5. 学习进度跟踪
- 学习时长统计
- 知识点掌握度分析
- 学习报告生成
- 个性化学习建议

## 非功能需求

### 性能要求
- 系统响应时间 < 2秒
- 支持10000并发用户
- 视频加载时间 < 5秒
- 99.9%系统可用性

### 安全要求
- 用户数据加密存储
- 支持HTTPS传输
- 防止视频盗录
- 定期安全审计

### 兼容性要求
- 支持主流浏览器（Chrome、Firefox、Safari、Edge）
- 支持移动端（iOS、Android）
- 支持平板设备
- 向下兼容旧版本浏览器

### 可扩展性要求
- 支持水平扩展
- 模块化架构设计
- 支持第三方集成
- 国际化支持

## 系统约束
- 必须符合教育部相关法规
- 保护未成年人隐私
- 内容审核机制
- 数据本地化存储
"""
    
    print("✅ 示例文档创建完成")
    print(f"📊 文档长度：{len(sample_markdown)} 字符")
    
    # 2. 解析Markdown文档
    print("\n📄 步骤2：解析Markdown文档")
    
    parser = MarkdownParser()
    document = parser.parse(sample_markdown)
    
    print("✅ Markdown解析完成")
    print(f"📋 文档标题：{document.title}")
    print(f"📑 章节数量：{len(document.sections)}")
    print(f"👥 用户故事：{len(document.user_stories)}")
    print(f"🔗 链接数量：{len(document.links)}")
    print(f"📊 表格数量：{len(document.tables)}")
    
    # 3. 使用qwen3:4b提取需求
    print("\n🤖 步骤3：AI需求提取（qwen3:4b）")
    
    extractor = LangChainExtractor(
        provider=AIProvider.OLLAMA,
        model="qwen3:4b",
        ollama_url="http://localhost:11434"
    )
    
    print("🔄 正在分析文档并提取需求...")
    print("⏳ 这可能需要10-30秒，请稍候...")
    
    requirements = await extractor.extract_async(document)
    
    print(f"✅ 需求提取完成！共提取 {len(requirements)} 个需求")
    
    # 4. 分析提取结果
    print("\n📊 步骤4：需求分析结果")
    
    # 按类型分组
    functional_reqs = [r for r in requirements if r.type == "functional"]
    non_functional_reqs = [r for r in requirements if r.type == "non_functional"]
    user_stories = [r for r in requirements if r.type == "user_story"]
    
    print(f"🔧 功能需求：{len(functional_reqs)} 个")
    print(f"⚡ 非功能需求：{len(non_functional_reqs)} 个")
    print(f"👤 用户故事：{len(user_stories)} 个")
    
    # 按优先级分组
    high_priority = [r for r in requirements if r.priority == "high"]
    medium_priority = [r for r in requirements if r.priority == "medium"]
    low_priority = [r for r in requirements if r.priority == "low"]
    
    print(f"🔴 高优先级：{len(high_priority)} 个")
    print(f"🟡 中优先级：{len(medium_priority)} 个")
    print(f"🟢 低优先级：{len(low_priority)} 个")
    
    # 5. 展示详细需求
    print("\n📋 步骤5：详细需求展示")
    
    for i, req in enumerate(requirements[:5], 1):  # 只显示前5个
        print(f"\n{'='*50}")
        print(f"📌 需求 {i}: {req.title}")
        print(f"🆔 ID: {req.id}")
        print(f"📝 类型: {req.type}")
        print(f"⭐ 优先级: {req.priority}")
        print(f"📄 描述: {req.description}")
        if req.acceptance_criteria:
            print(f"✅ 验收标准:")
            for j, criteria in enumerate(req.acceptance_criteria, 1):
                print(f"   {j}. {criteria}")
        else:
            print("✅ 验收标准: 无")
    
    if len(requirements) > 5:
        print(f"\n... 还有 {len(requirements) - 5} 个需求未显示")
    
    # 6. 质量评估
    print("\n🎯 步骤6：提取质量评估")
    
    quality = extractor.validate_extraction_quality(requirements)
    
    print(f"📊 质量分数: {quality['quality_score']:.2f}/1.0")
    print(f"⚠️  发现问题: {len(quality['issues'])} 个")
    print(f"💡 改进建议: {len(quality['recommendations'])} 个")
    
    if quality['issues']:
        print("\n⚠️  质量问题:")
        for issue in quality['issues'][:3]:
            print(f"   • {issue}")
    
    if quality['recommendations']:
        print("\n💡 改进建议:")
        for rec in quality['recommendations'][:3]:
            print(f"   • {rec}")
    
    # 7. 导出结果
    print("\n💾 步骤7：导出结果")
    
    # 创建需求集合
    collection = extractor.create_requirement_collection(requirements)
    
    # 导出为JSON
    output_file = "extracted_requirements.json"
    requirements_data = []

    for req in requirements:
        req_dict = req.model_dump()
        # 处理datetime序列化
        if req_dict.get('created_at'):
            created_at = req_dict['created_at']
            req_dict['created_at'] = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
        if req_dict.get('updated_at'):
            updated_at = req_dict['updated_at']
            req_dict['updated_at'] = updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
        requirements_data.append(req_dict)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(requirements_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ 需求已导出到: {output_file}")
    print(f"📊 统计信息:")
    print(f"   • 总需求数: {collection.total_count}")
    print(f"   • 功能需求: {collection.functional_count}")
    print(f"   • 非功能需求: {collection.non_functional_count}")
    print(f"   • 用户故事: {collection.user_story_count}")
    
    # 8. 总结
    print("\n🎉 演示完成！")
    print("=" * 60)
    print("✅ 成功展示了完整的需求提取流程：")
    print("   1. 📄 Markdown文档解析")
    print("   2. 🤖 AI智能需求提取")
    print("   3. 📊 结构化数据输出")
    print("   4. 🎯 质量评估和验证")
    print("   5. 💾 结果导出和存储")
    print("\n🆓 使用的是完全免费的本地AI方案！")
    print("🚀 您可以开始处理真实的需求文档了！")

async def main():
    """主函数"""
    try:
        await demo_complete_workflow()
        return 0
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("\n🔧 故障排除建议:")
        print("   1. 确保Ollama服务正在运行: ollama serve")
        print("   2. 确保qwen3:4b模型已下载: ollama list")
        print("   3. 检查网络连接和端口11434")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
