/**
 * Markdown 工具函数
 * 使用 marked 库将 Markdown 转换为 HTML
 */

import { marked } from 'marked'
import DOMPurify from 'dompurify'

/**
 * Markdown 转 HTML 配置选项
 */
export interface MdToHtmlOptions {
  /**
   * 是否清理 HTML（防止 XSS 攻击）
   * @default true
   */
  sanitize?: boolean

  /**
   * 是否支持 GitHub Flavored Markdown（GFM）
   * @default true
   */
  gfm?: boolean

  /**
   * 是否在新窗口打开链接
   * @default true
   */
  openLinksInNewWindow?: boolean

  /**
   * 是否支持代码高亮
   * @default false
   */
  highlightCode?: boolean
}

/**
 * 配置 marked 渲染器
 */
function configureMarked(options: MdToHtmlOptions = {}) {
  const { gfm = true, openLinksInNewWindow = true, highlightCode = false } = options

  // 基础配置
  marked.setOptions({
    gfm,
    breaks: true, // 支持 GFM 换行
    pedantic: false
  })

  // 自定义渲染器
  const renderer: any = {}

  // 链接渲染：在新窗口打开并添加安全属性
  if (openLinksInNewWindow) {
    renderer.link = function ({
      href,
      title,
      text
    }: {
      href: string
      title?: string | null
      text: string
    }) {
      const cleanHref = href || ''
      const cleanTitle = title ? ` title="${escapeHtml(title)}"` : ''
      return `<a href="${cleanHref}"${cleanTitle} target="_blank" rel="noopener noreferrer">${text}</a>`
    }
  }

  // 代码块渲染（可选添加语言标识）
  if (highlightCode) {
    renderer.code = function ({ text, lang }: { text: string; lang?: string }) {
      const language = lang || 'text'
      return `<pre><code class="language-${language}">${escapeHtml(text)}</code></pre>`
    }
  }

  marked.use({ renderer })
}

/**
 * HTML 转义函数
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.replace(/[&<>"']/g, (m) => map[m])
}

/**
 * 将 Markdown 转换为 HTML
 *
 * @param markdown - Markdown 文本
 * @param options - 转换选项
 * @returns HTML 文本
 *
 * @example
 * ```typescript
 * const html = markdownToHtml('# Hello World\n\nThis is **bold** text.')
 * ```
 */
export function markdownToHtml(markdown: string, options: MdToHtmlOptions = {}): string {
  if (!markdown || !markdown.trim()) {
    return ''
  }

  const { sanitize = true } = options

  try {
    // 配置 marked
    configureMarked(options)

    // 去除 BOM 标记
    const cleanMarkdown = markdown.replace(/^\uFEFF/, '')

    // 转换 Markdown 为 HTML
    let html = marked.parse(cleanMarkdown) as string

    // 清理 HTML（防止 XSS 攻击）
    if (sanitize) {
      html = DOMPurify.sanitize(html, {
        ALLOWED_TAGS: [
          'h1',
          'h2',
          'h3',
          'h4',
          'h5',
          'h6',
          'p',
          'br',
          'hr',
          'strong',
          'em',
          'u',
          's',
          'del',
          'ins',
          'mark',
          'sub',
          'sup',
          'ul',
          'ol',
          'li',
          'blockquote',
          'pre',
          'code',
          'a',
          'img',
          'table',
          'thead',
          'tbody',
          'tr',
          'th',
          'td',
          'div',
          'span'
        ],
        ALLOWED_ATTR: [
          'href',
          'title',
          'target',
          'rel',
          'src',
          'alt',
          'width',
          'height',
          'class',
          'id',
          'colspan',
          'rowspan'
        ],
        ALLOW_DATA_ATTR: false
      })
    }

    return html
  } catch (error) {
    console.error('Markdown 转换失败:', error)
    // 降级处理：返回转义后的纯文本
    return `<p>${escapeHtml(markdown)}</p>`
  }
}

/**
 * 从 Markdown 内容中提取标题
 *
 * @param markdown - Markdown 文本
 * @returns 第一个标题文本，如果没有则返回空字符串
 *
 * @example
 * ```typescript
 * const title = extractTitle('# My Title\n\nContent here')
 * console.log(title) // 'My Title'
 * ```
 */
export function extractTitle(markdown: string): string {
  if (!markdown || !markdown.trim()) {
    return ''
  }

  const lines = markdown.split(/\r?\n/)

  for (const line of lines) {
    const trimmed = line.trim()
    // 匹配 ATX 标题（# 开头）
    const atxMatch = trimmed.match(/^(#{1,6})\s+(.+)$/)
    if (atxMatch) {
      return atxMatch[2].trim()
    }

    // 如果遇到非空行且不是标题，停止查找
    if (trimmed.length > 0 && !trimmed.startsWith('#')) {
      break
    }
  }

  return ''
}

/**
 * 从 Markdown 内容中移除标题
 *
 * @param markdown - Markdown 文本
 * @returns 移除标题后的内容
 */
export function removeTitle(markdown: string): string {
  if (!markdown || !markdown.trim()) {
    return ''
  }

  const lines = markdown.split(/\r?\n/)
  let titleRemoved = false
  const result: string[] = []

  for (const line of lines) {
    const trimmed = line.trim()

    // 跳过第一个标题
    if (!titleRemoved && trimmed.match(/^#{1,6}\s+/)) {
      titleRemoved = true
      continue
    }

    result.push(line)
  }

  return result.join('\n')
}

/**
 * 处理 Markdown 文件内容
 * 提取标题和正文
 *
 * @param content - 文件内容
 * @returns { title: string, body: string }
 */
export function parseMarkdownFile(content: string): { title: string; body: string } {
  if (!content || !content.trim()) {
    return { title: '', body: '' }
  }

  // 去除 BOM 标记
  const cleanContent = content.replace(/^\uFEFF/, '')

  // 提取标题
  const title = extractTitle(cleanContent)

  // 获取正文（移除标题后的内容）
  const body = title ? removeTitle(cleanContent) : cleanContent

  return { title: title.trim(), body: body.trim() }
}

/**
 * 验证 Markdown 文件
 *
 * @param file - 文件对象
 * @returns 验证结果
 */
export function validateMarkdownFile(file: File): { valid: boolean; error?: string } {
  // 检查文件类型
  const validExtensions = ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']
  const fileName = file.name.toLowerCase()
  const isValidExtension = validExtensions.some((ext) => fileName.endsWith(ext))

  if (!isValidExtension) {
    return {
      valid: false,
      error: '请选择 Markdown 文件（.md 或 .markdown）'
    }
  }

  // 检查文件大小（限制 5MB）
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    return {
      valid: false,
      error: '文件大小不能超过 5MB'
    }
  }

  // 检查文件是否为空
  if (file.size === 0) {
    return {
      valid: false,
      error: '文件内容为空'
    }
  }

  return { valid: true }
}

/**
 * 读取 Markdown 文件
 *
 * @param file - 文件对象
 * @returns Promise<string> 文件内容
 */
export async function readMarkdownFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      const content = e.target?.result as string
      resolve(content || '')
    }

    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }

    reader.readAsText(file, 'UTF-8')
  })
}

// 默认导出
export default {
  markdownToHtml,
  extractTitle,
  removeTitle,
  parseMarkdownFile,
  validateMarkdownFile,
  readMarkdownFile
}
