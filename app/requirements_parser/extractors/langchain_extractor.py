"""
真正的LangChain需求提取器
使用LangChain框架实现AI驱动的需求提取，支持OpenAI、Gemini、Ollama三个供应商
"""
import json
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum

# 导入Pydantic（必需）
from pydantic import BaseModel, Field

# 导入环境配置
from app.core.env_loader import load_env_config, get_ai_config

# 导入LangChain相关模块
try:
    # Ollama
    from langchain_ollama import ChatOllama
    # OpenAI
    from langchain_openai import ChatOpenAI
    # Google Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
    # Core components
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain导入错误: {e}")
    ChatOllama = None
    ChatOpenAI = None
    ChatGoogleGenerativeAI = None
    HumanMessage = None
    SystemMessage = None
    ChatPromptTemplate = None
    JsonOutputParser = None
    StrOutputParser = None
    RunnablePassthrough = None
    LANGCHAIN_AVAILABLE = False

from app.core.config import get_settings
from app.requirements_parser.models.document import Document
from app.requirements_parser.models.requirement import Requirement, RequirementType, Priority, RequirementCollection


class AIProvider(str, Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    MOCK = "mock"


class RequirementSchema(BaseModel):
    """需求数据结构"""
    id: str = Field(description="需求ID")
    title: str = Field(description="需求标题")
    description: str = Field(description="需求描述")
    type: str = Field(description="需求类型: functional, non_functional, constraint")
    priority: str = Field(description="优先级: low, medium, high, critical")
    acceptance_criteria: List[str] = Field(description="验收标准列表")


class LangChainExtractor:
    """LangChain需求提取器，支持多种AI提供商"""

    def __init__(self,
                 provider: AIProvider = AIProvider.GEMINI,
                 model: Optional[str] = None,
                 temperature: float = 0.1,
                 ollama_url: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 google_api_key: Optional[str] = None):
        """
        初始化需求提取器

        Args:
            provider: AI提供商 (openai, gemini, ollama)
            model: 模型名称
            temperature: 温度参数，控制输出随机性
            ollama_url: Ollama服务地址（可选，从.env读取）
            openai_api_key: OpenAI API密钥（可选，从.env读取）
            google_api_key: Google API密钥（可选，从.env读取）
        """
        # 加载环境配置
        load_env_config()
        ai_config = get_ai_config()

        self.provider = provider
        self.temperature = temperature

        # 从环境配置获取设置
        self.ollama_url = ollama_url or ai_config["ollama_base_url"]
        self.openai_api_key = openai_api_key or ai_config["openai_api_key"]
        self.google_api_key = google_api_key or ai_config["google_api_key"]

        # 根据提供商设置默认模型
        if model:
            self.model = model
        else:
            if provider == AIProvider.OPENAI:
                self.model = ai_config.get("openai_model", "gpt-3.5-turbo")
            elif provider == AIProvider.GEMINI:
                self.model = ai_config.get("gemini_model", "gemini-2.5-flash-lite-preview-06-17")
            elif provider == AIProvider.OLLAMA:
                self.model = ai_config["ollama_model"]
            elif provider == AIProvider.MOCK:
                self.model = "mock-model"
            else:
                self.model = "llama3"

        # 初始化LangChain组件
        self._setup_langchain()

    def _setup_langchain(self):
        """设置LangChain组件"""
        # 根据提供商初始化LLM
        if self.provider == AIProvider.OPENAI:
            if not self.openai_api_key:
                raise ValueError("使用OpenAI提供商需要提供API密钥")

            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=self.openai_api_key
            )

        elif self.provider == AIProvider.GEMINI:
            if not self.google_api_key:
                raise ValueError("使用Gemini提供商需要提供Google API密钥")

            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                google_api_key=self.google_api_key
            )

        elif self.provider == AIProvider.OLLAMA:
            self.llm = ChatOllama(
                model=self.model,
                temperature=self.temperature,
                base_url=self.ollama_url
            )

        elif self.provider == AIProvider.MOCK:
            # 创建Mock LLM用于测试
            self.llm = self._create_mock_llm()

        else:
            raise ValueError(f"不支持的AI提供商: {self.provider}")

        # 设置输出解析器
        self.output_parser = JsonOutputParser(pydantic_object=RequirementSchema)

        # 设置提示词模板
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", self._get_user_prompt_template())
        ])

        # 构建LangChain链
        self.chain = (
            self.prompt_template
            | self.llm
            | self.output_parser
        )

    def _create_mock_llm(self):
        """创建Mock LLM用于测试"""

        class MockLLM:
            """简单的Mock LLM实现"""

            def __init__(self):
                self.mock_response = '''[
                    {
                        "id": "REQ-001",
                        "title": "API接口测试需求",
                        "description": "需要对FastAPI演示接口进行全面的自动化测试",
                        "type": "functional",
                        "priority": "high",
                        "acceptance_criteria": [
                            "能够测试GET /接口的欢迎消息",
                            "能够测试GET /items接口的项目列表",
                            "能够测试POST /items接口的项目创建",
                            "能够测试DELETE /items/{item_id}接口的项目删除"
                        ]
                    },
                    {
                        "id": "REQ-002",
                        "title": "测试用例生成需求",
                        "description": "使用AI自动生成pytest测试用例，包含正向、负向和边界测试",
                        "type": "functional",
                        "priority": "high",
                        "acceptance_criteria": [
                            "生成的测试用例使用httpx客户端",
                            "测试代码包含中文注释",
                            "支持异步测试执行",
                            "包含完整的断言验证"
                        ]
                    }
                ]'''

            def invoke(self, input_data):
                """同步调用"""
                return self.mock_response

            async def ainvoke(self, input_data):
                """异步调用"""
                return self.mock_response

        return MockLLM()
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的需求分析师。你的任务是从给定的文档中提取软件需求。

请严格按照以下JSON格式返回需求列表：
[
    {{
        "id": "REQ-001",
        "title": "需求标题",
        "description": "详细的需求描述",
        "type": "functional",
        "priority": "medium",
        "acceptance_criteria": ["验收标准1", "验收标准2"]
    }}
]

需求类型包括：
- functional: 功能性需求
- non_functional: 非功能性需求
- constraint: 约束条件

优先级包括：
- low: 低优先级
- medium: 中等优先级
- high: 高优先级
- critical: 关键优先级

请确保：
1. 每个需求都有唯一的ID
2. 标题简洁明了
3. 描述详细准确
4. 验收标准具体可测试
5. 只返回JSON格式，不要其他文字"""
    
    def _get_user_prompt_template(self) -> str:
        """获取用户提示词模板"""
        return """请分析以下文档并提取需求：

文档标题：{title}
文档内容：
{content}

请严格按照JSON格式返回提取的需求列表。"""
    
    async def extract_async(self, document: Document, custom_prompt: Optional[str] = None) -> List[Requirement]:
        """
        异步提取需求
        
        Args:
            document: 要分析的文档
            custom_prompt: 自定义提示词（暂不支持）
            
        Returns:
            List[Requirement]: 提取的需求列表
        """
        try:
            # 准备输入数据
            input_data = {
                "title": document.title,
                "content": document.content
            }
            
            # 使用LangChain链进行处理
            result = await self.chain.ainvoke(input_data)
            
            # 如果结果是字符串，尝试解析JSON
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    # 尝试提取JSON部分
                    import re

                    # 移除<think>...</think>标签
                    result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)

                    # 尝试提取JSON数组
                    json_match = re.search(r'\[.*\]', result, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            # 如果仍然无法解析，尝试清理JSON字符串
                            json_str = json_match.group()
                            # 移除可能的注释或多余文本
                            json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
                            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                            try:
                                result = json.loads(json_str)
                            except json.JSONDecodeError:
                                raise Exception("无法解析AI响应中的JSON")
                    else:
                        raise Exception("无法在AI响应中找到JSON数组")
            
            # 转换为Requirement对象
            requirements = []
            if isinstance(result, list):
                for req_data in result:
                    requirement = Requirement(
                        id=req_data.get("id", f"REQ-{len(requirements)+1:03d}"),
                        title=req_data.get("title", ""),
                        description=req_data.get("description", ""),
                        type=RequirementType(req_data.get("type", "functional")),
                        priority=Priority(req_data.get("priority", "medium")),
                        acceptance_criteria=req_data.get("acceptance_criteria", []),
                        source_document=document.title,
                        extracted_by=f"langchain_{self.provider.value}_extractor",
                        created_at=datetime.now()
                    )
                    requirements.append(requirement)
            
            return requirements
            
        except Exception as e:
            raise Exception(f"LangChain需求提取失败：{e}")
    
    def extract(self, document: Document, custom_prompt: Optional[str] = None) -> List[Requirement]:
        """
        同步提取需求
        
        Args:
            document: 要分析的文档
            custom_prompt: 自定义提示词（暂不支持）
            
        Returns:
            List[Requirement]: 提取的需求列表
        """
        return asyncio.run(self.extract_async(document, custom_prompt))
    
    async def extract_with_accuracy(self, document: Document, expected_count: int = None) -> Dict[str, Any]:
        """
        提取需求并计算准确率
        
        Args:
            document: 要分析的文档
            expected_count: 预期需求数量
            
        Returns:
            Dict: 包含需求列表和准确率信息
        """
        requirements = await self.extract_async(document)
        extracted_count = len(requirements)
        
        # 计算准确率
        if expected_count is not None:
            accuracy = min(extracted_count / expected_count, 1.0) if expected_count > 0 else 0.0
        else:
            accuracy = 1.0  # 没有预期数量时默认为100%
        
        # 计算置信度（基于需求的完整性）
        confidence = self._calculate_confidence(requirements)
        
        return {
            "requirements": requirements,
            "extracted_count": extracted_count,
            "expected_count": expected_count,
            "accuracy": accuracy,
            "confidence": confidence
        }
    
    def _calculate_confidence(self, requirements: List[Requirement]) -> float:
        """计算置信度"""
        if not requirements:
            return 0.0
        
        total_score = 0
        for req in requirements:
            score = 0
            # 检查各个字段的完整性
            if req.title and len(req.title.strip()) > 0:
                score += 0.3
            if req.description and len(req.description.strip()) > 0:
                score += 0.3
            if req.acceptance_criteria and len(req.acceptance_criteria) > 0:
                score += 0.4
            
            total_score += score
        
        return total_score / len(requirements)
    
    def create_requirement_collection(self, requirements: List[Requirement]) -> RequirementCollection:
        """创建需求集合"""
        return RequirementCollection(requirements=requirements)
    
    async def extract_batch(self, documents: List[Document]) -> Dict[str, List[Requirement]]:
        """
        批量提取需求
        
        Args:
            documents: 文档列表
            
        Returns:
            Dict: 文档标题到需求列表的映射
        """
        results = {}
        
        # 并发处理所有文档
        tasks = [self.extract_async(doc) for doc in documents]
        requirements_lists = await asyncio.gather(*tasks)
        
        # 构建结果字典
        for doc, requirements in zip(documents, requirements_lists):
            results[doc.title] = requirements
        
        return results
    
    def validate_extraction_quality(self, requirements: List[Requirement]) -> Dict[str, Any]:
        """验证提取质量"""
        issues = []
        recommendations = []
        
        for req in requirements:
            # 检查标题
            if not req.title or len(req.title.strip()) < 3:
                issues.append(f"需求 {req.id} 标题过短或为空")
                recommendations.append(f"为需求 {req.id} 提供更详细的标题")
            
            # 检查描述
            if not req.description or len(req.description.strip()) < 10:
                issues.append(f"需求 {req.id} 描述过短或为空")
                recommendations.append(f"为需求 {req.id} 提供更详细的描述")
            
            # 检查验收标准
            if not req.acceptance_criteria or len(req.acceptance_criteria) == 0:
                issues.append(f"需求 {req.id} 缺少验收标准")
                recommendations.append(f"为需求 {req.id} 添加具体的验收标准")
        
        # 计算质量分数
        total_checks = len(requirements) * 3  # 每个需求检查3个方面
        quality_score = max(0, (total_checks - len(issues)) / total_checks) if total_checks > 0 else 0
        
        return {
            "quality_score": quality_score,
            "issues": issues,
            "recommendations": recommendations
        }
