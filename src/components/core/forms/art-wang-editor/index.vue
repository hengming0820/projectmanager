<!-- WangEditor 富文本编辑器 插件地址：https://www.wangeditor.com/ -->
<template>
  <div class="editor-wrapper">
    <Toolbar
      class="editor-toolbar"
      :editor="editorRef"
      :mode="mode"
      :defaultConfig="toolbarConfig"
    />
    <Editor
      :style="{ height: height, overflowY: 'hidden' }"
      v-model="modelValue"
      :mode="mode"
      :defaultConfig="editorConfig"
      @onCreated="onCreateEditor"
    />
  </div>
</template>

<script setup lang="ts">
  import '@wangeditor/editor/dist/css/style.css'
  import { onBeforeUnmount, onMounted, shallowRef, computed, watch } from 'vue'
  import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
  import { useUserStore } from '@/store/modules/user'
  import { ElMessage } from 'element-plus'
  import EmojiText from '@/utils/ui/emojo'
  import { IDomEditor, IToolbarConfig, IEditorConfig } from '@wangeditor/editor'

  defineOptions({ name: 'ArtWangEditor' })

  // Props 定义
  interface Props {
    /** 编辑器高度 */
    height?: string
    /** 自定义工具栏配置 */
    toolbarKeys?: string[]
    /** 插入新工具到指定位置 */
    insertKeys?: { index: number; keys: string[] }
    /** 排除的工具栏项 */
    excludeKeys?: string[]
    /** 编辑器模式 */
    mode?: 'default' | 'simple'
    /** 占位符文本 */
    placeholder?: string
    /** 上传配置 */
    uploadConfig?: {
      maxFileSize?: number
      maxNumberOfFiles?: number
      server?: string
    }
    /** 外部传入的在线编辑者，用于渲染多人光标/选区 */
    activeEditors?: Array<{
      user_id: string
      user_name: string
      cursor_position?: number
      selection_range?: { start: number; end: number } | null
      color?: string
    }>
  }

  const props = withDefaults(defineProps<Props>(), {
    height: '500px',
    mode: 'default',
    placeholder: '请输入内容...',
    excludeKeys: () => ['fontFamily'],
    activeEditors: () => []
  })

  const modelValue = defineModel<string>({ required: true })
  const emit = defineEmits<{
    (
      e: 'presence',
      payload: { cursor_position?: number; selection_start?: number; selection_end?: number }
    ): void
  }>()

  // 编辑器实例
  const editorRef = shallowRef<IDomEditor>()
  const userStore = useUserStore()

  // 常量配置
  const DEFAULT_UPLOAD_CONFIG = {
    maxFileSize: 3 * 1024 * 1024, // 3MB
    maxNumberOfFiles: 10,
    fieldName: 'file',
    allowedFileTypes: ['image/*']
  } as const

  // 图标映射配置
  const ICON_MAP = {
    bold: '&#xe630;',
    blockquote: '&#xe61c;',
    underline: '&#xe65a;',
    italic: '&#xe638;',
    'group-more-style': '&#xe648;',
    color: '&#xe68c;',
    bgColor: '&#xe691;',
    bulletedList: '&#xe64e;',
    numberedList: '&#xe66c;',
    todo: '&#xe641;',
    'group-justify': '&#xe67e;',
    'group-indent': '&#xe63e;',
    emotion: '&#xe690;',
    insertLink: '&#xe63a;',
    'group-image': '&#xe634;',
    insertTable: '&#xe67b;',
    codeBlock: '&#xe68b;',
    divider: '&#xe66d;',
    undo: '&#xe65e;',
    redo: '&#xe659;',
    fullScreen: '&#xe633;',
    tableFullWidth: '&#xe67b;'
  } as const

  // 计算属性：上传服务器地址（避免 /api 重复）
  const uploadServer = computed(() => {
    if (props.uploadConfig?.server) return props.uploadConfig.server
    return `/api/common/upload/wangeditor`
  })

  // 合并上传配置
  const mergedUploadConfig = computed(() => ({
    ...DEFAULT_UPLOAD_CONFIG,
    ...props.uploadConfig
  }))

  // 工具栏配置
  const toolbarConfig = computed((): Partial<IToolbarConfig> => {
    const config: Partial<IToolbarConfig> = {}

    // 完全自定义工具栏
    if (props.toolbarKeys && props.toolbarKeys.length > 0) {
      config.toolbarKeys = props.toolbarKeys
    }

    // 插入新工具
    if (props.insertKeys) {
      config.insertKeys = props.insertKeys
    }

    // 排除工具
    if (props.excludeKeys && props.excludeKeys.length > 0) {
      config.excludeKeys = props.excludeKeys
    }

    return config
  })

  // 编辑器配置
  const editorConfig: Partial<IEditorConfig> = {
    placeholder: props.placeholder,
    MENU_CONF: {
      uploadImage: {
        fieldName: mergedUploadConfig.value.fieldName,
        maxFileSize: mergedUploadConfig.value.maxFileSize,
        maxNumberOfFiles: mergedUploadConfig.value.maxNumberOfFiles,
        allowedFileTypes: mergedUploadConfig.value.allowedFileTypes,
        server: uploadServer.value,
        headers: {
          Authorization: userStore.accessToken
        },
        // 统一将返回的 MinIO 直链转换为代理地址，保证编辑态可预览
        customInsert(res: any, insertFn: (url: string, alt?: string, href?: string) => void) {
          try {
            const rawUrl = res?.data?.url || res?.url
            const alt = res?.data?.alt || ''
            const href = res?.data?.href || rawUrl
            const rewrite = (u: string | undefined) => {
              if (!u) return ''
              return u.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/')
            }
            const finalUrl = rewrite(rawUrl)
            const finalHref = rewrite(href)
            insertFn(finalUrl || rawUrl, alt, finalHref || href)
          } catch (e) {
            // 回退到默认行为
            const fallback = res?.data?.url || res?.url
            insertFn(fallback, res?.data?.alt, res?.data?.href || fallback)
          }
        },
        onSuccess() {
          ElMessage.success(`图片上传成功 ${EmojiText[200]}`)
        },
        onError(file: File, err: any, res: any) {
          console.error('图片上传失败:', err, res)
          ElMessage.error(`图片上传失败 ${EmojiText[500]}`)
        }
      }
    }
  }

  // 编辑器创建回调
  const onCreateEditor = (editor: IDomEditor) => {
    editorRef.value = editor

    // 监听全屏事件
    editor.on('fullScreen', () => {
      console.log('编辑器进入全屏模式')
    })

    // 确保在编辑器创建后应用自定义图标
    applyCustomIcons()

    // 初始化多人高亮容器
    initPresenceOverlay()
  }

  // ============ 多人光标/选区渲染 ============
  let overlayEl: HTMLDivElement | null = null
  const colorForUser = (uid: string, name: string, fallback?: string) => {
    if (fallback) return fallback
    let hash = 0
    const s = uid || name || ''
    for (let i = 0; i < s.length; i++) hash = (hash << 5) - hash + s.charCodeAt(i)
    const hue = Math.abs(hash) % 360
    return `hsl(${hue}, 75%, 55%)`
  }

  const initPresenceOverlay = () => {
    const editor = editorRef.value
    if (!editor) return
    const container = editor.getEditableContainer()
    if (!container) return
    overlayEl = document.createElement('div')
    overlayEl.className = 'presence-overlay'
    overlayEl.style.position = 'absolute'
    overlayEl.style.pointerEvents = 'none'
    overlayEl.style.top = '0'
    overlayEl.style.left = '0'
    overlayEl.style.right = '0'
    overlayEl.style.bottom = '0'
    const wrapper = container.closest('.editor-wrapper') as HTMLElement
    if (wrapper && wrapper.style.position === '') {
      wrapper.style.position = 'relative'
    }
    ;(wrapper || container).appendChild(overlayEl)
    renderPresence()
  }

  const renderPresence = () => {
    const editor = editorRef.value
    if (!editor || !overlayEl) return
    overlayEl.innerHTML = ''

    const content = editor
      .getEditableContainer()
      .querySelector('.w-e-text-container .w-e-text') as HTMLElement
    if (!content) return

    const textNodes: Text[] = []
    const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT)
    let n: any
    while ((n = walker.nextNode())) textNodes.push(n as Text)

    const offsetToRange = (offset: number) => {
      let remain = Math.max(0, offset)
      for (const tn of textNodes) {
        const len = tn.nodeValue?.length || 0
        if (remain <= len) {
          const r = document.createRange()
          r.setStart(tn, remain)
          r.setEnd(tn, remain)
          return r
        }
        remain -= len
      }
      const r = document.createRange()
      if (textNodes.length > 0) {
        const last = textNodes[textNodes.length - 1]
        const len = last.nodeValue?.length || 0
        r.setStart(last, len)
        r.setEnd(last, len)
      } else {
        r.setStart(content, 0)
        r.setEnd(content, 0)
      }
      return r
    }

    props.activeEditors?.forEach((u) => {
      const color = colorForUser(u.user_id, u.user_name, (u as any).color)
      // caret
      if (typeof u.cursor_position === 'number') {
        const r = offsetToRange(u.cursor_position)
        const rect = r.getBoundingClientRect()
        const base = content.getBoundingClientRect()
        const caret = document.createElement('div')
        caret.className = 'presence-caret'
        caret.style.position = 'absolute'
        caret.style.width = '2px'
        caret.style.background = color
        caret.style.height = '1.2em'
        caret.style.top = `${rect.top - base.top + content.scrollTop}px`
        caret.style.left = `${rect.left - base.left + content.scrollLeft}px`
        overlayEl!.appendChild(caret)
      }
      // selection
      if (
        u.selection_range &&
        typeof u.selection_range.start === 'number' &&
        typeof u.selection_range.end === 'number'
      ) {
        const rs = offsetToRange(u.selection_range.start)
        const re = offsetToRange(u.selection_range.end)
        const r = document.createRange()
        r.setStart(rs.startContainer, rs.startOffset)
        r.setEnd(re.endContainer, re.endOffset)
        const rect = r.getBoundingClientRect()
        const base = content.getBoundingClientRect()
        const sel = document.createElement('div')
        sel.className = 'presence-selection'
        sel.style.position = 'absolute'
        sel.style.background = color
        sel.style.opacity = '0.15'
        sel.style.top = `${rect.top - base.top + content.scrollTop}px`
        sel.style.left = `${rect.left - base.left + content.scrollLeft}px`
        sel.style.width = `${Math.max(2, rect.width)}px`
        sel.style.height = `${Math.max(2, rect.height)}px`
        overlayEl!.appendChild(sel)
      }
    })
  }

  // 当父组件的 activeEditors 变更时，刷新 overlay
  watch(
    () => props.activeEditors,
    () => {
      renderPresence()
    },
    { deep: true }
  )

  // 监听本地选择变化，并向父组件上报字符偏移
  const computeOffsetsFromSelection = () => {
    try {
      const editor = editorRef.value
      if (!editor) return
      const content = editor
        .getEditableContainer()
        .querySelector('.w-e-text-container .w-e-text') as HTMLElement
      if (!content) return
      const sel = window.getSelection()
      if (!sel || sel.rangeCount === 0) return
      const range = sel.getRangeAt(0)

      // 将 DOM Range 转换为全局字符偏移
      const textNodes: Text[] = []
      const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT)
      let n: any
      while ((n = walker.nextNode())) textNodes.push(n as Text)
      const offsetOf = (container: Node, offset: number) => {
        let total = 0
        for (const tn of textNodes) {
          if (tn === container) {
            return total + offset
          }
          total += tn.nodeValue?.length || 0
        }
        return total
      }
      const start = offsetOf(range.startContainer, range.startOffset)
      const end = offsetOf(range.endContainer, range.endOffset)
      const cursor = end
      emit('presence', {
        cursor_position: cursor,
        selection_start: Math.min(start, end),
        selection_end: Math.max(start, end)
      })
    } catch {}
  }

  onMounted(() => {
    document.addEventListener('selectionchange', computeOffsetsFromSelection)
  })
  onBeforeUnmount(() => {
    document.removeEventListener('selectionchange', computeOffsetsFromSelection)
  })

  // 优化的图标替换函数 - 针对特定编辑器实例
  const overrideIcons = (editorInstance: IDomEditor) => {
    // 获取当前编辑器的工具栏容器
    const editorContainer = editorInstance.getEditableContainer().closest('.editor-wrapper')
    if (!editorContainer) return

    const toolbar = editorContainer.querySelector('.w-e-toolbar')
    if (!toolbar) return

    Object.entries(ICON_MAP).forEach(([menuKey, iconCode]) => {
      const button = toolbar.querySelector(`button[data-menu-key="${menuKey}"]`)
      if (button) {
        button.innerHTML = `<i class='iconfont-sys'>${iconCode}</i>`
      }
    })
  }

  // 应用自定义图标（带重试机制）
  const applyCustomIcons = () => {
    let retryCount = 0
    const maxRetries = 10
    const retryDelay = 100

    const tryApplyIcons = () => {
      const editor = editorRef.value
      if (!editor) {
        if (retryCount < maxRetries) {
          retryCount++
          setTimeout(tryApplyIcons, retryDelay)
        }
        return
      }

      // 获取当前编辑器的工具栏容器
      const editorContainer = editor.getEditableContainer().closest('.editor-wrapper')
      if (!editorContainer) {
        if (retryCount < maxRetries) {
          retryCount++
          setTimeout(tryApplyIcons, retryDelay)
        }
        return
      }

      const toolbar = editorContainer.querySelector('.w-e-toolbar')
      const toolbarButtons = editorContainer.querySelectorAll('.w-e-bar-item button[data-menu-key]')

      if (toolbar && toolbarButtons.length > 0) {
        overrideIcons(editor)
        return
      }

      // 如果工具栏还没渲染完成，继续重试
      if (retryCount < maxRetries) {
        retryCount++
        setTimeout(tryApplyIcons, retryDelay)
      } else {
        console.warn('工具栏渲染超时，无法应用自定义图标 - 编辑器实例:', editor.id)
      }
    }

    // 使用 requestAnimationFrame 确保在下一帧执行
    requestAnimationFrame(tryApplyIcons)
  }

  // 暴露编辑器实例和方法
  defineExpose({
    /** 获取编辑器实例 */
    getEditor: () => editorRef.value,
    /** 设置编辑器内容 */
    setHtml: (html: string) => editorRef.value?.setHtml(html),
    /** 获取编辑器内容 */
    getHtml: () => editorRef.value?.getHtml(),
    /** 清空编辑器 */
    clear: () => editorRef.value?.clear(),
    /** 聚焦编辑器 */
    focus: () => editorRef.value?.focus()
  })

  // 生命周期
  onMounted(() => {
    // 图标替换已在 onCreateEditor 中处理
  })

  onBeforeUnmount(() => {
    const editor = editorRef.value
    if (editor) {
      editor.destroy()
    }
  })
</script>

<style lang="scss">
  @use './style';
  /* 提升全局弹层，避免被编辑器覆盖 */
  .el-overlay,
  .el-message-box__wrapper {
    z-index: 5000 !important;
  }
  /* 确保下拉选择等 Popper 浮层在对话框之上 */
  .el-popper {
    z-index: 6000 !important;
  }
</style>
