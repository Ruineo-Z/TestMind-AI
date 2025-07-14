"""
Markdown文档解析器
解析Markdown格式的需求文档
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import markdown
    from markdown.extensions import codehilite, tables, toc
    import frontmatter
except ImportError:
    markdown = None
    frontmatter = None

from app.requirements_parser.parsers.base import BaseParser
from app.requirements_parser.models.document import Document, DocumentType, DocumentMetadata

class MarkdownParser(BaseParser):
    """Markdown文档解析器"""
    
    def __init__(self):
        """初始化Markdown解析器"""
        super().__init__()
        self.supported_extensions = {'.md', '.markdown', '.mdown', '.mkd'}
        
        # 检查依赖
        if markdown is None:
            raise ImportError("需要安装markdown库: pip install markdown")
        
        # 配置Markdown解析器
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.meta',
                'markdown.extensions.tables',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.fenced_code'
            ],
            extension_configs={
                'markdown.extensions.codehilite': {
                    'css_class': 'highlight'
                },
                'markdown.extensions.toc': {
                    'permalink': True
                }
            }
        )
    
    def parse(self, content: str, **kwargs) -> Document:
        """
        解析Markdown内容
        
        Args:
            content: Markdown内容
            **kwargs: 额外参数
            
        Returns:
            Document: 解析后的文档对象
        """
        # 验证内容
        self.validate_content(content)
        
        # 解析frontmatter（如果存在）
        frontmatter_data = {}
        clean_content = content
        
        if frontmatter and content.startswith('---'):
            try:
                post = frontmatter.loads(content)
                frontmatter_data = post.metadata
                clean_content = post.content
            except Exception:
                # 如果frontmatter解析失败，使用原始内容
                pass
        
        # 解析Markdown
        html_content = self.md.convert(clean_content)
        
        # 提取标题
        title = self._extract_title_from_frontmatter_or_content(frontmatter_data, clean_content)
        
        # 创建文档对象
        document = Document(
            title=title,
            content=clean_content,
            document_type=DocumentType.MARKDOWN
        )
        
        # 添加解析的结构化信息
        document.sections = self._extract_sections(clean_content)
        document.code_blocks = self._extract_code_blocks(clean_content)
        document.tables = self._extract_tables(clean_content)
        document.links = self._extract_links(clean_content)
        document.user_stories = self._extract_user_stories(clean_content)
        
        # 添加frontmatter数据
        if frontmatter_data:
            document.frontmatter = frontmatter_data
        
        return document
    
    def _extract_title_from_frontmatter_or_content(self, frontmatter_data: Dict, content: str) -> str:
        """从frontmatter或内容中提取标题"""
        # 优先使用frontmatter中的标题
        if frontmatter_data.get('title'):
            return frontmatter_data['title']
        
        # 从内容中提取第一个H1标题
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        return self.extract_title(content)
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """提取章节信息"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # 检查是否是标题
            if line.startswith('#'):
                # 保存上一个章节
                if current_section:
                    sections.append(current_section)
                
                # 创建新章节
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                current_section = {
                    'level': level,
                    'title': title,
                    'content': []
                }
            elif current_section:
                # 添加内容到当前章节
                current_section['content'].append(line)
        
        # 添加最后一个章节
        if current_section:
            sections.append(current_section)
        
        # 清理章节内容
        for section in sections:
            section['content'] = '\n'.join(section['content']).strip()
        
        return sections
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """提取代码块"""
        code_blocks = []

        # 提取围栏代码块 (```)
        fenced_pattern = r'```(\w+)?\n(.*?)\n```'
        fenced_ranges = []  # 记录围栏代码块的位置范围

        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2)
            code_blocks.append({
                'language': language,
                'code': code,
                'type': 'fenced'
            })
            # 记录围栏代码块的范围，避免重复检测
            fenced_ranges.append((match.start(), match.end()))

        # 只有在没有围栏代码块时才检测缩进代码块
        if not fenced_ranges:
            # 提取缩进代码块
            lines = content.split('\n')
            in_code_block = False
            current_code = []

            for line in lines:
                if line.startswith('    ') or line.startswith('\t'):
                    # 代码行
                    if not in_code_block:
                        in_code_block = True
                        current_code = []
                    current_code.append(line[4:] if line.startswith('    ') else line[1:])
                else:
                    # 非代码行
                    if in_code_block:
                        code_blocks.append({
                            'language': 'text',
                            'code': '\n'.join(current_code),
                            'type': 'indented'
                        })
                        in_code_block = False

            # 处理最后一个代码块
            if in_code_block:
                code_blocks.append({
                    'language': 'text',
                    'code': '\n'.join(current_code),
                    'type': 'indented'
                })

        return code_blocks
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格"""
        tables = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查是否是表格行（包含 | 分隔符）
            if '|' in line and line.count('|') >= 2:
                table_lines = [line]
                i += 1
                
                # 收集连续的表格行
                while i < len(lines):
                    next_line = lines[i].strip()
                    if '|' in next_line:
                        table_lines.append(next_line)
                        i += 1
                    else:
                        break
                
                # 解析表格
                if len(table_lines) >= 2:  # 至少需要标题行和分隔行
                    table = self._parse_table(table_lines)
                    if table:
                        tables.append(table)
            else:
                i += 1
        
        return tables
    
    def _parse_table(self, table_lines: List[str]) -> Optional[Dict[str, Any]]:
        """解析单个表格"""
        if len(table_lines) < 2:
            return None
        
        # 解析标题行
        header_line = table_lines[0].strip('|').strip()
        headers = [cell.strip() for cell in header_line.split('|')]
        
        # 跳过分隔行（第二行）
        data_lines = table_lines[2:] if len(table_lines) > 2 else []
        
        # 解析数据行
        rows = []
        for line in data_lines:
            if line.strip():
                row_data = line.strip('|').strip()
                cells = [cell.strip() for cell in row_data.split('|')]
                
                # 确保单元格数量与标题匹配
                while len(cells) < len(headers):
                    cells.append('')
                
                rows.append(dict(zip(headers, cells[:len(headers)])))
        
        return {
            'headers': headers,
            'rows': rows
        }
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """提取链接"""
        links = []
        
        # 提取Markdown链接 [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            
            link_type = 'internal' if url.startswith('#') else 'external'
            links.append({
                'text': text,
                'url': url,
                'type': link_type
            })
        
        return links
    
    def _extract_user_stories(self, content: str) -> List[Dict[str, Any]]:
        """提取用户故事"""
        user_stories = []
        
        # 查找用户故事模式
        story_pattern = r'##\s+作为(.+?)，我希望(.+?)(?=\n##|\n#|$)'
        
        for match in re.finditer(story_pattern, content, re.DOTALL):
            story_text = match.group(0)
            role = match.group(1).strip()
            goal = match.group(2).strip()
            
            # 提取验收标准
            acceptance_criteria = []
            criteria_pattern = r'\*\*验收标准：?\*\*\s*\n(.*?)(?=\n\*\*|\n##|\n#|$)'
            criteria_match = re.search(criteria_pattern, story_text, re.DOTALL)
            
            if criteria_match:
                criteria_text = criteria_match.group(1)
                # 提取列表项
                for line in criteria_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*'):
                        acceptance_criteria.append(line[1:].strip())
            
            # 提取优先级
            priority = "中"  # 默认优先级
            priority_pattern = r'\*\*优先级：?\*\*\s*(\S+)'
            priority_match = re.search(priority_pattern, story_text)
            if priority_match:
                priority = priority_match.group(1)
            
            user_stories.append({
                'title': f"作为{role}，我希望{goal}",
                'role': role,
                'goal': goal,
                'acceptance_criteria': acceptance_criteria,
                'priority': priority
            })
        
        return user_stories
    
    def validate_content(self, content: str) -> None:
        """验证Markdown内容"""
        super().validate_content(content)
        
        # Markdown特定验证
        if not content.strip():
            raise ValueError("Markdown内容不能为空")
