"""
LangChain需求提取器
支持多种AI模型：OpenAI、Ollama、Gemini等
"""
import json
import asyncio
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.core.config import get_settings
from app.requirements_parser.models.document import Document
from app.requirements_parser.models.requirement import (
    Requirement, RequirementType, Priority, RequirementCollection
)

class AIProvider(str, Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    MOCK = "mock"  # 用于测试

class LangChainExtractor:
    """多AI提供商需求提取器"""

    def __init__(self,
                 provider: AIProvider = AIProvider.OLLAMA,
                 api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 ollama_url: str = "http://localhost:11434"):
        """
        初始化需求提取器

        Args:
            provider: AI提供商
            api_key: API密钥（OpenAI/Gemini需要）
            model: 模型名称
            ollama_url: Ollama服务地址
        """
        self.provider = provider
        self.ollama_url = ollama_url
        settings = get_settings()

        # 根据提供商初始化
        if provider == AIProvider.OPENAI:
            if openai is None:
                raise ImportError("需要安装openai库: pip install openai")
            self.api_key = api_key or settings.openai_api_key
            if not self.api_key:
                raise ValueError("未设置OpenAI API密钥")
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.model = model or "gpt-3.5-turbo"

        elif provider == AIProvider.GEMINI:
            if genai is None:
                raise ImportError("需要安装google-generativeai库: pip install google-generativeai")
            self.api_key = api_key or getattr(settings, 'gemini_api_key', None)
            if not self.api_key:
                raise ValueError("未设置Gemini API密钥")
            genai.configure(api_key=self.api_key)
            self.model = model or "gemini-pro"

        elif provider == AIProvider.OLLAMA:
            # Ollama不需要API密钥
            self.model = model or "llama2"
            self.api_key = None

        elif provider == AIProvider.MOCK:
            # 测试模式
            self.api_key = api_key or "mock-key"
            self.model = model or "mock-model"

        # 通用配置
        self.temperature = 0.1
        self.max_tokens = 2000
        
        # 根据AI提供商优化提示词
        if provider == AIProvider.OLLAMA:
            # Ollama模型（特别是中文模型）需要更简洁明确的指令
            self.system_prompt = """你是需求分析师。从文档提取需求，输出JSON格式。

格式：[{"id":"REQ-001","title":"标题","description":"描述","type":"functional","priority":"medium","acceptance_criteria":["标准1"]}]

规则：
1. 只输出JSON，不要其他内容
2. type只能是：functional, non_functional, user_story
3. priority只能是：critical, high, medium, low
4. 每个需求包含所有字段

示例：
[{"id":"REQ-001","title":"用户登录","description":"用户通过邮箱密码登录","type":"functional","priority":"high","acceptance_criteria":["支持邮箱登录","密码验证"]}]"""
        else:
            # OpenAI/Gemini使用原始提示词
            self.system_prompt = """你是一个专业的需求分析师，擅长从文档中提取和分析软件需求。

请从给定的文档中提取需求信息，并按照以下JSON格式返回：

[
    {
        "id": "需求唯一标识符（如REQ-001）",
        "title": "需求标题",
        "description": "需求详细描述",
        "type": "需求类型（functional/non_functional/user_story/business_rule/constraint/assumption）",
        "priority": "优先级（critical/high/medium/low）",
        "acceptance_criteria": ["验收标准1", "验收标准2", "..."]
    }
]

提取规则：
1. 识别所有明确的功能需求、非功能需求和用户故事
2. 为每个需求生成唯一的ID
3. 提取验收标准或成功条件
4. 根据重要性评估优先级
5. 确保描述清晰、具体、可测试
6. 只返回JSON格式，不要添加其他文本"""
        
        self.user_prompt_template = """请分析以下文档并提取需求：

文档标题：{title}
文档内容：
{content}

请严格按照JSON格式返回提取的需求列表。"""
    
    async def _call_ai_api(self, messages: List[Dict[str, str]]) -> str:
        """
        调用AI API（支持多提供商）

        Args:
            messages: 消息列表

        Returns:
            str: AI响应内容
        """
        if self.provider == AIProvider.OPENAI:
            return await self._call_openai_api(messages)
        elif self.provider == AIProvider.OLLAMA:
            return await self._call_ollama_api(messages)
        elif self.provider == AIProvider.GEMINI:
            return await self._call_gemini_api(messages)
        elif self.provider == AIProvider.MOCK:
            return await self._call_mock_api(messages)
        else:
            raise ValueError(f"不支持的AI提供商: {self.provider}")

    async def _call_openai_api(self, messages: List[Dict[str, str]]) -> str:
        """调用OpenAI API"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content

    async def _call_ollama_api(self, messages: List[Dict[str, str]]) -> str:
        """调用Ollama API"""
        # 构建Ollama请求
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        # 异步HTTP请求
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API错误: {response.status}")

    async def _call_gemini_api(self, messages: List[Dict[str, str]]) -> str:
        """调用Gemini API"""
        model = genai.GenerativeModel(self.model)

        # 构建Gemini提示词
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )
        )
        return response.text

    async def _call_mock_api(self, messages: List[Dict[str, str]]) -> str:
        """模拟API调用（用于测试）"""
        # 返回模拟的需求提取结果
        return '''[
            {
                "id": "REQ-001",
                "title": "模拟需求",
                "description": "这是一个模拟的需求提取结果",
                "type": "functional",
                "priority": "medium",
                "acceptance_criteria": ["模拟验收标准1", "模拟验收标准2"]
            }
        ]'''

    async def extract_async(self, document: Document, custom_prompt: Optional[str] = None) -> List[Requirement]:
        """
        异步提取需求

        Args:
            document: 要分析的文档
            custom_prompt: 自定义提示词

        Returns:
            List[Requirement]: 提取的需求列表

        Raises:
            Exception: 提取失败时抛出
        """
        try:
            # 构建提示词
            user_prompt = custom_prompt or self.user_prompt_template.format(
                title=document.title,
                content=document.content
            )

            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 调用AI API
            content = await self._call_ai_api(messages)

            # 清理和解析响应
            requirements_data = self._parse_ai_response(content)

            # 转换为Requirement对象
            requirements = []
            for req_data in requirements_data:
                requirement = Requirement(
                    id=req_data.get("id", f"REQ-{len(requirements)+1:03d}"),
                    title=req_data.get("title", ""),
                    description=req_data.get("description", ""),
                    type=RequirementType(req_data.get("type", "functional")),
                    priority=Priority(req_data.get("priority", "medium")),
                    acceptance_criteria=req_data.get("acceptance_criteria", []),
                    source_document=document.title,
                    extracted_by=f"{self.provider}_extractor",
                    created_at=datetime.now()
                )
                requirements.append(requirement)

            return requirements

        except json.JSONDecodeError as e:
            raise Exception(f"需求提取失败：JSON解析错误 - {e}")
        except Exception as e:
            raise Exception(f"需求提取失败：{e}")

    def _parse_ai_response(self, content: str) -> List[Dict[str, Any]]:
        """
        解析AI响应内容，处理各种格式问题

        Args:
            content: AI返回的原始内容

        Returns:
            List[Dict]: 解析后的需求数据
        """
        if not content or not content.strip():
            return []

        # 清理内容
        cleaned_content = content.strip()

        # 移除可能的思考过程标记（qwen模型特有）
        if "<think>" in cleaned_content:
            # 提取</think>之后的内容
            think_end = cleaned_content.find("</think>")
            if think_end != -1:
                cleaned_content = cleaned_content[think_end + 8:].strip()

        # 移除markdown代码块标记
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        cleaned_content = cleaned_content.strip()

        # 尝试直接解析JSON
        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON数组
        import re
        json_pattern = r'\[.*?\]'
        json_matches = re.findall(json_pattern, cleaned_content, re.DOTALL)

        for match in json_matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # 尝试提取单个JSON对象并包装成数组
        json_pattern = r'\{.*?\}'
        json_matches = re.findall(json_pattern, cleaned_content, re.DOTALL)

        if json_matches:
            objects = []
            for match in json_matches:
                try:
                    obj = json.loads(match)
                    objects.append(obj)
                except json.JSONDecodeError:
                    continue
            if objects:
                return objects

        # 如果所有解析都失败，返回空列表并记录原始内容
        print(f"⚠️ JSON解析失败，原始内容: {cleaned_content[:200]}...")
        return []
    
    def extract(self, document: Document, custom_prompt: Optional[str] = None) -> List[Requirement]:
        """
        同步提取需求（内部调用异步方法）
        
        Args:
            document: 要分析的文档
            custom_prompt: 自定义提示词
            
        Returns:
            List[Requirement]: 提取的需求列表
        """
        return asyncio.run(self.extract_async(document, custom_prompt))
    
    async def extract_with_accuracy(self, document: Document, expected_count: Optional[int] = None) -> Dict[str, Any]:
        """
        提取需求并计算准确率
        
        Args:
            document: 要分析的文档
            expected_count: 预期需求数量（用于准确率计算）
            
        Returns:
            Dict: 包含需求列表、准确率和置信度的结果
        """
        requirements = await self.extract_async(document)
        
        # 计算准确率
        accuracy = 1.0  # 默认准确率
        if expected_count is not None:
            extracted_count = len(requirements)
            # 简单的准确率计算：提取数量与预期数量的比值
            accuracy = min(extracted_count / expected_count, 1.0) if expected_count > 0 else 0.0
        
        # 计算平均置信度
        confidence_scores = [req.confidence_score for req in requirements if req.confidence_score is not None]
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.8
        
        return {
            "requirements": requirements,
            "accuracy": accuracy,
            "confidence": average_confidence,
            "extracted_count": len(requirements),
            "expected_count": expected_count
        }
    
    async def extract_batch(self, documents: List[Document]) -> Dict[str, List[Requirement]]:
        """
        批量提取需求
        
        Args:
            documents: 文档列表
            
        Returns:
            Dict: 文档标题到需求列表的映射
        """
        results = {}
        
        # 并发处理多个文档
        tasks = []
        for doc in documents:
            task = self.extract_async(doc)
            tasks.append((doc.title, task))
        
        # 等待所有任务完成
        for title, task in tasks:
            try:
                requirements = await task
                results[title] = requirements
            except Exception as e:
                results[title] = []
                print(f"文档 {title} 提取失败: {e}")
        
        return results
    
    def create_requirement_collection(self, requirements: List[Requirement]) -> RequirementCollection:
        """
        创建需求集合
        
        Args:
            requirements: 需求列表
            
        Returns:
            RequirementCollection: 需求集合对象
        """
        collection = RequirementCollection()
        
        for req in requirements:
            collection.add_requirement(req)
        
        return collection
    
    def validate_extraction_quality(self, requirements: List[Requirement]) -> Dict[str, Any]:
        """
        验证提取质量
        
        Args:
            requirements: 需求列表
            
        Returns:
            Dict: 质量评估结果
        """
        if not requirements:
            return {
                "quality_score": 0.0,
                "issues": ["未提取到任何需求"],
                "recommendations": ["检查文档内容是否包含需求信息"]
            }
        
        issues = []
        recommendations = []
        quality_score = 1.0
        
        # 检查需求完整性
        for req in requirements:
            if not req.title.strip():
                issues.append(f"需求 {req.id} 缺少标题")
                quality_score -= 0.1
            
            if not req.description.strip():
                issues.append(f"需求 {req.id} 缺少描述")
                quality_score -= 0.1
            
            if not req.acceptance_criteria:
                issues.append(f"需求 {req.id} 缺少验收标准")
                quality_score -= 0.05
        
        # 检查需求类型分布
        type_counts = {}
        for req in requirements:
            type_counts[req.type] = type_counts.get(req.type, 0) + 1
        
        if len(type_counts) == 1:
            recommendations.append("考虑是否遗漏了其他类型的需求")
        
        # 检查优先级分布
        priority_counts = {}
        for req in requirements:
            priority_counts[req.priority] = priority_counts.get(req.priority, 0) + 1
        
        if len(priority_counts) == 1:
            recommendations.append("考虑重新评估需求优先级")
        
        quality_score = max(0.0, quality_score)
        
        return {
            "quality_score": quality_score,
            "issues": issues,
            "recommendations": recommendations,
            "type_distribution": type_counts,
            "priority_distribution": priority_counts
        }
