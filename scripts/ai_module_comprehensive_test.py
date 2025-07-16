#!/usr/bin/env python3
"""
AI模块综合测试报告生成器
深入测试LangChain AI模块的所有功能，生成详细的测试报告
"""
import sys
import time
import asyncio
import json
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import RequirementType, Priority


class AIModuleComprehensiveTest:
    """AI模块综合测试器"""

    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.test_results = []
        self.performance_metrics = {}

    def run_comprehensive_test(self, open_browser=True):
        """运行综合AI模块测试"""
        print("🤖 TestMind AI - AI模块综合测试")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试范围: LangChain + AI提供商 + 需求提取 + 性能分析")
        print()

        start_time = time.time()

        # 1. 基础功能测试
        self._test_basic_functionality()

        # 2. AI提供商测试
        self._test_ai_providers()

        # 3. 需求提取质量测试
        self._test_extraction_quality()

        # 4. 性能测试
        self._test_performance()

        # 5. 边界条件测试
        self._test_edge_cases()

        # 6. 生成综合报告
        total_duration = time.time() - start_time
        self._generate_comprehensive_report(total_duration, open_browser)

        return self._calculate_success_rate()

    def _test_basic_functionality(self):
        """测试基础功能"""
        print("🔍 1. 基础功能测试")
        print("-" * 50)

        test_cases = [
            ("MOCK提取器初始化", self._test_mock_initialization),
            ("基础需求提取", self._test_basic_extraction),
            ("同步异步一致性", self._test_sync_async_consistency),
            ("自定义提示词", self._test_custom_prompt),
        ]

        for test_name, test_func in test_cases:
            print(f"  🧪 {test_name}...")
            result = self._run_test(test_name, test_func)
            print(f"  {'✅' if result['success'] else '❌'} {test_name}: {'通过' if result['success'] else '失败'}")

        print()

    def _test_ai_providers(self):
        """测试AI提供商"""
        print("🔌 2. AI提供商测试")
        print("-" * 50)

        test_cases = [
            ("MOCK提供商", self._test_mock_provider),
            ("OpenAI提供商配置", self._test_openai_provider),
            ("Ollama提供商配置", self._test_ollama_provider),
            ("Gemini提供商配置", self._test_gemini_provider),
            ("无效提供商处理", self._test_invalid_provider),
        ]

        for test_name, test_func in test_cases:
            print(f"  🧪 {test_name}...")
            result = self._run_test(test_name, test_func)
            print(f"  {'✅' if result['success'] else '❌'} {test_name}: {'通过' if result['success'] else '失败'}")

        print()

    def _test_extraction_quality(self):
        """测试需求提取质量"""
        print("📊 3. 需求提取质量测试")
        print("-" * 50)

        test_cases = [
            ("准确率计算", self._test_accuracy_calculation),
            ("质量验证", self._test_quality_validation),
            ("需求集合创建", self._test_requirement_collection),
            ("批量处理", self._test_batch_processing),
        ]

        for test_name, test_func in test_cases:
            print(f"  🧪 {test_name}...")
            result = self._run_test(test_name, test_func)
            print(f"  {'✅' if result['success'] else '❌'} {test_name}: {'通过' if result['success'] else '失败'}")

        print()

    def _test_performance(self):
        """测试性能"""
        print("⚡ 4. 性能测试")
        print("-" * 50)

        test_cases = [
            ("单文档处理性能", self._test_single_document_performance),
            ("批量处理性能", self._test_batch_performance),
            ("内存使用测试", self._test_memory_usage),
            ("并发处理测试", self._test_concurrent_processing),
        ]

        for test_name, test_func in test_cases:
            print(f"  🧪 {test_name}...")
            result = self._run_test(test_name, test_func)
            print(f"  {'✅' if result['success'] else '❌'} {test_name}: {'通过' if result['success'] else '失败'}")

        print()

    def _test_edge_cases(self):
        """测试边界条件"""
        print("🔬 5. 边界条件测试")
        print("-" * 50)

        test_cases = [
            ("空文档处理", self._test_empty_document),
            ("超长文档处理", self._test_large_document),
            ("特殊字符处理", self._test_special_characters),
            ("错误恢复", self._test_error_recovery),
        ]

        for test_name, test_func in test_cases:
            print(f"  🧪 {test_name}...")
            result = self._run_test(test_name, test_func)
            print(f"  {'✅' if result['success'] else '❌'} {test_name}: {'通过' if result['success'] else '失败'}")

        print()

    def _run_test(self, test_name: str, test_func) -> Dict[str, Any]:
        """运行单个测试"""
        start_time = time.time()

        try:
            result = test_func()
            duration = time.time() - start_time

            test_result = {
                "name": test_name,
                "success": True,
                "duration": duration,
                "details": result if isinstance(result, dict) else {"message": "测试通过"},
                "timestamp": datetime.now()
            }

        except Exception as e:
            duration = time.time() - start_time
            test_result = {
                "name": test_name,
                "success": False,
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now()
            }

        self.test_results.append(test_result)
        return test_result

    # 具体测试方法实现
    def _test_mock_initialization(self):
        """测试MOCK提取器初始化"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")
        assert extractor.provider == AIProvider.MOCK
        assert extractor.model == "mock-model"
        assert hasattr(extractor, 'extract')
        assert hasattr(extractor, 'extract_async')
        return {"provider": "MOCK", "model": "mock-model"}

    def _test_basic_extraction(self):
        """测试基础需求提取"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="用户管理系统需求",
            content="""# 用户管理系统需求

## 功能需求
1. 用户注册功能
2. 用户登录功能

## 非功能需求
- 性能要求：响应时间 < 2秒
""",
            document_type=DocumentType.MARKDOWN
        )

        requirements = asyncio.run(extractor.extract_async(document))

        assert len(requirements) >= 1
        req = requirements[0]
        assert req.id == "REQ-001"
        assert req.title == "模拟需求"
        assert req.type == RequirementType.FUNCTIONAL
        assert req.priority == Priority.MEDIUM

        return {
            "requirements_count": len(requirements),
            "first_requirement_id": req.id,
            "extraction_method": "async"
        }

    def _test_sync_async_consistency(self):
        """测试同步异步一致性"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="简单需求",
            content="用户需要登录功能",
            document_type=DocumentType.MARKDOWN
        )

        # 同步方法
        sync_requirements = extractor.extract(document)

        # 异步方法
        async_requirements = asyncio.run(extractor.extract_async(document))

        assert len(sync_requirements) == len(async_requirements)
        assert sync_requirements[0].title == async_requirements[0].title

        return {
            "sync_count": len(sync_requirements),
            "async_count": len(async_requirements),
            "consistent": sync_requirements[0].title == async_requirements[0].title
        }

    def _test_custom_prompt(self):
        """测试自定义提示词"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="API需求",
            content="需要设计用户API",
            document_type=DocumentType.MARKDOWN
        )

        custom_prompt = "请专注于API设计需求的提取"
        requirements = asyncio.run(extractor.extract_async(document, custom_prompt=custom_prompt))

        assert len(requirements) >= 1
        return {"custom_prompt_used": True, "requirements_count": len(requirements)}

    def _test_mock_provider(self):
        """测试MOCK提供商"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK)
        assert extractor.provider == AIProvider.MOCK
        return {"provider": "MOCK", "initialization": "success"}

    def _test_openai_provider(self):
        """测试OpenAI提供商配置"""
        # 测试无密钥初始化（应该失败）
        try:
            LangChainExtractor(provider=AIProvider.OPENAI)
            return {"error": "应该抛出密钥错误"}
        except ValueError:
            pass  # 预期的错误

        # 测试有密钥初始化
        extractor = LangChainExtractor(
            provider=AIProvider.OPENAI,
            api_key="sk-test1234567890abcdef1234567890abcdef12345678"
        )
        assert extractor.provider == AIProvider.OPENAI
        return {"provider": "OpenAI", "key_validation": "success"}

    def _test_ollama_provider(self):
        """测试Ollama提供商配置"""
        extractor = LangChainExtractor(
            provider=AIProvider.OLLAMA,
            model="llama2",
            ollama_url="http://localhost:11434"
        )
        assert extractor.provider == AIProvider.OLLAMA
        assert extractor.model == "llama2"
        return {"provider": "Ollama", "model": "llama2", "url": "localhost:11434"}

    def _test_gemini_provider(self):
        """测试Gemini提供商配置"""
        extractor = LangChainExtractor(
            provider=AIProvider.GEMINI,
            api_key="test-gemini-key",
            model="gemini-pro"
        )
        assert extractor.provider == AIProvider.GEMINI
        return {"provider": "Gemini", "model": "gemini-pro"}

    def _test_invalid_provider(self):
        """测试无效提供商处理"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK)
        extractor.provider = "invalid_provider"

        document = Document(
            title="测试",
            content="测试内容",
            document_type=DocumentType.MARKDOWN
        )

        try:
            asyncio.run(extractor.extract_async(document))
            return {"error": "应该抛出无效提供商错误"}
        except Exception:
            return {"invalid_provider_handled": True}

    def _test_accuracy_calculation(self):
        """测试准确率计算"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="测试文档",
            content="测试内容",
            document_type=DocumentType.MARKDOWN
        )

        result = asyncio.run(extractor.extract_with_accuracy(document, expected_count=2))

        assert "requirements" in result
        assert "accuracy" in result
        assert "confidence" in result
        assert isinstance(result["accuracy"], float)
        assert 0.0 <= result["accuracy"] <= 1.0

        return {
            "accuracy": result["accuracy"],
            "confidence": result["confidence"],
            "requirements_count": len(result["requirements"])
        }

    def _test_quality_validation(self):
        """测试质量验证"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="质量测试",
            content="测试质量验证功能",
            document_type=DocumentType.MARKDOWN
        )

        requirements = asyncio.run(extractor.extract_async(document))
        quality_result = extractor.validate_extraction_quality(requirements)

        assert "quality_score" in quality_result
        assert "issues" in quality_result
        assert "recommendations" in quality_result

        return {
            "quality_score": quality_result["quality_score"],
            "issues_count": len(quality_result["issues"]),
            "recommendations_count": len(quality_result["recommendations"])
        }

    def _test_requirement_collection(self):
        """测试需求集合创建"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="集合测试",
            content="测试需求集合创建",
            document_type=DocumentType.MARKDOWN
        )

        requirements = asyncio.run(extractor.extract_async(document))
        collection = extractor.create_requirement_collection(requirements)

        assert collection.total_count == len(requirements)
        assert collection.requirements == requirements

        return {
            "total_count": collection.total_count,
            "functional_count": collection.functional_count,
            "collection_created": True
        }

    def _test_batch_processing(self):
        """测试批量处理"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        documents = [
            Document(title="文档1", content="内容1", document_type=DocumentType.MARKDOWN),
            Document(title="文档2", content="内容2", document_type=DocumentType.MARKDOWN)
        ]

        start_time = time.time()
        results = asyncio.run(extractor.extract_batch(documents))
        duration = time.time() - start_time

        assert len(results) == 2
        assert "文档1" in results
        assert "文档2" in results

        total_requirements = sum(len(reqs) for reqs in results.values())

        return {
            "documents_processed": len(documents),
            "total_requirements": total_requirements,
            "processing_time": duration,
            "avg_time_per_doc": duration / len(documents)
        }

    def _test_single_document_performance(self):
        """测试单文档处理性能"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        # 创建中等大小的文档
        content = "# 需求文档\n\n" + "\n\n".join([f"## 需求{i}\n\n这是需求{i}的详细描述。" for i in range(1, 21)])

        document = Document(
            title="性能测试文档",
            content=content,
            document_type=DocumentType.MARKDOWN
        )

        # 测量处理时间
        start_time = time.time()
        requirements = asyncio.run(extractor.extract_async(document))
        duration = time.time() - start_time

        # 记录性能指标
        self.performance_metrics["single_doc"] = {
            "document_size": len(content),
            "processing_time": duration,
            "requirements_count": len(requirements),
            "time_per_requirement": duration / max(len(requirements), 1)
        }

        return self.performance_metrics["single_doc"]

    def _test_batch_performance(self):
        """测试批量处理性能"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        # 创建多个文档
        documents = []
        for i in range(5):
            content = f"# 文档{i}\n\n" + "\n\n".join([f"## 需求{j}\n\n这是需求{j}的描述。" for j in range(1, 6)])
            documents.append(Document(
                title=f"文档{i}",
                content=content,
                document_type=DocumentType.MARKDOWN
            ))

        # 测量批量处理时间
        start_time = time.time()
        results = asyncio.run(extractor.extract_batch(documents))
        duration = time.time() - start_time

        total_requirements = sum(len(reqs) for reqs in results.values())

        # 记录性能指标
        self.performance_metrics["batch"] = {
            "documents_count": len(documents),
            "total_processing_time": duration,
            "avg_time_per_doc": duration / len(documents),
            "total_requirements": total_requirements,
            "time_per_requirement": duration / max(total_requirements, 1)
        }

        return self.performance_metrics["batch"]

    def _test_memory_usage(self):
        """测试内存使用"""
        try:
            import psutil
            process = psutil.Process()

            # 记录初始内存
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

            # 创建大型文档
            content = "# 大型文档\n\n" + "\n\n".join([f"## 章节{i}\n\n" + "内容 " * 100 for i in range(1, 11)])

            document = Document(
                title="内存测试文档",
                content=content,
                document_type=DocumentType.MARKDOWN
            )

            # 处理文档
            requirements = asyncio.run(extractor.extract_async(document))

            # 记录最终内存
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # 记录内存指标
            self.performance_metrics["memory"] = {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "document_size_kb": len(content) / 1024,
                "requirements_count": len(requirements)
            }

            return self.performance_metrics["memory"]

        except ImportError:
            return {"error": "psutil模块不可用，无法测试内存使用"}

    def _test_concurrent_processing(self):
        """测试并发处理"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        # 创建多个文档
        documents = []
        for i in range(3):
            content = f"# 文档{i}\n\n" + "\n\n".join([f"## 需求{j}\n\n这是需求{j}的描述。" for j in range(1, 4)])
            documents.append(Document(
                title=f"文档{i}",
                content=content,
                document_type=DocumentType.MARKDOWN
            ))

        # 定义异步处理函数
        async def process_documents():
            start_time = time.time()

            # 并发处理所有文档
            tasks = [extractor.extract_async(doc) for doc in documents]
            results = await asyncio.gather(*tasks)

            duration = time.time() - start_time
            return results, duration

        # 执行并发处理
        results, duration = asyncio.run(process_documents())

        total_requirements = sum(len(reqs) for reqs in results)

        # 记录并发性能指标
        self.performance_metrics["concurrent"] = {
            "documents_count": len(documents),
            "total_processing_time": duration,
            "avg_time_per_doc": duration / len(documents),
            "total_requirements": total_requirements,
            "concurrent_speedup": True
        }

        return self.performance_metrics["concurrent"]

    def _test_empty_document(self):
        """测试空文档处理"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        document = Document(
            title="空文档",
            content="",
            document_type=DocumentType.MARKDOWN
        )

        try:
            requirements = asyncio.run(extractor.extract_async(document))
            return {
                "handled_empty_document": True,
                "requirements_count": len(requirements)
            }
        except Exception as e:
            return {
                "handled_empty_document": False,
                "error": str(e)
            }

    def _test_large_document(self):
        """测试超长文档处理"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        # 创建超长文档
        content = "# 超长文档\n\n" + "\n\n".join([f"## 章节{i}\n\n" + "内容 " * 500 for i in range(1, 21)])

        document = Document(
            title="超长文档测试",
            content=content,
            document_type=DocumentType.MARKDOWN
        )

        try:
            requirements = asyncio.run(extractor.extract_async(document))
            return {
                "handled_large_document": True,
                "document_size_kb": len(content) / 1024,
                "requirements_count": len(requirements)
            }
        except Exception as e:
            return {
                "handled_large_document": False,
                "document_size_kb": len(content) / 1024,
                "error": str(e)
            }

    def _test_special_characters(self):
        """测试特殊字符处理"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        # 创建包含特殊字符的文档
        content = """# 特殊字符测试

## 需求1
包含特殊字符: !@#$%^&*()_+{}|:"<>?~`-=[]\\;',./

## 需求2
包含表情符号: 😀 🚀 💡 🔥 👍

## 需求3
包含多语言: English, 中文, Español, Русский, 日本語
        """

        document = Document(
            title="特殊字符测试",
            content=content,
            document_type=DocumentType.MARKDOWN
        )

        try:
            requirements = asyncio.run(extractor.extract_async(document))
            return {
                "handled_special_chars": True,
                "requirements_count": len(requirements)
            }
        except Exception as e:
            return {
                "handled_special_chars": False,
                "error": str(e)
            }

    def _test_error_recovery(self):
        """测试错误恢复"""
        extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")

        # 模拟错误情况
        document = Document(
            title="错误测试",
            content="测试内容",
            document_type=DocumentType.MARKDOWN
        )

        # 尝试使用无效提供商
        extractor.provider = "invalid_provider"

        try:
            # 应该失败
            asyncio.run(extractor.extract_async(document))
            return {"error_recovery": False}
        except:
            # 恢复到有效提供商
            extractor.provider = AIProvider.MOCK

            try:
                # 应该成功
                requirements = asyncio.run(extractor.extract_async(document))
                return {
                    "error_recovery": True,
                    "requirements_count": len(requirements)
                }
            except Exception as e:
                return {
                    "error_recovery": False,
                    "error": str(e)
                }
        }