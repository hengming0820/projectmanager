// 工作日志相关类型定义

export type WorkLogStatus = 'pending' | 'submitted' | 'approved' | 'rejected'
export type WorkLogPriority = 'low' | 'normal' | 'high' | 'urgent'
export type WorkWeekStatus = 'active' | 'archived' | 'deleted' | 'draft'

// 工作日志类型
export interface WorkLogType {
  id: string
  name: string
  description?: string
  color: string
  icon?: string
  isActive: boolean
  sortOrder: number
  createdAt: string
  updatedAt: string
}

export interface WorkLogTypeCreate {
  name: string
  description?: string
  color?: string
  icon?: string
  isActive?: boolean
  sortOrder?: number
}

// 工作周
export interface WorkWeek {
  id: string
  title: string
  week_start_date: string // YYYY-MM-DD
  week_end_date: string // YYYY-MM-DD
  description?: string
  status: WorkWeekStatus
  config?: Record<string, any>
  created_by: string
  created_at: string
  updated_at: string

  // 统计信息
  total_entries?: number
  submitted_entries?: number
  completion_rate?: number
}

export interface WorkWeekCreate {
  title: string
  week_start_date: string
  week_end_date: string
  week_number?: number
  status?: WorkWeekStatus
  description?: string
  config?: Record<string, any>
}

export interface WorkWeekUpdate {
  title?: string
  week_start_date?: string
  week_end_date?: string
  week_number?: number
  description?: string
  status?: WorkWeekStatus
  config?: Record<string, any>
}

// 工作日志条目
export interface WorkLogEntry {
  id: string
  work_week_id: string
  user_id: string
  work_date: string // YYYY-MM-DD
  day_of_week: number // 1-7, 1=Monday
  work_content?: string
  work_type?: string
  priority: WorkLogPriority
  planned_hours: number
  actual_hours?: number
  status: WorkLogStatus
  completion_rate: number
  difficulties?: string
  next_day_plan?: string
  remarks?: string
  submitted_at?: string
  reviewed_at?: string
  reviewed_by?: string
  review_comment?: string
  created_at: string
  updated_at: string

  // 关联信息
  user_name?: string
  reviewer_name?: string
  work_type_info?: WorkLogType
}

export interface WorkLogEntryCreate {
  work_week_id: string
  work_date: string
  work_content?: string
  work_type?: string
  priority?: WorkLogPriority
  planned_hours?: number
  actual_hours?: number
  completion_rate?: number
  difficulties?: string
  next_day_plan?: string
  remarks?: string
}

export interface WorkLogEntryUpdate {
  work_content?: string
  work_type?: string
  priority?: WorkLogPriority
  planned_hours?: number
  actual_hours?: number
  completion_rate?: number
  difficulties?: string
  next_day_plan?: string
  remarks?: string
}

export interface WorkLogEntrySubmit {
  actual_hours: number
  completion_rate: number
  remarks?: string
}

export interface WorkLogEntryReview {
  status: WorkLogStatus
  review_comment?: string
}

// 工作周汇总
export interface WorkWeekSummary {
  work_week_id: string
  user_id: string
  user_name: string
  total_planned_hours: number
  total_actual_hours: number
  average_completion_rate: number
  submitted_days: number
  total_days: number
  status_summary: Record<string, number>
}

export interface WorkWeekStatistics {
  work_week: WorkWeek
  user_summaries: WorkWeekSummary[]
  overall_stats: Record<string, any>
}

// 查询参数
export interface WorkLogQueryParams {
  work_week_id?: string
  user_id?: string
  work_date_start?: string
  work_date_end?: string
  status?: WorkLogStatus[]
  work_type?: string
  page?: number
  page_size?: number
}

export interface WorkWeekQueryParams {
  status?: WorkWeekStatus
  dateStart?: string
  dateEnd?: string
  createdBy?: string
  page?: number
  pageSize?: number
}

// 表格展示相关
export interface WorkLogTableRow {
  userId: string
  userName: string
  realName?: string
  department?: string
  monday?: WorkLogEntry
  tuesday?: WorkLogEntry
  wednesday?: WorkLogEntry
  thursday?: WorkLogEntry
  friday?: WorkLogEntry
  weekSummary?: {
    totalPlannedHours: number
    totalActualHours: number
    averageCompletionRate: number
    submittedDays: number
    totalDays: number
  }
}

// 工作日志模板配置
export interface WorkLogTemplate {
  id: string
  name: string
  description?: string
  fields: WorkLogTemplateField[]
  isDefault: boolean
  createdAt: string
  updatedAt: string
}

export interface WorkLogTemplateField {
  id: string
  name: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'select' | 'datetime'
  required: boolean
  defaultValue?: any
  options?: string[]
  placeholder?: string
  validation?: {
    min?: number
    max?: number
    pattern?: string
  }
}

// 日志导出
export interface WorkLogExportOptions {
  workWeekId: string
  format: 'excel' | 'pdf' | 'csv'
  includeFields: string[]
  userIds?: string[]
  dateRange?: [string, string]
}

// 统计图表数据
export interface WorkLogChartData {
  completionTrend: {
    dates: string[]
    data: number[]
  }
  workTypeDistribution: {
    name: string
    value: number
    color: string
  }[]
  userPerformance: {
    userName: string
    completionRate: number
    totalHours: number
  }[]
}

// 工作日志通知
export interface WorkLogNotification {
  id: string
  type: 'reminder' | 'approval' | 'rejection'
  title: string
  message: string
  workWeekId?: string
  entryId?: string
  isRead: boolean
  createdAt: string
}
