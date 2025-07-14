"""
基础文档解析器
定义所有解析器的通用接口和基础功能
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

from app.requirements_parser.models.document import Document, DocumentType

class BaseParser(ABC):
    """文档解析器基类"""
    
    def __init__(self):
        """初始化解析器"""
        self.supported_extensions = set()
    
    @abstractmethod
    def parse(self, content: str, **kwargs) -> Document:
        """
        解析文档内容
        
        Args:
            content: 文档内容字符串
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
            
        Raises:
            ValueError: 内容无效时抛出
        """
        pass
    
    def parse_from_string(self, content: str, file_path: Optional[str] = None, **kwargs) -> Document:
        """
        从字符串解析文档
        
        Args:
            content: 文档内容
            file_path: 文件路径（可选）
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        document = self.parse(content, **kwargs)
        
        if file_path:
            document.file_path = file_path
            
        return document
    
    def parse_from_file(self, file_path: str, encoding: str = "utf-8", **kwargs) -> Document:
        """
        从文件解析文档
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
            
        Raises:
            FileNotFoundError: 文件不存在时抛出
            UnicodeDecodeError: 编码错误时抛出
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"路径不是文件: {file_path}")
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end,
                f"无法使用编码 {encoding} 读取文件 {file_path}: {e.reason}"
            )
        
        document = self.parse(content, **kwargs)
        document.file_path = str(path)
        
        # 设置文件元数据
        if document.metadata:
            document.metadata.file_size = path.stat().st_size
            document.metadata.created_at = path.stat().st_ctime
            document.metadata.modified_at = path.stat().st_mtime
            document.metadata.encoding = encoding
        
        return document
    
    def can_parse(self, file_path: str) -> bool:
        """
        检查是否可以解析指定文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否可以解析
        """
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def validate_content(self, content: str) -> None:
        """
        验证内容有效性
        
        Args:
            content: 文档内容
            
        Raises:
            ValueError: 内容无效时抛出
        """
        if content is None:
            raise ValueError("文档内容不能为None")
        
        if not isinstance(content, str):
            raise ValueError("文档内容必须是字符串")
        
        if not content.strip():
            raise ValueError("文档内容不能为空")
    
    def extract_title(self, content: str) -> str:
        """
        从内容中提取标题（子类可重写）
        
        Args:
            content: 文档内容
            
        Returns:
            str: 提取的标题
        """
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # 移除可能的标记符号
                title = line.lstrip('#').lstrip('*').lstrip('-').strip()
                if title:
                    return title
        
        return "未命名文档"
