import { backendApi } from '@/utils/http/backendApi'
import type {
  WorkWeek,
  WorkWeekCreate,
  WorkWeekUpdate,
  WorkWeekQueryParams,
  WorkWeekStatistics,
  WorkLogEntry,
  WorkLogEntryCreate,
  WorkLogEntryUpdate,
  WorkLogEntrySubmit,
  WorkLogEntryReview,
  WorkLogQueryParams,
  WorkLogType,
  WorkLogTypeCreate,
  WorkLogExportOptions
} from '@/types/work-log'

// ==================== 工作周管理 ====================

export const workWeekApi = {
  // 创建工作周
  createWorkWeek: (data: WorkWeekCreate) => {
    return backendApi.post<WorkWeek>('/work-logs/weeks', data)
  },

  // 获取工作周列表
  getWorkWeeks: (params?: WorkWeekQueryParams) => {
    console.log('🌐 [WorkLogAPI] 调用 getWorkWeeks，参数:', params)
    const request = backendApi.get<any>('/work-logs/weeks', { params })
    console.log('📡 [WorkLogAPI] 请求对象创建完成')
    return request
  },

  // 获取工作周详情
  getWorkWeek: (weekId: string) => {
    return backendApi.get<WorkWeek>(`/work-logs/weeks/${weekId}`)
  },

  // 更新工作周
  updateWorkWeek: (weekId: string, data: WorkWeekUpdate) => {
    return backendApi.put<WorkWeek>(`/work-logs/weeks/${weekId}`, data)
  },

  // 删除工作周
  deleteWorkWeek: (weekId: string) => {
    return backendApi.delete(`/work-logs/weeks/${weekId}`)
  },

  // 获取工作周统计
  getWorkWeekStatistics: (weekId: string) => {
    return backendApi.get<WorkWeekStatistics>(`/work-logs/weeks/${weekId}/statistics`)
  },

  // 为工作周生成条目
  generateEntriesForWeek: (weekId: string, userIds?: string[]) => {
    return backendApi.post<{ message: string }>(`/work-logs/weeks/${weekId}/generate-entries`, {
      user_ids: userIds // 后端期望 user_ids（蛇形命名）
    })
  }
}

// ==================== 工作日志条目管理 ====================

export const workLogEntryApi = {
  // 获取工作周的日志条目
  getWorkLogEntries: (weekId: string, userId?: string) => {
    return backendApi.get<WorkLogEntry[]>(`/work-logs/weeks/${weekId}/entries`, {
      params: userId ? { user_id: userId } : {}
    })
  },

  // 创建工作日志条目
  createWorkLogEntry: (data: WorkLogEntryCreate) => {
    console.log('🚀 [WorkLogAPI] 创建工作日志条目，数据:', JSON.stringify(data, null, 2))
    return backendApi.post<WorkLogEntry>('/work-logs/entries', data)
  },

  // 更新工作日志条目
  updateWorkLogEntry: (entryId: string, data: WorkLogEntryUpdate) => {
    return backendApi.put<WorkLogEntry>(`/work-logs/entries/${entryId}`, data)
  },

  // 删除工作日志条目
  deleteWorkLogEntry: (entryId: string) => {
    return backendApi.delete(`/work-logs/entries/${entryId}`)
  },

  // 提交工作日志条目
  submitWorkLogEntry: (entryId: string, data: WorkLogEntrySubmit) => {
    return backendApi.post<WorkLogEntry>(`/work-logs/entries/${entryId}/submit`, data)
  },

  // 审核工作日志条目
  reviewWorkLogEntry: (entryId: string, data: WorkLogEntryReview) => {
    return backendApi.post<WorkLogEntry>(`/work-logs/entries/${entryId}/review`, data)
  },

  // 批量操作工作日志条目
  batchUpdateEntries: (entryIds: string[], data: WorkLogEntryUpdate) => {
    return backendApi.put<{ updated: number }>('/work-logs/entries/batch', {
      entry_ids: entryIds,
      updates: data
    })
  }
}

// ==================== 工作类型管理 ====================

export const workLogTypeApi = {
  // 获取工作类型列表
  getWorkLogTypes: (isActive?: boolean) => {
    return backendApi.get<WorkLogType[]>('/work-logs/types', {
      params: isActive !== undefined ? { is_active: isActive } : {}
    })
  },

  // 创建工作类型
  createWorkLogType: (data: WorkLogTypeCreate) => {
    return backendApi.post<WorkLogType>('/work-logs/types', data)
  },

  // 更新工作类型
  updateWorkLogType: (typeId: string, data: Partial<WorkLogTypeCreate>) => {
    return backendApi.put<WorkLogType>(`/work-logs/types/${typeId}`, data)
  },

  // 删除工作类型
  deleteWorkLogType: (typeId: string) => {
    return backendApi.delete(`/work-logs/types/${typeId}`)
  }
}

// ==================== 工具函数 ====================

export const workLogUtils = {
  // 获取状态文本
  getStatusText: (status: string) => {
    const statusMap = {
      pending: '待填写',
      submitted: '已提交',
      approved: '已通过',
      rejected: '已驳回'
    }
    return statusMap[status as keyof typeof statusMap] || status
  },

  // 获取状态类型（用于 el-tag）
  getStatusType: (status: string) => {
    const typeMap = {
      pending: 'info',
      submitted: 'warning',
      approved: 'success',
      rejected: 'danger'
    }
    return typeMap[status as keyof typeof typeMap] || 'info'
  },

  // 获取优先级文本
  getPriorityText: (priority: string) => {
    const priorityMap = {
      low: '低',
      normal: '普通',
      high: '高',
      urgent: '紧急'
    }
    return priorityMap[priority as keyof typeof priorityMap] || priority
  },

  // 获取优先级类型
  getPriorityType: (priority: string) => {
    const typeMap = {
      low: 'info',
      normal: '',
      high: 'warning',
      urgent: 'danger'
    }
    return typeMap[priority as keyof typeof typeMap] || ''
  },

  // 格式化工作日期（使用本地时区）
  formatWorkDate: (date: string) => {
    const d = new Date(date + 'T00:00:00') // 添加时间确保本地时区
    const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const month = (d.getMonth() + 1).toString().padStart(2, '0')
    const day = d.getDate().toString().padStart(2, '0')
    const weekDay = weekDays[d.getDay()]
    return `${month}-${day} ${weekDay}`
  },

  // 计算工作周的日期范围（使用本地时区）
  getWorkWeekDates: (startDate: string) => {
    const start = new Date(startDate + 'T00:00:00') // 添加时间确保本地时区
    const dates = []
    for (let i = 0; i < 5; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      dates.push(`${year}-${month}-${day}`)
    }
    return dates
  },

  // 获取当前周的周一日期（使用本地时区）
  getCurrentWeekMonday: () => {
    const today = new Date()
    const day = today.getDay()
    const diff = today.getDate() - day + (day === 0 ? -6 : 1) // 调整到周一
    const monday = new Date(today.getFullYear(), today.getMonth(), diff)

    // 使用本地时区格式化为 YYYY-MM-DD
    const year = monday.getFullYear()
    const month = String(monday.getMonth() + 1).padStart(2, '0')
    const dayStr = String(monday.getDate()).padStart(2, '0')
    return `${year}-${month}-${dayStr}`
  },

  // 获取指定日期所在周的周一（使用本地时区）
  getWeekMonday: (date: string) => {
    const d = new Date(date + 'T00:00:00') // 添加时间确保本地时区
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    const monday = new Date(d.getFullYear(), d.getMonth(), diff)

    // 使用本地时区格式化为 YYYY-MM-DD
    const year = monday.getFullYear()
    const month = String(monday.getMonth() + 1).padStart(2, '0')
    const dayStr = String(monday.getDate()).padStart(2, '0')
    return `${year}-${month}-${dayStr}`
  },

  // 验证工作周日期范围（使用本地时区）
  validateWorkWeekDates: (startDate: string, endDate: string) => {
    const start = new Date(startDate + 'T00:00:00') // 添加时间确保本地时区
    const end = new Date(endDate + 'T00:00:00') // 添加时间确保本地时区
    const diffDays = (end.getTime() - start.getTime()) / (1000 * 3600 * 24)

    return {
      isValid: diffDays === 4 && start.getDay() === 1 && end.getDay() === 5,
      error:
        diffDays !== 4
          ? '工作周必须是5天'
          : start.getDay() !== 1
            ? '开始日期必须是周一'
            : end.getDay() !== 5
              ? '结束日期必须是周五'
              : null
    }
  },

  // 计算完成率颜色
  getCompletionRateColor: (rate: number) => {
    if (rate >= 90) return '#67C23A' // 绿色
    if (rate >= 70) return '#E6A23C' // 橙色
    if (rate >= 50) return '#F56C6C' // 红色
    return '#909399' // 灰色
  },

  // 导出工作日志
  exportWorkLog: async (options: WorkLogExportOptions) => {
    try {
      const response = await backendApi.post<Blob>('/work-logs/export', options, {
        responseType: 'blob'
      })

      // 创建下载链接
      const blob = new Blob([response])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // 设置文件名
      const weekInfo = `工作周${options.workWeekId.slice(-8)}`
      const timestamp = new Date().toISOString().split('T')[0]
      link.download = `${weekInfo}_工作日志_${timestamp}.${options.format}`

      // 触发下载
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      return { success: true }
    } catch (error) {
      console.error('导出失败:', error)
      throw error
    }
  }
}

// ==================== Mock 数据（开发阶段使用） ====================

export const mockWorkLogData = {
  // 生成模拟工作周数据
  generateMockWorkWeeks: (count: number = 5): WorkWeek[] => {
    const weeks: WorkWeek[] = []
    const now = new Date()

    for (let i = 0; i < count; i++) {
      const startDate = new Date(now)
      startDate.setDate(now.getDate() - (now.getDay() - 1) - i * 7) // 获取之前几周的周一

      const endDate = new Date(startDate)
      endDate.setDate(startDate.getDate() + 4) // 周五

      weeks.push({
        id: `week-${i + 1}`,
        title: `第${i + 1}周工作日志`,
        week_start_date: startDate.toISOString().split('T')[0],
        week_end_date: endDate.toISOString().split('T')[0],
        description: `这是第${i + 1}周的工作日志模板`,
        status: i === 0 ? 'active' : 'archived',
        created_by: 'admin',
        created_at: new Date(now.getTime() - i * 7 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(now.getTime() - i * 7 * 24 * 60 * 60 * 1000).toISOString(),
        total_entries: 25, // 5个用户 * 5天
        submitted_entries: Math.floor(Math.random() * 25),
        completion_rate: Math.floor(Math.random() * 100)
      })
    }

    return weeks
  },

  // 生成模拟工作日志条目
  generateMockEntries: (weekId: string, userCount: number = 5): WorkLogEntry[] => {
    const entries: WorkLogEntry[] = []
    const workTypes = ['开发', '测试', '会议', '学习', '文档']
    const statuses: Array<'pending' | 'submitted' | 'approved' | 'rejected'> = [
      'pending',
      'submitted',
      'approved',
      'rejected'
    ]

    for (let userId = 1; userId <= userCount; userId++) {
      for (let day = 0; day < 5; day++) {
        const workDate = new Date()
        workDate.setDate(workDate.getDate() - workDate.getDay() + 1 + day) // 本周的工作日

        entries.push({
          id: `entry-${weekId}-${userId}-${day}`,
          work_week_id: weekId,
          user_id: `user${userId}`,
          work_date: workDate.toISOString().split('T')[0],
          day_of_week: day + 1,
          work_content: `用户${userId}第${day + 1}天的工作内容...`,
          work_type: workTypes[Math.floor(Math.random() * workTypes.length)],
          priority: 'normal',
          planned_hours: 8,
          actual_hours: Math.floor(Math.random() * 10) + 6,
          status: statuses[Math.floor(Math.random() * statuses.length)],
          completion_rate: Math.floor(Math.random() * 100),
          difficulties: Math.random() > 0.7 ? '遇到了一些技术难题' : undefined,
          next_day_plan: '明天计划继续推进项目进度',
          remarks: Math.random() > 0.8 ? '今天工作顺利' : undefined,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          user_name: `用户${userId}`,
          reviewer_name: Math.random() > 0.5 ? '审核员A' : undefined
        })
      }
    }

    return entries
  }
}
