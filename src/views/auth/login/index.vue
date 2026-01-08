<template>
  <div class="login">
    <LoginLeftView></LoginLeftView>

    <div class="right-wrap">
      <div class="top-right-wrap">
        <div class="btn theme-btn" @click="themeAnimation">
          <i class="iconfont-sys">
            {{ isDark ? '&#xe6b5;' : '&#xe725;' }}
          </i>
        </div>
        <ElDropdown @command="changeLanguage" popper-class="langDropDownStyle">
          <div class="btn language-btn">
            <i class="iconfont-sys icon-language">&#xe611;</i>
          </div>
          <template #dropdown>
            <ElDropdownMenu>
              <div v-for="lang in languageOptions" :key="lang.value" class="lang-btn-item">
                <ElDropdownItem
                  :command="lang.value"
                  :class="{ 'is-selected': locale === lang.value }"
                >
                  <span class="menu-txt">{{ lang.label }}</span>
                  <i v-if="locale === lang.value" class="iconfont-sys icon-check">&#xe621;</i>
                </ElDropdownItem>
              </div>
            </ElDropdownMenu>
          </template>
        </ElDropdown>
      </div>
      <div class="header">
        <ArtLogo class="icon" />
        <h1>{{ systemName }}</h1>
      </div>
      <div class="login-wrap">
        <div class="form">
          <h3 class="title">{{ $t('login.title') }}</h3>
          <p class="sub-title">{{ $t('login.subTitle') }}</p>
          <ElForm
            ref="formRef"
            :model="formData"
            :rules="rules"
            @keyup.enter="handleSubmit"
            style="margin-top: 25px"
          >
            <ElFormItem prop="username">
              <ElInput :placeholder="$t('login.placeholder[0]')" v-model.trim="formData.username" />
            </ElFormItem>
            <ElFormItem prop="password">
              <ElInput
                :placeholder="$t('login.placeholder[1]')"
                v-model.trim="formData.password"
                type="password"
                radius="8px"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <div class="forget-password">
              <ElCheckbox v-model="formData.rememberPassword">{{
                $t('login.rememberPwd')
              }}</ElCheckbox>
              <RouterLink :to="RoutesAlias.ForgetPassword">{{ $t('login.forgetPwd') }}</RouterLink>
            </div>

            <div style="margin-top: 30px">
              <ElButton
                class="login-btn"
                type="primary"
                @click="handleSubmit"
                :loading="loading"
                v-ripple
              >
                {{ $t('login.btnText') }}
              </ElButton>
            </div>

            <div class="footer">
              <p>
                {{ $t('login.noAccount') }}
                <RouterLink :to="RoutesAlias.Register">{{ $t('login.register') }}</RouterLink>
              </p>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import AppConfig from '@/config'
  import { RoutesAlias } from '@/router/routesAlias'
  import { ElNotification, ElMessage } from 'element-plus'
  import { useUserStore } from '@/store/modules/user'
  import { taskApi } from '@/api/projectApi'
  import { notificationApi } from '@/api/notificationApi'

  import { languageOptions } from '@/locales'
  import { LanguageEnum } from '@/enums/appEnum'
  import { useI18n } from 'vue-i18n'
  import { HttpError } from '@/utils/http/error'
  import { themeAnimation } from '@/utils/theme/animation'
  import { UserService } from '@/api/usersApi'

  defineOptions({ name: 'Login' })

  const { t } = useI18n()
  import { useSettingStore } from '@/store/modules/setting'
  import type { FormInstance, FormRules } from 'element-plus'

  const settingStore = useSettingStore()
  const { isDark } = storeToRefs(settingStore)

  const userStore = useUserStore()
  const router = useRouter()

  const systemName = AppConfig.systemInfo.name
  const formRef = ref<FormInstance>()

  const formData = reactive({
    username: '',
    password: '',
    rememberPassword: true
  })

  const rules = computed<FormRules>(() => ({
    username: [{ required: true, message: t('login.placeholder[0]'), trigger: 'blur' }],
    password: [{ required: true, message: t('login.placeholder[1]'), trigger: 'blur' }]
  }))

  const loading = ref(false)

  // 页面加载时恢复保存的登录信息
  onMounted(() => {
    try {
      const savedUsername = localStorage.getItem('saved_username')
      const savedPassword = localStorage.getItem('saved_password')
      const rememberPassword = localStorage.getItem('remember_password')

      if (rememberPassword === 'true' && savedUsername) {
        formData.username = savedUsername
        formData.rememberPassword = true

        // 如果保存了密码，解码并填充（Base64编码）
        if (savedPassword) {
          try {
            formData.password = atob(savedPassword)
          } catch (e) {
            console.warn('密码解码失败，清除保存的密码')
            localStorage.removeItem('saved_password')
          }
        }

        console.log('🔑 [Login] 已恢复保存的登录信息:', {
          username: savedUsername,
          hasPassword: !!savedPassword
        })
      }
    } catch (error) {
      console.error('恢复登录信息失败:', error)
    }
  })

  // 登录
  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      // 表单验证
      const valid = await formRef.value.validate()
      if (!valid) return

      loading.value = true

      // 登录请求
      const { username, password } = formData

      const loginResult = await UserService.login({
        userName: username,
        password
      })

      // 验证token
      if (!loginResult.token) {
        throw new Error('Login failed - no token received')
      }

      // 存储token
      userStore.setToken(loginResult.token, loginResult.refreshToken)

      // 设置登录状态
      userStore.setLoginStatus(true)

      // 获取用户信息（如果登录返回了用户信息，优先使用）
      let userInfo
      const hasUser = (v: any): v is { user: any } =>
        v && typeof v === 'object' && 'user' in v && v.user
      if (hasUser(loginResult)) {
        // 使用登录返回的用户信息
        console.log('📝 [Login] 使用登录返回的用户信息:', loginResult.user)

        // 转换后端数据格式为前端格式
        const mapRoleToFrontend = (role: string): string[] => {
          const r = (role || '').toLowerCase()
          if (r === 'super') return ['R_SUPER']
          if (r === 'admin' || r === 'administrator') return ['R_ADMIN']
          if (r === 'reviewer') return ['R_REVIEWER']
          if (r === 'annotator') return ['R_ANNOTATOR']
          return ['R_USER']
        }

        userInfo = {
          userId: loginResult.user.id, // 保持字符串格式
          userName: loginResult.user.username,
          roles: mapRoleToFrontend(loginResult.user.role),
          buttons: ['add', 'edit', 'delete', 'view'],
          avatar: loginResult.user.avatar_url || '',
          email: loginResult.user.email,
          phone: '',
          // 为用户存储组件添加必要字段
          id: loginResult.user.id,
          username: loginResult.user.username,
          real_name: loginResult.user.real_name,
          realName: loginResult.user.real_name,
          role: loginResult.user.role,
          department: loginResult.user.department || '',
          status: loginResult.user.status,
          created_at: loginResult.user.created_at,
          updated_at: loginResult.user.updated_at
        }
      } else {
        // 如果登录没有返回用户信息，单独获取
        userInfo = await UserService.getUserInfo()
      }

      userStore.setUserInfo(userInfo)

      // 处理"记住密码"功能
      if (formData.rememberPassword) {
        // 保存用户名和密码（密码使用Base64编码）
        localStorage.setItem('saved_username', username)
        localStorage.setItem('saved_password', btoa(password)) // Base64编码
        localStorage.setItem('remember_password', 'true')
        console.log('💾 [Login] 已保存登录信息（记住密码）')
      } else {
        // 清除保存的登录信息
        localStorage.removeItem('saved_username')
        localStorage.removeItem('saved_password')
        localStorage.removeItem('remember_password')
        console.log('🗑️ [Login] 已清除保存的登录信息')
      }

      // 登录成功处理
      showLoginSuccessNotice()

      // 跳转到首页，让路由守卫处理菜单加载
      router.push('/')
    } catch (error) {
      // 处理 HttpError
      if (error instanceof HttpError) {
        ElMessage.error(`登录失败: ${error.message}`)
        console.error('[Login] HttpError:', error)
      } else {
        // 处理非 HttpError
        const errorMessage = error instanceof Error ? error.message : '登录失败，请稍后重试'
        ElMessage.error(errorMessage)
        console.error('[Login] Unexpected error:', error)
      }
    } finally {
      loading.value = false
    }
  }

  // 登录成功提示
  const showLoginSuccessNotice = async () => {
    setTimeout(async () => {
      const info: any = userStore.getUserInfo
      console.log('📊 [Login] 用户信息:', info)

      const displayName = info?.realName || info?.userName || info?.username || ''
      const userRole = (info?.role || '').toLowerCase()

      console.log('👤 [Login] 用户角色:', userRole)
      console.log('🎭 [Login] 用户角色数组:', info?.roles)

      // 📬 优先显示离线期间的未读通知（从 Redis，7天内有效）
      try {
        console.log('📥 [Login] 开始拉取未读通知...')
        const unreadResult: any = await notificationApi.getNotifications({
          limit: 10 // 最多显示10条未读通知
        })

        const unreadNotifications = unreadResult?.notifications || []
        console.log('📬 [Login] 未读通知数量:', unreadNotifications.length)

        if (unreadNotifications.length > 0) {
          // 显示每一条未读通知（网页内通知 + 系统级通知）
          const userRealName = userStore.currentUser?.realName || formData.username

          unreadNotifications.forEach((notification: any, index: number) => {
            setTimeout(() => {
              const notifType =
                notification.priority === 'urgent'
                  ? 'error'
                  : notification.priority === 'high'
                    ? 'warning'
                    : notification.priority === 'normal'
                      ? 'info'
                      : 'success'

              // 构建更亲切的通知标题
              let friendlyTitle = notification.title
              if (notification.type === 'task_rejected') {
                friendlyTitle = `${userRealName}，您的任务需要修订`
              } else if (notification.type === 'task_approved') {
                friendlyTitle = `${userRealName}，恭喜任务通过！`
              } else if (notification.type === 'task_submitted') {
                friendlyTitle = `${userRealName}，有新任务待审核`
              } else if (notification.type === 'skip_requested') {
                friendlyTitle = `${userRealName}，有新的跳过申请`
              } else if (notification.type === 'skip_approved') {
                friendlyTitle = `${userRealName}，跳过申请已通过`
              } else if (notification.type === 'skip_rejected') {
                friendlyTitle = `${userRealName}，跳过申请被拒绝`
              } else {
                // 其他通知类型，保持原标题或添加称呼
                friendlyTitle = `${userRealName}，${notification.title}`
              }

              // 1. 网页内通知
              ElNotification({
                title: friendlyTitle,
                message: notification.content,
                type: notifType,
                duration: 6000,
                position: 'top-right',
                zIndex: 10000 + index
              })

              // 2. 系统级通知（Windows/macOS 通知中心）
              try {
                if ('Notification' in window && Notification.permission === 'granted') {
                  const systemNotif = new Notification(friendlyTitle, {
                    body: notification.content,
                    icon: '/xingxiang_logo.ico',
                    tag: `offline-notif-${notification.id}`,
                    requireInteraction: notification.priority === 'urgent' // 紧急通知需要用户交互
                  })
                  systemNotif.onclick = () => {
                    window.focus()
                  }
                }
              } catch (e) {
                console.error('系统通知发送失败:', e)
              }

              // 3. 自动标记为已读（显示即已读）
              notificationApi.markAsRead(notification.id).catch((e) => {
                console.error('⚠️ [Login] 自动标记通知已读失败:', e)
              })
            }, index * 500) // 每条通知延迟500ms显示，避免堆叠
          })

          console.log(
            `✅ [Login] 已显示 ${unreadNotifications.length} 条未读通知（自动标记为已读）`
          )
        } else {
          console.log('ℹ️ [Login] 没有未读通知')
        }
      } catch (error) {
        console.error('❌ [Login] 拉取未读通知失败:', error)
      }

      // 基础欢迎消息
      let message = `欢迎回来，${displayName}`
      let hasUrgentTasks = false // 是否有紧急任务

      // 判断角色
      const isAnnotator =
        userRole === 'annotator' ||
        (Array.isArray(info?.roles) && info.roles.includes('R_ANNOTATOR'))
      const isReviewer =
        userRole === 'reviewer' || (Array.isArray(info?.roles) && info.roles.includes('R_REVIEWER'))
      const isAdmin =
        userRole === 'admin' || (Array.isArray(info?.roles) && info.roles.includes('R_ADMIN'))

      console.log('✅ [Login] 角色判断:', { isAnnotator, isReviewer, isAdmin })

      // 为标注员添加任务统计信息
      if (isAnnotator) {
        try {
          const userId = info?.id || info?.userId
          console.log('🆔 [Login] 标注员用户ID:', userId)

          if (userId) {
            console.log('📥 [Login] 开始获取标注员任务列表...')
            const tasksResult: any = await taskApi.getTasks({
              assignedTo: userId,
              page: 1,
              pageSize: 100
            })

            console.log('📦 [Login] 标注员任务API返回结果:', tasksResult)

            const tasks = tasksResult?.data?.list || tasksResult?.list || []
            console.log('📋 [Login] 标注员任务列表:', tasks)
            console.log('📊 [Login] 标注员任务总数:', tasks.length)

            // 统计进行中的任务
            const inProgressCount = tasks.filter((t: any) => t.status === 'in_progress').length
            console.log('⏳ [Login] 进行中任务数:', inProgressCount)

            // 统计被驳回的任务
            const rejectedCount = tasks.filter((t: any) => t.status === 'rejected').length
            console.log('❌ [Login] 被驳回任务数:', rejectedCount)

            // 构建消息
            const taskInfo: string[] = []
            if (inProgressCount > 0) {
              taskInfo.push(`当前有 ${inProgressCount} 个任务进行中`)
            }
            if (rejectedCount > 0) {
              taskInfo.push(`⚠️ 您有 ${rejectedCount} 个被驳回任务，建议请您先修订`)
              hasUrgentTasks = true
            }

            console.log('💬 [Login] 标注员任务信息:', taskInfo)

            if (taskInfo.length > 0) {
              message = `欢迎回来，${displayName}\n\n${taskInfo.join('\n')}`
            }

            console.log('📝 [Login] 标注员最终消息:', message)

            // 如果有被驳回任务，额外显示独立的警告通知
            if (rejectedCount > 0) {
              setTimeout(() => {
                ElNotification({
                  title: '⚠️ 任务被驳回提醒',
                  message: `您有 ${rejectedCount} 个任务被驳回，请尽快修订并重新提交！`,
                  type: 'warning',
                  duration: 8000,
                  zIndex: 10001,
                  position: 'bottom-right'
                })
              }, 3000) // 延迟3秒显示，避免与登录成功提示重叠
            }
          } else {
            console.warn('⚠️ [Login] 标注员用户ID不存在')
          }
        } catch (error) {
          console.error('❌ [Login] 获取标注员任务统计失败:', error)
        }
      }

      // 为管理员和审核员添加待审核任务统计
      if (isReviewer || isAdmin) {
        try {
          console.log('📥 [Login] 开始获取待审核任务...')

          // 获取待审核任务（submitted状态）
          const submittedResult: any = await taskApi.getTasks({
            status: ['submitted'],
            page: 1,
            pageSize: 100,
            isReviewPage: true
          })

          console.log('📦 [Login] 待审核任务API返回结果:', submittedResult)

          const submittedTasks = submittedResult?.data?.list || submittedResult?.list || []
          const submittedCount = submittedTasks.length
          console.log('📋 [Login] 待审核任务数:', submittedCount)

          // 获取跳过申请（skip_pending状态）
          const skipPendingResult: any = await taskApi.getTasks({
            status: ['skip_pending'],
            page: 1,
            pageSize: 100,
            isReviewPage: true
          })

          console.log('📦 [Login] 跳过申请API返回结果:', skipPendingResult)

          const skipPendingTasks = skipPendingResult?.data?.list || skipPendingResult?.list || []
          const skipPendingCount = skipPendingTasks.length
          console.log('📋 [Login] 跳过申请数:', skipPendingCount)

          // 构建消息
          const reviewInfo: string[] = []
          if (submittedCount > 0) {
            reviewInfo.push(`📝 您有 ${submittedCount} 个任务待审核`)
            hasUrgentTasks = true
          }
          if (skipPendingCount > 0) {
            reviewInfo.push(`🔄 您有 ${skipPendingCount} 个跳过申请待处理`)
            hasUrgentTasks = true
          }

          console.log('💬 [Login] 审核任务信息:', reviewInfo)

          if (reviewInfo.length > 0) {
            message = `欢迎回来，${displayName}\n\n${reviewInfo.join('\n')}`

            // 如果有待审核任务，额外显示独立的提醒通知
            if (submittedCount > 0 || skipPendingCount > 0) {
              setTimeout(() => {
                const reminderItems: string[] = []
                if (submittedCount > 0) {
                  reminderItems.push(`📝 ${submittedCount} 个任务待审核`)
                }
                if (skipPendingCount > 0) {
                  reminderItems.push(`🔄 ${skipPendingCount} 个跳过申请`)
                }

                ElNotification({
                  title: '📋 待处理任务提醒',
                  message: `您有以下任务待处理：\n${reminderItems.join('\n')}`,
                  type: 'warning',
                  duration: 8000,
                  zIndex: 10001,
                  position: 'bottom-right',
                  dangerouslyUseHTMLString: true
                })
              }, 3000) // 延迟3秒显示
            }
          }

          console.log('📝 [Login] 审核员最终消息:', message)
        } catch (error) {
          console.error('❌ [Login] 获取待审核任务统计失败:', error)
        }
      }

      ElNotification({
        title: '登录成功',
        type: hasUrgentTasks ? 'warning' : 'success',
        duration: hasUrgentTasks ? 6000 : 2500, // 如果有紧急任务，延长显示时间
        zIndex: 10000,
        dangerouslyUseHTMLString: true,
        message: message.replace(/\n/g, '<br/>')
      })
    }, 150)
  }

  // 切换语言
  const { locale } = useI18n()

  const changeLanguage = (lang: LanguageEnum) => {
    if (locale.value === lang) return
    locale.value = lang
    userStore.setLanguage(lang)
  }
</script>

<style lang="scss" scoped>
  @use './index';
</style>
