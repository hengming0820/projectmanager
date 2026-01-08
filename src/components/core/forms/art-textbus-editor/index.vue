<!-- XNote 富文本编辑器 - 极简封装 -->
<template>
  <div class="xnote-editor-wrapper">
    <!-- 顶部静态工具栏容器 -->
    <div v-if="showStaticToolbar" ref="toolbarRef" class="xnote-toolbar-container"></div>
    <!-- 编辑器容器 -->
    <div ref="editorRef" class="xnote-editor"></div>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import axios from 'axios'

  interface Props {
    modelValue?: string
    height?: string
    placeholder?: string
    readonly?: boolean
    // 协作配置
    documentId?: string
    collaborationEnabled?: boolean
    currentUser?: {
      id: string
      username: string
      realName?: string // 真实姓名，用于显示
      color?: string
    }
    // 自动保存配置
    autoSave?: boolean // 是否启用自动保存
    autoSaveInterval?: number // 自动保存间隔（毫秒），默认 30秒
    // 工具栏配置
    showStaticToolbar?: boolean // 是否显示顶部静态工具栏（默认 false，悬浮工具栏始终启用）
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
    height: '600px',
    placeholder: '点击此处开始编辑...',
    readonly: false,
    documentId: '',
    collaborationEnabled: false,
    currentUser: undefined,
    autoSave: false,
    autoSaveInterval: 30000, // 默认 30 秒
    showStaticToolbar: false // 默认不显示静态工具栏
  })

  const emit = defineEmits<{
    'update:modelValue': [value: string]
    change: [value: string]
    ready: [editor: any]
    'collaboration-users-change': [
      users: Array<{ id: string; username: string; color: string; isSelf?: boolean }>
    ]
    'auto-save': [content: string] // 自动保存事件
  }>()

  const editorRef = ref<HTMLElement | null>(null)
  const toolbarRef = ref<HTMLElement | null>(null)
  let editorInstance: any = null

  // 协作用户列表
  const collaborationUsers = ref<
    Array<{
      id: string
      username: string
      color: string
      isSelf?: boolean
    }>
  >([])

  // 协作连接器实例
  let collaborationConnector: any = null

  // 自动保存定时器（使用去抖动）
  let autoSaveTimer: NodeJS.Timeout | null = null
  let lastSavedContent = '' // 记录上次保存的内容，避免重复保存
  let yjsDoc: any = null // Yjs 文档实例

  // 自动保存函数（去抖动）
  const triggerAutoSave = () => {
    if (!editorInstance || !props.autoSave) return

    // 清除之前的定时器（去抖动）
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer)
    }

    // 延迟保存（用户停止输入后 3 秒保存）
    autoSaveTimer = setTimeout(() => {
      try {
        const currentContent = editorInstance.getHTML()

        // 只有内容变化时才保存
        if (currentContent !== lastSavedContent) {
          console.log('💾 [XNote] 自动保存触发 (去抖动):', {
            contentLength: currentContent.length,
            documentId: props.documentId
          })

          lastSavedContent = currentContent
          emit('auto-save', currentContent)
        }
      } catch (error) {
        console.error('❌ [XNote] 自动保存失败:', error)
      }
    }, 3000) // 3秒去抖动
  }

  // 监听 Yjs 文档更新（协作模式）
  const setupYjsAutoSave = (yDoc: any) => {
    if (!props.autoSave || !yDoc) return

    yjsDoc = yDoc
    console.log('⏰ [XNote] 启动 Yjs 更新监听（协作模式自动保存）')

    // 监听 Yjs 文档的任何更新
    yDoc.on('update', (update: Uint8Array, origin: any) => {
      // origin 为 null 表示是本地操作，否则是远程操作
      console.log('📝 [XNote] Yjs 文档更新:', {
        updateSize: update.length,
        origin: origin ? 'remote' : 'local',
        documentId: props.documentId
      })

      // 触发去抖动保存
      triggerAutoSave()
    })

    console.log('✅ [XNote] Yjs 自动保存监听已启动')
  }

  // 启动自动保存（非协作模式，使用定时轮询）
  const startAutoSave = () => {
    if (!props.autoSave || props.collaborationEnabled) return

    console.log(`⏰ [XNote] 启动自动保存（定时轮询模式），间隔: ${props.autoSaveInterval}ms`)

    // 非协作模式下，使用定时轮询
    const pollInterval = setInterval(() => {
      if (!editorInstance) return

      try {
        const currentContent = editorInstance.getHTML()

        if (currentContent !== lastSavedContent) {
          lastSavedContent = currentContent
          emit('auto-save', currentContent)
        }
      } catch (error) {
        console.error('❌ [XNote] 自动保存失败:', error)
      }
    }, props.autoSaveInterval)

    // 保存定时器引用以便清理
    ;(editorInstance as any)._autoSavePollInterval = pollInterval
  }

  // 停止自动保存
  const stopAutoSave = () => {
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer)
      autoSaveTimer = null
    }

    // 清理 Yjs 监听
    if (yjsDoc) {
      try {
        yjsDoc.off('update')
        console.log('⏹️ [XNote] Yjs 自动保存监听已停止')
      } catch (e) {
        console.warn('⚠️ [XNote] 清理 Yjs 监听失败:', e)
      }
      yjsDoc = null
    }

    // 清理定时轮询
    if (editorInstance && (editorInstance as any)._autoSavePollInterval) {
      clearInterval((editorInstance as any)._autoSavePollInterval)
      ;(editorInstance as any)._autoSavePollInterval = null
    }

    console.log('⏹️ [XNote] 自动保存已停止')
  }

  // 设置协作监听器 - 使用官方 API（暂时简化）
  const setupCollaborationListeners = async (editorInstance: any) => {
    try {
      console.log('👥 [XNote] 开始设置协作监听器')

      // 使用延迟初始化，避免堆栈溢出
      setTimeout(async () => {
        try {
          const { XNoteMessageBus } = await import('@textbus/xnote')
          const msgBus = editorInstance.get(XNoteMessageBus)

          msgBus.onMessageChange.subscribe((msgs: any[]) => {
            const users = msgs.map((i: any) => {
              const user = i.message
              return {
                id: user.id,
                username: user.username, // 这里保持 username，因为它来自 Yjs
                color: user.color || '#6b7280',
                isSelf: user.id === props.currentUser?.id
              }
            })
            collaborationUsers.value = users
            emit('collaboration-users-change', users)
            console.log('👥 [XNote] 协作用户更新:', users.length, users)
          })
          console.log('✅ [XNote] 协作监听器已设置')
        } catch (error) {
          console.warn('⚠️ [XNote] XNoteMessageBus 初始化失败:', error)
          // 降级方案：只显示当前用户
          if (props.currentUser) {
            collaborationUsers.value = [
              {
                id: props.currentUser.id,
                username: props.currentUser.username,
                color: props.currentUser.color || '#4ade80',
                isSelf: true
              }
            ]
            emit('collaboration-users-change', collaborationUsers.value)
          }
        }
      }, 1000) // 延迟 1 秒，确保编辑器完全初始化
    } catch (error) {
      console.warn('⚠️ [XNote] 协作监听器设置失败:', error)
    }
  }

  // 动态注入暗色模式样式
  const injectDarkModeStyles = () => {
    // 检查是否为暗色模式
    const isDark = document.documentElement.classList.contains('dark')
    if (!isDark) return

    console.log('🌙 [XNote] 注入暗色模式样式')

    // 创建 MutationObserver 监听 DOM 变化
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            // 元素节点
            const element = node as HTMLElement

            // 检查元素的背景色
            const style = window.getComputedStyle(element)
            const bgColor = style.backgroundColor

            // 如果是白色背景，强制改为暗色
            if (
              bgColor === 'rgb(255, 255, 255)' ||
              bgColor === '#fff' ||
              bgColor === '#ffffff' ||
              bgColor === 'white'
            ) {
              element.style.setProperty('background-color', 'var(--art-main-bg-color)', 'important')
              console.log('🔧 [XNote] 修复白色背景元素:', element.className)
            }

            // 递归检查子元素
            element.querySelectorAll('*').forEach((child) => {
              const childStyle = window.getComputedStyle(child as HTMLElement)
              const childBgColor = childStyle.backgroundColor

              if (
                childBgColor === 'rgb(255, 255, 255)' ||
                childBgColor === '#fff' ||
                childBgColor === '#ffffff' ||
                childBgColor === 'white'
              ) {
                ;(child as HTMLElement).style.setProperty(
                  'background-color',
                  'var(--art-main-bg-color)',
                  'important'
                )
              }
            })
          }
        })
      })
    })

    // 监听整个 body
    observer.observe(document.body, {
      childList: true,
      subtree: true
    })

    // 立即检查现有元素
    setTimeout(() => {
      // 特别检查工具栏
      const toolbars = document.querySelectorAll('[class*="toolbar"]')
      toolbars.forEach((toolbar) => {
        const style = window.getComputedStyle(toolbar as HTMLElement)
        const bgColor = style.backgroundColor

        console.log('🔍 [XNote] 检查工具栏:', toolbar.className, '背景色:', bgColor)

        if (
          bgColor === 'rgb(255, 255, 255)' ||
          bgColor === '#fff' ||
          bgColor === '#ffffff' ||
          bgColor === 'white' ||
          bgColor === 'rgba(255, 255, 255, 1)'
        ) {
          ;(toolbar as HTMLElement).style.setProperty(
            'background',
            'var(--art-main-bg-color)',
            'important'
          )
          ;(toolbar as HTMLElement).style.setProperty(
            'background-color',
            'var(--art-main-bg-color)',
            'important'
          )
          console.log('🔧 [XNote] ✅ 修复工具栏白色背景:', toolbar.className)
        }
      })

      // 检查所有 TextBus/XNote 元素
      document.querySelectorAll('[class*="textbus"], [class*="xnote"]').forEach((element) => {
        const style = window.getComputedStyle(element as HTMLElement)
        const bgColor = style.backgroundColor

        if (
          bgColor === 'rgb(255, 255, 255)' ||
          bgColor === '#fff' ||
          bgColor === '#ffffff' ||
          bgColor === 'white' ||
          bgColor === 'rgba(255, 255, 255, 1)'
        ) {
          ;(element as HTMLElement).style.setProperty(
            'background',
            'var(--art-main-bg-color)',
            'important'
          )
          ;(element as HTMLElement).style.setProperty(
            'background-color',
            'var(--art-main-bg-color)',
            'important'
          )
          console.log('🔧 [XNote] 修复现有白色背景元素:', element.className)
        }
      })
    }, 100)

    // 每隔 500ms 检查一次（针对动态创建的元素）
    const interval = setInterval(() => {
      // 优先检查工具栏
      document.querySelectorAll('[class*="toolbar"]').forEach((toolbar) => {
        const style = window.getComputedStyle(toolbar as HTMLElement)
        const bgColor = style.backgroundColor

        if (
          bgColor === 'rgb(255, 255, 255)' ||
          bgColor === '#fff' ||
          bgColor === '#ffffff' ||
          bgColor === 'white' ||
          bgColor === 'rgba(255, 255, 255, 1)'
        ) {
          ;(toolbar as HTMLElement).style.setProperty(
            'background',
            'var(--art-main-bg-color)',
            'important'
          )
          ;(toolbar as HTMLElement).style.setProperty(
            'background-color',
            'var(--art-main-bg-color)',
            'important'
          )
        }
      })

      // 检查所有 TextBus/XNote 元素
      document.querySelectorAll('[class*="textbus"], [class*="xnote"]').forEach((element) => {
        const style = window.getComputedStyle(element as HTMLElement)
        const bgColor = style.backgroundColor

        if (
          bgColor === 'rgb(255, 255, 255)' ||
          bgColor === '#fff' ||
          bgColor === '#ffffff' ||
          bgColor === 'white' ||
          bgColor === 'rgba(255, 255, 255, 1)'
        ) {
          ;(element as HTMLElement).style.setProperty(
            'background',
            'var(--art-main-bg-color)',
            'important'
          )
          ;(element as HTMLElement).style.setProperty(
            'background-color',
            'var(--art-main-bg-color)',
            'important'
          )
        }
      })
    }, 500)

    // 组件卸载时清理
    onBeforeUnmount(() => {
      observer.disconnect()
      clearInterval(interval)
    })
  }

  // 文件上传器
  class CustomFileUploader {
    async uploadFile(type: string): Promise<string> {
      return new Promise((resolve, reject) => {
        const input = document.createElement('input')
        input.type = 'file'

        if (type === 'image') {
          input.accept = 'image/*'
        } else if (type === 'video') {
          input.accept = 'video/*'
        }

        input.onchange = async (e: any) => {
          const file = e.target?.files?.[0]
          if (!file) {
            reject(new Error('未选择文件'))
            return
          }

          try {
            console.log('📤 [XNote] 开始上传文件到 MinIO:', file.name, file.type)

            // 创建 FormData
            const formData = new FormData()
            formData.append('file', file)

            // 上传到服务器（MinIO）- 使用后端的通用图片上传接口
            const response = await axios.post('/api/common/upload/images', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })

            // 后端返回格式：{ code: 200, message: "上传成功", data: { files: [{url, ...}], count } }
            if (
              response.data &&
              response.data.code === 200 &&
              response.data.data?.files?.length > 0
            ) {
              const imageUrl = response.data.data.files[0].url
              console.log('✅ [XNote] 文件上传成功:', imageUrl)
              ElMessage.success('图片上传成功')
              resolve(imageUrl)
            } else {
              throw new Error('上传响应格式错误')
            }
          } catch (error: any) {
            console.error('❌ [XNote] 文件上传失败:', error)
            ElMessage.error(`图片上传失败: ${error.response?.data?.detail || error.message}`)

            // 如果上传失败，降级为 base64（临时方案）
            console.warn('⚠️ [XNote] 降级使用 base64 编码')
            const reader = new FileReader()
            reader.onload = (e) => {
              resolve(e.target?.result as string)
            }
            reader.onerror = () => reject(new Error('文件读取失败'))
            reader.readAsDataURL(file)
          }
        }

        input.click()
      })
    }
  }

  // 初始化编辑器
  const initEditor = async () => {
    if (!editorRef.value) return

    try {
      // 动态导入 XNote
      const { Editor, FileUploader, StaticToolbarPlugin } = await import('@textbus/xnote')

      // 最简单的编辑器配置 - 让 XNote 使用默认设置
      const editorConfig: any = {
        readonly: props.readonly,
        placeholder: props.placeholder,
        providers: [
          {
            provide: FileUploader,
            useValue: new CustomFileUploader()
          }
        ]
        // ❌ 不要设置 plugins: []，这会覆盖默认的 LeftToolbarPlugin 和 InlineToolbarPlugin
        // ✅ 让 XNote 使用默认插件配置（来自 editor.tsx 第351行）
      }

      // 只有在有内容时才设置 content
      if (props.modelValue && props.modelValue.trim()) {
        editorConfig.content = props.modelValue
        console.log('📝 [XNote] 加载已有内容，长度:', props.modelValue.length)
      } else {
        console.log('📝 [XNote] 创建空白编辑器')
      }

      // ✅ 如果需要顶部静态工具栏，可以额外添加 StaticToolbarPlugin
      // ⚠️ 注意：这会与默认的 LeftToolbarPlugin 同时显示
      if (props.showStaticToolbar && toolbarRef.value) {
        const isDark = document.documentElement.classList.contains('dark')
        const staticToolbarPlugin = new StaticToolbarPlugin({
          host: toolbarRef.value,
          theme: isDark ? 'dark' : 'light'
        })
        // 手动添加 plugins 数组（会与默认插件合并）
        if (!editorConfig.plugins) {
          editorConfig.plugins = []
        }
        editorConfig.plugins.push(staticToolbarPlugin)
        console.log('🔧 [XNote] 启用顶部静态工具栏（叠加模式）')
      }

      // 如果启用协作功能，添加协作配置（按照官方文档）
      if (props.collaborationEnabled && props.documentId && props.currentUser) {
        console.log('🤝 [XNote] 启用协作模式，文档ID:', props.documentId)

        try {
          // 动态导入协作模块
          const { YWebsocketConnector } = await import('@textbus/collaborate')

          // 生成用户颜色（如果未提供）
          const userColor =
            props.currentUser.color || `#${Math.floor(Math.random() * 16777215).toString(16)}`

          // 按照官方文档配置协作
          // 注意：username 字段会显示在编辑器光标上，所以用 realName 或 username
          const displayName = props.currentUser.realName || props.currentUser.username
          editorConfig.collaborateConfig = {
            userinfo: {
              id: props.currentUser.id,
              username: displayName, // 使用真实姓名（如果有）
              color: userColor
            },
            createConnector(yDoc: any) {
              try {
                // 构建 WebSocket URL
                const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
                const wsHost = window.location.host
                const wsUrl = `${wsProtocol}//${wsHost}/api/collaboration/yjs`

                console.log('🔌 [XNote] 创建协作连接器')
                console.log('   └─ URL:', wsUrl)
                console.log('   └─ 文档ID:', props.documentId)
                console.log('   └─ 用户:', props.currentUser?.username)

                // 保存 Yjs 文档实例（用于自动保存）
                yjsDoc = yDoc

                // 创建连接器（按照官方文档的方式）
                const connector = new YWebsocketConnector(wsUrl, props.documentId, yDoc)
                collaborationConnector = connector

                console.log('✅ [XNote] 协作连接器创建成功')

                // 设置 Yjs 自动保存监听（在连接器创建后）
                if (props.autoSave) {
                  setTimeout(() => {
                    setupYjsAutoSave(yDoc)
                  }, 1000) // 延迟 1 秒，确保连接已建立
                }

                return connector
              } catch (error) {
                console.error('❌ [XNote] 创建协作连接器失败:', error)
                throw error
              }
            }
          }

          console.log('✅ [XNote] 协作配置已添加到编辑器')
        } catch (error) {
          console.error('❌ [XNote] 协作配置失败:', error)
          ElMessage.warning('协作功能初始化失败，将使用单机模式')
          // 不抛出错误，让编辑器继续初始化（单机模式）
        }
      }

      // 创建编辑器
      editorInstance = new Editor(editorConfig)

      // 挂载编辑器
      await editorInstance.mount(editorRef.value)
      console.log('✅ [XNote] 编辑器初始化成功')

      // 动态注入暗色模式样式（针对内联样式）
      injectDarkModeStyles()

      // 监听内容变化（协作模式下由 Yjs 自动同步）
      if (!props.collaborationEnabled) {
        setupChangeListener()
      } else {
        console.log('🤝 [XNote] 协作模式：内容同步由 Yjs 管理')

        // 设置协作监听器（使用延迟初始化避免堆栈溢出）
        setupCollaborationListeners(editorInstance)
      }

      // 启动自动保存（如果启用）
      if (props.autoSave) {
        startAutoSave()
      }

      emit('ready', editorInstance)
    } catch (error) {
      console.error('❌ [XNote] 编辑器初始化失败:', error)
      ElMessage.error('编辑器初始化失败')
    }
  }

  // 设置内容变化监听
  const setupChangeListener = () => {
    if (!editorInstance) return

    // 使用轮询监听内容变化（简单可靠）
    let lastContent = props.modelValue || ''
    const pollInterval = setInterval(() => {
      if (!editorInstance || typeof editorInstance.getHTML !== 'function') {
        clearInterval(pollInterval)
        return
      }

      try {
        const currentContent = editorInstance.getHTML() || ''
        if (currentContent !== lastContent) {
          lastContent = currentContent
          emit('update:modelValue', currentContent)
          emit('change', currentContent)
        }
      } catch (e) {
        console.warn('⚠️ [XNote] 获取内容失败:', e)
      }
    }, 500)

    // 保存定时器引用
    ;(editorInstance as any)._pollInterval = pollInterval
  }

  // 监听外部内容变化
  watch(
    () => props.modelValue,
    (newVal) => {
      if (editorInstance && newVal !== editorInstance.getHTML()) {
        try {
          editorInstance.setContent(newVal || `<p>${props.placeholder}</p>`)
        } catch (error) {
          console.warn('⚠️ [XNote] 设置内容失败:', error)
        }
      }
    }
  )

  // 🔥 修复工具栏容器的 overflow - 确保工具栏不被裁剪
  const fixToolbarContainerOverflow = () => {
    if (!editorRef.value) return

    console.log('🔧 [XNote] 开始修复工具栏容器的 overflow...')

    // 查找所有工具栏元素
    const toolbarSelectors = [
      '.left-toolbar',
      '.toolbar',
      '.inline-toolbar',
      '[class*="toolbar"]'
    ]

    toolbarSelectors.forEach((selector) => {
      const toolbars = editorRef.value?.querySelectorAll(selector)
      if (!toolbars || toolbars.length === 0) return

      toolbars.forEach((toolbar) => {
        console.log('✅ [XNote] 找到工具栏:', toolbar.className)
        
        // 向上遍历所有父容器，设置 overflow: visible
        let parent = toolbar.parentElement
        let level = 0
        // 增加遍历深度到 20 层，确保能覆盖到最外层的容器
        while (parent && level < 20) {
          const currentOverflow = window.getComputedStyle(parent).overflow
          if (currentOverflow !== 'visible') {
            console.log(`  📦 修复父容器 (level ${level}):`, parent.className || parent.tagName, `overflow: ${currentOverflow} -> visible`)
            ;(parent as HTMLElement).style.setProperty('overflow', 'visible', 'important')
            ;(parent as HTMLElement).style.setProperty('overflow-x', 'visible', 'important')
            ;(parent as HTMLElement).style.setProperty('overflow-y', 'visible', 'important')
          }
          parent = parent.parentElement
          level++
        }
      })
    })

    console.log('✅ [XNote] 工具栏容器 overflow 修复完成')
  }

  // 修复协作光标标签位置 - 防止边缘遮挡
  const fixCursorLabelPositions = () => {
    if (!editorRef.value) return

    // 查找所有可能的光标标签元素
    const labelSelectors = [
      '.remote-caret',
      '.remote-cursor',
      '[class*="remote-caret"]',
      '[class*="yjs-cursor"]',
      '[class*="cursor"][class*="label"]',
      '.yRemoteSelectionHead'
    ]

    labelSelectors.forEach((selector) => {
      const labels = editorRef.value?.querySelectorAll(selector)
      if (!labels) return

      labels.forEach((label) => {
        const rect = label.getBoundingClientRect()
        const editorRect = editorRef.value!.getBoundingClientRect()

        // 检查是否接近右边缘（距离小于 150px）
        const distanceToRight = editorRect.right - rect.right
        if (distanceToRight < 150 && distanceToRight > 0) {
          // 添加类名，通过 CSS 调整位置
          ;(label as HTMLElement).classList.add('near-right-edge')
        } else {
          ;(label as HTMLElement).classList.remove('near-right-edge')
        }

        // 检查是否接近左边缘
        const distanceToLeft = rect.left - editorRect.left
        if (distanceToLeft < 20 && distanceToLeft > 0) {
          ;(label as HTMLElement).classList.add('near-left-edge')
        } else {
          ;(label as HTMLElement).classList.remove('near-left-edge')
        }
      })
    })
  }

  // 使用 MutationObserver 监听 DOM 变化（光标位置变化 + 工具栏插入）
  let cursorObserver: MutationObserver | null = null
  const startCursorObserver = () => {
    if (!editorRef.value) return

    cursorObserver = new MutationObserver(() => {
      fixCursorLabelPositions()
      // 🔥 每次 DOM 变化时也检查工具栏容器
      fixToolbarContainerOverflow()
    })

    cursorObserver.observe(editorRef.value, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style', 'class']
    })

    // 初始调整
    fixCursorLabelPositions()
    // 🔥 初始修复工具栏容器
    fixToolbarContainerOverflow()

    // 监听窗口大小变化
    window.addEventListener('resize', fixCursorLabelPositions)
  }

  const stopCursorObserver = () => {
    if (cursorObserver) {
      cursorObserver.disconnect()
      cursorObserver = null
    }
    window.removeEventListener('resize', fixCursorLabelPositions)
  }

  onMounted(() => {
    initEditor()
    // 延迟启动光标观察器，等待编辑器完全初始化
    setTimeout(startCursorObserver, 2000)
    // 🔥 多次尝试修复工具栏容器（因为工具栏可能延迟插入）
    setTimeout(fixToolbarContainerOverflow, 1000)
    setTimeout(fixToolbarContainerOverflow, 3000)
    setTimeout(fixToolbarContainerOverflow, 5000)
  })

  onBeforeUnmount(() => {
    // 停止光标观察器
    stopCursorObserver()
    // 停止自动保存
    stopAutoSave()

    // 清理协作连接
    if (collaborationConnector) {
      try {
        collaborationConnector.destroy?.()
      } catch (e) {
        console.warn('⚠️ [XNote] 清理协作连接失败:', e)
      }
      collaborationConnector = null
    }

    // 清理用户列表
    collaborationUsers.value = []

    if (editorInstance) {
      // 清理定时器
      const pollInterval = (editorInstance as any)._pollInterval
      if (pollInterval) {
        clearInterval(pollInterval)
      }

      // 销毁编辑器
      try {
        editorInstance.destroy?.()
      } catch (e) {
        console.warn('⚠️ [XNote] 销毁编辑器失败:', e)
      }
      editorInstance = null
    }
  })
</script>

<style lang="scss">
  /* XNote 编辑器容器样式 - 最简单配置 */
  .xnote-editor-wrapper {
    width: 100%;
    height: v-bind(height);
    position: relative;
    background: var(--art-main-bg-color);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    overflow: visible; /* 🔥 关键修复：允许工具栏溢出到容器外部 */
  }

  /* 顶部工具栏容器 */
  .xnote-toolbar-container {
    flex-shrink: 0;
    border-bottom: 1px solid var(--art-card-border);
    background: var(--art-main-bg-color);
    z-index: 999999; /* 工具栏在最顶层 */

    :deep(.textbus-toolbar) {
      background: var(--art-main-bg-color) !important;
      border: none !important;
    }
  }

  .xnote-editor {
    width: 100%;
    flex: 1;
    position: relative;
    overflow-y: auto;
    overflow-x: visible; /* 🔥 关键修复：允许水平方向溢出（左侧工具栏） */
    
    /* 移除 isolation 以避免创建独立的层叠上下文 */
    /* isolation: isolate; */
    
    /* 确保编辑器内所有元素的 z-index 都小于工具栏 */
    > * {
      z-index: auto;
    }
    
    /* 🔥 核心修复：确保 Textbus 的关键容器都允许溢出 */
    /* 逐个精确定位 XNote/Textbus 的容器 */

    // XNote 编辑器内部样式适配暗色模式 - 使用 !important 强制覆盖

    // 主容器 - 覆盖所有可能的容器类
    :deep(.textbus-container),
    :deep(.xnote-root),
    :deep(.xnote-container) {
      background: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
    }

    // 所有工具栏背景 - 覆盖所有工具栏相关类
    :deep(.textbus-toolbar),
    :deep(.textbus-toolbar-left),
    :deep(.textbus-toolbar-right),
    :deep(.textbus-toolbar-inline),
    :deep(.textbus-toolbar-static),
    :deep(.xnote-toolbar),
    :deep([class*='toolbar']) {
      background: var(--art-main-bg-color) !important;
      background-color: var(--art-main-bg-color) !important;
      border-color: var(--art-card-border) !important;
      z-index: 999999 !important; /* 工具栏在最顶层 */
    }

    // 工具栏项
    :deep(.textbus-toolbar-item),
    :deep(.textbus-toolbar-button) {
      color: var(--art-text-gray-700) !important;
      background: transparent !important;

      &:hover {
        background: var(--art-bg-color) !important;
        color: var(--art-text-gray-900) !important;
      }

      &.textbus-toolbar-item-active,
      &.textbus-toolbar-button-active {
        background: var(--el-color-primary-light-9) !important;
        color: var(--el-color-primary) !important;
      }
    }

    // 下拉菜单和弹出面板
    :deep(.textbus-dropdown),
    :deep(.textbus-dropdown-menu),
    :deep(.textbus-panel),
    :deep(.textbus-popover) {
      background: var(--art-main-bg-color) !important;
      border-color: var(--art-card-border) !important;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2) !important;
      color: var(--art-text-gray-900) !important;
      z-index: 999999 !important; /* 弹出面板也在最顶层 */
    }

    // 下拉菜单项
    :deep(.textbus-dropdown-menu-item),
    :deep(.textbus-menu-item) {
      color: var(--art-text-gray-900) !important;
      background: transparent !important;

      &:hover {
        background: var(--art-bg-color) !important;
      }
    }

    // 按钮
    :deep(.textbus-button) {
      background: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
      border-color: var(--art-card-border) !important;

      &:hover {
        background: var(--art-bg-color) !important;
      }
    }

    // 输入框
    :deep(.textbus-input),
    :deep(input),
    :deep(textarea) {
      background: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
      border-color: var(--art-card-border) !important;

      &::placeholder {
        color: var(--art-text-gray-500) !important;
      }
    }

    // 文档编辑区
    :deep(.textbus-document),
    :deep(.textbus-editor-content) {
      background: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
    }

    // 对话框
    :deep(.textbus-dialog),
    :deep(.textbus-modal) {
      background: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
      border-color: var(--art-card-border) !important;
    }

    // 标签页
    :deep(.textbus-tab) {
      background: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-700) !important;
      border-color: var(--art-card-border) !important;

      &.textbus-tab-active {
        background: var(--art-bg-color) !important;
        color: var(--art-text-gray-900) !important;
      }
    }

    // 分隔线
    :deep(.textbus-divider) {
      border-color: var(--art-card-border) !important;
    }

    // 图标
    :deep(.textbus-icon) {
      color: var(--art-text-gray-700) !important;
    }

    // 颜色选择器
    :deep(.textbus-color-picker),
    :deep(.textbus-color-panel) {
      background: var(--art-main-bg-color) !important;
      border-color: var(--art-card-border) !important;
    }

    // 表格工具
    :deep(.textbus-table-tool),
    :deep(.textbus-table-panel) {
      background: var(--art-main-bg-color) !important;
      border-color: var(--art-card-border) !important;
    }

    // 链接工具
    :deep(.textbus-link-tool),
    :deep(.textbus-link-panel) {
      background: var(--art-main-bg-color) !important;
      border-color: var(--art-card-border) !important;
    }

    // 所有弹出层
    :deep([class*='textbus-']) {
      &[class*='panel'],
      &[class*='dropdown'],
      &[class*='menu'],
      &[class*='picker'],
      &[class*='tool'] {
        background: var(--art-main-bg-color) !important;
        color: var(--art-text-gray-900) !important;
        border-color: var(--art-card-border) !important;
      }
    }

    // 确保所有白色背景都被覆盖
    :deep(*) {
      &[style*='background: white'],
      &[style*='background: #fff'],
      &[style*='background: #ffffff'],
      &[style*='background-color: white'],
      &[style*='background-color: #fff'],
      &[style*='background-color: #ffffff'] {
        background: var(--art-main-bg-color) !important;
      }
    }
  }

  /* 基础样式 - 让 XNote 自己管理工具栏 */

  // 全局样式 - 覆盖挂载在 body 下的 TextBus 弹出层（不使用 scoped）
  :global(body) {
    // ===== 工具栏专用样式（最高优先级） =====
    :global(.textbus-toolbar),
    :global(.xnote-toolbar),
    :global([class*='toolbar']) {
      background: var(--art-main-bg-color) !important;
      background-color: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
      border-color: var(--art-card-border) !important;

      // 工具栏内所有元素
      * {
        background-color: transparent !important;
        color: var(--art-text-gray-900) !important;
      }

      // 工具栏按钮
      :global(button),
      :global(.textbus-toolbar-button),
      :global(.xnote-toolbar-button),
      :global([role='button']) {
        background: transparent !important;
        color: var(--art-text-gray-900) !important;
        border-color: var(--art-card-border) !important;

        &:hover {
          background: var(--art-bg-color) !important;
        }
      }

      // 工具栏分组
      :global(.textbus-toolbar-group),
      :global(.xnote-toolbar-group) {
        background: transparent !important;
        border-color: var(--art-card-border) !important;
      }
    }

    // TextBus 的所有弹出层（可能挂载在 body 下）
    :global(.textbus-dropdown),
    :global(.textbus-dropdown-menu),
    :global(.textbus-panel),
    :global(.textbus-popover),
    :global(.textbus-tooltip),
    :global(.textbus-color-picker),
    :global(.textbus-color-panel),
    :global(.textbus-table-tool),
    :global(.textbus-table-panel),
    :global(.textbus-link-tool),
    :global(.textbus-link-panel),
    :global(.textbus-dialog),
    :global(.textbus-modal),
    :global(.xnote-dropdown),
    :global(.xnote-panel),
    :global(.xnote-popover) {
      background: var(--art-main-bg-color) !important;
      background-color: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
      border-color: var(--art-card-border) !important;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2) !important;

      // 内部元素
      :global(.textbus-dropdown-menu-item),
      :global(.textbus-menu-item),
      :global(.textbus-button),
      :global(.xnote-menu-item) {
        color: var(--art-text-gray-900) !important;
        background: transparent !important;

        &:hover {
          background: var(--art-bg-color) !important;
        }
      }

      :global(input),
      :global(textarea) {
        background: var(--art-main-bg-color) !important;
        color: var(--art-text-gray-900) !important;
        border-color: var(--art-card-border) !important;

        &::placeholder {
          color: var(--art-text-gray-500) !important;
        }
      }
    }

    // 通配符匹配所有 TextBus/XNote 相关的弹出层
    :global([class*='textbus-'][class*='panel']),
    :global([class*='textbus-'][class*='dropdown']),
    :global([class*='textbus-'][class*='menu']),
    :global([class*='textbus-'][class*='picker']),
    :global([class*='textbus-'][class*='tool']),
    :global([class*='xnote-'][class*='panel']),
    :global([class*='xnote-'][class*='dropdown']),
    :global([class*='xnote-'][class*='menu']) {
      background: var(--art-main-bg-color) !important;
      background-color: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
      border-color: var(--art-card-border) !important;
    }

    // 覆盖所有 div 中带有白色背景的内联样式
    :global([class*='textbus-']),
    :global([class*='xnote-']) {
      &:global([style*='background: white']),
      &:global([style*='background: #fff']),
      &:global([style*='background-color: white']),
      &:global([style*='background-color: #fff']) {
        background: var(--art-main-bg-color) !important;
        background-color: var(--art-main-bg-color) !important;
      }
    }
  }
</style>
<!-- 非 scoped 全局样式 - 强制覆盖 TextBus/XNote 样式 -->
<style lang="scss">
  // 覆盖所有 TextBus/XNote 相关元素的背景色
  [class*='textbus-'],
  [class*='xnote-'] {
    &[class*='toolbar'],
    &[class*='panel'],
    &[class*='dropdown'],
    &[class*='menu'],
    &[class*='picker'],
    &[class*='popover'],
    &[class*='tooltip'],
    &[class*='dialog'],
    &[class*='modal'] {
      background: var(--art-main-bg-color) !important;
      background-color: var(--art-main-bg-color) !important;
      color: var(--art-text-gray-900) !important;
    }
  }

  // 特定的工具栏和弹出层
  .textbus-toolbar,
  .textbus-toolbar-left,
  .textbus-toolbar-right,
  .textbus-toolbar-inline,
  .textbus-toolbar-static,
  .xnote-toolbar,
  .textbus-dropdown,
  .textbus-dropdown-menu,
  .textbus-panel,
  .textbus-popover,
  .textbus-tooltip,
  .textbus-color-picker,
  .textbus-color-panel,
  .textbus-table-tool,
  .textbus-table-panel,
  .textbus-link-tool,
  .textbus-link-panel,
  .textbus-dialog,
  .textbus-modal,
  .xnote-dropdown,
  .xnote-panel,
  .xnote-popover {
    background: var(--art-main-bg-color) !important;
    background-color: var(--art-main-bg-color) !important;
    color: var(--art-text-gray-900) !important;
    border-color: var(--art-card-border) !important;
  }

  // 工具栏项和按钮
  .textbus-toolbar-item,
  .textbus-toolbar-button,
  .xnote-toolbar-item {
    color: var(--art-text-gray-700) !important;

    &:hover {
      background: var(--art-bg-color) !important;
      color: var(--art-text-gray-900) !important;
    }
  }

  // 菜单项
  .textbus-dropdown-menu-item,
  .textbus-menu-item,
  .xnote-menu-item {
    color: var(--art-text-gray-900) !important;
    background: transparent !important;

    &:hover {
      background: var(--art-bg-color) !important;
    }
  }

  // 输入框
  .textbus-input,
  .xnote-input {
    background: var(--art-main-bg-color) !important;
    color: var(--art-text-gray-900) !important;
    border-color: var(--art-card-border) !important;

    &::placeholder {
      color: var(--art-text-gray-500) !important;
    }
  }

  // 编辑器容器和文档区
  .textbus-container,
  .textbus-document,
  .textbus-editor-content,
  .xnote-root,
  .xnote-container {
    background: var(--art-main-bg-color) !important;
    color: var(--art-text-gray-900) !important;
  }

  /* 协作光标标签样式优化 - 防止边缘遮挡 */
  :deep(.remote-caret),
  :deep(.remote-cursor),
  :deep([class*='remote-caret']),
  :deep([class*='cursor'][class*='label']),
  :deep([class*='yjs'][class*='cursor']) {
    /* 确保光标标签不被裁剪 */
    overflow: visible !important;
    position: relative !important;
    z-index: 50000 !important; /* 在工具栏之下 */
    
    /* 光标标签容器 */
    > span,
    > div {
      position: absolute !important;
      white-space: nowrap;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12px;
      line-height: 1.4;
      pointer-events: none;
      z-index: 50000 !important; /* 在工具栏之下 */
      
      /* 添加阴影增强可读性 */
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      
      /* 防止文本溢出 */
      max-width: 150px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  /* 修复光标标签在编辑器容器中的定位 */
  :deep(.textbus-container),
  :deep(.textbus-document),
  :deep(.xnote-root) {
    /* 允许子元素溢出显示（光标标签） */
    overflow: visible !important;
    
    /* 但内容区域仍然需要滚动 */
    > * {
      position: relative;
    }
  }

  /* 特别处理：当光标接近右边缘时，调整标签位置 */
  :deep(.near-right-edge) {
    /* 标签显示在光标左侧 */
    span,
    div,
    &::after {
      transform: translateX(-100%) !important;
      left: auto !important;
      right: 0 !important;
    }
  }

  /* 当光标接近左边缘时，确保标签显示在光标右侧 */
  :deep(.near-left-edge) {
    span,
    div,
    &::after {
      transform: translateX(0) !important;
      left: 0 !important;
      right: auto !important;
    }
  }

  /* Yjs 远程光标特定样式 */
  :deep(.yRemoteSelection) {
    position: relative;
    z-index: 50000 !important; /* 在工具栏之下 */
    pointer-events: none;
  }

  :deep(.yRemoteSelectionHead) {
    position: absolute;
    pointer-events: none;
    z-index: 50000 !important; /* 在工具栏之下 */
    
    /* 光标名称标签 */
    &::after {
      content: attr(data-username);
      position: absolute;
      top: -20px;
      left: 0;
      padding: 2px 6px;
      border-radius: 4px;
      background: inherit;
      color: white;
      font-size: 12px;
      white-space: nowrap;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      z-index: 50000 !important; /* 在工具栏之下 */
      
      /* 当标签可能超出右边缘时，调整位置 */
      max-width: 150px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  /* 强制覆盖所有可能的工具栏 z-index */
  :deep(.left-toolbar),
  :deep(.toolbar),
  :deep(.inline-toolbar),
  :deep([class*='toolbar']),
  :deep([class*='Toolbar']),
  :deep([data-toolbar]),
  :deep(div[class*='tool']),
  :deep(div[class*='Tool']) {
    z-index: 999999 !important; /* 工具栏在最顶层 */
    max-height: none !important; /* 防止工具栏裁剪 */
  }

  /* 左侧工具栏特别处理 */
  :deep(.left-toolbar),
  :deep(.left-toolbar .left-toolbar-btn),
  :deep(.left-toolbar .left-toolbar-btn-wrap),
  :deep(.left-toolbar button) {
    z-index: 999999 !important;
  }

  /* 强制所有弹出层也在最顶层 */
  :deep([class*='dropdown']),
  :deep([class*='popover']),
  :deep([class*='tooltip']),
  :deep([class*='menu']),
  :deep([class*='panel']) {
    z-index: 999999 !important;
  }

  /* 确保编辑器内容区域允许光标标签溢出 */
  :deep(.ProseMirror),
  :deep([contenteditable='true']) {
    position: relative;
    overflow: visible !important;
  }
</style>

<!-- 全局样式：正确的层级关系 -->
<style lang="scss">
/* 使用非 scoped 样式，确保能覆盖 Textbus 内部的所有样式 */

/* 层级关系（从高到低）：
   999999 - 工具栏（最顶层，不能被遮挡）
   50000  - 协作光标标签（在工具栏之下，内容之上）
   1      - 编辑内容（最底层）
*/

/* ========== 关键修复：使用多重选择器提高优先级 ========== */

/* 左侧工具栏（优先级最高的覆盖） */
.xnote-editor .left-toolbar,
.xnote-editor-wrapper .left-toolbar,
div.left-toolbar,
.left-toolbar {
  z-index: 999999 !important;
}

/* 左侧工具栏的按钮和菜单 */
.left-toolbar .left-toolbar-btn,
.left-toolbar .left-toolbar-btn-wrap,
.left-toolbar button,
.left-toolbar [class*='dropdown'],
.left-toolbar [class*='menu'] {
  z-index: 999999 !important;
}

/* 行内工具栏（InlineToolbar）*/
.xnote-editor .toolbar,
.xnote-editor-wrapper .toolbar,
div.toolbar,
.toolbar,
.inline-toolbar {
  z-index: 999999 !important;
}

/* 确保所有工具栏在最顶层 */
[class*='toolbar'],
[class*='Toolbar'],
[data-toolbar],
.suspension-toolbar,
.static-toolbar,
div[class*='tool'],
div[class*='Tool'] {
  z-index: 999999 !important;
}

/* 工具栏的所有下拉菜单、弹出层（使用更高特异性） */
.left-toolbar [class*='dropdown'],
.left-toolbar [class*='menu'],
.toolbar [class*='dropdown'],
.toolbar [class*='menu'],
[class*='toolbar'] [class*='dropdown'],
[class*='toolbar'] [class*='popover'],
[class*='toolbar'] [class*='tooltip'],
[class*='toolbar'] [class*='menu'],
[class*='toolbar'] [class*='panel'],
[class*='toolbar'] [class*='popup'],
[class*='dropdown'],
[class*='popover'],
[class*='tooltip'],
[class*='menu'],
[class*='panel'],
[class*='popup'] {
  z-index: 999999 !important;
}

/* 协作光标标签在工具栏之下 */
.remote-caret,
.remote-cursor,
[class*='remote-caret'],
[class*='cursor'][class*='label'],
[class*='yjs'][class*='cursor'],
.yRemoteSelection,
.yRemoteSelectionHead {
  z-index: 50000 !important;
  
  span,
  div {
    z-index: 50000 !important;
  }
  
  &::after,
  &::before {
    z-index: 50000 !important;
  }
}
</style>
