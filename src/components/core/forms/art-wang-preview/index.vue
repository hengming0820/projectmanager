<!-- WangEditor 富文本预览组件（只读模式） -->
<template>
  <div class="preview-wrapper" :class="{ 'preview-fullscreen': isFullscreen }">
    <Editor
      :style="{ height: height, overflowY: 'hidden' }"
      v-model="contentModel"
      :mode="mode"
      :defaultConfig="editorConfig"
      @onCreated="onCreateEditor"
    />
  </div>
</template>

<script setup lang="ts">
  import '@wangeditor/editor/dist/css/style.css'
  import { onBeforeUnmount, shallowRef, ref, watch } from 'vue'
  import { Editor } from '@wangeditor/editor-for-vue'
  import { IDomEditor, IEditorConfig } from '@wangeditor/editor'

  defineOptions({ name: 'ArtWangPreview' })

  // Props 定义
  interface Props {
    /** 预览内容（HTML格式） */
    content: string
    /** 编辑器高度 */
    height?: string
    /** 编辑器模式 */
    mode?: 'default' | 'simple'
    /** 是否显示全屏按钮 */
    showFullscreen?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    height: '500px',
    mode: 'default',
    showFullscreen: false
  })

  // 编辑器实例
  const editorRef = shallowRef<IDomEditor>()
  const contentModel = ref(props.content)
  const isFullscreen = ref(false)

  // 监听 content 变化，同步到编辑器
  watch(
    () => props.content,
    (newContent) => {
      contentModel.value = newContent
    }
  )

  // 编辑器配置 - 关键：设置 readOnly
  const editorConfig: Partial<IEditorConfig> = {
    readOnly: true, // 只读模式
    scroll: true, // 允许滚动
    placeholder: '暂无内容',
    // 禁用所有菜单
    MENU_CONF: {}
  }

  // 编辑器创建回调
  const onCreateEditor = (editor: IDomEditor) => {
    editorRef.value = editor

    // 确保禁用编辑（双重保险）
    editor.disable()

    console.log('📖 [ArtWangPreview] 预览组件已创建（只读模式）')
  }

  // 切换全屏
  const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value
  }

  // 组件卸载时销毁编辑器
  onBeforeUnmount(() => {
    const editor = editorRef.value
    if (editor) {
      editor.destroy()
    }
  })

  // 暴露方法给父组件
  defineExpose({
    toggleFullscreen,
    isFullscreen,
    editorRef
  })
</script>

<style lang="scss" scoped>
  .preview-wrapper {
    position: relative;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background: var(--art-main-bg-color);
    overflow: hidden;
    transition: all 0.3s ease;

    // 隐藏工具栏
    :deep(.w-e-toolbar) {
      display: none !important;
    }

    // 预览样式优化
    :deep(.w-e-text-container) {
      border: none !important;
      background: var(--art-main-bg-color);

      // 隐藏占位符
      .w-e-text-placeholder {
        display: none !important;
      }

      // 编辑区域样式
      .w-e-scroll {
        padding: 20px 24px;

        // 自定义滚动条
        &::-webkit-scrollbar {
          width: 8px;
        }

        &::-webkit-scrollbar-track {
          background: var(--art-bg-color);
          border-radius: 4px;
        }

        &::-webkit-scrollbar-thumb {
          background: var(--el-border-color);
          border-radius: 4px;

          &:hover {
            background: var(--el-border-color-dark);
          }
        }
      }
    }

    // 禁用编辑提示
    :deep(.w-e-text) {
      cursor: default !important;
      user-select: text !important;

      // 段落样式
      p {
        margin: 12px 0;
        line-height: 1.8;
        color: var(--art-text-gray-700);
      }

      // 标题样式
      h1 {
        font-size: 28px;
        font-weight: 600;
        margin: 24px 0 16px;
        color: var(--art-text-gray-900);
        border-bottom: 2px solid var(--el-border-color);
        padding-bottom: 8px;
      }

      h2 {
        font-size: 24px;
        font-weight: 600;
        margin: 20px 0 14px;
        color: var(--art-text-gray-900);
      }

      h3 {
        font-size: 20px;
        font-weight: 600;
        margin: 18px 0 12px;
        color: var(--art-text-gray-800);
      }

      h4 {
        font-size: 18px;
        font-weight: 600;
        margin: 16px 0 10px;
        color: var(--art-text-gray-800);
      }

      h5 {
        font-size: 16px;
        font-weight: 600;
        margin: 14px 0 8px;
        color: var(--art-text-gray-700);
      }

      // 图片样式
      img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease;

        &:hover {
          transform: scale(1.02);
        }
      }

      // 代码块
      pre {
        background: #282c34;
        color: #abb2bf;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 16px 0;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        line-height: 1.6;

        code {
          background: transparent;
          padding: 0;
          color: inherit;
          font-size: 14px;
        }
      }

      // 行内代码
      code {
        background: #f5f7fa;
        color: #e83e8c;
        padding: 3px 6px;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
      }

      // 引用
      blockquote {
        border-left: 4px solid var(--el-color-primary);
        padding-left: 16px;
        margin: 16px 0;
        color: var(--art-text-gray-600);
        background: var(--art-bg-color);
        padding: 12px 16px;
        border-radius: 4px;
        font-style: italic;
      }

      // 列表
      ul,
      ol {
        padding-left: 24px;
        margin: 12px 0;

        li {
          margin: 8px 0;
          line-height: 1.8;
          color: var(--art-text-gray-700);
        }
      }

      // 待办列表
      ul[data-w-e-type='todo'] {
        list-style: none;
        padding-left: 0;

        li {
          position: relative;
          padding-left: 28px;

          input[type='checkbox'] {
            position: absolute;
            left: 0;
            top: 6px;
            pointer-events: none;
          }
        }
      }

      // 表格
      table {
        border-collapse: collapse;
        width: 100%;
        margin: 16px 0;
        border: 1px solid var(--el-border-color);
        border-radius: 8px;
        overflow: hidden;

        th {
          background: var(--art-bg-color);
          font-weight: 600;
          padding: 12px;
          border: 1px solid var(--el-border-color);
          text-align: left;
          color: var(--art-text-gray-900);
        }

        td {
          padding: 10px 12px;
          border: 1px solid var(--el-border-color);
          color: var(--art-text-gray-700);
        }

        tr:nth-child(even) {
          background: var(--art-bg-color-light);
        }

        tr:hover {
          background: var(--el-fill-color-light);
        }
      }

      // 链接
      a {
        color: var(--el-color-primary);
        text-decoration: none;
        transition: all 0.2s ease;

        &:hover {
          text-decoration: underline;
          color: var(--el-color-primary-light-3);
        }
      }

      // 分割线
      hr {
        border: none;
        border-top: 2px solid var(--el-border-color-lighter);
        margin: 24px 0;
      }

      // 加粗
      strong,
      b {
        font-weight: 600;
        color: var(--art-text-gray-900);
      }

      // 斜体
      em,
      i {
        font-style: italic;
        color: var(--art-text-gray-600);
      }

      // 下划线
      u {
        text-decoration: underline;
        text-decoration-color: var(--el-color-primary);
      }

      // 删除线
      s,
      del {
        text-decoration: line-through;
        color: var(--art-text-gray-500);
      }
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

      :deep(.w-e-text-container) {
        .w-e-scroll {
          padding: 40px 80px;
        }
      }
    }
  }

  // 打印样式优化
  @media print {
    .preview-wrapper {
      border: none !important;

      :deep(.w-e-text-container) {
        .w-e-scroll {
          padding: 0 !important;
        }
      }
    }
  }
</style>
