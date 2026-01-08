import type { Router, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import { ref, nextTick } from 'vue'
import NProgress from 'nprogress'
import { useSettingStore } from '@/store/modules/setting'
import { useUserStore } from '@/store/modules/user'
import { useMenuStore } from '@/store/modules/menu'
import { setWorktab } from '@/utils/navigation'
import { setPageTitle, setSystemTheme } from '../utils/utils'
import { menuService } from '@/api/menuApi'
import { registerDynamicRoutes } from '../utils/registerRoutes'
import { AppRouteRecord } from '@/types/router'
import { RoutesAlias } from '../routesAlias'
import { menuDataToRouter } from '../utils/menuToRouter'
import { asyncRoutes } from '../routes/asyncRoutes'
import { loadingService } from '@/utils/ui'
import { useCommon } from '@/composables/useCommon'
import { useWorktabStore } from '@/store/modules/worktab'
import { UserService } from '@/api/usersApi'

// 前端权限模式 loading 关闭延时，提升用户体验
const LOADING_DELAY = 100

// 是否已注册动态路由
const isRouteRegistered = ref(false)

// 跟踪是否需要关闭 loading
const pendingLoading = ref(false)

/**
 * 设置路由全局前置守卫
 */
export function setupBeforeEachGuard(router: Router): void {
  router.beforeEach(
    async (
      to: RouteLocationNormalized,
      from: RouteLocationNormalized,
      next: NavigationGuardNext
    ) => {
      try {
        await handleRouteGuard(to, from, next, router)
      } catch (error) {
        console.error('路由守卫处理失败:', error)
        next('/exception/500')
      }
    }
  )

  // 设置后置守卫以关闭 loading 和进度条
  setupAfterEachGuard(router)
}

/**
 * 设置路由全局后置守卫
 */
function setupAfterEachGuard(router: Router): void {
  router.afterEach(() => {
    // 关闭进度条
    const settingStore = useSettingStore()
    if (settingStore.showNprogress) {
      NProgress.done()
    }

    // 关闭 loading 效果
    if (pendingLoading.value) {
      nextTick(() => {
        loadingService.hideLoading()
        pendingLoading.value = false
      })
    }
  })
}

/**
 * 处理路由守卫逻辑
 */
async function handleRouteGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext,
  router: Router
): Promise<void> {
  const settingStore = useSettingStore()
  const userStore = useUserStore()

  // 处理进度条
  if (settingStore.showNprogress) {
    NProgress.start()
  }

  // 设置系统主题
  setSystemTheme(to)

  // 如果是异常页面路由，直接放行，避免无限重定向
  if (to.path.startsWith('/exception/')) {
    next()
    return
  }

  // 处理登录状态
  if (!(await handleLoginStatus(to, userStore, next))) {
    return
  }

  // 处理动态路由注册
  if (!isRouteRegistered.value && userStore.isLogin) {
    await handleDynamicRoutes(to, from, next, router)
    return
  }

  // 处理根路径跳转到首页
  if (userStore.isLogin && isRouteRegistered.value && handleRootPathRedirect(to, next)) {
    return
  }

  // 处理已知的匹配路由
  if (to.matched.length > 0) {
    // 隐藏路由直接放行（例如功能性页面：创建页等不出现在菜单里）
    try {
      const isHidden = to.matched.some((r) => (r.meta as any)?.isHide)
      if (isHidden) {
        setWorktab(to)
        setPageTitle(to)
        next()
        return
      }
    } catch {}
    // 统一基于角色的权限控制：仅允许访问出现在菜单（或权限集）中的路由 name
    try {
      const menuStore = useMenuStore()
      const allowed = new Set<string>()
      const collect = (items: AppRouteRecord[] | undefined) => {
        if (!items) return
        for (const it of items) {
          if (it.name) allowed.add(String(it.name))
          if (it.children && it.children.length) collect(it.children)
        }
      }
      collect(menuStore.menuList as unknown as AppRouteRecord[])
      const targetName = to.name ? String(to.name) : ''
      if (targetName && allowed.size > 0 && !allowed.has(targetName)) {
        next(RoutesAlias.Exception403)
        return
      }
    } catch (e) {
      // 忽略权限集合构建异常，保持原逻辑
    }
    setWorktab(to)
    setPageTitle(to)
    next()
    return
  }

  // 尝试刷新路由重新注册
  if (userStore.isLogin && !isRouteRegistered.value) {
    await handleDynamicRoutes(to, from, next, router)
    return
  }

  // 未匹配到路由，跳转到 404
  next(RoutesAlias.Exception404)
}

/**
 * 处理登录状态
 */
async function handleLoginStatus(
  to: RouteLocationNormalized,
  userStore: ReturnType<typeof useUserStore>,
  next: NavigationGuardNext
): Promise<boolean> {
  // 如果访问的是登录页面或无需登录的页面，直接放行
  if (to.path === RoutesAlias.Login || to.meta.noLogin) {
    return true
  }

  // 检查是否有token（优先从 localStorage，兼容旧的 sessionStorage）
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    console.log('🔐 [RouteGuard] 没有token，跳转到登录页')
    userStore.logOut()
    next(RoutesAlias.Login)
    return false
  }

  // 如果有token但登录状态为false，尝试验证token有效性
  if (!userStore.isLogin) {
    try {
      console.log('🔐 [RouteGuard] 验证token有效性')
      const userInfo = await UserService.getUserInfo()
      userStore.setUserInfo(userInfo)
      // 仅在后端成功返回 /auth/me 后，才标记为登录
      userStore.setLoginStatus(true)
      console.log('✅ [RouteGuard] Token验证成功，恢复登录状态')

      // 确保 WebSocket 连接建立（延迟重试机制，提高连接成功率）
      setTimeout(() => {
        console.log('🔔 [RouteGuard] 尝试建立 WebSocket 连接（延迟500ms）')
        userStore.connectNotifyWS()
      }, 500)

      // 再次尝试（双重保险）
      setTimeout(() => {
        console.log('🔔 [RouteGuard] 再次尝试建立 WebSocket 连接（延迟1500ms）')
        userStore.connectNotifyWS()
      }, 1500)

      return true
    } catch (error) {
      console.error('❌ [RouteGuard] Token验证失败:', error)
      // Token无效，清除并跳转到登录页
      userStore.logOut()
      next(RoutesAlias.Login)
      return false
    }
  }

  return true
}

/**
 * 处理动态路由注册
 */
async function handleDynamicRoutes(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext,
  router: Router
): Promise<void> {
  try {
    // 显示 loading 并标记 pending
    pendingLoading.value = true
    loadingService.showLoading()

    // 获取用户信息
    const userStore = useUserStore()
    const isRefresh = from.path === '/'
    if (isRefresh || !userStore.info || Object.keys(userStore.info).length === 0) {
      try {
        console.log('👤 [RouteGuard] 开始获取用户信息')
        const data = await UserService.getUserInfo()
        console.log('✅ [RouteGuard] 用户信息获取成功:', data)
        userStore.setUserInfo(data)
        // 确保用户信息设置完成后再继续
        await nextTick()
        console.log('💾 [RouteGuard] 用户信息已设置到store:', userStore.info)
      } catch (error) {
        console.error('❌ [RouteGuard] 获取用户信息失败:', error)
        // Token已失效，清除登录状态并跳转到登录页
        userStore.logOut()
        pendingLoading.value = false
        loadingService.hideLoading()
        next(RoutesAlias.Login)
        return
      }
    }

    // 再次检查用户信息是否完整
    if (!userStore.info || !userStore.info.roles) {
      throw new Error('获取用户角色失败')
    }

    await getMenuData(router)

    // 处理根路径跳转
    if (handleRootPathRedirect(to, next)) {
      return
    }

    next({
      path: to.path,
      query: to.query,
      hash: to.hash,
      replace: true
    })
  } catch (error) {
    console.error('动态路由注册失败:', error)
    // 清理loading状态
    pendingLoading.value = false
    loadingService.hideLoading()
    // 标记路由已注册，避免重复尝试
    isRouteRegistered.value = true
    next('/exception/500')
  } finally {
    // 确保loading状态被清理
    if (pendingLoading.value) {
      pendingLoading.value = false
      loadingService.hideLoading()
    }
  }
}

/**
 * 获取菜单数据
 */
async function getMenuData(router: Router): Promise<void> {
  try {
    if (useCommon().isFrontendMode.value) {
      await processFrontendMenu(router)
    } else {
      await processBackendMenu(router)
    }
  } catch (error) {
    handleMenuError(error)
    throw error
  }
}

/**
 * 处理前端控制模式的菜单逻辑
 */
async function processFrontendMenu(router: Router): Promise<void> {
  const menuList = asyncRoutes.map((route) => menuDataToRouter(route))
  const userStore = useUserStore()

  // 安全检查用户信息和角色
  if (!userStore.info || !userStore.info.roles) {
    throw new Error('获取用户角色失败')
  }

  const roles = userStore.info.roles as unknown as string[]
  const filteredMenuList = filterMenuByRoles(menuList, roles)

  // 添加延时以提升用户体验
  await new Promise((resolve) => setTimeout(resolve, LOADING_DELAY))

  await registerAndStoreMenu(router, filteredMenuList)
}

/**
 * 处理后端控制模式的菜单逻辑
 */
async function processBackendMenu(router: Router): Promise<void> {
  const { menuList } = await menuService.getMenuList()
  await registerAndStoreMenu(router, menuList)
}

/**
 * 递归过滤空菜单项
 */
function filterEmptyMenus(menuList: AppRouteRecord[]): AppRouteRecord[] {
  return menuList
    .map((item) => {
      // 如果有子菜单，先递归过滤子菜单
      if (item.children && item.children.length > 0) {
        const filteredChildren = filterEmptyMenus(item.children)
        return {
          ...item,
          children: filteredChildren
        }
      }
      return item
    })
    .filter((item) => {
      // 过滤掉布局组件且没有子菜单的项
      const isEmptyLayoutMenu =
        item.component === RoutesAlias.Layout && (!item.children || item.children.length === 0)

      // 过滤掉组件为空字符串且没有子菜单的项
      const isEmptyComponentMenu =
        item.component === '' &&
        (!item.children || item.children.length === 0) &&
        item.meta.isIframe !== true

      return !(isEmptyLayoutMenu || isEmptyComponentMenu)
    })
}

/**
 * 注册路由并存储菜单数据
 */
async function registerAndStoreMenu(router: Router, menuList: AppRouteRecord[]): Promise<void> {
  if (!isValidMenuList(menuList)) {
    throw new Error('获取菜单列表失败，请重新登录')
  }
  const menuStore = useMenuStore()
  // 递归过滤掉为空的菜单项
  const list = filterEmptyMenus(menuList)
  menuStore.setMenuList(list)
  registerDynamicRoutes(router, list)

  // 补充隐藏的功能路由
  try {
    // 文章创建页
    if (router.hasRoute('Project') && !router.hasRoute('ArticleCreate')) {
      router.addRoute('Project', {
        path: 'article/create/:type',
        name: 'ArticleCreate',
        component: () => import('@/views/project/articles/create/index.vue'),
        meta: { title: '发布文章', keepAlive: false, isHide: true }
      })
    }

    // 协作文档编辑页（强制覆盖后端旧配置）
    if (router.hasRoute('Project')) {
      // 如果路由已存在，先删除
      if (router.hasRoute('CollaborationDocument')) {
        router.removeRoute('CollaborationDocument')
        console.log('🔄 [RouteGuard] 移除旧的 CollaborationDocument 路由')
      }

      // 添加新的协作文档编辑路由
      router.addRoute('Project', {
        path: 'collaboration/:documentId',
        name: 'CollaborationDocument',
        component: () => import('@/views/collaboration/edit/index.vue'),
        meta: {
          title: '编辑协作文档',
          keepAlive: false,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER'],
          activePath: '/project/collaboration',
          isHide: true
        }
      })
      console.log('✅ [RouteGuard] 已注册新的 CollaborationDocument 路由')
    }
  } catch (error) {
    console.error('❌ [RouteGuard] 补充路由失败:', error)
  }

  isRouteRegistered.value = true
  useWorktabStore().validateWorktabs(router)
}

/**
 * 处理菜单相关错误
 */
function handleMenuError(error: unknown): void {
  console.error('菜单处理失败:', error)
  useUserStore().logOut()
  throw error instanceof Error ? error : new Error('获取菜单列表失败，请重新登录')
}

/**
 * 根据角色过滤菜单
 */
const filterMenuByRoles = (menu: AppRouteRecord[], roles: string[]): AppRouteRecord[] => {
  return menu.reduce((acc: AppRouteRecord[], item) => {
    const itemRoles = item.meta?.roles
    const hasPermission = !itemRoles || itemRoles.some((role) => roles?.includes(role))

    if (hasPermission) {
      const filteredItem = { ...item }
      if (filteredItem.children?.length) {
        filteredItem.children = filterMenuByRoles(filteredItem.children, roles)
      }
      acc.push(filteredItem)
    }

    return acc
  }, [])
}

/**
 * 验证菜单列表是否有效
 */
function isValidMenuList(menuList: AppRouteRecord[]): boolean {
  return Array.isArray(menuList) && menuList.length > 0
}

/**
 * 重置路由相关状态
 */
export function resetRouterState(): void {
  isRouteRegistered.value = false
  const menuStore = useMenuStore()
  menuStore.removeAllDynamicRoutes()
  menuStore.setMenuList([])
}

/**
 * 处理根路径跳转到首页
 */
function handleRootPathRedirect(to: RouteLocationNormalized, next: NavigationGuardNext): boolean {
  if (to.path === '/') {
    const { homePath } = useCommon()
    if (homePath.value) {
      next({ path: homePath.value, replace: true })
      return true
    }
  }
  return false
}
