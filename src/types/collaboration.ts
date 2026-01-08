/**
 * 团队协作文档相关类型定义
 */

// 协作文档状态
export type CollaborationStatus = 'draft' | 'active' | 'completed' | 'archived'

// 协作文档优先级
export type CollaborationPriority = 'low' | 'normal' | 'high' | 'urgent'

// 协作者角色
export type CollaboratorRole = 'owner' | 'editor' | 'viewer'

// 协作者信息
export interface Collaborator {
  id: string
  user_id: string
  user_name: string
  user_avatar?: string
  role: CollaboratorRole
  joined_at: string
  last_active_at?: string
}

// 协作文档基本信息
export interface CollaborationDocument {
  id: string
  title: string
  description?: string
  content: string // 富文本内容
  status: CollaborationStatus
  priority: CollaborationPriority

  // 协作信息
  collaborators: Collaborator[]
  owner_id: string
  owner_name: string
  editable_user_ids?: string[] // 可编辑用户ID列表
  editable_roles?: string[] // 可编辑角色列表
  departments?: string[] // 所属部门列表

  // 项目关联
  project_id?: string
  project_name?: string

  // 标签和分类
  tags: string[]
  category?: string

  // 时间信息
  created_at: string
  updated_at: string
  last_edited_by?: string
  last_edited_at?: string

  // 统计信息
  view_count: number
  edit_count: number

  // 版本控制
  version: number
  is_locked?: boolean
  locked_by?: string
  locked_at?: string
}

// 创建协作文档的数据
export interface CollaborationDocumentCreate {
  title: string
  description?: string
  content?: string
  priority?: CollaborationPriority
  project_id?: string
  tags?: string[]
  category?: string
  collaborator_ids?: string[] // 初始协作者ID列表
}

// 更新协作文档的数据
export interface CollaborationDocumentUpdate {
  title?: string
  description?: string
  content?: string
  status?: CollaborationStatus
  priority?: CollaborationPriority
  project_id?: string
  tags?: string[]
  category?: string
  editable_user_ids?: string[] // 可编辑用户ID列表
  editable_roles?: string[] // 可编辑角色列表
  departments?: string[] // 所属部门列表
}

// 协作文档查询参数
export interface CollaborationDocumentQueryParams {
  page?: number
  page_size?: number
  status?: CollaborationStatus
  priority?: CollaborationPriority
  project_id?: string
  category?: string
  tag?: string
  search?: string
  owner_id?: string
  collaborator_id?: string
  created_start?: string
  created_end?: string
  sort_by?: 'created_at' | 'updated_at' | 'title' | 'priority' | 'view_count'
  sort_order?: 'asc' | 'desc'
}

// 协作文档列表响应
export interface CollaborationDocumentListResponse {
  items: CollaborationDocument[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 文档编辑历史
export interface DocumentEditHistory {
  id: string
  document_id: string
  editor_id: string
  editor_name: string
  action: 'create' | 'update' | 'delete' | 'lock' | 'unlock'
  changes_summary?: string
  content_diff?: string
  created_at: string
}

// 实时协作状态
export interface CollaborationState {
  document_id: string
  active_editors: {
    user_id: string
    user_name: string
    cursor_position?: number
    selection_range?: { start: number; end: number }
    last_active: string
  }[]
  is_locked: boolean
  locked_by?: string
}

// 文档评论
export interface DocumentComment {
  id: string
  document_id: string
  user_id: string
  user_name: string
  user_avatar?: string
  content: string
  position?: number // 在文档中的位置
  parent_id?: string // 回复的评论ID
  created_at: string
  updated_at: string
}

// 协作统计信息
export interface CollaborationStatistics {
  total_documents: number
  active_documents: number
  total_collaborators: number
  documents_by_status: Record<CollaborationStatus, number>
  documents_by_priority: Record<CollaborationPriority, number>
  recent_activities: {
    document_id: string
    document_title: string
    action: string
    user_name: string
    created_at: string
  }[]
}
