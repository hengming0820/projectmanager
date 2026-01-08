import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/userApi'
import type { User, UserCreate, UserUpdate } from '@/types/project'
import { LanguageEnum } from '@/enums/appEnum'

export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const total = ref(0)

  // 初始化登录状态（检查localStorage中的token）
  const isLogin = ref(false)
  const token = ref('')

  // 初始化恢复登录状态
  const initLoginState = () => {
    // 优先从 localStorage 读取（支持多标签页共享）
    const savedToken = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (savedToken) {
      token.value = savedToken
      // 如果是从 sessionStorage 迁移，同步到 localStorage
      if (!localStorage.getItem('token') && sessionStorage.getItem('token')) {
        localStorage.setItem('token', savedToken)
        sessionStorage.removeItem('token')
      }
      // 不直接标记已登录，交由路由守卫通过 /auth/me 校验后再设为 true，避免"伪登录"状态
      console.log('🔑 [UserStore] 从 localStorage 恢复 token，待校验')
    }
  }

  // 初始化时执行
  initLoginState()
  const userStats = ref({
    total_users: 0,
    active_users: 0,
    inactive_users: 0,
    admin_users: 0,
    annotator_users: 0
  })
  // 语言（用于头部栏语言初始化等）
  const language = ref<LanguageEnum>(LanguageEnum.ZH)

  // 锁屏相关状态
  const isLock = ref(false)
  const lockPassword = ref('')

  // 通知 WebSocket（审核员/管理员）
  let notifySocket: WebSocket | null = null
  let reconnectTimer: number | null = null // 重连定时器
  let heartbeatTimer: number | null = null // 心跳定时器
  let reconnectAttempts = 0 // 重连尝试次数
  const MAX_RECONNECT_ATTEMPTS = 10 // 最大重连次数
  const RECONNECT_DELAY = 3000 // 重连延迟（毫秒）
  const HEARTBEAT_INTERVAL = 30000 // 心跳间隔（30秒）

  // 消息去重机制：记录最近处理过的消息
  const processedMessages = new Map<string, number>() // key: 消息唯一标识, value: 处理时间戳
  const MESSAGE_DEDUPE_WINDOW = 3000 // 3秒内的重复消息会被过滤

  // 定期清理过期的消息记录，防止内存泄漏
  setInterval(() => {
    const now = Date.now()
    const expiredKeys: string[] = []
    processedMessages.forEach((timestamp, key) => {
      if (now - timestamp > MESSAGE_DEDUPE_WINDOW) {
        expiredKeys.push(key)
      }
    })
    expiredKeys.forEach((key) => processedMessages.delete(key))
    if (expiredKeys.length > 0) {
      console.log(`🧹 [WS] 清理了 ${expiredKeys.length} 条过期消息记录`)
    }
  }, 10000) // 每10秒清理一次

  // 浏览器系统通知（Windows/ macOS 原生提示）
  const canUseNotification = () => typeof window !== 'undefined' && 'Notification' in window
  const ensureNotificationPermission = async (): Promise<boolean> => {
    try {
      if (!canUseNotification()) return false
      if ((window as any).Notification.permission === 'granted') return true
      if ((window as any).Notification.permission !== 'denied') {
        const perm = await (window as any).Notification.requestPermission()
        return perm === 'granted'
      }
      return false
    } catch {
      return false
    }
  }
  const showSystemNotification = async (title: string, body: string) => {
    try {
      if (!canUseNotification()) return false
      const ok = await ensureNotificationPermission()
      if (!ok) return false
      const n = new (window as any).Notification(title, {
        body,
        icon: '/xingxiang_logo.ico',
        tag: 'pm-notify',
        renotify: true
      })
      n.onclick = () => {
        try {
          window.focus()
        } catch {}
      }
      return true
    } catch {
      return false
    }
  }
  const shouldConnectNotify = () => {
    const u: any = currentUser.value
    if (!u) {
      console.log('🔔 [WS] 跳过连接：未登录用户')
      return false
    }
    const role = (u.role || '').toLowerCase()
    const rolesArr: string[] = Array.isArray(u.roles) ? u.roles : []
    const isReviewer = role === 'reviewer' || rolesArr.includes('R_REVIEWER')
    const isAdmin = role === 'admin' || rolesArr.includes('R_ADMIN')
    const isAnnotator = role === 'annotator' || rolesArr.includes('R_ANNOTATOR')
    const should = true // 登录用户统一建立 WS 连接，用于接收各类通知
    console.log('🔔 [WS] 角色判定:', {
      role,
      rolesArr,
      isReviewer,
      isAdmin,
      isAnnotator,
      shouldConnect: should
    })
    return should
  }
  const buildWsUrl = (path: string) => {
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    const envUrl = (import.meta as any).env?.VITE_API_URL as string | undefined
    let host = location.host
    try {
      if (envUrl && /^https?:\/\//i.test(envUrl)) {
        host = new URL(envUrl).host
      } else {
        // 非 http(s) 开头的一律使用当前 host
        host = location.host
      }
    } catch (e) {
      host = location.host
    }
    const url = `${protocol}://${host}${path}`
    console.log('🔔 [WS] 构造 URL:', { envUrl, host, path, url })
    return url
  }
  const connectNotifyWS = () => {
    try {
      if (!shouldConnectNotify()) {
        console.log('🔔 [WS] 不需要建立连接（用户未登录或角色不符）')
        return
      }

      // 检查现有连接状态
      if (notifySocket) {
        const state = notifySocket.readyState
        const stateNames = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED']
        console.log(`🔔 [WS] 现有连接状态: ${stateNames[state]} (${state})`)

        if (state === 0 || state === 1) {
          console.log('🔔 [WS] 连接正在进行或已打开，跳过重连')
          return
        } else {
          console.log('🔔 [WS] 连接已关闭，清理旧连接')
          notifySocket = null
        }
      }

      const user: any = currentUser.value

      // 修复角色判断逻辑，确保审核员角色正确识别
      let userRole = (user.role || '').toLowerCase()
      const rolesArr: string[] = Array.isArray(user.roles) ? user.roles : []

      // 优先判断 admin，其次是 reviewer，最后是 annotator
      if (userRole === 'admin' || rolesArr.includes('R_ADMIN')) {
        userRole = 'admin'
      } else if (userRole === 'reviewer' || rolesArr.includes('R_REVIEWER')) {
        userRole = 'reviewer'
      } else if (userRole === 'annotator' || rolesArr.includes('R_ANNOTATOR')) {
        userRole = 'annotator'
      }

      const payload = {
        role: userRole,
        user: { id: user.id, username: user.username, real_name: user.realName || user.real_name }
      }

      console.log('🔔 [WS] 准备连接，角色信息:', {
        originalRole: user.role,
        finalRole: userRole,
        payload
      })
      const hostname = location.hostname
      const tryTargets = [
        (host: string) => {
          const cached = localStorage.getItem('ws_notify_url')
          if (cached) {
            console.log('🔔 [WS] 使用缓存 WS 地址优先尝试:', cached)
            return cached
          }
          return buildWsUrl('/api/ws/notifications')
        },
        (host: string) => buildWsUrl('/ws/notifications'),
        (host: string) => {
          // 第三重本地回退：指向后端 8000 端口（仅开发场景）
          const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
          const port8000 = `${protocol}://${host}:8000/ws/notifications`
          console.warn('🔔 [WS] 尝试本地回退到 8000 端口:', port8000)
          return port8000
        }
      ]
      let attempt = 0
      const openNext = () => {
        if (attempt >= tryTargets.length) return
        const url = tryTargets[attempt++](hostname)
        console.log('🔔 [WS] 尝试连接:', url)
        try {
          notifySocket = new WebSocket(url)
        } catch (e) {
          console.warn('🔔 [WS] 创建 WebSocket 失败，继续回退:', e)
          return openNext()
        }

        let opened = false
        const safetyTimer = setTimeout(() => {
          if (!opened && notifySocket && notifySocket.readyState !== 1) {
            console.warn('🔔 [WS] 连接超时，回退到下一个目标:', url)
            try {
              notifySocket.close()
            } catch {}
            openNext()
          }
        }, 2000)

        notifySocket.onopen = () => {
          opened = true
          clearTimeout(safetyTimer)
          reconnectAttempts = 0 // 重置重连次数

          try {
            localStorage.setItem('ws_notify_url', url)
          } catch {}
          try {
            notifySocket?.send(JSON.stringify(payload))
            console.log('🔔 [WS] 通知连接已建立:', url, '角色:', payload.role)
          } catch {}

          // 建立连接后尝试申请系统通知权限（审核员和管理员）
          const role = payload.role
          if (role === 'reviewer' || role === 'admin') {
            setTimeout(() => {
              ensureNotificationPermission().then((granted) => {
                console.log(`🔔 [WS] ${role} 通知权限请求结果:`, granted ? '已授予' : '未授予')
              })
            }, 800)
          }

          // 启动心跳
          startHeartbeat()
        }
        notifySocket.onmessage = (evt) => {
          try {
            const data = JSON.parse(evt.data || '{}')
            console.log('🔔 [WS] 收到消息:', data)

            // 处理心跳响应（pong）
            if (data.type === 'pong') {
              const serverTime = data.server_time
              const clientTime = data.timestamp
              const latency = serverTime && clientTime ? Date.now() - clientTime : 0
              console.log('💓 [WS] 收到心跳响应', latency > 0 ? `延迟: ${latency}ms` : '')
              return
            }

            if (!data || !data.type) return

            // 消息去重：生成消息唯一标识
            const messageId = `${data.timestamp || Date.now()}_${data.type}_${(data.content || '').substring(0, 50)}`
            const now = Date.now()

            // 检查是否为重复消息
            if (processedMessages.has(messageId)) {
              const lastProcessedTime = processedMessages.get(messageId)!
              if (now - lastProcessedTime < MESSAGE_DEDUPE_WINDOW) {
                console.log(
                  `🔄 [WS] 过滤重复消息: ${data.type}, 间隔: ${now - lastProcessedTime}ms`
                )
                return // 忽略重复消息
              }
            }

            // 记录消息处理时间
            processedMessages.set(messageId, now)
            console.log(`✅ [WS] 处理新消息: ${data.type}, 缓存大小: ${processedMessages.size}`)
            // 获取用户真实姓名用于友好通知
            const userRealName = currentUser.value?.realName || currentUser.value?.username || '您'

            if (data.type === 'task_submitted') {
              const msg = `${data.content}（待审核：${data.pending}）`
              ElMessage.success(msg)
              showSystemNotification(`${userRealName}，有新任务待审核`, msg)
            } else if (data.type === 'skip_requested') {
              const msg = data.content || '有新的跳过申请'
              ElMessage.info(msg)
              showSystemNotification(`${userRealName}，有新的跳过申请`, msg)
            } else if (data.type === 'task_approved') {
              const msg = data.content || '任务审核通过'
              ElMessage.success(msg)
              showSystemNotification(`${userRealName}，恭喜任务通过！`, msg)
            } else if (data.type === 'task_rejected') {
              const msg = data.content || '任务需修订，请修改'
              ElMessage.warning(msg)
              showSystemNotification(`${userRealName}，您的任务需要修订`, msg)
            } else if (data.type === 'skip_approved') {
              const msg = data.content || '跳过申请已同意'
              ElMessage.success(msg)
              showSystemNotification(`${userRealName}，跳过申请已通过`, msg)
            } else if (data.type === 'skip_rejected') {
              const msg = data.content || '跳过申请被拒绝'
              ElMessage.warning(msg)
              showSystemNotification(`${userRealName}，跳过申请被拒绝`, msg)
            } else if (data.type === 'work_end_reminder') {
              // 下班提醒
              const msg = data.content || '请及时保存文件，填写好今天的工作日志，下班请关电脑！'
              const title = `${userRealName}，该下班了~`
              ElMessage({
                message: msg,
                type: 'warning',
                duration: 10000, // 显示10秒
                showClose: true
              })
              showSystemNotification(title, msg)
            } else {
              // 通用通知处理（用于未来扩展）
              const msg = data.content || data.message || '您有新的通知'
              const title = data.title
                ? `${userRealName}，${data.title}`
                : `${userRealName}，系统通知`
              const priority = data.priority || 'normal'

              // 根据优先级显示不同类型的消息
              if (priority === 'high') {
                ElMessage.warning({ message: msg, duration: 8000, showClose: true })
              } else {
                ElMessage.info({ message: msg, duration: 5000, showClose: true })
              }

              showSystemNotification(title, msg)
            }
          } catch {}
        }
        notifySocket.onerror = (err) => {
          clearTimeout(safetyTimer)
          stopHeartbeat()
          console.error('🔔 [WS] 通知连接出错:', url, err)

          // 清理当前连接
          if (notifySocket) {
            try {
              notifySocket.close()
            } catch (e) {
              console.error('🔔 [WS] 关闭出错连接失败:', e)
            }
            notifySocket = null
          }

          // 出错立即切换下一个
          openNext()
        }
        notifySocket.onclose = (event) => {
          clearTimeout(safetyTimer)
          stopHeartbeat()

          const isNormalClosure = event.code === 1000
          const wasClean = event.wasClean

          console.warn('🔔 [WS] 通知连接已关闭:', {
            url,
            code: event.code,
            reason: event.reason || '无',
            wasClean,
            isNormalClosure,
            reconnectAttempts
          })

          // 清理连接引用
          notifySocket = null

          // 自动重连（如果不是主动关闭且未超过最大重连次数）
          if (shouldConnectNotify() && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++
            const delay = RECONNECT_DELAY * reconnectAttempts // 递增延迟
            console.log(
              `🔔 [WS] 尝试第 ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS} 次重连，${delay}ms 后重试...`
            )

            reconnectTimer = window.setTimeout(() => {
              console.log(`🔔 [WS] 开始第 ${reconnectAttempts} 次重连...`)
              connectNotifyWS()
            }, delay)
          } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            console.error(`🔔 [WS] 已达到最大重连次数 (${MAX_RECONNECT_ATTEMPTS})，停止重连`)
            console.error('🔔 [WS] 如需恢复连接，请刷新页面或重新登录')
          }
        }
      }
      openNext()
    } catch {}
  }
  // 启动心跳
  const startHeartbeat = () => {
    stopHeartbeat() // 先清除旧的
    heartbeatTimer = window.setInterval(() => {
      if (notifySocket && notifySocket.readyState === WebSocket.OPEN) {
        try {
          const user: any = currentUser.value
          const heartbeatData = {
            type: 'ping',
            timestamp: Date.now(),
            user_id: user?.id,
            username: user?.username || user?.realName
          }
          notifySocket.send(JSON.stringify(heartbeatData))
          console.log('💓 [WS] 发送心跳:', heartbeatData)
        } catch (error) {
          console.error('💓 [WS] 心跳发送失败:', error)
          // 心跳失败可能意味着连接已断开，触发重连
          if (notifySocket) {
            try {
              notifySocket.close()
            } catch (e) {
              console.error('💓 [WS] 关闭失败连接异常:', e)
            }
            notifySocket = null
          }
        }
      } else if (notifySocket) {
        const state = notifySocket.readyState
        const stateNames = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED']
        console.warn(`💓 [WS] 心跳检测到连接异常，状态: ${stateNames[state]} (${state})`)
      }
    }, HEARTBEAT_INTERVAL)
  }

  // 停止心跳
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  // 断开连接
  const disconnectNotifyWS = () => {
    try {
      stopHeartbeat()
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      reconnectAttempts = MAX_RECONNECT_ATTEMPTS // 阻止自动重连
      if (notifySocket) {
        notifySocket.close()
        notifySocket = null
      }
      console.log('🔔 [WS] 已主动断开连接')
    } catch (error) {
      console.error('🔔 [WS] 断开连接失败:', error)
    }
  }

  // 计算属性
  const activeUsers = computed(() => users.value.filter((user) => user.status === 'active'))
  const adminUsers = computed(() => users.value.filter((user) => user.role === 'admin'))
  const annotatorUsers = computed(() => users.value.filter((user) => user.role === 'annotator'))

  // 添加info计算属性，用于路由守卫
  const info = computed(() => currentUser.value)

  // 添加accessToken计算属性，用于HTTP请求
  const accessToken = computed(() => {
    // 优先使用内存中的token，其次是 localStorage 中的（兼容 sessionStorage）
    const currentToken =
      token.value || localStorage.getItem('token') || sessionStorage.getItem('token') || ''
    // 确保返回的token包含Bearer前缀
    if (currentToken && !currentToken.startsWith('Bearer ')) {
      return `Bearer ${currentToken}`
    }
    return currentToken
  })

  // 添加getUserInfo计算属性，用于组件中访问用户信息
  const getUserInfo = computed(() => {
    if (!currentUser.value) {
      return {
        id: '',
        username: '',
        userName: '', // 兼容模板中的userName字段
        realName: '',
        email: '',
        role: '',
        roles: [] as string[],
        avatar: '',
        department: '',
        status: '',
        buttons: [] as string[]
      }
    }

    // 安全地访问用户信息
    const user = currentUser.value as any
    return {
      ...user,
      userName: user.username, // 添加userName字段以兼容模板
      roles: user.roles || [], // 确保 roles 总是数组
      buttons: user.buttons || [] // 确保 buttons 总是数组
    }
  })

  // 获取用户列表
  const fetchUsers = async (params?: {
    skip?: number
    limit?: number
    role?: string
    status?: string
  }) => {
    loading.value = true
    try {
      // 优先使用 /users/basic（所有登录用户可访问）
      // 如果失败（403），则降级到 /users/（需要管理员权限）
      let res: any
      try {
        res = await userApi.getUsersBasic({
          status: params?.status || 'active',
          size: params?.limit || 500
        })
      } catch (error: any) {
        // 如果没有权限，尝试使用管理员API
        if (error.message?.includes('403') || error.message?.includes('Not authorized')) {
          console.log('ℹ️ [UserStore] /users/basic 无权限，尝试 /users/')
          res = await userApi.getUsers(params)
        } else {
          throw error
        }
      }

      // 兼容多种返回结构：
      // 1) { data: User[]; total }
      // 2) { data: { list: User[]; total } }
      // 3) { list: User[]; total }
      // 4) User[]
      const data = res?.data ?? res
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.list)
          ? data.list
          : Array.isArray(res?.list)
            ? res.list
            : []
      users.value = list as unknown as User[]
      total.value = data?.total ?? res?.total ?? list.length
    } catch (error) {
      console.error('获取用户列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取用户详情
  const fetchUser = async (userId: string) => {
    try {
      const response = await userApi.getUser(userId)
      return response as User
    } catch (error) {
      console.error('获取用户详情失败:', error)
      throw error
    }
  }

  // 创建用户
  const createUser = async (userData: UserCreate) => {
    try {
      const response = await userApi.createUser(userData)
      users.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建用户失败:', error)
      throw error
    }
  }

  // 更新用户
  const updateUser = async (userId: string, userData: UserUpdate) => {
    try {
      const response = await userApi.updateUser(userId, userData)
      const index = users.value.findIndex((user) => user.id === userId)
      if (index !== -1) {
        users.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新用户失败:', error)
      throw error
    }
  }

  // 删除用户
  const deleteUser = async (userId: string) => {
    try {
      await userApi.deleteUser(userId)
      const index = users.value.findIndex((user) => user.id === userId)
      if (index !== -1) {
        users.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      throw error
    }
  }

  // 切换用户状态
  const toggleUserStatus = async (userId: string) => {
    try {
      const response = await userApi.toggleUserStatus(userId)
      const user = users.value.find((u) => u.id === userId)
      if (user) {
        user.status = user.status === 'active' ? 'inactive' : 'active'
      }
      return response.data
    } catch (error) {
      console.error('切换用户状态失败:', error)
      throw error
    }
  }

  // 获取用户统计
  const fetchUserStats = async () => {
    try {
      const response = await userApi.getUserStats()
      userStats.value = response.data
    } catch (error) {
      console.error('获取用户统计失败:', error)
      throw error
    }
  }

  // 设置Token
  const setToken = (newToken: string, refreshToken?: string) => {
    // 保存原始的token，不添加Bearer前缀（由HTTP客户端处理）
    token.value = newToken
    // 使用 localStorage 支持多标签页共享
    // 配合后端 Redis Token 白名单实现安全的会话管理
    localStorage.setItem('token', newToken)
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken)
    }

    // 设置token后立即设置登录状态为true
    isLogin.value = true

    console.log('🔑 [UserStore] Token已设置到 localStorage:', {
      token: newToken ? 'exists' : 'empty',
      isLogin: isLogin.value
    })
  }

  // 设置用户信息
  const setUserInfo = (userInfo: any) => {
    console.log('🔍 [UserStore] 接收到的userInfo:', userInfo)
    console.log('📅 [UserStore] userInfo中的hire_date:', userInfo.hire_date)
    console.log('📅 [UserStore] userInfo中的hireDate:', userInfo.hireDate)
    console.log('👤 [UserStore] 用户角色:', userInfo.role, userInfo.roles)

    // 处理不同格式的用户信息
    if (userInfo.userId || userInfo.userName) {
      // API 返回的格式
      currentUser.value = {
        id: String(userInfo.id || userInfo.userId || ''), // 确保ID是字符串
        username: userInfo.userName || userInfo.username,
        realName: userInfo.realName || userInfo.real_name,
        email: userInfo.email,
        role: userInfo.role || 'user',
        department: userInfo.department || '',
        avatar: userInfo.avatar || '',
        status: userInfo.status || 'active',
        createdAt: userInfo.created_at || new Date().toISOString(),
        lastLoginAt: userInfo.updated_at || new Date().toISOString(),
        hireDate: userInfo.hire_date || userInfo.hireDate || '', // ✅ 添加入职日期映射
        // 添加用于前端的扩展字段
        roles: userInfo.roles || ['R_USER'],
        buttons: userInfo.buttons || [],
        phone: userInfo.phone || ''
      } as any
    } else {
      // 直接的用户对象 - 也需要确保 hireDate 字段存在
      currentUser.value = {
        ...userInfo,
        hireDate: userInfo.hire_date || userInfo.hireDate || '' // ✅ 兼容两种命名格式
      }
    }

    console.log('💾 [UserStore] 用户信息已设置:', currentUser.value)
    console.log('📅 [UserStore] 设置后的hireDate:', currentUser.value?.hireDate)

    // 对于所有用户，立即请求通知权限（包括定时提醒等系统通知）
    const role = (currentUser.value?.role || '').toLowerCase()
    console.log('🔔 [UserStore] 用户登录成功，请求通知权限')
    setTimeout(() => {
      ensureNotificationPermission().then((granted) => {
        if (granted) {
          console.log('✅ [UserStore] 通知权限已授予')
        } else {
          console.warn('⚠️ [UserStore] 通知权限未授予，用户可能拒绝了通知')
          console.warn('⚠️ [UserStore] 您将无法收到系统通知（如下班提醒等）')
        }
      })
    }, 500)

    // 登录后立即尝试建立通知连接（审核员/管理员/标注员）
    console.log('🔔 [UserStore] 用户信息设置完成，准备建立 WebSocket 连接')
    try {
      // 重置重连计数
      reconnectAttempts = 0
      connectNotifyWS()
      // 延迟再尝试一次（双保险）
      setTimeout(() => {
        console.log('🔔 [UserStore] 延迟200ms后再次尝试连接')
        connectNotifyWS()
      }, 200)
    } catch (error) {
      console.error('🔔 [UserStore] 建立 WebSocket 连接异常:', error)
    }
  }

  // 获取个人中心资料
  const fetchMyProfile = async () => {
    const res: any = await userApi.getMyProfile()
    console.log('📋 [UserStore] fetchMyProfile 获取到的数据:', res)
    console.log('📅 [UserStore] fetchMyProfile - hire_date:', res.hire_date)
    console.log('📅 [UserStore] fetchMyProfile - hireDate:', res.hireDate)

    // 同步到 currentUser
    if (currentUser.value) {
      currentUser.value.realName = res.real_name || currentUser.value.realName
      currentUser.value.email = res.email || currentUser.value.email
      ;(currentUser.value as any).avatar = res.avatar_url || (currentUser.value as any).avatar
      currentUser.value.department = res.department || currentUser.value.department
      currentUser.value.hireDate = res.hire_date || res.hireDate || currentUser.value.hireDate || '' // ✅ 添加 hireDate 同步

      console.log(
        '💾 [UserStore] fetchMyProfile 更新后的 currentUser.hireDate:',
        currentUser.value.hireDate
      )
    }
    return res
  }

  // 更新个人中心资料
  const updateUserProfile = async (data: {
    real_name?: string
    email?: string
    avatar_url?: string
    department?: string
  }) => {
    const res: any = await userApi.updateMyProfile(data)
    // 更新本地 currentUser
    if (currentUser.value) {
      currentUser.value.realName = res.real_name || currentUser.value.realName
      currentUser.value.email = res.email || currentUser.value.email
      ;(currentUser.value as any).avatar = res.avatar_url || (currentUser.value as any).avatar
      currentUser.value.department = res.department || currentUser.value.department
    }
    return res
  }

  // 设置登录状态
  const setLoginStatus = (status: boolean) => {
    isLogin.value = status
    if (status) {
      console.log('🔔 [UserStore] 登录状态变为 true，准备建立 WebSocket 连接')
      // 登录状态切换为 true 时再次尝试连接
      try {
        // 重置重连计数
        reconnectAttempts = 0
        connectNotifyWS()
      } catch (error) {
        console.error('🔔 [UserStore] 建立 WebSocket 连接失败:', error)
      }
    } else {
      console.log('🔔 [UserStore] 登录状态变为 false，断开 WebSocket 连接')
      disconnectNotifyWS()
    }
  }

  // 设置语言
  const setLanguage = (lang: LanguageEnum) => {
    language.value = lang
    try {
      const storageKey = 'user_language'
      localStorage.setItem(storageKey, lang)
    } catch {}
  }

  // 设置锁屏状态
  const setLockStatus = (status: boolean) => {
    isLock.value = status
  }

  // 监听角色/用户变化，自动建立连接
  watch(
    () => currentUser.value && (currentUser.value as any).role,
    () => {
      try {
        connectNotifyWS()
      } catch {}
    }
  )

  // 设置锁屏密码
  const setLockPassword = (password: string) => {
    lockPassword.value = password
  }

  // 登录
  const login = async (credentials: { username: string; password: string }) => {
    try {
      // 这里应该调用登录API
      // const response = await authApi.login(credentials)
      // token.value = response.token
      // currentUser.value = response.user
      isLogin.value = true
      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  // 登出
  const logOut = () => {
    token.value = ''
    currentUser.value = null
    isLogin.value = false
    // 清除 localStorage 和 sessionStorage 中的token（兼容旧版本）
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userId')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('refreshToken')
    sessionStorage.removeItem('userId')
    // 断开通知连接
    disconnectNotifyWS()
    console.log('🚪 [UserStore] 用户已登出，所有认证信息已清除')
  }

  // 强制重新认证（用于token过期等情况）
  const forceReauth = () => {
    console.log('🔄 [UserStore] 强制重新认证')
    logOut()
    // 刷新页面到登录页
    window.location.href = '/login'
  }

  // 权限检查方法
  const hasPermission = (permission: string): boolean => {
    if (!currentUser.value) return false

    // 超级管理员拥有所有权限
    if (currentUser.value.role === 'admin') return true

    // 检查用户角色是否有特定权限
    // TODO: 这里需要根据实际的权限系统来实现
    // 目前简化处理，基于角色判断
    const rolePermissions: Record<string, string[]> = {
      admin: ['*'], // 管理员拥有所有权限
      annotator: ['WorkLogView', 'WorkLogEdit'], // 可以查看和编辑自己的工作日志
      reviewer: ['WorkLogView', 'WorkLogReview', 'WorkLogManagement'], // 可以查看、审核和管理工作日志
      user: ['WorkLogView']
    }

    // 注意：WorkLogEdit 表示可以编辑自己的日志
    //       WorkLogManagement 表示可以管理所有人的日志

    const userPermissions = rolePermissions[currentUser.value.role] || []
    return userPermissions.includes('*') || userPermissions.includes(permission)
  }

  // 重置状态
  const reset = () => {
    users.value = []
    currentUser.value = null
    loading.value = false
    total.value = 0
    isLogin.value = false
    token.value = ''
    isLock.value = false
    lockPassword.value = ''
    userStats.value = {
      total_users: 0,
      active_users: 0,
      inactive_users: 0,
      admin_users: 0,
      annotator_users: 0
    }
  }

  return {
    // 状态
    users,
    currentUser,
    loading,
    total,
    isLogin,
    token,
    userStats,
    language,
    isLock,
    lockPassword,

    // 计算属性
    activeUsers,
    adminUsers,
    annotatorUsers,
    info,
    accessToken, // 添加accessToken计算属性
    getUserInfo, // 添加这个计算属性

    // 方法
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    toggleUserStatus,
    fetchUserStats,
    setToken,
    setUserInfo,
    setLoginStatus,
    setLanguage,
    setLockStatus,
    setLockPassword,
    login,
    logOut,
    forceReauth, // 添加强制重新认证方法
    reset,
    fetchMyProfile,
    updateUserProfile,
    hasPermission,
    connectNotifyWS, // 导出 WebSocket 连接方法
    disconnectNotifyWS // 导出 WebSocket 断开方法
  }
})
