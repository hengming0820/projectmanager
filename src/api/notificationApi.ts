/**
 * 通知 API
 * 基于 Redis 存储，通知 7 天自动过期
 */
import http from '@/utils/http'

export const notificationApi = {
  /**
   * 获取通知列表（从 Redis，只返回未读通知）
   */
  getNotifications: (params?: { limit?: number }) => {
    return http.get({ url: '/notifications/', params })
  },

  /**
   * 获取未读通知数量
   */
  getUnreadCount: () => {
    return http.get({ url: '/notifications/unread-count' })
  },

  /**
   * 标记通知为已读
   */
  markAsRead: (notificationId: string) => {
    return http.post({ url: `/notifications/${notificationId}/read` })
  },

  /**
   * 标记所有通知为已读
   */
  markAllAsRead: () => {
    return http.post({ url: '/notifications/read-all' })
  },

  /**
   * 删除通知
   */
  deleteNotification: (notificationId: string) => {
    return http.del({ url: `/notifications/${notificationId}` })
  },

  /**
   * 清空所有已读通知
   */
  clearReadNotifications: () => {
    return http.del({ url: '/notifications/clear-read' })
  }
}
