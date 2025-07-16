#!/usr/bin/env python3
"""
AI模块专项测试脚本（仅Ollama版本）
专门测试LangChain AI模块的Ollama功能
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.models.document import Document, DocumentType

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class AIModuleTesterOllamaOnly:
    """AI模块测试器（仅Ollama版本）"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = []
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_ai_tests(self, test_level="all", save_logs=True):
        """运行AI模块测试"""
        logger.info("🤖 TestMind AI - AI模块专项测试（仅Ollama版本）")
        logger.info("=" * 60)
        logger.info(f"测试级别: {test_level}")
        logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"工作目录: {self.project_root}")
        
        start_time = time.time()
        
        # 执行不同级别的测试
        if test_level == "basic":
            self._run_basic_tests()
        elif test_level == "configuration":
            self._run_configuration_tests()
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
        
        # 测试1: Ollama提供商初始化
        self._test_ollama_provider_initialization()
        
        # 测试2: 提取器基础功能
        self._test_extractor_basic_functionality()
    
    def _run_configuration_tests(self):
        """运行配置测试"""
        logger.info("\n🔧 Ollama配置测试")
        logger.info("-" * 40)
        
        # 测试Ollama配置
        self._test_ollama_configuration()
        
        # 测试提示词配置
        self._test_prompt_configuration()
    
    def _run_advanced_tests(self):
        """运行高级AI测试"""
        logger.info("\n🚀 高级AI功能测试")
        logger.info("-" * 40)
        
        # 测试配置验证
        self._test_configuration_validation()
        
        # 测试错误处理
        self._test_error_handling()
    
    def _run_all_tests(self):
        """运行所有AI测试"""
        self._run_basic_tests()
        self._run_configuration_tests()
        self._run_advanced_tests()
    
    def _test_ollama_provider_initialization(self):
        """测试Ollama提供商初始化"""
        test_name = "Ollama提供商初始化"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(
                provider=AIProvider.OLLAMA,
                model="llama2",
                ollama_url="http://localhost:11434"
            )
            
            assert extractor.provider == AIProvider.OLLAMA
            assert extractor.model == "llama2"
            assert extractor.ollama_url == "http://localhost:11434"
            assert hasattr(extractor, 'extract')
            assert hasattr(extractor, 'extract_async')
            
            self._record_success(test_name, "Ollama提供商初始化成功")
            logger.info("✅ Ollama提供商初始化测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ Ollama提供商初始化测试失败: {e}")
    
    def _test_extractor_basic_functionality(self):
        """测试提取器基础功能"""
        test_name = "提取器基础功能"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(
                provider=AIProvider.OLLAMA,
                model="llama2",
                ollama_url="http://localhost:11434"
            )
            
            # 验证基础属性
            assert extractor.provider == AIProvider.OLLAMA
            assert extractor.model == "llama2"
            assert hasattr(extractor, 'system_prompt')
            assert hasattr(extractor, 'user_prompt_template')
            assert extractor.temperature == 0.1
            assert extractor.max_tokens == 2000
            
            self._record_success(test_name, "提取器基础功能验证成功")
            logger.info("✅ 提取器基础功能测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 提取器基础功能测试失败: {e}")
    
    def _test_ollama_configuration(self):
        """测试Ollama配置"""
        test_name = "Ollama配置"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            # 测试默认配置
            default_extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
            assert default_extractor.model == "llama2"
            assert default_extractor.ollama_url == "http://localhost:11434"
            
            # 测试自定义配置
            custom_extractor = LangChainExtractor(
                provider=AIProvider.OLLAMA,
                model="llama3",
                ollama_url="http://custom:11434"
            )
            assert custom_extractor.model == "llama3"
            assert custom_extractor.ollama_url == "http://custom:11434"
            
            self._record_success(test_name, "Ollama配置验证成功")
            logger.info("✅ Ollama配置测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ Ollama配置测试失败: {e}")
    
    def _test_prompt_configuration(self):
        """测试提示词配置"""
        test_name = "提示词配置"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
            
            # 验证系统提示词
            assert extractor.system_prompt is not None
            assert "需求分析师" in extractor.system_prompt
            assert "JSON格式" in extractor.system_prompt
            
            # 验证用户提示词模板
            assert extractor.user_prompt_template is not None
            assert "{title}" in extractor.user_prompt_template
            assert "{content}" in extractor.user_prompt_template
            
            self._record_success(test_name, "提示词配置验证成功")
            logger.info("✅ 提示词配置测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 提示词配置测试失败: {e}")
    
    def _test_configuration_validation(self):
        """测试配置验证"""
        test_name = "配置验证"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            # 测试默认配置
            extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
            assert extractor.temperature == 0.1
            assert extractor.max_tokens == 2000
            assert extractor.system_prompt is not None
            assert extractor.user_prompt_template is not None
            
            # 验证提示词模板包含必要的占位符
            assert "{title}" in extractor.user_prompt_template
            assert "{content}" in extractor.user_prompt_template
            
            self._record_success(test_name, "配置验证成功")
            logger.info("✅ 配置验证测试通过")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 配置验证测试失败: {e}")
    
    def _test_error_handling(self):
        """测试错误处理"""
        test_name = "错误处理"
        logger.info(f"🔍 测试: {test_name}")
        
        try:
            # 测试无效提供商错误
            extractor = LangChainExtractor(provider=AIProvider.OLLAMA)
            extractor.provider = "invalid_provider"
            
            document = Document(
                title="测试",
                content="测试内容",
                document_type=DocumentType.MARKDOWN
            )
            
            try:
                import asyncio
                asyncio.run(extractor.extract_async(document))
                self._record_failure(test_name, "无效提供商应该抛出异常")
            except Exception as e:
                if "不支持的AI提供商" in str(e):
                    self._record_success(test_name, "正确处理无效提供商")
                    logger.info("✅ 错误处理测试通过")
                else:
                    self._record_failure(test_name, f"错误消息不正确: {e}")
            
        except Exception as e:
            self._record_failure(test_name, str(e))
            logger.error(f"❌ 错误处理测试失败: {e}")
    
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
            log_file = self.reports_dir / f"ai_module_ollama_{test_level}_{timestamp}.log"
            
            # 收集所有日志信息
            log_content = []
            log_content.append(f"🤖 TestMind AI - AI模块专项测试日志（仅Ollama版本）")
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
            success_rate = f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%"
            log_content.append(f"成功率: {success_rate}")
            
            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))
            
            logger.info(f"💾 AI模块测试日志已保存: {log_file}")
            
        except Exception as e:
            logger.error(f"❌ 保存AI模块测试日志失败: {e}")
    
    def _display_results(self, duration):
        """显示测试结果"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 AI模块测试结果（仅Ollama版本）")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"⏱️  执行时间: {duration:.2f}秒")
        logger.info(f"📈 总测试数: {total_tests}")
        logger.info(f"✅ 通过: {passed_tests}")
        logger.info(f"❌ 失败: {failed_tests}")
        success_rate = f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%"
        logger.info(f"🎯 成功率: {success_rate}")
        
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
    
    parser = argparse.ArgumentParser(description="AI模块专项测试（仅Ollama版本）")
    parser.add_argument(
        "--level",
        choices=["basic", "configuration", "advanced", "all"],
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
    
    tester = AIModuleTesterOllamaOnly()
    success = tester.run_ai_tests(test_level=args.level, save_logs=not args.no_logs)
    
    # 如果需要查看日志
    if args.view_logs and not args.no_logs:
        # 查找最新的日志文件
        log_files = list(tester.reports_dir.glob(f"ai_module_ollama_{args.level}_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            print(f"\n📝 查看日志文件: {latest_log}")
            print("-" * 60)
            with open(latest_log, 'r', encoding='utf-8') as f:
                print(f.read())
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
