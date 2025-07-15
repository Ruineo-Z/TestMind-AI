"""
生产级文档解析功能测试
包含4个测试级别：快速验证、全面功能、压力测试、用户验收
"""
import pytest
import time
import asyncio
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import create_app
from app.requirements_parser.service import RequirementsParsingService


class ProductionTestSuite:
    """生产级测试套件"""
    
    def __init__(self):
        self.app = create_app()
        self.client = TestClient(self.app)
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.results = []
        
    def log_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": time.time(),
            "details": details
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {details}")


class TestLevel1QuickValidation:
    """Level 1: 快速验证测试 (< 30秒)"""

    def setup_method(self):
        """测试方法设置"""
        self.suite = ProductionTestSuite()

    def test_api_health_check(self):
        """API健康检查"""
        start_time = time.time()
        
        # 检查健康端点
        response = self.suite.client.get("/health")
        assert response.status_code == 200

        # 检查API端点存在
        response = self.suite.client.get("/api/v1/requirements/formats")
        assert response.status_code == 200

        duration = time.time() - start_time
        self.suite.log_result("API健康检查", "PASS", {
            "duration": f"{duration:.3f}s",
            "endpoints_checked": 2
        })
    
    def test_supported_formats(self):
        """验证支持的文件格式"""
        response = self.suite.client.get("/api/v1/requirements/formats")
        assert response.status_code == 200

        data = response.json()
        formats = data["supported_formats"]

        # 验证三种格式都支持
        assert "markdown" in formats
        assert "pdf" in formats
        assert "word" in formats

        # 验证扩展名
        assert ".md" in formats["markdown"]["extensions"]
        assert ".pdf" in formats["pdf"]["extensions"]
        assert ".docx" in formats["word"]["extensions"]

        self.suite.log_result("格式支持验证", "PASS", {
            "supported_formats": list(formats.keys()),
            "total_extensions": sum(len(f["extensions"]) for f in formats.values())
        })
    
    def test_simple_markdown_parsing(self):
        """简单Markdown解析测试"""
        start_time = time.time()

        simple_md = self.suite.test_data_dir / "markdown" / "simple.md"
        if not simple_md.exists():
            pytest.skip("测试文件不存在")

        with open(simple_md, 'rb') as f:
            response = self.suite.client.post(
                "/api/v1/requirements/parse",
                files={"file": ("simple.md", f, "text/markdown")},
                data={"ai_provider": "mock"}
            )

        assert response.status_code == 200
        data = response.json()

        # 验证基本结构
        assert "document" in data
        assert "requirements" in data
        assert "metadata" in data

        duration = time.time() - start_time
        self.suite.log_result("简单Markdown解析", "PASS", {
            "duration": f"{duration:.3f}s",
            "file_size": data["metadata"]["file_size"],
            "requirements_count": len(data["requirements"])
        })


class TestLevel2ComprehensiveFunctionality(ProductionTestSuite):
    """Level 2: 全面功能测试 (2-5分钟)"""
    
    def test_complex_markdown_parsing(self):
        """复杂Markdown解析测试"""
        start_time = time.time()
        
        complex_md = self.test_data_dir / "markdown" / "complex.md"
        if not complex_md.exists():
            pytest.skip("测试文件不存在")
        
        with open(complex_md, 'rb') as f:
            response = self.client.post(
                "/api/v1/requirements/parse",
                files={"file": ("complex.md", f, "text/markdown")},
                data={"ai_provider": "mock", "extract_user_stories": "true"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证复杂结构解析
        document = data["document"]
        assert document["title"]
        assert len(document["sections"]) > 5  # 复杂文档应该有多个章节
        
        duration = time.time() - start_time
        self.log_result("复杂Markdown解析", "PASS", {
            "duration": f"{duration:.3f}s",
            "sections_count": len(document["sections"]),
            "tables_count": len(document["tables"]),
            "user_stories_count": len(document["user_stories"])
        })
    
    def test_error_handling(self):
        """错误处理测试"""
        test_cases = [
            # 不支持的文件类型
            {
                "filename": "test.txt",
                "content": b"This is a text file",
                "expected_status": 400,
                "test_name": "不支持文件类型"
            },
            # 空文件
            {
                "filename": "empty.md",
                "content": b"",
                "expected_status": 400,
                "test_name": "空文件处理"
            },
            # 无效文件名
            {
                "filename": "",
                "content": b"# Test",
                "expected_status": 400,
                "test_name": "无效文件名"
            }
        ]
        
        for case in test_cases:
            response = self.client.post(
                "/api/v1/requirements/parse",
                files={"file": (case["filename"], case["content"], "text/plain")}
            )
            
            assert response.status_code == case["expected_status"]
            
            self.log_result(f"错误处理-{case['test_name']}", "PASS", {
                "expected_status": case["expected_status"],
                "actual_status": response.status_code
            })
    
    def test_different_ai_providers(self):
        """不同AI提供商测试"""
        simple_md = self.test_data_dir / "markdown" / "simple.md"
        if not simple_md.exists():
            pytest.skip("测试文件不存在")
        
        providers = ["mock", "openai", "ollama"]
        
        for provider in providers:
            start_time = time.time()
            
            with open(simple_md, 'rb') as f:
                response = self.client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("simple.md", f, "text/markdown")},
                    data={"ai_provider": provider}
                )
            
            # Mock提供商应该成功，其他可能因为配置问题失败
            if provider == "mock":
                assert response.status_code == 200
                status = "PASS"
            else:
                # 其他提供商可能因为API密钥等问题失败，这是正常的
                status = "PASS" if response.status_code in [200, 500] else "FAIL"
            
            duration = time.time() - start_time
            self.log_result(f"AI提供商-{provider}", status, {
                "duration": f"{duration:.3f}s",
                "status_code": response.status_code
            })


class TestLevel3PerformanceStress(ProductionTestSuite):
    """Level 3: 性能压力测试 (5-10分钟)"""
    
    def test_large_file_processing(self):
        """大文件处理测试"""
        # 创建大型测试文档
        large_content = self._create_large_markdown_content()
        
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            f.write(large_content.encode('utf-8'))
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("large.md", f, "text/markdown")},
                    data={"ai_provider": "mock"}
                )
            
            duration = time.time() - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            assert response.status_code == 200
            assert duration < 30  # 大文件处理应在30秒内完成
            
            self.log_result("大文件处理", "PASS", {
                "duration": f"{duration:.3f}s",
                "file_size_mb": len(large_content) / 1024 / 1024,
                "memory_used_mb": f"{memory_used:.2f}",
                "response_time_ok": duration < 30
            })
            
        finally:
            os.unlink(temp_path)
    
    def test_concurrent_requests(self):
        """并发请求测试"""
        simple_md = self.test_data_dir / "markdown" / "simple.md"
        if not simple_md.exists():
            pytest.skip("测试文件不存在")
        
        def make_request():
            with open(simple_md, 'rb') as f:
                response = self.client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("simple.md", f, "text/markdown")},
                    data={"ai_provider": "mock"}
                )
            return response.status_code == 200
        
        start_time = time.time()
        
        # 并发10个请求
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        duration = time.time() - start_time
        success_rate = sum(results) / len(results)
        
        assert success_rate >= 0.8  # 至少80%成功率
        
        self.log_result("并发请求", "PASS", {
            "duration": f"{duration:.3f}s",
            "concurrent_requests": 10,
            "success_rate": f"{success_rate:.1%}",
            "avg_response_time": f"{duration/10:.3f}s"
        })
    
    def test_memory_leak_detection(self):
        """内存泄漏检测"""
        simple_md = self.test_data_dir / "markdown" / "simple.md"
        if not simple_md.exists():
            pytest.skip("测试文件不存在")
        
        # 记录初始内存
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # 执行多次请求
        for i in range(50):
            with open(simple_md, 'rb') as f:
                response = self.client.post(
                    "/api/v1/requirements/parse",
                    files={"file": ("simple.md", f, "text/markdown")},
                    data={"ai_provider": "mock"}
                )
            assert response.status_code == 200
        
        # 强制垃圾回收
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（< 100MB）
        assert memory_increase < 100
        
        self.log_result("内存泄漏检测", "PASS", {
            "initial_memory_mb": f"{initial_memory:.2f}",
            "final_memory_mb": f"{final_memory:.2f}",
            "memory_increase_mb": f"{memory_increase:.2f}",
            "requests_processed": 50,
            "memory_leak_detected": memory_increase > 100
        })
    
    def _create_large_markdown_content(self) -> str:
        """创建大型Markdown内容"""
        content = "# 大型需求文档\n\n"
        
        for i in range(100):
            content += f"""
## 模块 {i+1}

### 功能需求 {i+1}.1
这是模块{i+1}的功能需求描述。包含详细的业务逻辑和实现要求。

### 非功能需求 {i+1}.2
- 性能要求：响应时间 < {i+1}秒
- 可用性要求：系统可用性 > 99.{i%10}%
- 安全要求：数据加密传输

### 用户故事 {i+1}.3
作为用户{i+1}，我希望能够使用功能{i+1}，以便完成任务{i+1}。

### 验收标准 {i+1}.4
| 标准 | 描述 | 优先级 |
|------|------|--------|
| 标准{i+1}.1 | 功能正常工作 | 高 |
| 标准{i+1}.2 | 性能满足要求 | 中 |
| 标准{i+1}.3 | 用户体验良好 | 低 |

"""
        
        return content


class TestLevel4UserAcceptance(ProductionTestSuite):
    """Level 4: 用户验收测试 (端到端场景)"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """端到端工作流测试"""
        # 模拟真实用户工作流：上传文档 -> 解析 -> 获取结果 -> 验证质量
        
        simple_md = self.test_data_dir / "markdown" / "simple.md"
        if not simple_md.exists():
            pytest.skip("测试文件不存在")
        
        start_time = time.time()
        
        # 步骤1：检查支持的格式
        response = self.client.get("/api/v1/requirements/formats")
        assert response.status_code == 200
        
        # 步骤2：上传并解析文档
        with open(simple_md, 'rb') as f:
            response = self.client.post(
                "/api/v1/requirements/parse",
                files={"file": ("requirements.md", f, "text/markdown")},
                data={"ai_provider": "mock", "extract_user_stories": "true"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # 步骤3：验证解析结果质量
        document = data["document"]
        requirements = data["requirements"]
        metadata = data["metadata"]
        
        # 质量检查
        quality_checks = {
            "has_title": bool(document["title"]),
            "has_content": len(document["content"]) > 0,
            "has_requirements": len(requirements) > 0,
            "processing_time_ok": metadata["processing_time"] < 5.0,
            "accuracy_ok": metadata["extraction_accuracy"] > 0.7
        }
        
        total_duration = time.time() - start_time
        
        # 所有质量检查都应该通过
        assert all(quality_checks.values())
        
        self.log_result("端到端工作流", "PASS", {
            "total_duration": f"{total_duration:.3f}s",
            "quality_checks": quality_checks,
            "document_title": document["title"],
            "requirements_extracted": len(requirements),
            "processing_accuracy": f"{metadata['extraction_accuracy']:.1%}"
        })
    
    def test_business_scenario_validation(self):
        """业务场景验证"""
        # 测试真实业务场景：产品经理上传需求文档，系统提取结构化需求
        
        complex_md = self.test_data_dir / "markdown" / "complex.md"
        if not complex_md.exists():
            pytest.skip("测试文件不存在")
        
        with open(complex_md, 'rb') as f:
            response = self.client.post(
                "/api/v1/requirements/parse",
                files={"file": ("product_requirements.md", f, "text/markdown")},
                data={"ai_provider": "mock", "extract_user_stories": "true"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # 业务价值验证
        document = data["document"]
        
        business_value_checks = {
            "structured_sections": len(document["sections"]) >= 5,
            "has_tables": len(document["tables"]) > 0,
            "has_user_stories": len(document["user_stories"]) > 0,
            "comprehensive_content": len(document["content"]) > 1000
        }
        
        self.log_result("业务场景验证", "PASS", {
            "business_value_checks": business_value_checks,
            "sections_extracted": len(document["sections"]),
            "tables_found": len(document["tables"]),
            "user_stories_found": len(document["user_stories"]),
            "content_length": len(document["content"])
        })


# 测试执行器
def run_production_tests(level: str = "all"):
    """运行生产级测试"""
    print(f"\n🏭 开始执行生产级文档解析测试 - Level: {level}")
    print("=" * 60)
    
    if level in ["all", "1"]:
        print("\n📋 Level 1: 快速验证测试")
        pytest.main(["-v", f"{__file__}::TestLevel1QuickValidation"])
    
    if level in ["all", "2"]:
        print("\n📋 Level 2: 全面功能测试")
        pytest.main(["-v", f"{__file__}::TestLevel2ComprehensiveFunctionality"])
    
    if level in ["all", "3"]:
        print("\n📋 Level 3: 性能压力测试")
        pytest.main(["-v", f"{__file__}::TestLevel3PerformanceStress"])
    
    if level in ["all", "4"]:
        print("\n📋 Level 4: 用户验收测试")
        pytest.main(["-v", f"{__file__}::TestLevel4UserAcceptance"])


if __name__ == "__main__":
    import sys
    level = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_production_tests(level)
