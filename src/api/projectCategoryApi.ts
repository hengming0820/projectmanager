/**
 * 项目分类 API
 */
import { backendApi } from '@/utils/http/backendApi'

export interface ProjectCategory {
  id: string
  project_id: string
  name: string
  type: string
  icon?: string
  description?: string
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ProjectCategoryCreate {
  project_id: string
  name: string
  type: string
  icon?: string
  description?: string
  sort_order?: number
}

export interface ProjectCategoryUpdate {
  name?: string
  icon?: string
  description?: string
  sort_order?: number
}

export interface ProjectCategoryListResponse {
  items: ProjectCategory[]
  total: number
}

export const projectCategoryApi = {
  /**
   * 获取项目的所有分类
   */
  getProjectCategories: (projectId: string) => {
    return backendApi.get<ProjectCategoryListResponse>(`/projects/${projectId}/categories`)
  },

  /**
   * 创建项目分类
   */
  createCategory: (projectId: string, data: ProjectCategoryCreate) => {
    return backendApi.post<ProjectCategory>(`/projects/${projectId}/categories`, data)
  },

  /**
   * 更新项目分类
   */
  updateCategory: (categoryId: string, data: ProjectCategoryUpdate) => {
    return backendApi.put<ProjectCategory>(`/categories/${categoryId}`, data)
  },

  /**
   * 删除项目分类
   */
  deleteCategory: (categoryId: string) => {
    return backendApi.delete<void>(`/categories/${categoryId}`)
  }
}

export default projectCategoryApi
