import { backendApi, ExtendedAxiosRequestConfig } from '@/utils/http/backendApi'

export const roleApi = {
  // 获取角色列表
  getRoles: (
    params?: { current?: number; size?: number; name?: string },
    config?: ExtendedAxiosRequestConfig
  ) => backendApi.get('/roles/', { ...config, params }),

  // 获取角色详情
  getRole: (roleId: string) => backendApi.get(`/roles/${roleId}`),

  // 创建角色
  createRole: (roleData: any) => backendApi.post('/roles/', roleData),

  // 更新角色
  updateRole: (roleId: string, roleData: any) => backendApi.put(`/roles/${roleId}`, roleData),

  // 删除角色
  deleteRole: (roleId: string) => backendApi.delete(`/roles/${roleId}`),
  // 获取角色已勾选权限
  getRolePermissions: (roleId: string) => backendApi.get(`/roles/${roleId}/permissions`),
  // 更新角色权限
  updateRolePermissions: (roleId: string, permissions: string[]) =>
    backendApi.put(`/roles/${roleId}/permissions`, { permissions })
}
