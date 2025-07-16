"""
Prompt文档解析器
解析Prompt设计文档，支持Markdown、JSON、YAML格式
"""
import json
import yaml
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.requirements_parser.parsers.base import BaseParser
from app.requirements_parser.models.document import Document, DocumentType
from app.requirements_parser.models.prompt_document import (
    PromptDocument, PromptTemplate, PromptTestCase, PromptScenario,
    PromptVariable, PromptEvaluation, PromptType, PromptRole, TestCaseType
)


class PromptParser(BaseParser):
    """Prompt文档解析器"""
    
    def __init__(self):
        """初始化Prompt解析器"""
        super().__init__()
        self.supported_extensions = {'.md', '.markdown', '.json', '.yaml', '.yml'}
        
        # Prompt类型映射
        self.prompt_types = {
            'system': PromptType.SYSTEM,
            'user': PromptType.USER,
            'assistant': PromptType.ASSISTANT,
            'function': PromptType.FUNCTION,
            'template': PromptType.TEMPLATE
        }
        
        # 测试用例类型映射
        self.test_case_types = {
            'functional': TestCaseType.FUNCTIONAL,
            'performance': TestCaseType.PERFORMANCE,
            'safety': TestCaseType.SAFETY,
            'bias': TestCaseType.BIAS,
            'robustness': TestCaseType.ROBUSTNESS
        }
    
    def parse(self, content: str, **kwargs) -> Document:
        """
        解析Prompt文档内容
        
        Args:
            content: Prompt文档内容
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        try:
            # 检测格式并解析
            if content.strip().startswith('{'):
                # JSON格式
                prompt_document = self._parse_json_format(content)
                source_format = 'json'
            elif content.strip().startswith('---') or 'prompts:' in content:
                # YAML格式
                prompt_document = self._parse_yaml_format(content)
                source_format = 'yaml'
            else:
                # Markdown格式
                prompt_document = self._parse_markdown_format(content)
                source_format = 'markdown'
            
            # 设置源格式
            prompt_document.source_format = source_format
            
            # 创建Document对象
            document = Document(
                title=prompt_document.title,
                content=content,
                document_type=DocumentType.PROMPT,
                **kwargs
            )
            
            # 将PromptDocument作为额外数据存储
            document.prompt_document = prompt_document
            
            return document
            
        except Exception as e:
            raise ValueError(f"解析Prompt文档失败: {str(e)}")
    
    def parse_from_file(self, file_path: str, **kwargs) -> Document:
        """
        从文件解析Prompt文档
        
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
    
    def _parse_json_format(self, content: str) -> PromptDocument:
        """解析JSON格式的Prompt文档"""
        try:
            data = json.loads(content)
            return self._convert_to_prompt_document(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {str(e)}")
    
    def _parse_yaml_format(self, content: str) -> PromptDocument:
        """解析YAML格式的Prompt文档"""
        try:
            data = yaml.safe_load(content)
            return self._convert_to_prompt_document(data)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML格式错误: {str(e)}")
    
    def _parse_markdown_format(self, content: str) -> PromptDocument:
        """解析Markdown格式的Prompt文档"""
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled Prompt Document"
        
        # 解析Prompt模板
        prompts = self._extract_prompts_from_markdown(content)
        
        # 解析测试用例
        test_cases = self._extract_test_cases_from_markdown(content)
        
        # 解析使用场景
        scenarios = self._extract_scenarios_from_markdown(content)
        
        return PromptDocument(
            title=title,
            prompts=prompts,
            test_cases=test_cases,
            scenarios=scenarios,
            source_format='markdown'
        )
    
    def _convert_to_prompt_document(self, data: Dict[str, Any]) -> PromptDocument:
        """将字典数据转换为PromptDocument对象"""
        # 解析Prompt模板
        prompts = []
        for prompt_data in data.get('prompts', []):
            prompt = self._parse_prompt_template(prompt_data)
            prompts.append(prompt)
        
        # 解析测试用例
        test_cases = []
        for test_case_data in data.get('test_cases', []):
            test_case = self._parse_test_case(test_case_data)
            test_cases.append(test_case)
        
        # 解析使用场景
        scenarios = []
        for scenario_data in data.get('scenarios', []):
            scenario = self._parse_scenario(scenario_data)
            scenarios.append(scenario)
        
        # 解析评估标准
        evaluations = []
        for eval_data in data.get('evaluations', []):
            evaluation = self._parse_evaluation(eval_data)
            evaluations.append(evaluation)
        
        return PromptDocument(
            title=data.get('title', 'Untitled Prompt Document'),
            version=data.get('version', '1.0'),
            description=data.get('description'),
            author=data.get('author'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            prompts=prompts,
            test_cases=test_cases,
            scenarios=scenarios,
            evaluations=evaluations,
            tags=data.get('tags'),
            categories=data.get('categories'),
            dependencies=data.get('dependencies'),
            source_format=data.get('source_format', 'structured')
        )
    
    def _parse_prompt_template(self, prompt_data: Dict[str, Any]) -> PromptTemplate:
        """解析Prompt模板"""
        # 解析变量
        variables = []
        for var_data in prompt_data.get('variables', []):
            variable = PromptVariable(
                name=var_data.get('name', ''),
                type=var_data.get('type', 'string'),
                description=var_data.get('description'),
                required=var_data.get('required', True),
                default=var_data.get('default'),
                examples=var_data.get('examples'),
                constraints=var_data.get('constraints')
            )
            variables.append(variable)
        
        # 确定Prompt类型
        prompt_type = prompt_data.get('type', 'template')
        if prompt_type not in self.prompt_types:
            prompt_type = 'template'
        
        return PromptTemplate(
            id=prompt_data.get('id', ''),
            name=prompt_data.get('name', ''),
            description=prompt_data.get('description'),
            type=self.prompt_types[prompt_type],
            role=PromptRole(prompt_data.get('role')) if prompt_data.get('role') else None,
            content=prompt_data.get('content', ''),
            variables=variables,
            tags=prompt_data.get('tags'),
            version=prompt_data.get('version', '1.0'),
            created_at=prompt_data.get('created_at'),
            updated_at=prompt_data.get('updated_at')
        )
    
    def _parse_test_case(self, test_case_data: Dict[str, Any]) -> PromptTestCase:
        """解析测试用例"""
        # 确定测试类型
        test_type = test_case_data.get('type', 'functional')
        if test_type not in self.test_case_types:
            test_type = 'functional'
        
        return PromptTestCase(
            id=test_case_data.get('id', ''),
            name=test_case_data.get('name', ''),
            description=test_case_data.get('description'),
            type=self.test_case_types[test_type],
            prompt_template_id=test_case_data.get('prompt_template_id', ''),
            input_data=test_case_data.get('input_data', {}),
            expected_output=test_case_data.get('expected_output'),
            evaluation_criteria=test_case_data.get('evaluation_criteria', []),
            tags=test_case_data.get('tags'),
            priority=test_case_data.get('priority', 'medium')
        )
    
    def _parse_scenario(self, scenario_data: Dict[str, Any]) -> PromptScenario:
        """解析使用场景"""
        return PromptScenario(
            id=scenario_data.get('id', ''),
            name=scenario_data.get('name', ''),
            description=scenario_data.get('description'),
            context=scenario_data.get('context'),
            user_personas=scenario_data.get('user_personas'),
            success_criteria=scenario_data.get('success_criteria', []),
            failure_scenarios=scenario_data.get('failure_scenarios'),
            related_prompts=scenario_data.get('related_prompts', [])
        )
    
    def _parse_evaluation(self, eval_data: Dict[str, Any]) -> PromptEvaluation:
        """解析评估标准"""
        return PromptEvaluation(
            criteria=eval_data.get('criteria', ''),
            description=eval_data.get('description'),
            weight=eval_data.get('weight', 1.0),
            measurement_method=eval_data.get('measurement_method', ''),
            threshold=eval_data.get('threshold')
        )
    
    def _extract_prompts_from_markdown(self, content: str) -> List[PromptTemplate]:
        """从Markdown中提取Prompt模板"""
        prompts = []
        
        # 查找Prompt章节
        prompt_pattern = r'##\s+Prompt[:\s]*(.+?)\n(.*?)(?=##|\Z)'
        matches = re.findall(prompt_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (title, prompt_content) in enumerate(matches):
            # 提取Prompt内容
            content_match = re.search(r'```(?:prompt|template)?\n(.*?)\n```', prompt_content, re.DOTALL)
            prompt_text = content_match.group(1) if content_match else prompt_content.strip()
            
            prompt = PromptTemplate(
                id=f"prompt_{i+1}",
                name=title.strip(),
                content=prompt_text,
                type=PromptType.TEMPLATE
            )
            prompts.append(prompt)
        
        return prompts
    
    def _extract_test_cases_from_markdown(self, content: str) -> List[PromptTestCase]:
        """从Markdown中提取测试用例"""
        test_cases = []
        
        # 查找测试用例章节
        test_pattern = r'##\s+Test Case[:\s]*(.+?)\n(.*?)(?=##|\Z)'
        matches = re.findall(test_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (title, test_content) in enumerate(matches):
            # 提取输入和期望输出
            input_match = re.search(r'Input[:\s]*\n(.*?)(?=Output|Expected|\n##|\Z)', test_content, re.DOTALL | re.IGNORECASE)
            output_match = re.search(r'(?:Output|Expected)[:\s]*\n(.*?)(?=\n##|\Z)', test_content, re.DOTALL | re.IGNORECASE)
            
            input_data = {"input": input_match.group(1).strip()} if input_match else {}
            expected_output = {"output": output_match.group(1).strip()} if output_match else None
            
            test_case = PromptTestCase(
                id=f"test_{i+1}",
                name=title.strip(),
                type=TestCaseType.FUNCTIONAL,
                prompt_template_id=f"prompt_{i+1}",  # 假设与Prompt对应
                input_data=input_data,
                expected_output=expected_output
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _extract_scenarios_from_markdown(self, content: str) -> List[PromptScenario]:
        """从Markdown中提取使用场景"""
        scenarios = []
        
        # 查找场景章节
        scenario_pattern = r'##\s+(?:Scenario|场景)[:\s]*(.+?)\n(.*?)(?=##|\Z)'
        matches = re.findall(scenario_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (title, scenario_content) in enumerate(matches):
            scenario = PromptScenario(
                id=f"scenario_{i+1}",
                name=title.strip(),
                description=scenario_content.strip()
            )
            scenarios.append(scenario)
        
        return scenarios
