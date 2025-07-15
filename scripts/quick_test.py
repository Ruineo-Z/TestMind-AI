#!/usr/bin/env python3
"""
快速文档解析功能测试脚本
专门用于快速验证三种文档格式的解析功能
"""
import sys
import time
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import create_app


def test_markdown_parsing():
    """测试Markdown解析"""
    print("📝 测试Markdown解析...")
    
    app = create_app()
    client = TestClient(app)
    
    # 创建测试Markdown内容
    markdown_content = """
# 用户管理系统需求

## 功能需求
1. 用户注册功能
2. 用户登录功能

## 非功能需求
- 性能要求：响应时间 < 2秒
- 安全要求：密码加密存储

## 用户故事
作为一个新用户，我希望能够快速注册账号，以便开始使用系统。
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_content)
        temp_file = f.name
    
    try:
        start_time = time.time()
        
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/v1/requirements/parse",
                files={"file": ("test.md", f, "text/markdown")},
                data={"ai_provider": "mock"}
            )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Markdown解析成功 ({duration:.2f}s)")
            print(f"     文档标题: {data['document']['title']}")
            print(f"     章节数量: {len(data['document']['sections'])}")
            print(f"     提取需求: {len(data['requirements'])}个")
            return True
        else:
            print(f"  ❌ Markdown解析失败: {response.status_code}")
            print(f"     错误信息: {response.text}")
            return False
            
    finally:
        import os
        os.unlink(temp_file)


def test_pdf_parsing():
    """测试PDF解析（模拟）"""
    print("📄 测试PDF解析...")
    
    app = create_app()
    client = TestClient(app)
    
    # 由于无法在测试中创建真实PDF，我们测试PDF解析器的文本处理能力
    from app.requirements_parser.parsers.pdf_parser import PDFParser
    
    try:
        parser = PDFParser()
        
        # 测试文本内容解析
        pdf_text = """
# API设计文档

## 接口需求
1. 用户管理接口
2. 数据查询接口

## 性能要求
- 响应时间 < 1秒
- 支持1000并发
"""
        
        start_time = time.time()
        document = parser._parse_text_content(pdf_text, "test.pdf")
        duration = time.time() - start_time
        
        print(f"  ✅ PDF解析器功能正常 ({duration:.2f}s)")
        print(f"     文档标题: {document.title}")
        print(f"     章节数量: {len(document.sections)}")
        print(f"     内容长度: {len(document.content)}字符")
        return True
        
    except Exception as e:
        print(f"  ❌ PDF解析失败: {e}")
        return False


def test_word_parsing():
    """测试Word解析（模拟）"""
    print("📋 测试Word解析...")
    
    try:
        from app.requirements_parser.parsers.word_parser import WordParser
        
        parser = WordParser()
        
        # 测试段落解析
        paragraphs = [
            "电商系统需求文档",
            "",
            "1. 用户管理模块",
            "用户可以注册、登录和管理个人信息。",
            "",
            "2. 商品管理模块", 
            "管理员可以添加、编辑和删除商品。",
            "",
            "性能要求：",
            "- 页面响应时间 < 3秒",
            "- 支持10000并发用户"
        ]
        
        start_time = time.time()
        document = parser._parse_paragraphs(paragraphs, "test.docx")
        duration = time.time() - start_time
        
        print(f"  ✅ Word解析器功能正常 ({duration:.2f}s)")
        print(f"     文档标题: {document.title}")
        print(f"     章节数量: {len(document.sections)}")
        print(f"     内容长度: {len(document.content)}字符")
        return True
        
    except Exception as e:
        print(f"  ❌ Word解析失败: {e}")
        return False


def test_api_endpoints():
    """测试API端点"""
    print("🔗 测试API端点...")
    
    app = create_app()
    client = TestClient(app)
    
    try:
        # 测试健康检查
        response = client.get("/health")
        if response.status_code != 200:
            print(f"  ❌ 健康检查失败: {response.status_code}")
            return False
        
        # 测试格式支持查询
        response = client.get("/api/v1/requirements/formats")
        if response.status_code != 200:
            print(f"  ❌ 格式查询失败: {response.status_code}")
            return False
        
        data = response.json()
        formats = data["supported_formats"]
        
        if not all(fmt in formats for fmt in ["markdown", "pdf", "word"]):
            print("  ❌ 支持格式不完整")
            return False
        
        print("  ✅ API端点正常")
        print(f"     支持格式: {list(formats.keys())}")
        return True
        
    except Exception as e:
        print(f"  ❌ API测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🏭 TestMind AI - 快速文档解析功能测试")
    print("=" * 50)
    
    start_time = time.time()
    
    # 执行测试
    tests = [
        ("API端点", test_api_endpoints),
        ("Markdown解析", test_markdown_parsing),
        ("PDF解析", test_pdf_parsing),
        ("Word解析", test_word_parsing)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 {test_name}测试异常: {e}")
            results.append((test_name, False))
        print()
    
    # 统计结果
    total_time = time.time() - start_time
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("📊 测试结果汇总")
    print("-" * 30)
    print(f"总耗时: {total_time:.2f}秒")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    print("\n📋 详细结果:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 所有测试通过！文档解析功能正常工作。")
        return 0
    else:
        print(f"\n⚠️  {total-passed}个测试失败，请检查相关功能。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
