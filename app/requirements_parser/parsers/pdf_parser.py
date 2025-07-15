"""
PDF文档解析器
解析PDF格式的需求文档
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from pypdf import PdfReader
    PyPDF2 = True  # 兼容性标记
except ImportError:
    try:
        import PyPDF2
        from PyPDF2 import PdfReader
    except ImportError:
        PyPDF2 = None
        PdfReader = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from app.requirements_parser.parsers.base import BaseParser
from app.requirements_parser.models.document import Document, DocumentType, DocumentMetadata


class PDFParser(BaseParser):
    """PDF文档解析器"""
    
    def __init__(self):
        """初始化PDF解析器"""
        super().__init__()
        self.supported_extensions = {'.pdf'}
        
        # 检查依赖
        if PyPDF2 is None and pdfplumber is None:
            raise ImportError("需要安装PDF解析库: pip install PyPDF2 pdfplumber")
    
    def parse(self, content: str, **kwargs) -> Document:
        """
        解析PDF内容（从文件路径）
        
        Args:
            content: PDF文件路径
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        if isinstance(content, str) and Path(content).exists():
            return self.parse_from_file(content, **kwargs)
        else:
            raise ValueError("PDF解析器需要文件路径作为输入")
    
    def parse_from_file(self, file_path: str, encoding: str = "utf-8", **kwargs) -> Document:
        """
        从PDF文件解析文档
        
        Args:
            file_path: PDF文件路径
            encoding: 编码（PDF不需要，保持接口一致性）
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"路径不是文件: {file_path}")
        
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"不是PDF文件: {file_path}")
        
        # 提取PDF文本内容
        text_content = self._extract_text_from_pdf(file_path)
        
        # 解析文本内容
        document = self._parse_text_content(text_content, str(path))
        document.file_path = str(path)
        
        # 设置文件元数据
        if document.metadata:
            document.metadata.file_size = path.stat().st_size
            document.metadata.created_at = path.stat().st_ctime
            document.metadata.modified_at = path.stat().st_mtime
            document.metadata.encoding = "binary"  # PDF是二进制格式
        
        return document
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        从PDF文件提取文本内容
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            str: 提取的文本内容
        """
        text_content = ""
        
        # 优先使用pdfplumber（更好的表格和布局支持）
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                
                if text_content.strip():
                    return text_content
            except Exception:
                # 如果pdfplumber失败，尝试PyPDF2
                pass
        
        # 使用PyPDF2作为备选方案
        if PyPDF2:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            except Exception as e:
                raise ValueError(f"无法解析PDF文件 {file_path}: {e}")
        
        if not text_content.strip():
            raise ValueError(f"无法从PDF文件提取文本内容: {file_path}")
        
        return text_content
    
    def _parse_text_content(self, text_content: str, file_name: str) -> Document:
        """
        解析PDF提取的文本内容
        
        Args:
            text_content: 文本内容
            file_name: 文件名
            
        Returns:
            Document: 解析后的文档对象
        """
        # 验证内容
        if not text_content or not text_content.strip():
            raise ValueError("PDF内容为空")
        
        # 清理文本内容
        clean_content = self._clean_text_content(text_content)
        
        # 提取标题
        title = self._extract_title_from_content(clean_content, file_name)
        
        # 创建文档对象
        document = Document(
            title=title,
            content=clean_content,
            document_type=DocumentType.PDF
        )
        
        # 添加解析的结构化信息
        document.sections = self._extract_sections(clean_content)
        document.tables = self._extract_tables(clean_content)
        document.links = self._extract_links(clean_content)
        document.user_stories = self._extract_user_stories(clean_content)
        
        return document
    
    def _clean_text_content(self, text: str) -> str:
        """
        清理PDF提取的文本内容

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本
        """
        # 先按行分割，保持原始结构
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line:
                # 跳过可能的页码
                if re.match(r'^\d+$', line):
                    continue
                # 跳过可能的页眉页脚（但保留标题）
                if len(line) < 5 and not re.match(r'^#+\s', line):
                    continue
                cleaned_lines.append(line)
            else:
                # 保留空行以维持文档结构
                cleaned_lines.append('')

        return '\n'.join(cleaned_lines)
    
    def _extract_title_from_content(self, content: str, file_name: str) -> str:
        """
        从内容中提取标题
        
        Args:
            content: 文档内容
            file_name: 文件名
            
        Returns:
            str: 文档标题
        """
        lines = content.split('\n')
        
        # 查找第一个标题行
        for line in lines:
            line = line.strip()
            if line:
                # Markdown风格标题
                if line.startswith('#'):
                    return line.lstrip('#').strip()
                # 可能的标题（较短且在前面）
                if len(line) < 100 and not line.startswith('-') and not line.startswith('*'):
                    return line
        
        # 如果没有找到合适的标题，使用文件名
        return Path(file_name).stem
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """提取章节信息"""
        sections = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # 检测标题行
            if line.startswith('#') or (line and i > 0 and lines[i-1].strip() == ''):
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    title = line.lstrip('#').strip()
                else:
                    level = 1
                    title = line
                
                sections.append({
                    'title': title,
                    'level': level,
                    'line_number': i + 1
                })
        
        return sections
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格信息"""
        tables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 简单的表格检测（包含|字符的行）
            if '|' in line and line.count('|') >= 2:
                tables.append({
                    'content': line.strip(),
                    'line_number': i + 1
                })
        
        return tables
    
    def _extract_links(self, content: str) -> List[Dict[str, Any]]:
        """提取链接信息"""
        links = []
        
        # 查找URL
        url_pattern = r'https?://[^\s]+'
        for match in re.finditer(url_pattern, content):
            links.append({
                'url': match.group(),
                'position': match.start()
            })
        
        return links
    
    def _extract_user_stories(self, content: str) -> List[Dict[str, Any]]:
        """提取用户故事"""
        user_stories = []
        
        # 查找用户故事模式
        story_pattern = r'作为.*?，我希望.*?，以便.*?[。.]'
        for match in re.finditer(story_pattern, content):
            user_stories.append({
                'story': match.group(),
                'position': match.start()
            })
        
        return user_stories
