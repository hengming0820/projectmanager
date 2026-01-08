import { backendApi } from '@/utils/http/backendApi'
import type { User, UserCreate, UserUpdate } from '@/types/project'

export const userApi = {
  // 获取用户基本信息列表（所有用户可访问）
  getUsersBasic: (params?: { status?: string; size?: number }) =>
    backendApi.get('/users/basic', { params }),

  // 获取简化的用户列表（所有登录用户可访问）
  getSimpleUsers: () => backendApi.get('/users/simple'),

  // 获取用户列表（需要管理员权限）
  getUsers: (params?: {
    current?: number
    size?: number
    role?: string
    status?: string
    level?: string
  }) => backendApi.get('/users/', { params }),

  // 获取用户详情
  getUser: (userId: string) => backendApi.get(`/users/${userId}`),

  // 创建用户
  createUser: (userData: UserCreate) => backendApi.post('/users/', userData),

  // 更新用户
  updateUser: (userId: string, userData: UserUpdate) =>
    backendApi.put(`/users/${userId}`, userData),

  // 删除用户
  deleteUser: (userId: string) => backendApi.delete(`/users/${userId}`),

  // 切换用户状态
  toggleUserStatus: (userId: string) => backendApi.post(`/users/${userId}/toggle-status`),

  // 获取用户统计
  getUserStats: () => backendApi.get('/users/stats/summary'),

  // 个人中心：获取资料
  getMyProfile: () => backendApi.get('/users/me/profile'),
  // 个人中心：更新资料
  updateMyProfile: (data: {
    real_name?: string
    email?: string
    avatar_url?: string
    department?: string
  }) => backendApi.put('/users/me/profile', data),
  // 个人中心：修改密码
  changeMyPassword: (data: { current_password: string; new_password: string }) =>
    backendApi.put('/users/me/change-password', data)
}
