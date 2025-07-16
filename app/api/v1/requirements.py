"""
文档解析API端点
提供多种文档类型的解析功能：需求文档、API文档、Prompt文档等
"""
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.requirements_parser.service import DocumentParsingService
from app.requirements_parser.models.document import DocumentType


router = APIRouter(prefix="/requirements", tags=["requirements"])


# 支持的文件格式配置
SUPPORTED_FORMATS = {
    "markdown": {
        "extensions": [".md", ".markdown", ".mdown", ".mkd"],
        "mime_types": ["text/markdown", "text/x-markdown"],
        "description": "Markdown格式文档（需求文档、API文档、Prompt文档）"
    },
    "pdf": {
        "extensions": [".pdf"],
        "mime_types": ["application/pdf"],
        "description": "PDF格式文档（需求文档）"
    },
    "word": {
        "extensions": [".docx", ".doc"],
        "mime_types": [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ],
        "description": "Microsoft Word文档（需求文档）"
    },
    "openapi": {
        "extensions": [".json", ".yaml", ".yml"],
        "mime_types": ["application/json", "application/x-yaml", "text/yaml"],
        "description": "OpenAPI/Swagger格式API文档"
    }
}


def _get_file_type(filename: str) -> Optional[str]:
    """
    根据文件名确定文件类型
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件类型，如果不支持则返回None
    """
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    for format_name, format_info in SUPPORTED_FORMATS.items():
        if extension in format_info["extensions"]:
            return format_name
    
    return None


@router.post("/parse")
async def parse_document(
    file: UploadFile = File(...),
    test_type: str = Form(...),
    ai_provider: str = Form(default="gemini"),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    解析文档并生成测试用例

    Args:
        file: 上传的文档文件
        test_type: 测试类型 (api_test, prompt_test) - 必填
        ai_provider: AI提供商 (openai, gemini, ollama, mock)
        background_tasks: 后台任务

    Returns:
        Dict: 解析结果，包含文档信息和测试相关数据

    Raises:
        HTTPException: 文件类型不支持或解析失败时抛出
    """
    # 验证测试类型
    valid_test_types = ["api_test", "prompt_test"]
    if test_type not in valid_test_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的测试类型。支持的类型: {', '.join(valid_test_types)}"
        )

    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 检查文件类型
    file_type = _get_file_type(file.filename)
    if not file_type:
        supported_exts = []
        for format_info in SUPPORTED_FORMATS.values():
            supported_exts.extend(format_info["extensions"])
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。支持的格式: {', '.join(supported_exts)}"
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
        parsing_service = DocumentParsingService(ai_provider=ai_provider)

        # 根据测试类型确定文档类型和处理方式
        if test_type == "api_test":
            # API测试：优先检测OpenAPI格式，否则按API Markdown处理
            doc_type = None  # 让系统自动检测API文档格式
            extract_requirements = False  # API测试不需要提取需求
        elif test_type == "prompt_test":
            # Prompt测试：按Prompt文档处理
            doc_type = DocumentType.PROMPT
            extract_requirements = False  # Prompt测试不需要提取需求
        else:
            # 默认处理
            doc_type = None
            extract_requirements = True

        # 解析文档
        result = await parsing_service.parse_document(
            file_path=temp_file_path,
            document_type=doc_type,
            extract_requirements=extract_requirements
        )
        
        # 构建响应（支持多种测试类型）
        response_data = {
            "test_type": test_type,
            "document": {
                "title": result["document"].title,
                "content": result["document"].content,
                "document_type": result["document"].document_type,
                "sections": result["document"].sections,
                "tables": result["document"].tables,
                "links": result["document"].links,
                "user_stories": result["document"].user_stories
            },
            "document_category": result["document_category"],
            "metadata": {
                "file_name": file.filename,
                "file_type": file_type,
                "file_size": len(file_content),
                "ai_provider": ai_provider,
                "test_type": test_type,
                "extraction_accuracy": result.get("accuracy", 0.0),
                "processing_time": result.get("processing_time", 0.0)
            }
        }

        # 根据文档类型添加特定数据
        if "requirements" in result:
            response_data["requirements"] = [
                {
                    "id": req.id,
                    "title": req.title,
                    "description": req.description,
                    "type": req.type,
                    "priority": req.priority,
                    "acceptance_criteria": req.acceptance_criteria,
                    "source_document": req.source_document,
                    "extracted_by": req.extracted_by
                }
                for req in result["requirements"]
            ]

        if "api_document" in result:
            api_doc = result["api_document"]
            response_data["api_document"] = {
                "info": {
                    "title": api_doc.info.title,
                    "version": api_doc.info.version,
                    "description": api_doc.info.description
                },
                "servers": [
                    {"url": server.url, "description": server.description}
                    for server in api_doc.servers
                ],
                "endpoints": [
                    {
                        "path": endpoint.path,
                        "method": endpoint.method,
                        "summary": endpoint.summary,
                        "description": endpoint.description,
                        "parameters": [
                            {
                                "name": param.name,
                                "location": param.location,
                                "type": param.type,
                                "required": param.required,
                                "description": param.description
                            }
                            for param in endpoint.parameters
                        ],
                        "responses": {
                            status: {
                                "description": resp.description,
                                "content_type": resp.content_type
                            }
                            for status, resp in endpoint.responses.items()
                        }
                    }
                    for endpoint in api_doc.endpoints
                ]
            }

        if "prompt_document" in result:
            prompt_doc = result["prompt_document"]
            response_data["prompt_document"] = {
                "title": prompt_doc.title,
                "description": prompt_doc.description,
                "templates": [
                    {
                        "name": template.name,
                        "content": template.content,
                        "variables": template.variables,
                        "description": template.description
                    }
                    for template in prompt_doc.templates
                ],
                "test_cases": [
                    {
                        "name": case.name,
                        "input": case.input,
                        "expected_output": case.expected_output,
                        "description": case.description
                    }
                    for case in prompt_doc.test_cases
                ]
            }
        
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


@router.get("/parse/status/{task_id}")
async def get_parse_status(task_id: str) -> Dict[str, Any]:
    """
    获取解析任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 任务状态信息
        
    Raises:
        HTTPException: 任务不存在时抛出
    """
    # TODO: 实现任务状态查询逻辑
    # 这里暂时返回404，表示任务不存在
    raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")


@router.get("/formats")
async def list_supported_formats() -> Dict[str, Any]:
    """
    获取支持的文件格式列表
    
    Returns:
        Dict: 支持的文件格式信息
    """
    return {
        "supported_formats": SUPPORTED_FORMATS,
        "total_formats": len(SUPPORTED_FORMATS)
    }
