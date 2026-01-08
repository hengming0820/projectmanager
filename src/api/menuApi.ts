import { asyncRoutes } from '@/router/routes/asyncRoutes'
import { menuDataToRouter } from '@/router/utils/menuToRouter'
import { AppRouteRecord } from '@/types/router'
import { backendApi } from '@/utils/http/backendApi'
import AppConfig from '@/config'

interface MenuResponse {
  menuList: AppRouteRecord[]
}

// 菜单接口
export const menuService = {
  async getMenuList(delay = 300): Promise<MenuResponse> {
    try {
      // 检查是否启用mock模式或前端模式
      const isFrontendMode = import.meta.env.VITE_ACCESS_MODE === 'frontend'

      if (AppConfig.mockMode.enabled || isFrontendMode) {
        console.log('🎭 [MenuService] 使用前端模式或Mock模式获取菜单')
        // 模拟接口返回的菜单数据
        const menuData = asyncRoutes
        // 处理菜单数据
        const menuList = menuData.map((route) => menuDataToRouter(route))
        // 模拟接口延迟
        await new Promise((resolve) => setTimeout(resolve, delay))

        return { menuList }
      }

      // 使用真实后端 API
      console.log('🌐 [MenuService] 使用后端 API 获取菜单')
      const response = await backendApi.get<MenuResponse>('/menu/list')

      console.log('✅ [MenuService] 后端菜单获取成功:', response)

      // 转换后端返回的菜单数据为前端路由格式
      const backendMenuList = response.menuList.map((route) => menuDataToRouter(route))

      // 顶层及子菜单去重合并（以 path 为准，合并 children）
      const deduped = dedupeAndMergeMenus(backendMenuList)

      console.log('✅ [MenuService] 后端菜单去重后:', deduped)

      return { menuList: deduped }
    } catch (error) {
      console.error('❌ [MenuService] 获取菜单失败:', error)
      throw error instanceof Error ? error : new Error('获取菜单失败')
    }
  }
}

function normalizeRoute(r: AppRouteRecord): AppRouteRecord {
  // 仅保证 children 为数组，避免不必要的深拷贝以提升性能
  return { ...r, children: Array.isArray(r.children) ? r.children : [] }
}

function ensurePerformancePersonal(
  primary: AppRouteRecord[],
  fallback: AppRouteRecord[]
): AppRouteRecord[] {
  const list = primary.map((r) => normalizeRoute(r))
  const perfFallback = fallback.find((r) => r.path === '/performance')
  if (!perfFallback) return list
  const perfIndex = list.findIndex((r) => r.path === '/performance')
  if (perfIndex === -1) {
    // 后端未下发绩效系统，直接追加后备绩效菜单
    list.push(normalizeRoute({ ...perfFallback, children: perfFallback.children || [] }))
    return list
  }
  // 确认“我的绩效”子路由存在
  const perf = list[perfIndex]
  const existing = new Set((perf.children || []).map((c) => c.path))
  // 合并后备绩效菜单下缺失的所有子路由（包含 team/personal 等）
  for (const child of perfFallback.children || []) {
    if (!existing.has(child.path)) {
      perf.children = [
        ...(perf.children || []),
        normalizeRoute({ ...child, children: child.children || [] })
      ]
      existing.add(child.path)
    }
  }
  return list
}

// 按 path 去重并合并同一路径分组的 children，保留较完整的一份 meta
function dedupeAndMergeMenus(list: AppRouteRecord[]): AppRouteRecord[] {
  const map = new Map<string, AppRouteRecord>()
  for (const item of list) {
    const key = item.path
    if (!key) continue
    const existed = map.get(key)
    if (!existed) {
      map.set(key, cloneRoute(item))
    } else {
      // 合并 children
      const mergedChildren = mergeChildren(existed.children || [], item.children || [])
      const merged: AppRouteRecord = {
        ...existed,
        // 优先保留已有 meta，若不存在则用新 meta
        meta: existed.meta || item.meta,
        children: mergedChildren
      }
      map.set(key, merged)
    }
  }
  return Array.from(map.values())
}

function mergeChildren(a: AppRouteRecord[], b: AppRouteRecord[]): AppRouteRecord[] {
  const result: AppRouteRecord[] = []
  const byPath = new Map<string, AppRouteRecord>()
  const push = (r: AppRouteRecord) => {
    const key = r.path
    if (!key) return
    const existed = byPath.get(key)
    if (!existed) {
      byPath.set(key, cloneRoute(r))
    } else {
      // 递归合并子节点
      const merged: AppRouteRecord = {
        ...existed,
        meta: existed.meta || r.meta,
        children: mergeChildren(existed.children || [], r.children || [])
      }
      byPath.set(key, merged)
    }
  }
  a.forEach(push)
  b.forEach(push)
  byPath.forEach((v) => result.push(v))
  return result
}

function cloneRoute(r: AppRouteRecord): AppRouteRecord {
  return {
    ...r,
    children: r.children ? r.children.map((c) => cloneRoute(c)) : []
  }
}
