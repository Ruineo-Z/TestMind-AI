"""
需求解析服务
整合文档解析器和需求提取器，提供统一的解析服务
"""
import time
from pathlib import Path
from typing import Dict, List, Any

from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.requirement import Requirement, RequirementType, Priority
from app.requirements_parser.parsers.markdown_parser import MarkdownParser
from app.requirements_parser.parsers.pdf_parser import PDFParser
from app.requirements_parser.parsers.word_parser import WordParser
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider


class RequirementsParsingService:
    """需求解析服务"""
    
    def __init__(self, ai_provider: str = "mock"):
        """
        初始化解析服务
        
        Args:
            ai_provider: AI提供商 (openai, ollama, gemini, mock)
        """
        self.ai_provider = ai_provider
        
        # 初始化解析器
        self.parsers = {
            DocumentType.MARKDOWN: MarkdownParser(),
            DocumentType.PDF: PDFParser(),
            DocumentType.WORD: WordParser()
        }
        
        # 初始化需求提取器
        self.extractor = LangChainExtractor(
            provider=AIProvider(ai_provider),
            model="gpt-3.5-turbo" if ai_provider == "openai" else "llama2"
        )
    
    async def parse_document(
        self,
        file_path: str,
        extract_user_stories: bool = True
    ) -> Dict[str, Any]:
        """
        解析文档并提取需求
        
        Args:
            file_path: 文档文件路径
            extract_user_stories: 是否提取用户故事
            
        Returns:
            Dict: 解析结果，包含文档和需求信息
            
        Raises:
            ValueError: 文件类型不支持或解析失败时抛出
        """
        start_time = time.time()
        
        try:
            # 确定文档类型
            document_type = self._detect_document_type(file_path)
            
            # 解析文档
            document = await self._parse_document(file_path, document_type)
            
            # 提取需求
            requirements = await self._extract_requirements(
                document, 
                extract_user_stories
            )
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 计算准确率（简单估算）
            accuracy = self._estimate_accuracy(document, requirements)
            
            return {
                "document": document,
                "requirements": requirements,
                "accuracy": accuracy,
                "processing_time": processing_time
            }
            
        except Exception as e:
            raise ValueError(f"解析文档失败: {str(e)}")
    
    def _detect_document_type(self, file_path: str) -> DocumentType:
        """
        检测文档类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            DocumentType: 文档类型
            
        Raises:
            ValueError: 不支持的文件类型时抛出
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension in {'.md', '.markdown', '.mdown', '.mkd'}:
            return DocumentType.MARKDOWN
        elif extension == '.pdf':
            return DocumentType.PDF
        elif extension in {'.docx', '.doc'}:
            return DocumentType.WORD
        else:
            raise ValueError(f"不支持的文件类型: {extension}")
    
    async def _parse_document(self, file_path: str, document_type: DocumentType) -> Document:
        """
        解析文档
        
        Args:
            file_path: 文件路径
            document_type: 文档类型
            
        Returns:
            Document: 解析后的文档对象
        """
        parser = self.parsers.get(document_type)
        if not parser:
            raise ValueError(f"没有找到适合的解析器: {document_type}")
        
        # 对于Markdown，直接从文件解析
        if document_type == DocumentType.MARKDOWN:
            return parser.parse_from_file(file_path)
        else:
            # 对于PDF和Word，使用文件路径
            return parser.parse(file_path)
    
    async def _extract_requirements(
        self, 
        document: Document, 
        extract_user_stories: bool
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
