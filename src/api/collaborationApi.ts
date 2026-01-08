/**
 * 团队协作文档 API
 */

import http from '@/utils/http'
import type {
  CollaborationDocument,
  CollaborationDocumentCreate,
  CollaborationDocumentUpdate,
  CollaborationDocumentQueryParams,
  CollaborationDocumentListResponse,
  Collaborator,
  DocumentEditHistory,
  CollaborationState,
  DocumentComment,
  CollaborationStatistics
} from '@/types/collaboration'

export const collaborationApi = {
  // ==================== 协作文档管理 ====================

  // 获取协作文档列表
  getDocuments: (params?: CollaborationDocumentQueryParams) => {
    console.log('📋 [CollaborationAPI] 获取协作文档列表，参数:', params)
    return http.get<CollaborationDocumentListResponse>({
      url: '/collaboration/documents',
      params
    })
  },

  // 获取协作文档详情
  getDocument: (documentId: string) => {
    console.log('📄 [CollaborationAPI] 获取协作文档详情:', documentId)
    return http.get<CollaborationDocument>({
      url: `/collaboration/documents/${documentId}`
    })
  },

  // 创建协作文档
  createDocument: (data: CollaborationDocumentCreate) => {
    console.log('➕ [CollaborationAPI] 创建协作文档，数据:', JSON.stringify(data, null, 2))
    return http.post<CollaborationDocument>({
      url: '/collaboration/documents',
      data
    })
  },

  // 更新协作文档
  updateDocument: (documentId: string, data: CollaborationDocumentUpdate) => {
    console.log('✏️ [CollaborationAPI] 更新协作文档:', documentId, data)
    return http.put<CollaborationDocument>({
      url: `/collaboration/documents/${documentId}`,
      data
    })
  },

  // 删除协作文档
  deleteDocument: (documentId: string) => {
    console.log('🗑️ [CollaborationAPI] 删除协作文档:', documentId)
    return http.del({
      url: `/collaboration/documents/${documentId}`
    })
  },

  // ==================== 协作者管理 ====================

  // 添加协作者
  addCollaborator: (documentId: string, userId: string, role: 'editor' | 'viewer' = 'editor') => {
    console.log('👥 [CollaborationAPI] 添加协作者:', documentId, userId, role)
    return http.post<Collaborator>({
      url: `/collaboration/documents/${documentId}/collaborators`,
      data: { user_id: userId, role }
    })
  },

  // 更新协作者角色
  updateCollaboratorRole: (documentId: string, userId: string, role: 'editor' | 'viewer') => {
    console.log('🔄 [CollaborationAPI] 更新协作者角色:', documentId, userId, role)
    return http.put<Collaborator>({
      url: `/collaboration/documents/${documentId}/collaborators/${userId}`,
      data: { role }
    })
  },

  // 移除协作者
  removeCollaborator: (documentId: string, userId: string) => {
    console.log('❌ [CollaborationAPI] 移除协作者:', documentId, userId)
    return http.del({
      url: `/collaboration/documents/${documentId}/collaborators/${userId}`
    })
  },

  // ==================== 实时协作 ====================

  // 锁定文档（开始编辑）
  lockDocument: (documentId: string) => {
    console.log('🔒 [CollaborationAPI] 锁定文档:', documentId)
    return http.post({
      url: `/collaboration/documents/${documentId}/lock`
    })
  },

  // 解锁文档（结束编辑）
  unlockDocument: (documentId: string) => {
    console.log('🔓 [CollaborationAPI] 解锁文档:', documentId)
    return http.post({
      url: `/collaboration/documents/${documentId}/unlock`
    })
  },

  // 编辑心跳/光标位置上报
  presence: (
    documentId: string,
    payload: { cursor_position?: number; selection_start?: number; selection_end?: number }
  ) => {
    return http.post({
      url: `/collaboration/documents/${documentId}/presence`,
      data: payload
    })
  },

  // 获取协作状态
  getCollaborationState: (documentId: string) => {
    return http.get<CollaborationState>({
      url: `/collaboration/documents/${documentId}/state`
    })
  },

  // 更新文档内容（实时保存）
  updateDocumentContent: (documentId: string, content: string) => {
    return http.put({
      url: `/collaboration/documents/${documentId}/content`,
      data: { content }
    })
  },

  // 获取文档内容 + 版本（用于前端轮询同步）
  getDocumentContent: (documentId: string) => {
    return http.get<{
      content: string
      version: number
      updated_at: string
      last_edited_by?: string
    }>({
      url: `/collaboration/documents/${documentId}/content`
    })
  },

  // ==================== 历史记录 ====================

  // 获取编辑历史
  getEditHistory: (documentId: string, page?: number, pageSize?: number) => {
    return http.get<{ items: DocumentEditHistory[]; total: number }>({
      url: `/collaboration/documents/${documentId}/history`,
      params: { page, page_size: pageSize }
    })
  },

  // ==================== 评论功能 ====================

  // 获取文档评论
  getComments: (documentId: string) => {
    return http.get<DocumentComment[]>({
      url: `/collaboration/documents/${documentId}/comments`
    })
  },

  // 添加评论
  addComment: (documentId: string, content: string, position?: number, parentId?: string) => {
    return http.post<DocumentComment>({
      url: `/collaboration/documents/${documentId}/comments`,
      data: { content, position, parent_id: parentId }
    })
  },

  // 删除评论
  deleteComment: (documentId: string, commentId: string) => {
    return http.del({
      url: `/collaboration/documents/${documentId}/comments/${commentId}`
    })
  },

  // ==================== 统计信息 ====================

  // 获取协作统计
  getStatistics: () => {
    return http.get<CollaborationStatistics>({
      url: '/collaboration/statistics'
    })
  },

  // ==================== 搜索和过滤 ====================

  // 搜索文档
  searchDocuments: (query: string, filters?: Partial<CollaborationDocumentQueryParams>) => {
    return http.get<CollaborationDocumentListResponse>({
      url: '/collaboration/documents/search',
      params: { search: query, ...filters }
    })
  },

  // 获取我参与的文档
  getMyDocuments: (params?: Partial<CollaborationDocumentQueryParams>) => {
    return http.get<CollaborationDocumentListResponse>({
      url: '/collaboration/documents/my',
      params
    })
  },

  // 获取最近访问的文档
  getRecentDocuments: (limit: number = 10) => {
    return http.get<CollaborationDocument[]>({
      url: '/collaboration/documents/recent',
      params: { limit }
    })
  }
}

// 协作文档工具函数
export const collaborationUtils = {
  // 格式化协作者显示
  formatCollaborators: (collaborators: Collaborator[]) => {
    return collaborators.map((c) => ({
      ...c,
      displayName: c.user_name,
      roleText: {
        owner: '所有者',
        editor: '编辑者',
        viewer: '查看者'
      }[c.role]
    }))
  },

  // 检查用户权限
  canEdit: (document: CollaborationDocument, userId: string, userRole?: string) => {
    // 管理员拥有所有权限
    if (userRole === 'admin') return true
    // 文档所有者可以编辑
    if (document.owner_id === userId) return true
    // 协作者中的编辑者可以编辑
    const collaborator = document.collaborators.find((c) => c.user_id === userId)
    return collaborator?.role === 'editor'
  },

  // 检查是否可以管理协作者
  canManageCollaborators: (document: CollaborationDocument, userId: string, userRole?: string) => {
    // 管理员拥有所有权限
    if (userRole === 'admin') return true
    // 文档所有者可以管理协作者
    return document.owner_id === userId
  },

  // 检查是否可以删除文档
  canDelete: (document: CollaborationDocument, userId: string, userRole?: string) => {
    // 管理员拥有所有权限
    if (userRole === 'admin') return true
    // 文档所有者可以删除
    return document.owner_id === userId
  },

  // 获取状态显示文本
  getStatusText: (status: string) => {
    const statusMap = {
      draft: '草稿',
      active: '进行中',
      completed: '已完成',
      archived: '已归档'
    }
    return statusMap[status as keyof typeof statusMap] || status
  },

  // 获取优先级显示文本和颜色
  getPriorityInfo: (priority: string) => {
    const priorityMap = {
      low: { text: '低', color: '#909399' },
      normal: { text: '普通', color: '#409eff' },
      high: { text: '高', color: '#e6a23c' },
      urgent: { text: '紧急', color: '#f56c6c' }
    }
    return priorityMap[priority as keyof typeof priorityMap] || { text: priority, color: '#909399' }
  },

  // 生成文档摘要
  generateSummary: (content: string, maxLength: number = 100) => {
    // 移除HTML标签
    const textContent = content.replace(/<[^>]*>/g, '').trim()
    if (textContent.length <= maxLength) return textContent
    return textContent.substring(0, maxLength) + '...'
  }
}
