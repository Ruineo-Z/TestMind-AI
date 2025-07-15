# 测试数据说明

## 目录结构
```
test_data/
├── markdown/           # Markdown测试文档
│   ├── simple.md      # 简单文档
│   ├── complex.md     # 复杂文档
│   └── large.md       # 大型文档
├── pdf/               # PDF测试文档
│   ├── simple.pdf     # 简单PDF
│   ├── complex.pdf    # 复杂PDF
│   └── large.pdf      # 大型PDF
├── word/              # Word测试文档
│   ├── simple.docx    # 简单Word文档
│   ├── complex.docx   # 复杂Word文档
│   └── large.docx     # 大型Word文档
└── expected/          # 期望结果
    ├── simple_expected.json
    ├── complex_expected.json
    └── large_expected.json
```

## 测试文档特点

### 简单文档 (simple)
- 基础结构：标题、段落、列表
- 文件大小：< 10KB
- 用途：快速验证基础功能

### 复杂文档 (complex)
- 复杂结构：多级标题、表格、链接、代码块
- 包含用户故事和需求描述
- 文件大小：10KB - 100KB
- 用途：验证解析器的完整功能

### 大型文档 (large)
- 大量内容：100+ 页面
- 复杂格式：图片、表格、多种样式
- 文件大小：> 1MB
- 用途：性能和稳定性测试
