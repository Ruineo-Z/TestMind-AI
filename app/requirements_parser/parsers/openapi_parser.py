"""
OpenAPI文档解析器
解析OpenAPI 3.0和Swagger 2.0格式的API文档
"""
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.requirements_parser.parsers.base import BaseParser
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.api_document import (
    APIDocument, APIEndpoint, APIParameter, APIRequestBody, APIResponse,
    APIInfo, APIServer, HTTPMethod, ParameterLocation
)


class OpenAPIParser(BaseParser):
    """OpenAPI文档解析器"""
    
    def __init__(self):
        """初始化OpenAPI解析器"""
        super().__init__()
        self.supported_extensions = {'.json', '.yaml', '.yml'}
        
        # HTTP方法映射
        self.http_methods = {
            'get': HTTPMethod.GET,
            'post': HTTPMethod.POST,
            'put': HTTPMethod.PUT,
            'delete': HTTPMethod.DELETE,
            'patch': HTTPMethod.PATCH,
            'head': HTTPMethod.HEAD,
            'options': HTTPMethod.OPTIONS
        }
        
        # 参数位置映射
        self.parameter_locations = {
            'query': ParameterLocation.QUERY,
            'path': ParameterLocation.PATH,
            'header': ParameterLocation.HEADER,
            'cookie': ParameterLocation.COOKIE,
            'body': ParameterLocation.BODY
        }
    
    def parse(self, content: str, **kwargs) -> Document:
        """
        解析OpenAPI内容
        
        Args:
            content: OpenAPI文档内容（JSON或YAML字符串）
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        try:
            # 解析JSON或YAML
            if content.strip().startswith('{'):
                openapi_data = json.loads(content)
            else:
                openapi_data = yaml.safe_load(content)
            
            # 转换为APIDocument
            api_document = self._convert_to_api_document(openapi_data)
            
            # 创建Document对象
            document = Document(
                title=api_document.info.title,
                content=content,
                document_type=DocumentType.OPENAPI,
                **kwargs
            )
            
            # 将APIDocument作为额外数据存储
            document.api_document = api_document
            
            return document
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"OpenAPI文档格式错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"解析OpenAPI文档失败: {str(e)}")
    
    def parse_from_file(self, file_path: str, **kwargs) -> Document:
        """
        从文件解析OpenAPI文档
        
        Args:
            file_path: 文件路径
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加文件路径信息
            kwargs['file_path'] = file_path
            
            return self.parse(content, **kwargs)
            
        except FileNotFoundError:
            raise ValueError(f"文件不存在: {file_path}")
        except Exception as e:
            raise ValueError(f"读取文件失败: {str(e)}")
    
    def _convert_to_api_document(self, openapi_data: Dict[str, Any]) -> APIDocument:
        """
        将OpenAPI数据转换为APIDocument对象
        
        Args:
            openapi_data: OpenAPI原始数据
            
        Returns:
            APIDocument: 转换后的API文档对象
        """
        # 解析基本信息
        info = self._parse_info(openapi_data.get('info', {}))
        
        # 解析服务器信息
        servers = self._parse_servers(openapi_data.get('servers', []))
        
        # 解析API端点
        endpoints = self._parse_paths(openapi_data.get('paths', {}))
        
        # 确定源格式和版本
        if 'openapi' in openapi_data:
            source_format = 'openapi'
            source_version = openapi_data['openapi']
        elif 'swagger' in openapi_data:
            source_format = 'swagger'
            source_version = openapi_data['swagger']
        else:
            source_format = 'unknown'
            source_version = None
        
        return APIDocument(
            info=info,
            servers=servers,
            endpoints=endpoints,
            components=openapi_data.get('components'),
            security=openapi_data.get('security'),
            tags=openapi_data.get('tags'),
            external_docs=openapi_data.get('externalDocs'),
            source_format=source_format,
            source_version=source_version
        )
    
    def _parse_info(self, info_data: Dict[str, Any]) -> APIInfo:
        """解析API信息"""
        return APIInfo(
            title=info_data.get('title', 'Untitled API'),
            version=info_data.get('version', '1.0.0'),
            description=info_data.get('description'),
            terms_of_service=info_data.get('termsOfService'),
            contact=info_data.get('contact'),
            license=info_data.get('license')
        )
    
    def _parse_servers(self, servers_data: List[Dict[str, Any]]) -> List[APIServer]:
        """解析服务器信息"""
        servers = []
        for server_data in servers_data:
            server = APIServer(
                url=server_data.get('url', ''),
                description=server_data.get('description'),
                variables=server_data.get('variables')
            )
            servers.append(server)
        return servers
    
    def _parse_paths(self, paths_data: Dict[str, Any]) -> List[APIEndpoint]:
        """解析API路径"""
        endpoints = []
        
        for path, path_item in paths_data.items():
            if not isinstance(path_item, dict):
                continue
            
            # 解析每个HTTP方法
            for method, operation in path_item.items():
                if method.lower() not in self.http_methods:
                    continue  # 跳过非HTTP方法的字段
                
                if not isinstance(operation, dict):
                    continue
                
                endpoint = self._parse_operation(path, method.lower(), operation)
                endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_operation(self, path: str, method: str, operation: Dict[str, Any]) -> APIEndpoint:
        """解析单个操作"""
        # 解析参数
        parameters = self._parse_parameters(operation.get('parameters', []))
        
        # 解析请求体
        request_body = self._parse_request_body(operation.get('requestBody'))
        
        # 解析响应
        responses = self._parse_responses(operation.get('responses', {}))
        
        return APIEndpoint(
            path=path,
            method=self.http_methods[method],
            summary=operation.get('summary', ''),
            description=operation.get('description'),
            operation_id=operation.get('operationId'),
            tags=operation.get('tags'),
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            deprecated=operation.get('deprecated', False),
            security=operation.get('security')
        )
    
    def _parse_parameters(self, parameters_data: List[Dict[str, Any]]) -> List[APIParameter]:
        """解析参数列表"""
        parameters = []
        
        for param_data in parameters_data:
            if not isinstance(param_data, dict):
                continue
            
            # 处理参数位置
            location = param_data.get('in', 'query')
            if location not in self.parameter_locations:
                location = 'query'  # 默认为query参数
            
            # 处理参数类型
            param_type = 'string'  # 默认类型
            if 'schema' in param_data:
                param_type = param_data['schema'].get('type', 'string')
            elif 'type' in param_data:  # Swagger 2.0格式
                param_type = param_data['type']
            
            parameter = APIParameter(
                name=param_data.get('name', ''),
                location=self.parameter_locations[location],
                type=param_type,
                required=param_data.get('required', False),
                description=param_data.get('description'),
                example=param_data.get('example'),
                default=param_data.get('default'),
                enum=param_data.get('enum'),
                format=param_data.get('format')
            )
            parameters.append(parameter)
        
        return parameters
    
    def _parse_request_body(self, request_body_data: Optional[Dict[str, Any]]) -> Optional[APIRequestBody]:
        """解析请求体"""
        if not request_body_data:
            return None
        
        # 获取第一个content类型
        content = request_body_data.get('content', {})
        if not content:
            return None
        
        # 通常使用application/json
        content_type = 'application/json'
        schema = {}
        
        for ct, ct_data in content.items():
            content_type = ct
            schema = ct_data.get('schema', {})
            break
        
        return APIRequestBody(
            content_type=content_type,
            body_schema=schema,
            required=request_body_data.get('required', True),
            description=request_body_data.get('description')
        )
    
    def _parse_responses(self, responses_data: Dict[str, Any]) -> Dict[str, APIResponse]:
        """解析响应定义"""
        responses = {}
        
        for status_code, response_data in responses_data.items():
            if not isinstance(response_data, dict):
                continue
            
            # 获取响应内容
            content = response_data.get('content', {})
            content_type = 'application/json'
            schema = {}
            
            if content:
                for ct, ct_data in content.items():
                    content_type = ct
                    schema = ct_data.get('schema', {})
                    break
            
            response = APIResponse(
                status_code=str(status_code),
                description=response_data.get('description', ''),
                content_type=content_type,
                response_schema=schema,
                examples=response_data.get('examples')
            )
            responses[str(status_code)] = response
        
        return responses
