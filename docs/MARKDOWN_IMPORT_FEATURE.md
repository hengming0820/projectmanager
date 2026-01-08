# Markdown 导入功能实现详解

## 📋 概述

当前系统在多个文章编辑页面实现了 Markdown 导入功能，允许用户直接上传 `.md` 文件并自动转换为 HTML 格式，插入到富文本编辑器中。

## 🎯 实现位置

Markdown 导入功能已在以下页面实现：

1. **项目文章详情页** - `src/views/project/management/components/ArticleDetailView.vue`
2. **团队协作文档页** - `src/views/collaboration/index.vue`
3. **团队协作创建页** - `src/views/collaboration/create/index.vue`
4. **会议记录页** - `src/views/project/articles/meeting/index.vue`
5. **模型测试页** - `src/views/project/articles/model-test/index.vue`
6. **文章创建页** - `src/views/project/articles/create/index.vue`

## 🔧 核心实现

### 1. UI 交互流程

#### 触发导入

```vue
<el-button @click="openImportMarkdown">
  <el-icon><Upload /></el-icon>
  导入 Markdown
</el-button>
```

#### 打开导入对话框

```typescript
const openImportMarkdown = () => {
  showMdDialog.value = true
  mdFileName.value = ''
}
```

#### 文件选择对话框

```vue
<el-dialog v-model="showMdDialog" title="导入 Markdown" width="500px">
  <el-upload
    :auto-upload="false"
    :show-file-list="false"
    :on-change="onMdSelected"
    accept=".md,.markdown"
    drag
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      将 Markdown 文件拖到此处，或<em>点击上传</em>
    </div>
  </el-upload>
  <div v-if="mdFileName" class="file-name">
    已选择: {{ mdFileName }}
  </div>
</el-dialog>
```

### 2. 文件处理核心逻辑

```typescript
const onMdSelected = async (file: any) => {
  try {
    // 1. 获取原始文件对象
    const raw: File = file?.raw || file
    if (!raw) return

    // 2. 记录文件名
    mdFileName.value = raw.name

    // 3. 读取文件内容
    const text = await raw.text()

    // 4. 去除 BOM 标记（如果存在）
    const content = text.replace(/^\uFEFF/, '')

    // 5. 分割行并处理（部分实现会提取标题）
    const lines = content.split(/\r?\n/)
    const firstIdx = lines.findIndex((l: string) => l.trim().length > 0)

    // 6. 获取正文内容
    const bodyMd = lines.slice(firstIdx >= 0 ? firstIdx : 0).join('\n')

    // 7. 转换 Markdown 为 HTML
    const html = simpleMdToHtml(bodyMd)

    // 8. 插入到编辑器
    editForm.value.content = html

    // 9. 关闭对话框并提示成功
    showMdDialog.value = false
    ElMessage.success('Markdown 已导入')
  } catch (e) {
    ElMessage.error('Markdown 导入失败')
  }
}
```

### 3. Markdown 转 HTML 核心函数

系统实现了一个轻量级的 `simpleMdToHtml` 函数，支持常见的 Markdown 语法：

````typescript
function simpleMdToHtml(md: string): string {
  // HTML 转义函数
  const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  const lines = md.replace(/\r/g, '').split('\n')
  let i = 0
  const out: string[] = []

  while (i < lines.length) {
    const line = lines[i]

    // 1️⃣ 代码块处理 (```)
    if (/^```/.test(line)) {
      i++
      const code: string[] = []
      while (i < lines.length && !/^```/.test(lines[i])) {
        code.push(lines[i])
        i++
      }
      i++
      out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`)
      continue
    }

    // 2️⃣ 标题处理 (# - ######)
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/)
    if (headingMatch) {
      const level = headingMatch[1].length
      out.push(`<h${level}>${esc(headingMatch[2])}</h${level}>`)
      i++
      continue
    }

    // 3️⃣ 无序列表 (- 或 *)
    if (/^\s*[-*]\s+/.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(`<li>${inline(lines[i].replace(/^\s*[-*]\s+/, ''))}</li>`)
        i++
      }
      out.push(`<ul>${items.join('')}</ul>`)
      continue
    }

    // 4️⃣ 引用块 (>)
    if (/^>\s+/.test(line)) {
      const quotes: string[] = []
      while (i < lines.length && /^>\s+/.test(lines[i])) {
        quotes.push(lines[i].replace(/^>\s+/, ''))
        i++
      }
      out.push(`<blockquote>${inline(quotes.join(' '))}</blockquote>`)
      continue
    }

    // 5️⃣ 空行跳过
    if (!line.trim()) {
      i++
      continue
    }

    // 6️⃣ 普通段落
    out.push(`<p>${inline(line)}</p>`)
    i++
  }

  return out.join('\n')

  // 行内样式处理函数
  function inline(t: string): string {
    let s = esc(t)
    // 粗体 **text**
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜体 *text*
    s = s.replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 行内代码 `code`
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>')
    // 链接 [text](url)
    s = s.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noreferrer noopener">$1</a>'
    )
    return s
  }
}
````

## ✨ 支持的 Markdown 语法

### 块级元素

| Markdown         | HTML                            | 示例         |
| ---------------- | ------------------------------- | ------------ |
| `# 标题`         | `<h1>标题</h1>`                 | H1 - H6 标题 |
| ` ```代码块``` ` | `<pre><code>代码</code></pre>`  | 多行代码     |
| `- 列表项`       | `<ul><li>列表项</li></ul>`      | 无序列表     |
| `* 列表项`       | `<ul><li>列表项</li></ul>`      | 无序列表     |
| `> 引用`         | `<blockquote>引用</blockquote>` | 引用块       |
| 普通文本         | `<p>普通文本</p>`               | 段落         |

### 行内元素

| Markdown      | HTML                     | 说明     |
| ------------- | ------------------------ | -------- |
| `**粗体**`    | `<strong>粗体</strong>`  | 加粗     |
| `*斜体*`      | `<em>斜体</em>`          | 斜体     |
| `` `代码` ``  | `<code>代码</code>`      | 行内代码 |
| `[链接](url)` | `<a href="url">链接</a>` | 超链接   |

## 🔒 安全性考虑

### HTML 转义

所有用户输入的文本都经过 HTML 转义处理，防止 XSS 攻击：

```typescript
const esc = (s: string) =>
  s
    .replace(/&/g, '&amp;') // & → &amp;
    .replace(/</g, '&lt;') // < → &lt;
    .replace(/>/g, '&gt;') // > → &gt;
```

### 链接安全

生成的链接都添加了安全属性：

```html
<a href="url" target="_blank" rel="noreferrer noopener">链接</a>
```

- `target="_blank"` - 新窗口打开
- `rel="noreferrer"` - 不发送 referrer 信息
- `rel="noopener"` - 防止 `window.opener` 访问

## 📊 实现差异

不同页面的实现略有差异：

### 版本 1：完整版（项目文章详情页）

```typescript
// 特点：包含完整的行内样式处理函数
function simpleMdToHtml(md: string): string {
  // ... 完整实现
  function inline(t: string): string {
    let s = esc(t)
    s = s
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    return s
  }
}
```

### 版本 2：简化版（团队协作页）

```typescript
// 特点：仅处理基本块级元素，不处理行内样式
function simpleMdToHtml(md: string): string {
  const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  // 仅处理标题、列表、代码块等
  // 不处理粗体、斜体、链接等行内样式
}
```

## 🎨 UI 设计

### 导入按钮样式

```vue
<el-button type="primary" @click="openImportMarkdown">
  <el-icon><Upload /></el-icon>
  导入 Markdown
</el-button>
```

### 拖拽上传区域

```vue
<el-upload
  drag
  :auto-upload="false"
  :show-file-list="false"
  :on-change="onMdSelected"
  accept=".md,.markdown"
>
  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
  <div class="el-upload__text">
    将 Markdown 文件拖到此处，或<em>点击上传</em>
  </div>
  <div class="el-upload__tip">
    支持 .md 和 .markdown 格式
  </div>
</el-upload>
```

### 文件名显示

```vue
<div v-if="mdFileName" class="file-name">
  <el-icon><Document /></el-icon>
  已选择: {{ mdFileName }}
</div>
```

## 📝 使用示例

### Markdown 输入

````markdown
# 项目需求文档

## 背景介绍

这是一个**重要的**项目需求文档。

## 功能列表

- 用户登录
- 数据导入
- 报表导出

## 代码示例

```javascript
function hello() {
  console.log('Hello World')
}
```
````

> 注意：这是一个重要的提示信息

详细信息请访问 [官方文档](https://example.com)

````

### HTML 输出
```html
<h1>项目需求文档</h1>
<h2>背景介绍</h2>
<p>这是一个<strong>重要的</strong>项目需求文档。</p>
<h2>功能列表</h2>
<ul>
  <li>用户登录</li>
  <li>数据导入</li>
  <li>报表导出</li>
</ul>
<h2>代码示例</h2>
<pre><code>function hello() {
  console.log('Hello World')
}
</code></pre>
<blockquote>注意：这是一个重要的提示信息</blockquote>
<p>详细信息请访问 <a href="https://example.com" target="_blank" rel="noreferrer noopener">官方文档</a></p>
````

## 🚀 优化建议

### 1. 功能增强

- ✅ 支持有序列表 (`1. 列表项`)
- ✅ 支持表格语法
- ✅ 支持任务列表 (`- [ ] 待办事项`)
- ✅ 支持代码块语言高亮标记
- ✅ 支持图片 `![alt](url)`
- ✅ 支持分隔线 `---`
- ✅ 支持脚注

### 2. 使用第三方库

建议使用成熟的 Markdown 解析库，如：

#### marked.js

```bash
npm install marked
```

```typescript
import { marked } from 'marked'

const html = marked.parse(markdownText)
```

**优势**：

- ✅ 完整支持 CommonMark 规范
- ✅ 支持扩展语法（GFM）
- ✅ 性能优化
- ✅ 社区支持完善

#### markdown-it

```bash
npm install markdown-it
```

```typescript
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const html = md.render(markdownText)
```

**优势**：

- ✅ 插件系统完善
- ✅ 可扩展性强
- ✅ 支持自定义规则
- ✅ 性能优秀

### 3. 用户体验优化

- **实时预览**：导入前显示预览效果
- **拖拽提示**：优化拖拽区域的视觉反馈
- **错误处理**：更详细的错误提示
- **进度显示**：大文件导入时显示进度
- **历史记录**：保存最近导入的文件
- **批量导入**：支持同时导入多个文件

### 4. 格式兼容性

- **标题提取**：智能识别文档标题
- **格式转换**：支持其他格式转换（docx、txt等）
- **样式保留**：尽可能保留原始格式
- **字符集处理**：自动检测和处理不同字符集

### 5. 性能优化

```typescript
// 大文件分块处理
const onMdSelected = async (file: any) => {
  const raw: File = file?.raw || file
  if (!raw) return

  // 大文件警告
  if (raw.size > 1024 * 1024) {
    // 1MB
    ElMessage.warning('文件较大，处理可能需要一些时间...')
  }

  // 使用 FileReader 流式读取
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    const html = simpleMdToHtml(text)
    editForm.value.content = html
    ElMessage.success('Markdown 已导入')
  }
  reader.readAsText(raw)
}
```

## 🔗 相关功能

系统还实现了以下相关导入功能：

### 1. Word 文档导入

使用 `mammoth.js` 将 `.docx` 文件转换为 HTML：

```typescript
import mammoth from 'mammoth'

const onWordSelected = async (file: any) => {
  const raw: File = file?.raw || file
  const arrayBuffer = await raw.arrayBuffer()
  const result = await mammoth.convertToHtml({ arrayBuffer })

  if (result.value) {
    editForm.value.content = result.value
    ElMessage.success('Word 文档已导入')
  }
}
```

### 2. 图片上传

支持拖拽或选择图片上传，并自动插入到编辑器。

### 3. 文件附件

支持上传其他类型的附件文件。

## 📚 代码位置总结

### 核心文件

1. **项目文章详情页**

   - 文件：`src/views/project/management/components/ArticleDetailView.vue`
   - 行数：720-833

2. **团队协作页**

   - 文件：`src/views/collaboration/index.vue`
   - 行数：1074-1197

3. **团队协作创建页**
   - 文件：`src/views/collaboration/create/index.vue`
   - 行数：216-329

### 共同点

- 都使用 Element Plus 的 `el-upload` 组件
- 都实现了 `simpleMdToHtml` 转换函数
- 都处理了 BOM 标记和字符编码问题
- 都提供了用户友好的拖拽上传界面

### 差异点

- 标题提取：部分实现会提取第一行作为标题
- 行内样式：部分实现支持粗体、斜体、链接等
- 错误处理：不同页面的错误提示略有差异

## 🎯 最佳实践

### 1. 统一实现

建议将 `simpleMdToHtml` 提取为公共工具函数：

```typescript
// src/utils/markdown.ts
export function simpleMdToHtml(md: string): string {
  // 统一的实现
}
```

### 2. 配置化

提供配置选项，允许不同场景使用不同的转换策略：

```typescript
interface MdToHtmlOptions {
  extractTitle?: boolean // 是否提取标题
  supportInlineStyles?: boolean // 是否支持行内样式
  sanitizeHtml?: boolean // 是否清理 HTML
}

export function simpleMdToHtml(md: string, options?: MdToHtmlOptions): string {
  // 根据配置转换
}
```

### 3. 测试覆盖

为转换函数编写单元测试：

```typescript
describe('simpleMdToHtml', () => {
  it('应该正确转换标题', () => {
    expect(simpleMdToHtml('# 标题')).toBe('<h1>标题</h1>')
  })

  it('应该正确转换列表', () => {
    expect(simpleMdToHtml('- 项目1\n- 项目2')).toBe('<ul><li>项目1</li><li>项目2</li></ul>')
  })

  // ... 更多测试用例
})
```

---

**文档版本**: v1.0.0  
**最后更新**: 2025-11-04  
**维护者**: 开发团队  
**相关功能**: Word 导入、图片上传、富文本编辑
