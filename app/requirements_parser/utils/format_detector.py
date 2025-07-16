"""
文档格式检测器
自动检测上传文档的类型和格式，支持API文档、Prompt文档等多种格式
"""
import json
import yaml
import re
from typing import Dict, Optional, Any
from pathlib import Path

from app.requirements_parser.models.document import DocumentType


class DocumentFormatDetector:
    """文档格式检测器"""
    
    def __init__(self):
        """初始化格式检测器"""
        # OpenAPI关键字
        self.openapi_keywords = [
            "openapi", "swagger", "paths", "components", "info", "servers"
        ]
        
        # Prompt文档关键字
        self.prompt_keywords = [
            "prompts", "prompt_template", "test_cases", "scenarios", "evaluation"
        ]
        
        # API文档的Markdown特征
        self.api_markdown_patterns = [
            r"##?\s*(GET|POST|PUT|DELETE|PATCH)\s+/",  # HTTP方法和路径
            r"###?\s*(Request|Response|Parameters)",    # API文档章节
            r"```\s*(json|yaml|curl)",                  # 代码块
            r"Status Code:\s*\d{3}",                    # 状态码
        ]
        
        # Prompt文档的Markdown特征
        self.prompt_markdown_patterns = [
            r"##?\s*(Prompt|Template|Test Case)",       # Prompt文档章节
            r"Role:\s*(system|user|assistant)",         # 角色定义
            r"```\s*(prompt|template)",                 # Prompt代码块
            r"Input:|Output:|Expected:",                # 输入输出
        ]
    
    def detect_format(self, content: str, filename: str) -> DocumentType:
        """
        检测文档格式
        
        Args:
            content: 文档内容
            filename: 文件名
            
        Returns:
            DocumentType: 检测到的文档类型
        """
        # 1. 根据文件扩展名初步判断
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        # 2. 根据内容进行精确检测
        if extension in ['.json', '.yaml', '.yml']:
            return self._detect_structured_format(content, extension)
        elif extension in ['.md', '.markdown']:
            return self._detect_markdown_format(content)
        else:
            # 其他格式按现有逻辑处理
            return self._get_default_type_by_extension(extension)
    
    def _detect_structured_format(self, content: str, extension: str) -> DocumentType:
        """
        检测结构化文档格式（JSON/YAML）
        
        Args:
            content: 文档内容
            extension: 文件扩展名
            
        Returns:
            DocumentType: 检测到的文档类型
        """
        try:
            # 解析JSON/YAML内容
            if extension == '.json':
                data = json.loads(content)
            else:  # .yaml or .yml
                data = yaml.safe_load(content)
            
            if not isinstance(data, dict):
                return DocumentType.TXT
            
            # 检测OpenAPI/Swagger格式
            if self._is_openapi_format(data):
                return DocumentType.OPENAPI
            
            # 检测Prompt文档格式
            if self._is_prompt_format(data):
                return DocumentType.PROMPT
            
            # 默认返回OpenAPI（假设JSON/YAML主要用于API文档）
            return DocumentType.OPENAPI
            
        except (json.JSONDecodeError, yaml.YAMLError):
            # 解析失败，返回文本格式
            return DocumentType.TXT
    
    def _detect_markdown_format(self, content: str) -> DocumentType:
        """
        检测Markdown文档格式
        
        Args:
            content: Markdown内容
            
        Returns:
            DocumentType: 检测到的文档类型
        """
        content_lower = content.lower()
        
        # 检测API文档特征
        api_score = self._calculate_pattern_score(content, self.api_markdown_patterns)
        
        # 检测Prompt文档特征
        prompt_score = self._calculate_pattern_score(content, self.prompt_markdown_patterns)
        
        # 根据得分判断类型
        if api_score > prompt_score and api_score > 0:
            return DocumentType.API_MARKDOWN
        elif prompt_score > 0:
            return DocumentType.PROMPT
        else:
            # 默认为传统需求文档
            return DocumentType.MARKDOWN
    
    def _is_openapi_format(self, data: Dict[str, Any]) -> bool:
        """
        检测是否为OpenAPI格式
        
        Args:
            data: 解析后的数据
            
        Returns:
            bool: 是否为OpenAPI格式
        """
        # 检查OpenAPI 3.x
        if "openapi" in data:
            return True
        
        # 检查Swagger 2.0
        if "swagger" in data and data.get("swagger", "").startswith("2."):
            return True
        
        # 检查必要的字段
        required_fields = ["info", "paths"]
        if all(field in data for field in required_fields):
            return True
        
        # 检查关键字出现次数
        keyword_count = sum(1 for keyword in self.openapi_keywords if keyword in data)
        return keyword_count >= 3
    
    def _is_prompt_format(self, data: Dict[str, Any]) -> bool:
        """
        检测是否为Prompt文档格式
        
        Args:
            data: 解析后的数据
            
        Returns:
            bool: 是否为Prompt文档格式
        """
        # 检查Prompt文档的关键字段
        prompt_fields = ["prompts", "prompt_templates", "test_cases"]
        if any(field in data for field in prompt_fields):
            return True
        
        # 检查关键字出现次数
        keyword_count = sum(1 for keyword in self.prompt_keywords if keyword in str(data))
        return keyword_count >= 2
    
    def _calculate_pattern_score(self, content: str, patterns: list) -> int:
        """
        计算模式匹配得分
        
        Args:
            content: 文档内容
            patterns: 正则表达式模式列表
            
        Returns:
            int: 匹配得分
        """
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            score += len(matches)
        return score
    
    def _get_default_type_by_extension(self, extension: str) -> DocumentType:
        """
        根据扩展名获取默认文档类型
        
        Args:
            extension: 文件扩展名
            
        Returns:
            DocumentType: 文档类型
        """
        extension_mapping = {
            ".md": DocumentType.MARKDOWN,
            ".markdown": DocumentType.MARKDOWN,
            ".pdf": DocumentType.PDF,
            ".doc": DocumentType.WORD,
            ".docx": DocumentType.WORD,
            ".txt": DocumentType.TXT,
        }
        return extension_mapping.get(extension, DocumentType.TXT)
    
    def get_format_info(self, content: str, filename: str) -> Dict[str, Any]:
        """
        获取详细的格式信息
        
        Args:
            content: 文档内容
            filename: 文件名
            
        Returns:
            Dict: 格式信息
        """
        detected_type = self.detect_format(content, filename)
        
        info = {
            "detected_type": detected_type,
            "filename": filename,
            "file_extension": Path(filename).suffix.lower(),
            "content_length": len(content),
            "confidence": self._calculate_confidence(content, detected_type)
        }
        
        # 添加特定格式的额外信息
        if detected_type in [DocumentType.OPENAPI, DocumentType.SWAGGER]:
            info.update(self._get_api_format_info(content))
        elif detected_type == DocumentType.PROMPT:
            info.update(self._get_prompt_format_info(content))
        
        return info
    
    def _calculate_confidence(self, content: str, detected_type: DocumentType) -> float:
        """
        计算检测置信度
        
        Args:
            content: 文档内容
            detected_type: 检测到的类型
            
        Returns:
            float: 置信度 (0.0-1.0)
        """
        # 简单的置信度计算逻辑
        if detected_type in [DocumentType.OPENAPI, DocumentType.SWAGGER]:
            try:
                data = json.loads(content) if content.strip().startswith('{') else yaml.safe_load(content)
                if self._is_openapi_format(data):
                    return 0.9
                else:
                    return 0.6
            except:
                return 0.3
        elif detected_type == DocumentType.API_MARKDOWN:
            score = self._calculate_pattern_score(content, self.api_markdown_patterns)
            return min(score * 0.1, 1.0)
        elif detected_type == DocumentType.PROMPT:
            score = self._calculate_pattern_score(content, self.prompt_markdown_patterns)
            return min(score * 0.1, 1.0)
        else:
            return 0.8  # 传统格式的默认置信度
    
    def _get_api_format_info(self, content: str) -> Dict[str, Any]:
        """获取API格式的额外信息"""
        try:
            data = json.loads(content) if content.strip().startswith('{') else yaml.safe_load(content)
            return {
                "api_version": data.get("openapi") or data.get("swagger"),
                "api_title": data.get("info", {}).get("title"),
                "paths_count": len(data.get("paths", {})),
                "has_components": "components" in data
            }
        except:
            return {}
    
    def _get_prompt_format_info(self, content: str) -> Dict[str, Any]:
        """获取Prompt格式的额外信息"""
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
            elif content.strip().startswith('---'):
                data = yaml.safe_load(content)
            else:
                # Markdown格式
                return {
                    "format": "markdown",
                    "prompt_count": len(re.findall(r"##?\s*Prompt", content, re.IGNORECASE)),
                    "test_case_count": len(re.findall(r"##?\s*Test Case", content, re.IGNORECASE))
                }
            
            return {
                "format": "structured",
                "prompt_count": len(data.get("prompts", [])),
                "test_case_count": len(data.get("test_cases", []))
            }
        except:
            return {}
