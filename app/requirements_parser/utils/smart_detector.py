"""
智能文档类型检测器
结合规则检测和AI分析，提供更准确的文档类型识别
"""
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from app.requirements_parser.models.document import DocumentType
from app.requirements_parser.utils.format_detector import DocumentFormatDetector
from app.requirements_parser.extractors.langchain_extractor import LangChainExtractor, AIProvider


@dataclass
class DetectionResult:
    """检测结果"""
    document_type: DocumentType
    confidence: float  # 置信度 0-1
    method: str  # 检测方法：rule/ai/hybrid
    details: Dict[str, Any]  # 详细信息


class SmartDocumentDetector:
    """智能文档检测器"""
    
    def __init__(self, ai_provider: str = "gemini"):
        """
        初始化智能检测器
        
        Args:
            ai_provider: AI提供商
        """
        self.rule_detector = DocumentFormatDetector()
        self.ai_provider = ai_provider
        self.cache = {}  # 简单的内存缓存
        
        # 置信度阈值
        self.HIGH_CONFIDENCE = 0.8
        self.MEDIUM_CONFIDENCE = 0.5
        
        # AI分类提示词
        self.classification_prompt = """请分析以下文档内容，判断其类型。

文档内容：
{content}

请从以下类型中选择一个：
1. requirements - 产品需求文档（PRD），包含功能需求、用户故事、业务流程等
2. api - API接口文档，包含接口定义、参数说明、请求响应示例等
3. prompt - AI提示词文档，包含prompt模板、测试用例、角色定义等

分析要点：
- 查看文档的主要内容和结构
- 识别关键词汇和术语
- 理解文档的用途和目标

请只回答类型名称（requirements/api/prompt），不需要解释。"""

    def detect_document_type(self, content: str, filename: str) -> DetectionResult:
        """
        智能检测文档类型
        
        Args:
            content: 文档内容
            filename: 文件名
            
        Returns:
            DetectionResult: 检测结果
        """
        # 1. 生成内容hash用于缓存
        content_hash = self._get_content_hash(content)
        if content_hash in self.cache:
            return self.cache[content_hash]
        
        # 2. 规则检测
        rule_result = self._rule_detection(content, filename)
        
        # 3. 根据置信度决定是否使用AI
        if rule_result.confidence >= self.HIGH_CONFIDENCE:
            # 高置信度，直接使用规则结果
            result = rule_result
        elif rule_result.confidence >= self.MEDIUM_CONFIDENCE:
            # 中等置信度，AI辅助判断
            ai_result = self._ai_detection(content)
            result = self._combine_results(rule_result, ai_result)
        else:
            # 低置信度，主要依赖AI
            ai_result = self._ai_detection(content)
            if ai_result.confidence > rule_result.confidence:
                result = ai_result
            else:
                result = self._create_uncertain_result(rule_result, ai_result)
        
        # 4. 缓存结果
        self.cache[content_hash] = result
        return result
    
    def _rule_detection(self, content: str, filename: str) -> DetectionResult:
        """
        基于规则的检测
        
        Args:
            content: 文档内容
            filename: 文件名
            
        Returns:
            DetectionResult: 检测结果
        """
        # 使用现有的格式检测器
        doc_type = self.rule_detector.detect_format(content, filename)
        
        # 计算置信度
        confidence = self._calculate_rule_confidence(content, filename, doc_type)
        
        return DetectionResult(
            document_type=doc_type,
            confidence=confidence,
            method="rule",
            details={
                "filename": filename,
                "detected_patterns": self._get_detected_patterns(content, doc_type)
            }
        )
    
    def _ai_detection(self, content: str) -> DetectionResult:
        """
        基于AI的检测
        
        Args:
            content: 文档内容
            
        Returns:
            DetectionResult: 检测结果
        """
        try:
            # 截取内容前部分用于分析（避免token过多）
            analysis_content = content[:2000] if len(content) > 2000 else content
            
            # 构建提示词
            prompt = self.classification_prompt.format(content=analysis_content)
            
            # 调用AI分析
            extractor = LangChainExtractor(provider=AIProvider(self.ai_provider))
            
            # 这里需要一个简单的分类方法，暂时用同步方式
            # TODO: 实现专门的分类方法
            response = "requirements"  # 临时返回，实际需要调用AI
            
            # 解析AI响应
            doc_type = self._parse_ai_response(response)
            
            return DetectionResult(
                document_type=doc_type,
                confidence=0.85,  # AI检测的默认置信度
                method="ai",
                details={
                    "ai_provider": self.ai_provider,
                    "ai_response": response,
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            # AI检测失败，返回低置信度结果
            return DetectionResult(
                document_type=DocumentType.MARKDOWN,
                confidence=0.3,
                method="ai_failed",
                details={"error": str(e)}
            )
    
    def _calculate_rule_confidence(self, content: str, filename: str, doc_type: DocumentType) -> float:
        """
        计算规则检测的置信度
        
        Args:
            content: 文档内容
            filename: 文件名
            doc_type: 检测到的文档类型
            
        Returns:
            float: 置信度 0-1
        """
        confidence = 0.5  # 基础置信度
        
        # 文件扩展名匹配度
        if filename.endswith('.json') and doc_type == DocumentType.OPENAPI:
            confidence += 0.3
        elif filename.endswith('.md') and doc_type in [DocumentType.MARKDOWN, DocumentType.API_MARKDOWN]:
            confidence += 0.2
        
        # 内容特征匹配度
        content_lower = content.lower()
        
        if doc_type == DocumentType.OPENAPI:
            openapi_keywords = ['openapi', 'swagger', 'paths', 'components']
            matches = sum(1 for keyword in openapi_keywords if keyword in content_lower)
            confidence += min(matches * 0.1, 0.3)
        
        elif doc_type == DocumentType.API_MARKDOWN:
            api_patterns = ['get /', 'post /', 'request', 'response', 'status code']
            matches = sum(1 for pattern in api_patterns if pattern in content_lower)
            confidence += min(matches * 0.05, 0.2)
        
        elif doc_type == DocumentType.MARKDOWN:
            req_patterns = ['需求', '功能', '用户故事', 'requirement', 'feature']
            matches = sum(1 for pattern in req_patterns if pattern in content_lower)
            confidence += min(matches * 0.05, 0.2)
        
        return min(confidence, 1.0)
    
    def _parse_ai_response(self, response: str) -> DocumentType:
        """
        解析AI响应
        
        Args:
            response: AI响应内容
            
        Returns:
            DocumentType: 文档类型
        """
        response_lower = response.lower().strip()
        
        if 'api' in response_lower:
            return DocumentType.API_MARKDOWN
        elif 'prompt' in response_lower:
            return DocumentType.PROMPT
        elif 'requirements' in response_lower:
            return DocumentType.MARKDOWN
        else:
            return DocumentType.MARKDOWN  # 默认
    
    def _combine_results(self, rule_result: DetectionResult, ai_result: DetectionResult) -> DetectionResult:
        """
        组合规则和AI检测结果
        
        Args:
            rule_result: 规则检测结果
            ai_result: AI检测结果
            
        Returns:
            DetectionResult: 组合结果
        """
        # 如果两者一致，提高置信度
        if rule_result.document_type == ai_result.document_type:
            confidence = min((rule_result.confidence + ai_result.confidence) / 2 + 0.2, 1.0)
            return DetectionResult(
                document_type=rule_result.document_type,
                confidence=confidence,
                method="hybrid_consistent",
                details={
                    "rule_details": rule_result.details,
                    "ai_details": ai_result.details
                }
            )
        else:
            # 不一致，选择置信度更高的
            if ai_result.confidence > rule_result.confidence:
                return DetectionResult(
                    document_type=ai_result.document_type,
                    confidence=ai_result.confidence * 0.9,  # 略微降低置信度
                    method="hybrid_ai_preferred",
                    details={
                        "rule_result": rule_result.document_type,
                        "ai_result": ai_result.document_type,
                        "reason": "AI confidence higher"
                    }
                )
            else:
                return DetectionResult(
                    document_type=rule_result.document_type,
                    confidence=rule_result.confidence * 0.9,
                    method="hybrid_rule_preferred",
                    details={
                        "rule_result": rule_result.document_type,
                        "ai_result": ai_result.document_type,
                        "reason": "Rule confidence higher"
                    }
                )
    
    def _create_uncertain_result(self, rule_result: DetectionResult, ai_result: DetectionResult) -> DetectionResult:
        """
        创建不确定的检测结果
        
        Args:
            rule_result: 规则检测结果
            ai_result: AI检测结果
            
        Returns:
            DetectionResult: 不确定结果
        """
        return DetectionResult(
            document_type=rule_result.document_type,  # 默认使用规则结果
            confidence=0.4,  # 低置信度
            method="uncertain",
            details={
                "rule_result": rule_result.document_type,
                "ai_result": ai_result.document_type,
                "suggestion": "建议用户手动确认文档类型"
            }
        )
    
    def _get_detected_patterns(self, content: str, doc_type: DocumentType) -> list:
        """获取检测到的模式"""
        patterns = []
        content_lower = content.lower()
        
        if 'openapi' in content_lower:
            patterns.append('openapi_keyword')
        if 'swagger' in content_lower:
            patterns.append('swagger_keyword')
        if 'paths' in content_lower:
            patterns.append('paths_field')
        
        return patterns
    
    def _get_content_hash(self, content: str) -> str:
        """生成内容hash"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
