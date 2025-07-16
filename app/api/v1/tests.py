"""
AI驱动的测试用例生成API端点
Sprint3核心功能：利用AI能力实现测试自动化
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.api.models.requests import (
    TestGenerateRequest, TestGenerateResponse, TaskStatusResponse,
    TestType, AIProvider, TaskStatus, GeneratedTestCase
)
from app.test_case_generator.service import AITestCaseGenerationService
from app.requirements_parser.models.api_document import APIDocument


router = APIRouter(prefix="/tests", tags=["tests"])


# 简单的内存任务存储（生产环境应使用数据库）
task_storage: Dict[str, Dict[str, Any]] = {}


@router.post("/generate", response_model=TestGenerateResponse)
async def generate_test_cases(
    request: TestGenerateRequest,
    background_tasks: BackgroundTasks
) -> TestGenerateResponse:
    """
    AI驱动的测试用例生成

    这是Sprint3的核心功能：利用AI能力分析API文档并自动生成pytest测试用例

    Args:
        request: 测试生成请求，包含API文档数据和生成配置
        background_tasks: 后台任务

    Returns:
        TestGenerateResponse: 生成的测试用例和pytest代码

    Raises:
        HTTPException: AI生成失败或参数错误时抛出
    """
    try:
        # 验证请求参数
        if not request.document_data:
            raise HTTPException(
                status_code=400,
                detail="document_data不能为空，请先使用/documents/parse解析API文档"
            )

        # 根据测试类型使用AI生成测试用例
        if request.test_type == TestType.API_TEST:
            return await _generate_ai_api_tests(request)
        elif request.test_type == TestType.PROMPT_TEST:
            return await _generate_ai_prompt_tests(request)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的测试类型: {request.test_type}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI测试用例生成失败: {str(e)}")


@router.post("/generate-async")
async def generate_test_cases_async(
    request: TestGenerateRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    异步生成测试用例
    
    Args:
        request: 测试生成请求
        background_tasks: 后台任务
        
    Returns:
        Dict: 包含任务ID的响应
    """
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建任务记录
    task_storage[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "progress": 0.0,
        "message": "任务已创建，等待处理",
        "result": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    # 添加后台任务
    background_tasks.add_task(_process_test_generation, task_id, request)
    
    return {"task_id": task_id, "message": "测试用例生成任务已启动"}


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        TaskStatusResponse: 任务状态信息
        
    Raises:
        HTTPException: 任务不存在时抛出
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    task_data = task_storage[task_id]
    return TaskStatusResponse(**task_data)


@router.get("/capabilities")
async def get_generation_capabilities() -> Dict[str, Any]:
    """
    获取AI测试生成能力信息

    Returns:
        Dict: 支持的功能和配置选项
    """
    return {
        "ai_providers": [provider.value for provider in AIProvider],
        "test_frameworks": ["pytest", "unittest"],
        "test_types": {
            "positive": "正向测试 - 验证API正常功能",
            "negative": "负向测试 - 验证错误处理",
            "boundary": "边界测试 - 验证边界条件"
        },
        "supported_api_formats": [
            "OpenAPI 3.0 (JSON/YAML)",
            "Swagger 2.0 (JSON/YAML)",
            "API Markdown"
        ],
        "ai_capabilities": {
            "api_analysis": "智能分析API结构和复杂度",
            "test_strategy": "基于API特征生成测试策略",
            "test_generation": "自动生成具体测试用例",
            "code_generation": "生成可执行的pytest代码"
        },
        "quality_features": {
            "real_data": "使用真实测试数据，避免mock",
            "chinese_comments": "生成中文注释的代码",
            "httpx_client": "使用httpx作为HTTP客户端",
            "async_support": "支持异步测试执行"
        }
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    AI测试生成服务健康检查

    Returns:
        Dict: 服务状态信息
    """
    return {
        "status": "healthy",
        "service": "AI Test Case Generation Service",
        "version": "1.0.0",
        "description": "利用AI能力实现测试自动化"
    }


async def _generate_ai_api_tests(request: TestGenerateRequest) -> TestGenerateResponse:
    """
    使用AI生成API测试用例

    Args:
        request: 测试生成请求

    Returns:
        TestGenerateResponse: AI生成的API测试用例
    """
    # 提取API文档对象
    api_document = _extract_api_document(request.document_data)
    if not api_document:
        raise HTTPException(
            status_code=400,
            detail="无法从document_data中提取API文档，请确保文档类型为API文档"
        )

    # 创建AI测试生成服务
    ai_service = AITestCaseGenerationService(ai_provider=request.ai_provider.value)

    # 使用AI生成测试套件
    generation_result = await ai_service.generate_test_suite(
        api_document=api_document,
        include_positive=request.include_positive_tests,
        include_negative=request.include_negative_tests,
        include_boundary=request.include_boundary_tests,
        test_framework=request.test_framework
    )

    # 构建响应
    test_suite = generation_result["test_suite"]

    return TestGenerateResponse(
        test_type=request.test_type,
        test_cases=[],  # 简化响应，主要返回文件内容
        test_file_content=generation_result["test_file_content"],
        total_tests=test_suite.total_tests,
        positive_tests=test_suite.positive_tests,
        negative_tests=test_suite.negative_tests,
        boundary_tests=test_suite.boundary_tests,
        metadata={
            "ai_provider": request.ai_provider.value,
            "generation_time": generation_result["generation_metadata"]["generation_time"],
            "processing_time": generation_result["processing_time"],
            "api_title": api_document.info.title,
            "api_version": api_document.info.version,
            "endpoints_analyzed": generation_result["generation_metadata"]["api_endpoints_count"],
            "ai_analysis": generation_result.get("api_analysis", {}),
            "test_strategy": generation_result.get("test_strategy", {})
        }
    )


def _extract_api_document(document_data: Dict[str, Any]) -> APIDocument:
    """
    从文档数据中提取API文档对象

    Args:
        document_data: 来自Sprint2解析的文档数据

    Returns:
        APIDocument: API文档对象，如果不是API文档则返回None
    """
    try:
        # 检查是否包含API文档数据
        if "api_document" not in document_data:
            return None

        api_data = document_data["api_document"]

        # 适配Sprint2解析的数据结构到APIDocument模型
        adapted_data = _adapt_api_document_data(api_data)

        return APIDocument(**adapted_data)

    except Exception as e:
        raise ValueError(f"解析API文档数据失败: {str(e)}")


def _adapt_api_document_data(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    适配Sprint2解析的API数据结构到APIDocument模型

    Args:
        api_data: Sprint2解析的API数据

    Returns:
        Dict: 适配后的数据结构
    """
    adapted = api_data.copy()

    # 添加必需的source_format字段
    adapted["source_format"] = "openapi"

    # 适配endpoints中的responses结构
    if "endpoints" in adapted:
        for endpoint in adapted["endpoints"]:
            if "responses" in endpoint:
                # 转换responses格式：从 {"200": {...}} 到 {"200": {"status_code": "200", ...}}
                adapted_responses = {}
                for status_code, response_data in endpoint["responses"].items():
                    adapted_response = response_data.copy()
                    adapted_response["status_code"] = status_code
                    adapted_responses[status_code] = adapted_response
                endpoint["responses"] = adapted_responses

    return adapted


async def _generate_ai_prompt_tests(request: TestGenerateRequest) -> TestGenerateResponse:
    """
    生成Prompt测试用例
    
    Args:
        request: 测试生成请求
        
    Returns:
        TestGenerateResponse: 生成的Prompt测试用例
    """
    # 检查是否有Prompt文档数据
    prompt_document = request.document_data.get("prompt_document")
    if not prompt_document:
        raise HTTPException(status_code=400, detail="缺少Prompt文档数据")
    
    test_cases = []
    
    # 基于Prompt模板生成测试用例
    templates = prompt_document.get("templates", [])
    for template in templates:
        test_case = _generate_prompt_test_case(template)
        test_cases.append(test_case)
    
    # 生成完整的测试文件内容
    test_file_content = _build_prompt_test_file(test_cases, prompt_document)
    
    return TestGenerateResponse(
        test_type=request.test_type,
        test_cases=test_cases,
        test_file_content=test_file_content,
        total_tests=len(test_cases),
        positive_tests=len(test_cases),  # Prompt测试主要是正向测试
        negative_tests=0,
        boundary_tests=0,
        metadata={
            "ai_provider": request.ai_provider,
            "test_framework": request.test_framework,
            "templates_count": len(templates),
            "generated_at": datetime.now().isoformat()
        }
    )


def _generate_positive_api_test(endpoint: Dict[str, Any]) -> GeneratedTestCase:
    """生成正向API测试用例"""
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "/")
    summary = endpoint.get("summary", "")
    
    test_name = f"test_{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}_success"
    
    code = f'''def {test_name}():
    """测试{summary} - 正向用例"""
    response = requests.{method.lower()}("{path}")
    assert response.status_code == 200
    # TODO: 添加更多断言
'''
    
    return GeneratedTestCase(
        name=test_name,
        description=f"测试{summary} - 正向用例",
        test_type="positive",
        code=code,
        dependencies=["requests", "pytest"]
    )


def _generate_negative_api_test(endpoint: Dict[str, Any]) -> GeneratedTestCase:
    """生成负向API测试用例"""
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "/")
    summary = endpoint.get("summary", "")
    
    test_name = f"test_{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}_invalid_params"
    
    code = f'''def {test_name}():
    """测试{summary} - 负向用例（无效参数）"""
    response = requests.{method.lower()}("{path}", params={{"invalid": "data"}})
    assert response.status_code in [400, 422]
    # TODO: 添加更多断言
'''
    
    return GeneratedTestCase(
        name=test_name,
        description=f"测试{summary} - 负向用例",
        test_type="negative",
        code=code,
        dependencies=["requests", "pytest"]
    )


def _generate_boundary_api_test(endpoint: Dict[str, Any]) -> GeneratedTestCase:
    """生成边界API测试用例"""
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "/")
    summary = endpoint.get("summary", "")
    
    test_name = f"test_{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}_boundary"
    
    code = f'''def {test_name}():
    """测试{summary} - 边界用例"""
    # 测试边界值
    response = requests.{method.lower()}("{path}")
    assert response.status_code in [200, 400]
    # TODO: 添加边界值测试逻辑
'''
    
    return GeneratedTestCase(
        name=test_name,
        description=f"测试{summary} - 边界用例",
        test_type="boundary",
        code=code,
        dependencies=["requests", "pytest"]
    )


def _generate_prompt_test_case(template: Dict[str, Any]) -> GeneratedTestCase:
    """生成Prompt测试用例"""
    name = template.get("name", "unknown")
    content = template.get("content", "")
    
    test_name = f"test_prompt_{name.replace(' ', '_').lower()}"
    
    code = f'''def {test_name}():
    """测试Prompt模板: {name}"""
    prompt = """{content}"""
    
    # TODO: 调用AI模型测试
    # response = ai_model.generate(prompt)
    # assert response is not None
    # assert len(response) > 0
    pass
'''
    
    return GeneratedTestCase(
        name=test_name,
        description=f"测试Prompt模板: {name}",
        test_type="positive",
        code=code,
        dependencies=["pytest"]
    )


def _build_api_test_file(test_cases: list, api_document: Dict[str, Any]) -> str:
    """构建完整的API测试文件"""
    api_title = api_document.get("info", {}).get("title", "API")
    
    header = f'''"""
{api_title} 自动生成测试用例
生成时间: {datetime.now().isoformat()}
"""
import requests
import pytest


class TestAPI:
    """API测试类"""
    
    BASE_URL = "https://api.example.com"  # TODO: 配置实际的API地址

'''
    
    test_methods = []
    for test_case in test_cases:
        # 缩进测试方法
        indented_code = "    " + test_case.code.replace("\n", "\n    ")
        test_methods.append(indented_code)
    
    return header + "\n".join(test_methods)


def _build_prompt_test_file(test_cases: list, prompt_document: Dict[str, Any]) -> str:
    """构建完整的Prompt测试文件"""
    title = prompt_document.get("title", "Prompt")
    
    header = f'''"""
{title} 自动生成测试用例
生成时间: {datetime.now().isoformat()}
"""
import pytest


class TestPrompts:
    """Prompt测试类"""

'''
    
    test_methods = []
    for test_case in test_cases:
        # 缩进测试方法
        indented_code = "    " + test_case.code.replace("\n", "\n    ")
        test_methods.append(indented_code)
    
    return header + "\n".join(test_methods)


async def _process_test_generation(task_id: str, request: TestGenerateRequest):
    """后台处理测试生成任务"""
    try:
        # 更新任务状态
        task_storage[task_id]["status"] = TaskStatus.PROCESSING
        task_storage[task_id]["progress"] = 10.0
        task_storage[task_id]["message"] = "开始生成测试用例"
        task_storage[task_id]["updated_at"] = datetime.now().isoformat()
        
        # 执行生成逻辑
        if request.test_type == TestType.API_TEST:
            result = await _generate_api_tests(request)
        else:
            result = await _generate_prompt_tests(request)
        
        # 更新完成状态
        task_storage[task_id]["status"] = TaskStatus.COMPLETED
        task_storage[task_id]["progress"] = 100.0
        task_storage[task_id]["message"] = "测试用例生成完成"
        task_storage[task_id]["result"] = result.dict()
        task_storage[task_id]["updated_at"] = datetime.now().isoformat()
        
    except Exception as e:
        # 更新失败状态
        task_storage[task_id]["status"] = TaskStatus.FAILED
        task_storage[task_id]["message"] = f"生成失败: {str(e)}"
        task_storage[task_id]["updated_at"] = datetime.now().isoformat()
