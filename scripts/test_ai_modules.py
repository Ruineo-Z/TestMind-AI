#!/usr/bin/env python3
"""
AI模块专项测试脚本
专门测试LangChain AI模块的功能
"""
import sys
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import RequirementType, Priority

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class AIModuleTester:
    """AI模块测试器"""

    def __init__(self):
        self.project_root = project_root
        self.test_results = []
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)

    def run_ai_tests(self, test_level="all", save_logs=True):
        """运行AI模块测试"""
        logger.info("🤖 TestMind AI - AI模块专项测试")
        logger.info("=" * 60)
        logger.info(f"测试级别: {test_level}")
        logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"工作目录: {self.project_root}")

        start_time = time.time()

        # 执行不同级别的测试
        if test_level == "basic":
            self._run_basic_tests()
        elif test_level == "providers":
            self._run_provider_tests()
        elif test_level == "advanced":
            self._run_advanced_tests()
        else:
            self._run_all_tests()

        duration = time.time() - start_time

        # 保存详细日志
        if save_logs:
            self._save_test_logs(test_level, duration)

        self._display_results(duration)

        return all(result["success"] for result in self.test_results)
    
    def _run_basic_tests(self):
        """运行基础AI测试"""
        logger.info("\n🧪 基础AI功能测试")
        logger.info("-" * 40)
        
        # 测试1: MOCK提供商初始化
        self._test_mock_provider_initialization()
        
        # 测试2: 基础需求提取
        self._test_basic_requirement_extraction()
        
        # 测试3: 同步和异步方法
        self._test_sync_async_methods()
    
    def _run_provider_tests(self):
        """运行AI提供商测试"""
        logger.info("\n🔌 AI提供商测试")
        logger.info("-" * 40)
        
        # 测试不同AI提供商的初始化
        self._test_all_providers_initialization()
        
        # 测试提供商配置验证
        self._test_provider_configuration()
    
    def _run_advanced_tests(self):
        """运行高级AI测试"""
        logger.info("\n🚀 高级AI功能测试")
        logger.info("-" * 40)
        
        # 测试准确率计算
        self._test_accuracy_calculation()
        
        # 测试批量处理
        self._test_batch_processing()
        
        # 测试需求集合创建
        self._test_requirement_collection()
    
    def _run_all_tests(self):
        """运行所有AI测试"""
        self._run_basic_tests()
        self._run_provider_tests()
        self._run_advanced_tests()
    
    def _test_mock_provider_initialization(self):
        """测试MOCK提供商初始化"""
        test_name = "MOCK提供商初始化"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")
            
            assert extractor.provider == AIProvider.MOCK
            assert extractor.model == "mock-model"
            assert hasattr(extractor, 'extract')
            assert hasattr(extractor, 'extract_async')
            
            self._record_success(test_name, "MOCK提供商初始化成功")
            logger.info("✅ MOCK提供商初始化测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ MOCK提供商初始化测试失败: {e}")
    
    def _test_basic_requirement_extraction(self):
        """测试基础需求提取"""
        test_name = "基础需求提取"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")
            
            document = Document(
                title="用户管理系统需求",
                content="""# 用户管理系统需求
                
## 功能需求

### 1. 用户注册
- 用户可以通过邮箱注册
- 密码必须包含大小写字母和数字

### 2. 用户登录
- 支持邮箱登录
- 支持记住登录状态
""",
                document_type=DocumentType.MARKDOWN
            )
            
            # 异步提取测试
            requirements = asyncio.run(extractor.extract_async(document))
            
            assert len(requirements) >= 1
            req = requirements[0]
            assert req.id == "REQ-001"
            assert req.title == "模拟需求"
            assert req.type == RequirementType.FUNCTIONAL
            assert req.priority == Priority.MEDIUM
            assert len(req.acceptance_criteria) >= 1
            assert req.source_document == document.title
            
            self._record_success(test_name, f"成功提取 {len(requirements)} 个需求")
            logger.info(f"✅ 基础需求提取测试通过 - 提取了 {len(requirements)} 个需求")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 基础需求提取测试失败: {e}")
    
    def _test_sync_async_methods(self):
        """测试同步和异步方法"""
        test_name = "同步异步方法"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")
            
            document = Document(
                title="简单需求",
                content="用户需要登录功能",
                document_type=DocumentType.MARKDOWN
            )
            
            # 测试同步方法
            sync_requirements = extractor.extract(document)
            
            # 测试异步方法
            async_requirements = asyncio.run(extractor.extract_async(document))
            
            assert len(sync_requirements) >= 1
            assert len(async_requirements) >= 1
            assert sync_requirements[0].title == async_requirements[0].title
            
            self._record_success(test_name, "同步和异步方法都正常工作")
            logger.info("✅ 同步异步方法测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 同步异步方法测试失败: {e}")
    
    def _test_all_providers_initialization(self):
        """测试所有AI提供商初始化"""
        test_name = "AI提供商初始化"
        logger.info(f"🔍 测试: {test_name}")
        
        providers_tested = 0
        providers_passed = 0
        
        try:
            # 测试MOCK提供商
            mock_extractor = LangChainExtractor(provider=AIProvider.MOCK)
            assert mock_extractor.provider == AIProvider.MOCK
            providers_tested += 1
            providers_passed += 1
            logger.info("  ✅ MOCK提供商初始化成功")
            
            # 测试Ollama提供商
            ollama_extractor = LangChainExtractor(
                provider=AIProvider.OLLAMA,
                model="llama2",
                ollama_url="http://localhost:11434"
            )
            assert ollama_extractor.provider == AIProvider.OLLAMA
            assert ollama_extractor.model == "llama2"
            providers_tested += 1
            providers_passed += 1
            logger.info("  ✅ Ollama提供商初始化成功")
            
            # 测试OpenAI提供商（无密钥应该失败）
            try:
                LangChainExtractor(provider=AIProvider.OPENAI)
                logger.warning("  ⚠️  OpenAI提供商无密钥初始化应该失败")
            except ValueError:
                providers_tested += 1
                providers_passed += 1
                logger.info("  ✅ OpenAI提供商正确验证密钥")
            
            # 测试OpenAI提供商（有密钥）
            openai_extractor = LangChainExtractor(
                provider=AIProvider.OPENAI,
                api_key="sk-test1234567890abcdef1234567890abcdef12345678"
            )
            assert openai_extractor.provider == AIProvider.OPENAI
            providers_tested += 1
            providers_passed += 1
            logger.info("  ✅ OpenAI提供商有密钥初始化成功")
            
            self._record_success(test_name, f"{providers_passed}/{providers_tested} 提供商测试通过")
            logger.info(f"✅ AI提供商初始化测试通过 - {providers_passed}/{providers_tested}")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ AI提供商初始化测试失败: {e}")
    
    def _test_provider_configuration(self):
        """测试提供商配置验证"""
        test_name = "提供商配置验证"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            # 测试无效提供商错误
            extractor = LangChainExtractor(provider=AIProvider.MOCK)
            extractor.provider = "invalid_provider"
            
            document = Document(
                title="测试",
                content="测试内容",
                document_type=DocumentType.MARKDOWN
            )
            
            try:
                asyncio.run(extractor.extract_async(document))
                self._record_failure(test_name, "无效提供商应该抛出异常")
            except Exception:
                self._record_success(test_name, "正确处理无效提供商")
                logger.info("✅ 提供商配置验证测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 提供商配置验证测试失败: {e}")
    
    def _test_accuracy_calculation(self):
        """测试准确率计算"""
        test_name = "准确率计算"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
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
            
            self._record_success(test_name, f"准确率: {result['accuracy']:.2%}")
            logger.info(f"✅ 准确率计算测试通过 - 准确率: {result['accuracy']:.2%}")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 准确率计算测试失败: {e}")
    
    def _test_batch_processing(self):
        """测试批量处理"""
        test_name = "批量处理"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")
            
            documents = [
                Document(title="文档1", content="内容1", document_type=DocumentType.MARKDOWN),
                Document(title="文档2", content="内容2", document_type=DocumentType.MARKDOWN)
            ]
            
            results = asyncio.run(extractor.extract_batch(documents))
            
            assert len(results) == 2
            assert "文档1" in results
            assert "文档2" in results
            assert len(results["文档1"]) >= 1
            assert len(results["文档2"]) >= 1
            
            total_requirements = sum(len(reqs) for reqs in results.values())
            self._record_success(test_name, f"批量处理 {len(documents)} 个文档，提取 {total_requirements} 个需求")
            logger.info(f"✅ 批量处理测试通过 - 处理了 {len(documents)} 个文档")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 批量处理测试失败: {e}")
    
    def _test_requirement_collection(self):
        """测试需求集合创建"""
        test_name = "需求集合创建"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(provider=AIProvider.MOCK, api_key="mock-key")
            
            document = Document(
                title="测试文档",
                content="测试内容",
                document_type=DocumentType.MARKDOWN
            )
            
            requirements = asyncio.run(extractor.extract_async(document))
            collection = extractor.create_requirement_collection(requirements)
            
            assert collection is not None
            assert len(collection.requirements) == len(requirements)
            
            self._record_success(test_name, f"创建包含 {len(requirements)} 个需求的集合")
            logger.info(f"✅ 需求集合创建测试通过 - 集合包含 {len(requirements)} 个需求")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 需求集合创建测试失败: {e}")
    
    def _record_success(self, test_name, details):
        """记录成功的测试"""
        self.test_results.append({
            "name": test_name,
            "success": True,
            "details": details,
            "timestamp": datetime.now()
        })
    
    def _record_failure(self, test_name, error):
        """记录失败的测试"""
        self.test_results.append({
            "name": test_name,
            "success": False,
            "error": error,
            "timestamp": datetime.now()
        })

    def _save_test_logs(self, test_level, duration):
        """保存测试日志"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = self.reports_dir / f"ai_module_test_{test_level}_{timestamp}.log"

            # 收集所有日志信息
            log_content = []
            log_content.append(f"🤖 TestMind AI - AI模块专项测试日志")
            log_content.append(f"=" * 60)
            log_content.append(f"测试级别: {test_level}")
            log_content.append(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            log_content.append(f"工作目录: {self.project_root}")
            log_content.append(f"总执行时间: {duration:.2f}秒")
            log_content.append("")

            # 添加测试结果详情
            log_content.append("📋 测试结果详情:")
            log_content.append("-" * 40)

            for i, result in enumerate(self.test_results, 1):
                status = "✅ 通过" if result["success"] else "❌ 失败"
                log_content.append(f"{i}. {result['name']}: {status}")
                log_content.append(f"   时间: {result['timestamp'].strftime('%H:%M:%S')}")

                if result["success"]:
                    log_content.append(f"   详情: {result.get('details', '测试通过')}")
                else:
                    log_content.append(f"   错误: {result.get('error', '未知错误')}")
                log_content.append("")

            # 添加统计信息
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r["success"])
            failed_tests = total_tests - passed_tests

            log_content.append("📊 测试统计:")
            log_content.append("-" * 40)
            log_content.append(f"总测试数: {total_tests}")
            log_content.append(f"通过: {passed_tests}")
            log_content.append(f"失败: {failed_tests}")
            log_content.append(f"成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "成功率: 0%")

            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))

            logger.info(f"💾 AI模块测试日志已保存: {log_file}")

        except Exception as e:
            logger.error(f"❌ 保存AI模块测试日志失败: {e}")
    
    def _display_results(self, duration):
        """显示测试结果"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 AI模块测试结果")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"⏱️  执行时间: {duration:.2f}秒")
        logger.info(f"📈 总测试数: {total_tests}")
        logger.info(f"✅ 通过: {passed_tests}")
        logger.info(f"❌ 失败: {failed_tests}")
        logger.info(f"🎯 成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "🎯 成功率: 0%")
        
        if failed_tests > 0:
            logger.info("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['name']}: {result['error']}")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 所有AI模块测试通过！")
        else:
            logger.info(f"\n⚠️  {failed_tests} 个AI模块测试失败")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AI模块专项测试")
    parser.add_argument(
        "--level",
        choices=["basic", "providers", "advanced", "all"],
        default="all",
        help="测试级别"
    )
    parser.add_argument(
        "--no-logs",
        action="store_true",
        help="不保存日志文件"
    )
    parser.add_argument(
        "--view-logs",
        action="store_true",
        help="测试后查看日志文件"
    )

    args = parser.parse_args()

    tester = AIModuleTester()
    success = tester.run_ai_tests(test_level=args.level, save_logs=not args.no_logs)

    # 如果需要查看日志
    if args.view_logs and not args.no_logs:
        # 查找最新的日志文件
        log_files = list(tester.reports_dir.glob(f"ai_module_test_{args.level}_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            print(f"\n📝 查看日志文件: {latest_log}")
            print("-" * 60)
            with open(latest_log, 'r', encoding='utf-8') as f:
                print(f.read())

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
