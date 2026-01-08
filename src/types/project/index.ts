/**
 * 项目管理系统类型定义
 */

// 项目状态
export type ProjectStatus = 'active' | 'completed' | 'paused' | 'cancelled'

// 任务状态
export type TaskStatus =
  | 'pending'
  | 'assigned'
  | 'in_progress'
  | 'submitted'
  | 'approved'
  | 'rejected'
  | 'abandoned'
  | 'skipped'
  | 'skip_pending'

// 任务优先级
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

// 项目分类
export type ProjectCategory = 'case' | 'ai_annotation'
export type CaseSubCategory = 'trial' | 'research' | 'paid'
export type AISubCategory = 'research' | 'daily'

// 项目分类配置
export interface ProjectCategoryConfig {
  category: ProjectCategory
  subCategory: CaseSubCategory | AISubCategory
}

// 用户角色
export type UserRole = 'admin' | 'annotator' | 'reviewer'

// 项目信息
export interface Project {
  id: string
  name: string
  description?: string
  status: ProjectStatus
  priority: TaskPriority
  category: ProjectCategory
  subCategory: CaseSubCategory | AISubCategory
  startDate: string
  endDate?: string
  createdAt: string
  updatedAt: string
  createdBy: string
  totalTasks: number
  completedTasks: number
  assignedTasks: number
}

// 任务信息
export interface Task {
  id: string
  projectId: string
  projectName: string
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  assignedTo?: string
  assignedAt?: string
  startedAt?: string
  submittedAt?: string
  reviewedAt?: string
  reviewedBy?: string
  reviewComment?: string
  // 跳过相关
  skippedAt?: string
  skipReason?: string
  skipImages?: string[]
  // 跳过申请相关
  skipRequestedAt?: string
  skipRequestReason?: string
  skipRequestImages?: string[]
  skipRequestedBy?: string
  skipReviewedAt?: string
  skipReviewedBy?: string
  skipReviewComment?: string
  imageUrl?: string
  annotationData?: any
  createdAt: string
  updatedAt: string
  createdBy: string
  estimatedHours?: number
  actualHours?: number
  score?: number
}

// 用户信息
export interface User {
  id: string
  username: string
  realName: string
  email: string
  role: UserRole
  roles: string[]
  avatar?: string
  department?: string
  phone?: string
  status: 'active' | 'inactive'
  createdAt: string
  lastLoginAt?: string
  hireDate?: string // 入职日期
}

// 绩效统计
export interface PerformanceStats {
  userId: string
  username: string
  realName: string
  totalTasks: number
  completedTasks: number
  approvedTasks: number
  rejectedTasks: number
  totalScore: number
  averageScore: number
  totalHours: number
  averageHours: number
  period: 'daily' | 'weekly' | 'monthly' | 'yearly'
  date: string
  // 分类统计
  categoryStats?: CategoryStats
}

// 项目统计数据
export interface ProjectStats {
  projectId: string
  projectName: string
  totalTasks: number
  pendingTasks: number
  inProgressTasks: number
  submittedTasks: number
  completedTasks: number
  approvedTasks: number
  rejectedTasks: number
  completionRate: number
  averageScore: number
  totalHours: number
}

// 分类统计
export interface CategoryStats {
  case?: {
    trial: TaskCategoryStats
    research: TaskCategoryStats
    paid: TaskCategoryStats
    total: TaskCategoryStats
  }
  ai_annotation?: {
    research: TaskCategoryStats
    daily: TaskCategoryStats
    total: TaskCategoryStats
  }
  grandTotal: TaskCategoryStats
}

// 任务分类统计
export interface TaskCategoryStats {
  totalTasks: number
  completedTasks: number
  approvedTasks: number
  rejectedTasks: number
  averageScore: number
  totalScore: number
}

// 项目统计
export interface ProjectStats {
  projectId: string
  projectName: string
  totalTasks: number
  pendingTasks: number
  inProgressTasks: number
  submittedTasks: number
  completedTasks: number
  approvedTasks: number
  rejectedTasks: number
  completionRate: number
  averageScore: number
  totalHours: number
}

// 任务查询参数
export interface TaskQueryParams {
  projectId?: string
  status?: TaskStatus[]
  assignedTo?: string
  priority?: TaskPriority[]
  startDate?: string
  endDate?: string
  keyword?: string
  page: number
  pageSize: number
  isReviewPage?: boolean // 标识是否为审核页面，用于特殊筛选逻辑
  includeCompletedProjects?: boolean // ✅ 是否包含完结项目的任务（用于历史查看）
}

// 项目查询参数
export interface ProjectQueryParams {
  status?: ProjectStatus[]
  priority?: TaskPriority[]
  startDate?: string
  endDate?: string
  keyword?: string
  page: number
  pageSize: number
}

// 绩效查询参数
export interface PerformanceQueryParams {
  userId?: string
  projectId?: string
  period: 'daily' | 'weekly' | 'monthly' | 'yearly'
  startDate: string
  endDate: string
  page: number
  pageSize: number
}

// 任务操作结果
export interface TaskOperationResult {
  success: boolean
  message: string
  task?: Task
  performancePoints?: number
}

// 批量导入任务结果
export interface BatchImportResult {
  success: boolean
  message: string
  totalCount: number
  successCount: number
  failedCount: number
  failedItems?: Array<{
    row: number
    reason: string
  }>
}

// 用户相关类型
export interface UserCreate {
  username: string
  real_name: string
  email: string
  password: string
  role: UserRole
  department?: string
  avatar_url?: string
  hire_date?: string
}

export interface UserUpdate {
  real_name?: string
  email?: string
  role?: UserRole
  department?: string
  avatar_url?: string
  status?: 'active' | 'inactive'
  hire_date?: string
}
