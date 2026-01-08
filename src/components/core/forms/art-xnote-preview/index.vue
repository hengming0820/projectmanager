<!-- XNote 编辑器预览组件（只读模式） -->
<template>
  <div class="xnote-preview-wrapper" :class="{ 'preview-fullscreen': isFullscreen }">
    <div ref="previewRef" class="xnote-preview-container" :style="{ height: height }"></div>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

  defineOptions({ name: 'ArtXnotePreview' })

  interface Props {
    /** 预览内容（HTML格式） */
    content: string
    /** 编辑器高度 */
    height?: string
    /** 是否全屏 */
    showFullscreen?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    content: '',
    height: '500px',
    showFullscreen: false
  })

  const previewRef = ref<HTMLElement | null>(null)
  let editorInstance: any = null
  const isFullscreen = ref(false)

  // 初始化预览编辑器
  const initPreviewEditor = async () => {
    if (!previewRef.value) return

    try {
      console.log('📖 [XNotePreview] 开始初始化预览编辑器')

      // 动态导入 XNote
      const { Editor } = await import('@textbus/xnote')

      // 创建只读编辑器
      const editorConfig: any = {
        content: props.content || '<p></p>',
        readonly: true // 只读模式 - 关键配置！
      }

      editorInstance = new Editor(editorConfig)

      // 挂载编辑器
      await editorInstance.mount(previewRef.value)

      // 确保文本可选（移除可能的限制）
      setTimeout(() => {
        if (previewRef.value) {
          const container = previewRef.value
          // 移除可能阻止文本选择的属性
          container.style.userSelect = 'text'
          container.style.webkitUserSelect = 'text'
          container.style.cursor = 'text'

          // 递归设置所有子元素
          const setSelectable = (element: HTMLElement) => {
            element.style.userSelect = 'text'
            element.style.webkitUserSelect = 'text'
            element.style.cursor = 'text'

            Array.from(element.children).forEach((child) => {
              if (child instanceof HTMLElement) {
                setSelectable(child)
              }
            })
          }

          setSelectable(container)
          console.log('✅ [XNotePreview] 文本选择功能已启用')
        }
      }, 500)

      console.log('✅ [XNotePreview] 预览编辑器初始化成功（只读模式）')
    } catch (error) {
      console.error('❌ [XNotePreview] 预览编辑器初始化失败:', error)
    }
  }

  // 更新内容
  const updateContent = (newContent: string) => {
    if (!editorInstance) return

    try {
      editorInstance.setContent(newContent || '<p></p>')
      console.log('🔄 [XNotePreview] 内容已更新')
    } catch (error) {
      console.error('❌ [XNotePreview] 更新内容失败:', error)
    }
  }

  // 监听内容变化
  watch(
    () => props.content,
    (newContent) => {
      updateContent(newContent)
    }
  )

  // 切换全屏
  const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value
  }

  // 初始化
  onMounted(() => {
    initPreviewEditor()
  })

  // 组件卸载时销毁编辑器
  onBeforeUnmount(() => {
    if (editorInstance) {
      try {
        editorInstance.destroy?.()
        console.log('🗑️ [XNotePreview] 预览编辑器已销毁')
      } catch (e) {
        console.warn('⚠️ [XNotePreview] 销毁编辑器失败:', e)
      }
      editorInstance = null
    }
  })

  // 暴露方法给父组件
  defineExpose({
    toggleFullscreen,
    isFullscreen,
    editorInstance
  })
</script>

<style lang="scss" scoped>
  .xnote-preview-wrapper {
    position: relative;
    border: 1px solid var(--art-card-border);
    border-radius: 8px;
    background: var(--art-main-bg-color);
    overflow: hidden;
    transition: all 0.3s ease;

    .xnote-preview-container {
      width: 100%;
      overflow-y: auto;

      // 自定义滚动条
      &::-webkit-scrollbar {
        width: 8px;
      }

      &::-webkit-scrollbar-track {
        background: var(--art-bg-color);
        border-radius: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background: var(--art-card-border);
        border-radius: 4px;

        &:hover {
          background: var(--art-text-gray-400);
        }
      }
    }

    // 隐藏所有工具栏
    :deep(.textbus-toolbar),
    :deep(.xnote-toolbar),
    :deep([class*='toolbar']) {
      display: none !important;
    }

    // 编辑器容器样式
    :deep(.textbus-container),
    :deep(.xnote-container) {
      border: none !important;
      background: var(--art-main-bg-color);
      min-height: 100%;
      user-select: text !important;
      -webkit-user-select: text !important;
      cursor: text !important;
    }

    // 编辑区域样式优化
    :deep(.textbus-content),
    :deep(.xnote-content),
    :deep([class*='content']) {
      padding: 20px 24px !important;
      color: var(--art-text-gray-900);
      font-size: 15px;
      line-height: 1.8;
      cursor: text !important;
      user-select: text !important;
      -webkit-user-select: text !important;
      -moz-user-select: text !important;

      // 标题样式
      h1 {
        font-size: 32px;
        font-weight: 700;
        margin: 24px 0 16px 0;
        line-height: 1.3;
        color: var(--art-text-gray-900);
        border-bottom: 2px solid var(--art-card-border);
        padding-bottom: 12px;
      }

      h2 {
        font-size: 28px;
        font-weight: 600;
        margin: 20px 0 14px 0;
        line-height: 1.3;
        color: var(--art-text-gray-900);
      }

      h3 {
        font-size: 24px;
        font-weight: 600;
        margin: 18px 0 12px 0;
        line-height: 1.4;
        color: var(--art-text-gray-900);
      }

      h4 {
        font-size: 20px;
        font-weight: 600;
        margin: 16px 0 10px 0;
        line-height: 1.4;
        color: var(--art-text-gray-900);
      }

      h5 {
        font-size: 18px;
        font-weight: 600;
        margin: 14px 0 8px 0;
        line-height: 1.5;
        color: var(--art-text-gray-900);
      }

      h6 {
        font-size: 16px;
        font-weight: 600;
        margin: 12px 0 8px 0;
        line-height: 1.5;
        color: var(--art-text-gray-900);
      }

      // 段落样式
      p {
        margin: 12px 0;
        line-height: 1.8;
        color: var(--art-text-gray-900);
      }

      // 列表样式
      ul,
      ol {
        margin: 12px 0;
        padding-left: 28px;

        li {
          margin: 6px 0;
          line-height: 1.8;
          color: var(--art-text-gray-900);
        }
      }

      ul {
        list-style-type: disc;

        ul {
          list-style-type: circle;

          ul {
            list-style-type: square;
          }
        }
      }

      ol {
        list-style-type: decimal;
      }

      // 引用块样式
      blockquote {
        margin: 16px 0;
        padding: 12px 16px;
        border-left: 4px solid #3b82f6;
        background: var(--art-bg-color);
        color: var(--art-text-gray-700);
        border-radius: 4px;

        p {
          margin: 6px 0;
        }
      }

      // 代码样式
      code {
        padding: 2px 6px;
        background: var(--art-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
        color: var(--art-text-gray-900);
        font-weight: 500;
      }

      pre {
        margin: 16px 0;
        padding: 16px;
        background: var(--art-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: 8px;
        overflow-x: auto;

        code {
          padding: 0;
          background: transparent;
          border: none;
          color: var(--art-text-gray-900);
          font-size: 14px;
          line-height: 1.6;
          font-weight: normal;
        }
      }

      // 表格样式
      table {
        width: 100%;
        margin: 16px 0;
        border-collapse: collapse;
        border: 1px solid var(--art-card-border);
        border-radius: 8px;
        overflow: hidden;

        thead {
          background: var(--art-bg-color);

          th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: var(--art-text-gray-900);
            border-bottom: 2px solid var(--art-card-border);
          }
        }

        tbody {
          tr {
            border-bottom: 1px solid var(--art-card-border);

            &:hover {
              background: var(--art-bg-color);
            }

            &:last-child {
              border-bottom: none;
            }
          }

          td {
            padding: 12px;
            color: var(--art-text-gray-900);
            border: 1px solid var(--art-card-border);
          }
        }
      }

      // 图片样式
      img {
        max-width: 100%;
        height: auto;
        margin: 16px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;

        &:hover {
          transform: scale(1.02);
        }
      }

      // 分割线样式
      hr {
        margin: 24px 0;
        border: none;
        border-top: 2px solid var(--art-card-border);
      }

      // 链接样式
      a {
        color: #3b82f6;
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: all 0.2s;

        &:hover {
          color: #2563eb;
          border-bottom-color: #2563eb;
        }
      }

      // 强调样式
      strong,
      b {
        font-weight: 700;
        color: var(--art-text-gray-900);
      }

      em,
      i {
        font-style: italic;
      }

      u {
        text-decoration: underline;
      }

      s,
      del {
        text-decoration: line-through;
        opacity: 0.7;
      }

      // 上标和下标
      sup {
        vertical-align: super;
        font-size: 0.75em;
      }

      sub {
        vertical-align: sub;
        font-size: 0.75em;
      }

      // 高亮标记
      mark {
        background: #fef08a;
        color: #854d0e;
        padding: 2px 4px;
        border-radius: 2px;
      }
    }

    // 日间模式下的额外样式优化
    html:not(.dark) & {
      :deep(.textbus-content),
      :deep(.xnote-content),
      :deep([class*='content']) {
        // 代码块在日间模式下使用更柔和的背景
        pre {
          background: #f6f8fa !important;
          border-color: #e1e4e8 !important;

          code {
            color: #24292e !important;
          }
        }

        // 行内代码在日间模式下的颜色
        code:not(pre code) {
          background: #f6f8fa !important;
          border-color: #e1e4e8 !important;
          color: #24292e !important;
        }

        // 引用块在日间模式下
        blockquote {
          background: #f6f8fa !important;
          border-left-color: #3b82f6 !important;
        }

        // 表格头部在日间模式下
        table thead {
          background: #f6f8fa !important;
        }
      }
    }

    // 夜间模式下的额外样式优化
    html.dark & {
      :deep(.textbus-content),
      :deep(.xnote-content),
      :deep([class*='content']) {
        // 代码块在夜间模式下
        pre {
          background: #1e1e1e !important;
          border-color: #333 !important;

          code {
            color: #d4d4d4 !important;
          }
        }

        // 行内代码在夜间模式下的颜色
        code:not(pre code) {
          background: #1e1e1e !important;
          border-color: #333 !important;
          color: #d4d4d4 !important;
        }

        // 高亮标记在夜间模式下
        mark {
          background: #854d0e !important;
          color: #fef08a !important;
        }
      }
    }

    // 允许文本选择和复制（最高优先级）
    :deep(*) {
      user-select: text !important;
      -webkit-user-select: text !important;
      -moz-user-select: text !important;
      -ms-user-select: text !important;
      cursor: text !important;

      &::selection {
        background: rgba(59, 130, 246, 0.3) !important;
        color: inherit !important;
      }

      &::-moz-selection {
        background: rgba(59, 130, 246, 0.3) !important;
        color: inherit !important;
      }
    }

    // 确保所有文本元素可选
    :deep(p),
    :deep(span),
    :deep(div),
    :deep(li),
    :deep(td),
    :deep(th),
    :deep(h1),
    :deep(h2),
    :deep(h3),
    :deep(h4),
    :deep(h5),
    :deep(h6),
    :deep(code),
    :deep(pre),
    :deep(blockquote),
    :deep(a),
    :deep(strong),
    :deep(em),
    :deep(u),
    :deep(s) {
      user-select: text !important;
      -webkit-user-select: text !important;
      cursor: text !important;
    }

    // 全屏模式
    &.preview-fullscreen {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 9999;
      border-radius: 0;

      .xnote-preview-container {
        height: 100vh !important;
      }

      :deep(.textbus-content),
      :deep(.xnote-content),
      :deep([class*='content']) {
        padding: 40px 80px !important;
      }
    }
  }

  // 打印样式优化
  @media print {
    .xnote-preview-wrapper {
      border: none !important;

      :deep(.textbus-content),
      :deep(.xnote-content),
      :deep([class*='content']) {
        padding: 0 !important;
      }
    }
  }
</style>
