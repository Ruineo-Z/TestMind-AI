"""
文档解析API端点
专门负责文档解析功能，返回结构化的文档数据
"""
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.api.models.requests import (
    DocumentParseRequest, DocumentParseResponse, ErrorResponse,
    TestType, AIProvider, DocumentCategory
)
from app.requirements_parser.service import DocumentParsingService
from app.requirements_parser.models.document import DocumentType


router = APIRouter(prefix="/documents", tags=["documents"])


# 支持的文件格式配置
SUPPORTED_FORMATS = {
    "api_test": {
        "extensions": [".json", ".yaml", ".yml", ".md"],
        "description": "API文档格式：OpenAPI JSON/YAML, API Markdown"
    },
    "prompt_test": {
        "extensions": [".md", ".json", ".yaml", ".yml"],
        "description": "Prompt文档格式：Markdown, JSON, YAML"
    }
}


def validate_file_for_test_type(filename: str, test_type: TestType) -> bool:
    """
    验证文件格式是否适合指定的测试类型
    
    Args:
        filename: 文件名
        test_type: 测试类型
        
    Returns:
        bool: 是否支持
    """
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    supported_extensions = SUPPORTED_FORMATS.get(test_type.value, {}).get("extensions", [])
    return extension in supported_extensions


@router.post("/parse", response_model=DocumentParseResponse)
async def parse_document(
    file: UploadFile = File(...),
    test_type: TestType = Form(...),
    ai_provider: AIProvider = Form(default=AIProvider.GEMINI)
) -> DocumentParseResponse:
    """
    解析文档并返回结构化数据
    
    Args:
        file: 上传的文档文件
        test_type: 测试类型 (api_test, prompt_test)
        ai_provider: AI提供商 (gemini, openai, ollama, mock)
        
    Returns:
        DocumentParseResponse: 解析后的结构化文档数据
        
    Raises:
        HTTPException: 文件类型不支持或解析失败时抛出
    """
    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 验证文件格式是否适合测试类型
    if not validate_file_for_test_type(file.filename, test_type):
        supported_formats = SUPPORTED_FORMATS.get(test_type.value, {})
        raise HTTPException(
            status_code=400,
            detail=f"文件格式不适合{test_type.value}。{supported_formats.get('description', '')}"
        )
    
    # 读取文件内容
    try:
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="文件内容为空")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取文件失败: {str(e)}")
    
    # 创建临时文件
    temp_file_path = None
    try:
        # 根据文件类型创建临时文件
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # 创建解析服务
        parsing_service = DocumentParsingService(ai_provider=ai_provider.value)

        # 根据测试类型确定文档类型和处理方式
        if test_type == TestType.API_TEST:
            # API测试：让系统自动检测API文档格式
            doc_type = None
            extract_requirements = False
        elif test_type == TestType.PROMPT_TEST:
            # Prompt测试：按Prompt文档处理
            doc_type = DocumentType.PROMPT
            extract_requirements = False
        else:
            # 默认处理
            doc_type = None
            extract_requirements = False

        # 解析文档
        result = await parsing_service.parse_document(
            file_path=temp_file_path,
            document_type=doc_type,
            extract_requirements=extract_requirements
        )
        
        # 构建响应数据
        response_data = DocumentParseResponse(
            test_type=test_type,
            document=_build_document_info(result["document"]),
            document_category=DocumentCategory(result["document_category"]),
            metadata={
                "file_name": file.filename,
                "file_size": len(file_content),
                "ai_provider": ai_provider.value,
                "test_type": test_type.value,
                "extraction_accuracy": result.get("accuracy", 0.0),
                "processing_time": result.get("processing_time", 0.0)
            }
        )
        
        # 根据文档类型添加特定数据
        if "api_document" in result:
            response_data.api_document = _build_api_document_info(result["api_document"])
        
        if "prompt_document" in result:
            response_data.prompt_document = _build_prompt_document_info(result["prompt_document"])
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文档失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # 忽略清理错误


def _build_document_info(document) -> Dict[str, Any]:
    """构建文档基础信息"""
    return {
        "title": getattr(document, 'title', ''),
        "content": getattr(document, 'content', ''),
        "document_type": getattr(document, 'document_type', ''),
        "sections": getattr(document, 'sections', []),
        "tables": getattr(document, 'tables', []),
        "links": getattr(document, 'links', []),
        "user_stories": getattr(document, 'user_stories', [])
    }


def _build_api_document_info(api_doc) -> Dict[str, Any]:
    """构建API文档信息"""
    info = getattr(api_doc, 'info', None)
    return {
        "info": {
            "title": getattr(info, 'title', '') if info else '',
            "version": getattr(info, 'version', '') if info else '',
            "description": getattr(info, 'description', '') if info else ''
        },
        "servers": [
            {"url": getattr(server, 'url', ''), "description": getattr(server, 'description', '')}
            for server in getattr(api_doc, 'servers', [])
        ],
        "endpoints": [
            {
                "path": getattr(endpoint, 'path', ''),
                "method": getattr(endpoint, 'method', ''),
                "summary": getattr(endpoint, 'summary', ''),
                "description": getattr(endpoint, 'description', ''),
                "parameters": [
                    {
                        "name": getattr(param, 'name', ''),
                        "location": getattr(param, 'location', ''),
                        "type": getattr(param, 'type', ''),
                        "required": getattr(param, 'required', False),
                        "description": getattr(param, 'description', '')
                    }
                    for param in getattr(endpoint, 'parameters', [])
                ],
                "responses": {
                    status: {
                        "description": getattr(resp, 'description', ''),
                        "content_type": getattr(resp, 'content_type', '')
                    }
                    for status, resp in getattr(endpoint, 'responses', {}).items()
                }
            }
            for endpoint in getattr(api_doc, 'endpoints', [])
        ]
    }


def _build_prompt_document_info(prompt_doc) -> Dict[str, Any]:
    """构建Prompt文档信息"""
    return {
        "title": getattr(prompt_doc, 'title', ''),
        "description": getattr(prompt_doc, 'description', ''),
        "templates": [
            {
                "name": getattr(template, 'name', ''),
                "content": getattr(template, 'content', ''),
                "variables": getattr(template, 'variables', []),
                "description": getattr(template, 'description', '')
            }
            for template in getattr(prompt_doc, 'templates', [])
        ],
        "test_cases": [
            {
                "name": getattr(case, 'name', ''),
                "input": getattr(case, 'input', {}),
                "expected_output": getattr(case, 'expected_output', ''),
                "description": getattr(case, 'description', '')
            }
            for case in getattr(prompt_doc, 'test_cases', [])
        ]
    }


@router.get("/formats")
async def list_supported_formats() -> Dict[str, Any]:
    """
    获取支持的文件格式列表
    
    Returns:
        Dict: 支持的文件格式信息
    """
    return {
        "supported_formats": SUPPORTED_FORMATS,
        "test_types": [test_type.value for test_type in TestType]
    }
