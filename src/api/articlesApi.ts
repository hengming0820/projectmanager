import http from '@/utils/http'

export interface Article {
  id: string
  title: string
  content: string
  summary?: string
  type: string // 支持任意文章类型，如meeting、model_test、需求文档、设计文档等
  status: 'draft' | 'published'
  tags: string[]
  cover_url?: string
  category?: string
  is_public?: boolean
  editable_user_ids?: string[]
  editable_roles?: string[]
  departments?: string[]
  project_id?: string // 所属项目ID
  author_id: string
  author_name: string
  view_count: number
  edit_count: number
  version: number
  // 编辑锁字段
  is_locked?: boolean
  locked_by?: string
  locked_at?: string
  created_at: string
  updated_at: string
}

export interface ArticleListResponse {
  items: Article[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const articlesApi = {
  list: (params: {
    page?: number
    page_size?: number
    type?: string // 支持任意文章类型
    status?: string
    search?: string
    year?: number
    month?: number
    author_name?: string
    project_id?: string // 按项目筛选
  }) => {
    return http.get<ArticleListResponse>({ url: '/articles/', params })
  },
  create: (data: Partial<Article>) => {
    return http.post<Article>({ url: '/articles/', data })
  },
  get: (id: string) => {
    return http.get<Article>({ url: `/articles/${id}` })
  },
  update: (id: string, data: Partial<Article>) => {
    return http.put<Article>({ url: `/articles/${id}`, data })
  },
  remove: (id: string) => {
    return http.del({ url: `/articles/${id}` })
  },
  history: (id: string) => {
    return http.get<
      {
        id: string
        editor_name: string
        action: string
        changes_summary?: string
        created_at: string
      }[]
    >({ url: `/articles/${id}/history` })
  },
  // 编辑锁相关
  lock: (id: string) => {
    return http.post<{ message: string; locked_by: string }>({ url: `/articles/${id}/lock` })
  },
  unlock: (id: string) => {
    return http.post<{ message: string }>({ url: `/articles/${id}/unlock` })
  },
  // 便捷方法
  getArticles: (params: any) => {
    return articlesApi.list(params)
  },
  createArticle: (data: any) => {
    return articlesApi.create(data)
  },
  deleteArticle: (id: string) => {
    return articlesApi.remove(id)
  }
}
