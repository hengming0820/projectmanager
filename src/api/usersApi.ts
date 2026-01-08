import request from '@/utils/http'
import { backendApi } from '@/utils/http/backendApi'
import AppConfig from '@/config'
import { MockUserService } from '@/mock/user/mockUserService'

export class UserService {
  // 登录
  static async login(params: Api.Auth.LoginParams) {
    console.log('🔐 [UserService] 开始登录流程:', {
      userName: params.userName,
      mockMode: AppConfig.mockMode.enabled
    })

    // 检查是否启用mock模式
    if (AppConfig.mockMode.enabled) {
      console.log('🎭 [UserService] 使用Mock模式登录')
      try {
        const mockResponse = await MockUserService.login({
          userName: params.userName,
          password: params.password
        })

        console.log('✅ [UserService] Mock登录成功:', mockResponse)
        return {
          token: mockResponse.token,
          refreshToken: mockResponse.refreshToken
        }
      } catch (error) {
        console.error('❌ [UserService] Mock登录失败:', error)
        throw new Error(error instanceof Error ? error.message : '登录失败')
      }
    }

    // 使用真实API
    console.log('🌐 [UserService] 使用真实API登录')
    try {
      const response = await backendApi.post<{
        access_token: string
        token_type: string
        user: {
          id: string
          username: string
          real_name: string
          email: string
          role: string
          department?: string
          avatar_url?: string
          status: string
          created_at: string
          updated_at: string
        }
      }>('/auth/login', {
        username: params.userName,
        password: params.password
      })

      console.log('✅ [UserService] 真实API登录成功:', response)

      // 转换响应格式以匹配前端期望
      const result = {
        token: response.access_token,
        refreshToken: response.access_token, // 后端没有refreshToken，暂时使用access_token
        user: response.user // 保存用户信息以便后续使用
      }

      console.log('🔄 [UserService] 转换后的登录结果:', result)
      return result
    } catch (error) {
      console.error('❌ [UserService] 真实API登录失败:', error)
      throw new Error(error instanceof Error ? error.message : '登录失败')
    }
  }

  // 获取用户信息
  static async getUserInfo() {
    console.log('👤 [UserService] 开始获取用户信息')

    // 检查是否启用mock模式
    if (AppConfig.mockMode.enabled) {
      console.log('🎭 [UserService] 使用Mock模式获取用户信息')
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token')
        console.log('🔑 [UserService] Mock模式使用的token:', token)

        const mockUser = await MockUserService.getUserInfo(token || '')

        console.log('✅ [UserService] Mock获取用户信息成功:', mockUser)

        return {
          id: mockUser.id,
          username: mockUser.username,
          realName: mockUser.realName,
          email: mockUser.email,
          role: mockUser.role,
          roles: mockUser.roles, // 添加roles字段
          avatar: mockUser.avatar,
          department: mockUser.department,
          status: mockUser.status,
          buttons: ['add', 'edit', 'delete', 'view'] // 默认权限按钮
        }
      } catch (error) {
        console.error('❌ [UserService] Mock获取用户信息失败:', error)
        throw new Error(error instanceof Error ? error.message : '获取用户信息失败')
      }
    }

    // 使用真实API
    console.log('🌐 [UserService] 使用真实API获取用户信息')
    try {
      const response = await backendApi.get<{
        id: string
        username: string
        real_name: string
        email: string
        role: string
        department?: string
        avatar_url?: string
        status: string
        created_at: string
        updated_at: string
      }>('/auth/me')

      console.log('✅ [UserService] 真实API获取用户信息成功:', response)

      // 后端角色到前端角色标识的映射
      const mapRoleToFrontend = (role: string): string[] => {
        const r = (role || '').toLowerCase()
        if (r === 'super') return ['R_SUPER', 'R_ADMIN']
        if (r === 'admin' || r === 'administrator') return ['R_ADMIN']
        if (r === 'annotator') return ['R_ANNOTATOR']
        if (r === 'reviewer') return ['R_REVIEWER']
        return ['R_USER']
      }
      const mappedRoles = mapRoleToFrontend(response.role)
      console.log('🔐 [UserService] 角色映射:', {
        backendRole: response.role,
        frontendRoles: mappedRoles
      })

      // 转换响应格式以匹配前端期望
      const result = {
        userId: response.id, // 保持字符串格式，不转换为数字
        userName: response.username,
        roles: mappedRoles,
        buttons: ['add', 'edit', 'delete', 'view'],
        avatar: response.avatar_url || '',
        email: response.email,
        phone: '',
        // 为用户存储组件添加必要字段
        id: response.id,
        username: response.username,
        real_name: response.real_name,
        realName: response.real_name, // 兼容性字段
        role: response.role,
        department: response.department || '',
        status: response.status,
        created_at: response.created_at,
        updated_at: response.updated_at
      }

      console.log('🔄 [UserService] 转换后的用户信息:', result)
      return result
    } catch (error) {
      console.error('❌ [UserService] 真实API获取用户信息失败:', error)
      throw new Error(error instanceof Error ? error.message : '获取用户信息失败')
    }
  }

  // 获取用户列表
  static async getUserList(params: Api.Common.PaginatingSearchParams) {
    console.log('📋 [UserService] 开始获取用户列表:', params)

    // 检查是否启用mock模式
    if (AppConfig.mockMode.enabled) {
      console.log('🎭 [UserService] 使用Mock模式获取用户列表')
      try {
        const mockResult = await MockUserService.getUserList(params)

        console.log('✅ [UserService] Mock获取用户列表成功:', mockResult)

        return {
          list: mockResult.list.map((user) => ({
            id: user.id,
            username: user.username,
            realName: user.realName,
            email: user.email,
            role: user.role,
            avatar: user.avatar,
            department: user.department,
            status: user.status
          })),
          total: mockResult.total
        }
      } catch (error) {
        console.error('❌ [UserService] Mock获取用户列表失败:', error)
        throw new Error(error instanceof Error ? error.message : '获取用户列表失败')
      }
    }

    // 使用真实API
    console.log('🌐 [UserService] 使用真实API获取用户列表')
    try {
      const result = await backendApi.get<Api.User.UserListData>('/users', { params })
      console.log('✅ [UserService] 真实API获取用户列表成功:', result)
      return result
    } catch (error) {
      console.error('❌ [UserService] 真实API获取用户列表失败:', error)
      throw new Error(error instanceof Error ? error.message : '获取用户列表失败')
    }
  }
}
