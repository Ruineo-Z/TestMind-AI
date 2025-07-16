"""
文档解析服务
整合多种文档解析器，提供统一的解析服务，支持需求文档、API文档、Prompt文档等
"""
import time
from pathlib import Path
from typing import Dict, List, Any, Union

from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import Requirement, RequirementType, Priority
from app.requirements_parser.models.api_document import APIDocument
from app.requirements_parser.models.prompt_document import PromptDocument
from app.requirements_parser.parsers.markdown_parser import MarkdownParser
from app.requirements_parser.parsers.pdf_parser import PDFParser
from app.requirements_parser.parsers.word_parser import WordParser
from app.requirements_parser.parsers.openapi_parser import OpenAPIParser
from app.requirements_parser.parsers.prompt_parser import PromptParser
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider
from app.requirements_parser.utils.format_detector import DocumentFormatDetector


class DocumentParsingService:
    """文档解析服务 - 支持多种文档类型的统一解析"""

    def __init__(self, ai_provider: str = "gemini"):
        """
        初始化解析服务

        Args:
            ai_provider: AI提供商 (openai, gemini, ollama, mock)
        """
        self.ai_provider = ai_provider

        # 初始化格式检测器
        self.format_detector = DocumentFormatDetector()

        # 初始化所有解析器
        self.parsers = {
            DocumentType.MARKDOWN: MarkdownParser(),
            DocumentType.PDF: PDFParser(),
            DocumentType.WORD: WordParser(),
            DocumentType.OPENAPI: OpenAPIParser(),
            DocumentType.SWAGGER: OpenAPIParser(),
            DocumentType.API_MARKDOWN: MarkdownParser(),
            DocumentType.PROMPT: PromptParser()
        }

        # 初始化AI提取器（仅用于需求文档）
        self.requirements_extractor = LangChainExtractor(
            provider=AIProvider(ai_provider),
            model="gemini-1.5-pro" if ai_provider == "gemini" else "gpt-3.5-turbo"
        )
    
    async def parse_document(
        self,
        file_path: str,
        document_type: DocumentType = None,
        extract_requirements: bool = True
    ) -> Dict[str, Any]:
        """
        解析文档（支持多种文档类型）

        Args:
            file_path: 文档文件路径
            document_type: 指定文档类型（可选，不指定则自动检测）
            extract_requirements: 是否提取需求（仅对需求文档有效）

        Returns:
            Dict: 解析结果，包含文档信息和解析内容

        Raises:
            ValueError: 文件类型不支持或解析失败时抛出
        """
        start_time = time.time()

        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 自动检测文档类型（如果未指定）
            if document_type is None:
                document_type = self.format_detector.detect_format(content, file_path)

            # 解析文档
            document = await self._parse_document_by_type(file_path, content, document_type)

            # 根据文档类型进行不同的处理
            result = await self._process_document_by_type(document, extract_requirements)

            # 计算处理时间
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time

            return result
            
        except Exception as e:
            raise ValueError(f"解析文档失败: {str(e)}")
    
    async def _parse_document_by_type(
        self,
        file_path: str,
        content: str,
        document_type: DocumentType
    ) -> Document:
        """
        根据文档类型解析文档

        Args:
            file_path: 文件路径
            content: 文件内容
            document_type: 文档类型

        Returns:
            Document: 解析后的文档对象
        """
        parser = self.parsers.get(document_type)
        if not parser:
            raise ValueError(f"不支持的文档类型: {document_type}")

        # 根据不同类型使用不同的解析方式
        if document_type in [DocumentType.OPENAPI, DocumentType.SWAGGER]:
            # API文档直接解析内容
            return parser.parse(content, file_path=file_path)
        elif document_type == DocumentType.PROMPT:
            # Prompt文档直接解析内容
            return parser.parse(content, file_path=file_path)
        elif document_type in [DocumentType.PDF, DocumentType.WORD]:
            # PDF和Word需要文件路径
            return parser.parse_from_file(file_path)
        else:
            # Markdown等文本格式
            return parser.parse(content, file_path=file_path)

    async def _process_document_by_type(
        self,
        document: Document,
        extract_requirements: bool
    ) -> Dict[str, Any]:
        """
        根据文档类型进行不同的处理

        Args:
            document: 解析后的文档
            extract_requirements: 是否提取需求

        Returns:
            Dict: 处理结果
        """
        result = {"document": document}

        if document.document_type in [DocumentType.MARKDOWN, DocumentType.PDF, DocumentType.WORD]:
            # 传统需求文档 - 提取需求
            if extract_requirements:
                requirements = await self._extract_requirements_from_document(document)
                result["requirements"] = requirements
                result["accuracy"] = self._estimate_accuracy(document, requirements)
            result["document_category"] = "requirements"

        elif document.document_type in [DocumentType.OPENAPI, DocumentType.SWAGGER, DocumentType.API_MARKDOWN]:
            # API文档 - 提取API信息
            api_document = getattr(document, 'api_document', None)
            if api_document:
                result["api_document"] = api_document
                result["endpoints_count"] = len(api_document.endpoints)
                result["parsing_accuracy"] = api_document.parsing_accuracy
            result["document_category"] = "api"

        elif document.document_type == DocumentType.PROMPT:
            # Prompt文档 - 提取Prompt信息
            prompt_document = getattr(document, 'prompt_document', None)
            if prompt_document:
                result["prompt_document"] = prompt_document
                result["prompts_count"] = len(prompt_document.prompts)
                result["test_cases_count"] = len(prompt_document.test_cases)
                result["parsing_accuracy"] = prompt_document.parsing_accuracy
            result["document_category"] = "prompt"

        return result
    
    async def _extract_requirements_from_document(
        self,
        document: Document,
        extract_user_stories: bool = True
    ) -> List[Requirement]:
        """
        从文档中提取需求
        
        Args:
            document: 文档对象
            extract_user_stories: 是否提取用户故事
            
        Returns:
            List[Requirement]: 提取的需求列表
        """
        try:
            # 使用LangChain提取器提取需求
            requirements = await self.extractor.extract_async(document)
            
            # 如果需要，额外提取用户故事
            if extract_user_stories and document.user_stories:
                # 将文档中的用户故事转换为需求
                for story in document.user_stories:
                    story_requirement = Requirement(
                        id=f"US-{len(requirements)+1:03d}",
                        title="用户故事",
                        description=story.get("story", ""),
                        type=RequirementType.USER_STORY,
                        priority=Priority.MEDIUM,
                        acceptance_criteria=[],
                        source_document=document.title,
                        extracted_by="document_parser"
                    )
                    requirements.append(story_requirement)
            
            return requirements
            
        except Exception as e:
            # 如果AI提取失败，返回基于文档结构的简单需求
            return self._extract_simple_requirements(document)
    
    def _extract_simple_requirements(self, document: Document) -> List[Requirement]:
        """
        基于文档结构提取简单需求（备用方案）
        
        Args:
            document: 文档对象
            
        Returns:
            List[Requirement]: 简单提取的需求列表
        """
        requirements = []
        
        # 基于章节提取需求
        for i, section in enumerate(document.sections):
            if any(keyword in section['title'].lower() for keyword in ['需求', '功能', 'requirement', 'feature']):
                requirement = Requirement(
                    id=f"REQ-{i+1:03d}",
                    title=section['title'],
                    description=f"基于章节 '{section['title']}' 提取的需求",
                    type=RequirementType.FUNCTIONAL,
                    priority=Priority.MEDIUM,
                    acceptance_criteria=[],
                    source_document=document.title,
                    extracted_by="simple_extractor"
                )
                requirements.append(requirement)
        
        # 如果没有找到需求相关章节，创建一个默认需求
        if not requirements:
            requirement = Requirement(
                id="REQ-001",
                title="文档需求",
                description=f"从文档 '{document.title}' 中提取的需求",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.MEDIUM,
                acceptance_criteria=[],
                source_document=document.title,
                extracted_by="simple_extractor"
            )
            requirements.append(requirement)
        
        return requirements
    
    def _estimate_accuracy(self, document: Document, requirements: List[Requirement]) -> float:
        """
        估算需求提取准确率
        
        Args:
            document: 文档对象
            requirements: 提取的需求列表
            
        Returns:
            float: 估算的准确率 (0.0-1.0)
        """
        if not requirements:
            return 0.0
        
        # 简单的准确率估算逻辑
        base_accuracy = 0.7  # 基础准确率
        
        # 根据文档结构调整
        if document.sections:
            base_accuracy += 0.1
        
        if document.user_stories:
            base_accuracy += 0.1
        
        # 根据需求数量调整
        if len(requirements) > 1:
            base_accuracy += 0.05
        
        # 根据AI提供商调整
        if self.ai_provider == "openai":
            base_accuracy += 0.05
        elif self.ai_provider == "mock":
            base_accuracy = 0.8  # Mock提供商固定准确率
        
        return min(base_accuracy, 1.0)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        获取支持的文件格式
        
        Returns:
            Dict: 支持的格式信息
        """
        return {
            "markdown": [".md", ".markdown", ".mdown", ".mkd"],
            "pdf": [".pdf"],
            "word": [".docx", ".doc"]
        }
