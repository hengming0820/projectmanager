import http from '@/utils/http'
import { backendApi } from '@/utils/http/backendApi'
import type {
  Project,
  Task,
  User,
  PerformanceStats,
  ProjectStats,
  TaskQueryParams,
  ProjectQueryParams,
  PerformanceQueryParams,
  TaskOperationResult,
  BatchImportResult,
  TaskStatus
} from '@/types/project'
import { mockProjects, mockTasks, mockUsers, mockPerformanceStats } from '@/mock/project/mockData'
import AppConfig from '@/config'

/**
 * 项目管理API - Mock版本
 */

// 项目管理
export const projectApi = {
  // 获取项目列表
  getProjects: async (params: ProjectQueryParams) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      return mockProjects
    }
    const response = await backendApi.get<any[]>('/projects/', { params })
    // backendApi 可能返回 { code, msg, data: [...] } 或直接返回数组
    const raw = (response as any)?.data || response
    const mapped = (Array.isArray(raw) ? raw : []).map((p: any) => ({
      id: p.id,
      name: p.name,
      description: p.description || '',
      status: p.status || 'active',
      priority: p.priority || 'medium',
      category: p.category || 'case',
      subCategory: p.sub_category || 'trial',
      startDate: p.start_date || p.startDate || '',
      endDate: p.end_date || p.endDate || '',
      createdAt: p.created_at || p.createdAt || '',
      updatedAt: p.updated_at || p.updatedAt || '',
      createdBy: p.created_by || p.createdBy || '',
      totalTasks: Number(p.total_tasks ?? p.totalTasks ?? 0),
      completedTasks: Number(p.completed_tasks ?? p.completedTasks ?? 0),
      assignedTasks: Number(p.assigned_tasks ?? p.assignedTasks ?? 0)
    }))
    return mapped
  },

  // 获取项目详情
  getProject: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      const project = mockProjects.find((p) => p.id === id)
      if (!project) throw new Error('项目不存在')
      return { data: project }
    }
    const p: any = await backendApi.get<any>(`/projects/${id}`)
    const mapped: Project = {
      id: p.id,
      name: p.name,
      description: p.description || '',
      status: p.status || 'active',
      priority: p.priority || 'medium',
      category: p.category || 'case',
      subCategory: p.sub_category || 'trial',
      startDate: p.start_date || '',
      endDate: p.end_date || '',
      createdAt: p.created_at || '',
      updatedAt: p.updated_at || '',
      createdBy: p.created_by || '',
      totalTasks: Number(p.total_tasks ?? 0),
      completedTasks: Number(p.completed_tasks ?? 0),
      assignedTasks: Number(p.assigned_tasks ?? 0)
    }
    return { data: mapped }
  },

  // 创建项目
  createProject: async (data: Partial<Project>) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      const newProject: Project = {
        id: `project${Date.now()}`,
        name: data.name || '新项目',
        description: data.description || '',
        status: 'active',
        priority: 'medium',
        category: data.category || 'case',
        subCategory: data.subCategory || 'trial',
        startDate: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: 'system',
        totalTasks: 0,
        completedTasks: 0,
        assignedTasks: 0
      }
      mockProjects.push(newProject)
      return { data: newProject }
    }
    const payload: any = {
      name: data.name,
      description: data.description || '',
      status: data.status || 'active',
      priority: data.priority || 'medium',
      category: data.category || 'case',
      sub_category: data.subCategory || 'trial',
      start_date: data.startDate || new Date().toISOString().split('T')[0],
      end_date: data.endDate || null
    }
    const p: any = await backendApi.post<any>('/projects/', payload)
    const mapped: Project = {
      id: p.id,
      name: p.name,
      description: p.description || '',
      status: p.status || 'active',
      priority: p.priority || 'medium',
      category: p.category || 'case',
      subCategory: p.sub_category || 'trial',
      startDate: p.start_date || '',
      endDate: p.end_date || '',
      createdAt: p.created_at || '',
      updatedAt: p.updated_at || '',
      createdBy: p.created_by || '',
      totalTasks: Number(p.total_tasks ?? 0),
      completedTasks: Number(p.completed_tasks ?? 0),
      assignedTasks: Number(p.assigned_tasks ?? 0)
    }
    return { data: mapped }
  },

  // 更新项目
  updateProject: async (id: string, data: Partial<Project>) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      const projectIndex = mockProjects.findIndex((p) => p.id === id)
      if (projectIndex === -1) throw new Error('项目不存在')

      const updatedProject = { ...mockProjects[projectIndex], ...data }
      updatedProject.updatedAt = new Date().toISOString()
      mockProjects[projectIndex] = updatedProject
      return { data: updatedProject }
    }
    const payload: any = {
      name: data.name,
      description: data.description,
      status: data.status,
      priority: data.priority,
      category: data.category,
      sub_category: data.subCategory,
      start_date: data.startDate,
      end_date: data.endDate
    }
    // 移除 undefined 字段
    Object.keys(payload).forEach((k) => payload[k] === undefined && delete payload[k])
    const p: any = await backendApi.put<any>(`/projects/${id}`, payload)
    const mapped: Project = {
      id: p.id,
      name: p.name,
      description: p.description || '',
      status: p.status || 'active',
      priority: p.priority || 'medium',
      category: p.category || 'case',
      subCategory: p.sub_category || 'trial',
      startDate: p.start_date || '',
      endDate: p.end_date || '',
      createdAt: p.created_at || '',
      updatedAt: p.updated_at || '',
      createdBy: p.created_by || '',
      totalTasks: Number(p.total_tasks ?? 0),
      completedTasks: Number(p.completed_tasks ?? 0),
      assignedTasks: Number(p.assigned_tasks ?? 0)
    }
    return { data: mapped }
  },

  // 删除项目
  deleteProject: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const projectIndex = mockProjects.findIndex((p) => p.id === id)
      if (projectIndex === -1) throw new Error('项目不存在')
      mockProjects.splice(projectIndex, 1)
      return { success: true }
    }
    return backendApi.delete(`/projects/${id}`)
  },

  // 获取项目统计
  getProjectStats: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const project = mockProjects.find((p) => p.id === id)
      if (!project) throw new Error('项目不存在')

      const projectTasks = mockTasks.filter((t) => t.projectId === id)
      const totalTasks = projectTasks.length
      const completedTasks = projectTasks.filter((t) => t.status === 'approved').length

      return {
        data: {
          projectId: id,
          projectName: project.name,
          totalTasks,
          completedTasks,
          completionRate: totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0
        }
      }
    }
    return http.get<ProjectStats>({ url: `/projects/${id}/stats` })
  }
}

// 任务管理
export const taskApi = {
  // 获取任务列表
  getTasks: async (params: TaskQueryParams) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))

      let filteredTasks = [...mockTasks]

      // 对于审核页面，只返回可审核的任务
      if (params.isReviewPage) {
        if (
          !params.status ||
          params.status.length === 0 ||
          params.status.includes('reviewable' as TaskStatus)
        ) {
          // 显示所有可审核的任务（待审核、已通过、已驳回）
          filteredTasks = filteredTasks.filter((task) =>
            ['submitted', 'approved', 'rejected'].includes(task.status)
          )
        } else {
          // 按指定状态筛选，但仍然只限于可审核的状态
          const reviewableStatuses = params.status.filter((s) =>
            ['submitted', 'approved', 'rejected'].includes(s)
          )
          filteredTasks = filteredTasks.filter((task) =>
            reviewableStatuses.includes(task.status as TaskStatus)
          )
        }
      } else {
        // 非审核页面，正常筛选
        if (params.status && params.status.length > 0) {
          filteredTasks = filteredTasks.filter((task) =>
            params.status!.includes(task.status as TaskStatus)
          )
        }
      }

      if (params.projectId) {
        filteredTasks = filteredTasks.filter((task) => task.projectId === params.projectId)
      }
      if (params.assignedTo) {
        filteredTasks = filteredTasks.filter((task) => task.assignedTo === params.assignedTo)
      }
      if (params.keyword) {
        filteredTasks = filteredTasks.filter(
          (task) =>
            task.title.includes(params.keyword!) || task.description?.includes(params.keyword!)
        )
      }

      return {
        data: {
          list: filteredTasks,
          total: filteredTasks.length
        }
      }
    }
    console.log('🎯 [ProjectAPI] 调用真实API获取任务:', params)

    // 转换参数格式以匹配后端API
    let effectiveStatus: string | undefined

    // 对于审核页面的特殊处理
    if (params.isReviewPage) {
      if (!params.status || params.status.length === 0) {
        // “总计”统一用 accepted，由后端聚合筛选，避免前端再筛导致分页错位
        effectiveStatus = 'accepted'
      } else {
        // 只取第一个审核相关状态（包含 跳过申请/已跳过）
        const reviewableStatuses = params.status.filter((s) =>
          ['submitted', 'approved', 'rejected', 'skip_pending', 'skipped'].includes(s)
        )
        effectiveStatus = reviewableStatuses.length > 0 ? reviewableStatuses[0] : undefined
      }
    } else {
      effectiveStatus = params.status?.[0]
    }

    const backendParams = {
      project_id: params.projectId,
      status: effectiveStatus,
      assigned_to: params.assignedTo,
      skip: (params.page - 1) * params.pageSize,
      limit: params.pageSize,
      include_completed_projects: params.includeCompletedProjects || false // ✅ 支持包含完结项目
      // keyword参数暂不支持，因为后端没有实现搜索功能
    }

    // 移除空值参数
    Object.keys(backendParams).forEach((key) => {
      if (backendParams[key as keyof typeof backendParams] === undefined) {
        delete backendParams[key as keyof typeof backendParams]
      }
    })

    console.log('🔄 [ProjectAPI] 转换后的后端参数:', backendParams)

    const result = await backendApi.get<{ list: Task[]; total: number }>('/tasks/', {
      params: backendParams
    })
    console.log('✅ [ProjectAPI] 任务数据获取成功:', result)

    let list = result.list || (result as any).data?.list || []
    const total = result.total ?? (result as any).data?.total ?? list.length

    // 审核页“全部”时仅筛选审核相关（包含：已提交、跳过申请、已跳过、已通过、已驳回；排除未分配/进行中等）
    if (params.isReviewPage && (!params.status || params.status.length === 0)) {
      const accepted = new Set(['submitted', 'skip_pending', 'skipped', 'approved', 'rejected'])
      list = list.filter((task) => accepted.has((task as any).status))
    }

    return { data: { list, total } }
  },

  // 获取任务详情
  getTask: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      return { data: task }
    }
    const task = await backendApi.get<Task>(`/tasks/${id}`)
    return { data: task }
  },

  // 创建任务
  createTask: async (data: Partial<Task>) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      const newTask: Task = {
        id: `task${Date.now()}`,
        title: data.title || '新任务',
        description: data.description || '',
        projectId: data.projectId || '',
        projectName: data.projectName || '未知项目',
        assignedTo: data.assignedTo || '',
        status: 'pending',
        priority: 'medium',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: 'system',
        estimatedHours: data.estimatedHours || 0,
        actualHours: data.actualHours || 0
      }
      mockTasks.push(newTask)
      return { data: newTask }
    }
    return http.post<Task>({ url: '/tasks', data })
  },

  // 批量创建任务
  batchCreateTasks: async (data: Partial<Task>[]) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 800))
      const newTasks: Task[] = data.map((taskData, index) => ({
        id: `task${Date.now()}_${index}`,
        title: taskData.title || `批量任务${index + 1}`,
        description: taskData.description || '',
        projectId: taskData.projectId || '',
        projectName: taskData.projectName || '未知项目',
        assignedTo: taskData.assignedTo || '',
        status: 'pending',
        priority: 'medium',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: 'system',
        estimatedHours: taskData.estimatedHours || 0,
        actualHours: taskData.actualHours || 0
      }))
      mockTasks.push(...newTasks)
      return {
        data: {
          success: true,
          created: newTasks.length,
          failed: 0,
          errors: []
        }
      }
    }
    return http.post<BatchImportResult>({ url: '/tasks/batch', data })
  },

  // 更新任务
  updateTask: async (id: string, data: Partial<Task>) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      const taskIndex = mockTasks.findIndex((t) => t.id === id)
      if (taskIndex === -1) throw new Error('任务不存在')

      const updatedTask = { ...mockTasks[taskIndex], ...data }
      updatedTask.updatedAt = new Date().toISOString()
      mockTasks[taskIndex] = updatedTask
      return { data: updatedTask }
    }
    return http.put<Task>({ url: `/tasks/${id}`, data })
  },

  // 删除任务
  deleteTask: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const taskIndex = mockTasks.findIndex((t) => t.id === id)
      if (taskIndex === -1) throw new Error('任务不存在')
      // 改为标记为 skipped
      mockTasks[taskIndex].status = 'skipped' as any
      mockTasks[taskIndex].skippedAt = new Date().toISOString() as any
      return { success: true }
    }
    // 兼容旧调用：仍然调用删除，后端已改为 /skip，新UI应改用 skipTask
    return http.del({ url: `/tasks/${id}` })
  },

  // 跳过任务（带原因与截图）
  skipTask: async (id: string, data: { reason: string; images?: string[] }) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      ;(task as any).status = 'skipped'
      ;(task as any).skippedAt = new Date().toISOString()
      ;(task as any).skipReason = data.reason
      ;(task as any).skipImages = data.images || []
      return { data: { success: true, message: '任务已跳过' } }
    }
    return backendApi.post(`/tasks/${id}/skip`, { reason: data.reason, images: data.images })
  },

  // 领取任务
  claimTask: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      task.status = 'in_progress'
      task.assignedTo = 'current_user_id'
      return { data: { success: true, message: '任务领取成功' } }
    }
    console.log('🎯 [ProjectAPI] 调用真实API领取任务:', id)
    const result = await backendApi.post<TaskOperationResult>(`/tasks/${id}/claim`)
    console.log('✅ [ProjectAPI] 任务领取成功:', result)
    return { data: result }
  },

  // 开始任务
  startTask: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      task.status = 'in_progress'
      return { data: { success: true, message: '任务开始成功' } }
    }
    console.log('🚀 [ProjectAPI] 调用真实API开始任务:', id)
    const result = await backendApi.post<TaskOperationResult>(`/tasks/${id}/start`)
    console.log('✅ [ProjectAPI] 任务开始成功:', result)
    return { data: result }
  },

  // 提交任务
  submitTask: async (
    id: string,
    data: { annotationData?: any; comment?: string; organCount?: number; images?: any[] }
  ) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      task.status = 'submitted'
      task.annotationData = data.annotationData || {}
      return { data: { success: true, message: '任务提交成功' } }
    }
    console.log('📝 [ProjectAPI] 调用真实API提交任务:', id, data)

    // 严格按照后端的TaskSubmit模式转换数据格式
    // TaskSubmit期望: {annotation_data: Dict[str, Any], comment: str, organ_count: int}
    const backendData = {
      annotation_data: data.annotationData || {},
      comment: data.comment || '标注已完成',
      organ_count: data.organCount || 1
    }

    console.log('🔄 [ProjectAPI] 转换后的后端数据格式:', {
      taskId: id,
      backendData
    })

    try {
      const result = await backendApi.post<TaskOperationResult>(`/tasks/${id}/submit`, backendData)
      console.log('✅ [ProjectAPI] 任务提交成功:', result)
      return { data: result }
    } catch (error) {
      console.error('❌ [ProjectAPI] 任务提交失败:', error)
      throw error
    }
  },

  // 放弃任务
  abandonTask: async (id: string, reason?: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      task.status = 'abandoned'
      return { data: { success: true, message: '任务放弃成功' } }
    }
    console.log('🚫 [ProjectAPI] 调用真实API放弃任务:', id, reason)
    const result = await backendApi.post<TaskOperationResult>(`/tasks/${id}/abandon`, { reason })
    console.log('✅ [ProjectAPI] 任务放弃成功:', result)
    return { data: result }
  },

  // 重新开始驳回的任务
  restartTask: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      if (task.status !== 'rejected') throw new Error('只有已驳回的任务才能重新开始')
      task.status = 'in_progress'
      return { data: { success: true, message: '任务重新开始成功' } }
    }
    console.log('🔄 [ProjectAPI] 调用真实API重新开始驳回任务:', id)
    const result = await backendApi.post<TaskOperationResult>(`/tasks/${id}/restart`)
    console.log('✅ [ProjectAPI] 驳回任务重新开始成功:', result)
    return { data: result }
  },

  // 审核任务
  reviewTask: async (
    id: string,
    data: { approved: boolean; comment?: string; score?: number; reject_images?: string[] }
  ) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      const task = mockTasks.find((t) => t.id === id)
      if (!task) throw new Error('任务不存在')
      task.status = data.approved ? 'approved' : 'rejected'
      return { data: { success: true, message: data.approved ? '任务审核通过' : '任务已打回重标' } }
    }
    console.log('📋 [ProjectAPI] 调用真实API审核任务:', id, data)
    // 转换参数格式以匹配后端API
    const reviewData = {
      action: data.approved ? 'approve' : 'reject',
      comment: data.comment || '',
      score: data.score,
      reject_images: data.reject_images
    }

    // 过滤掉 undefined 字段
    Object.keys(reviewData).forEach((key) => {
      if (reviewData[key as keyof typeof reviewData] === undefined) {
        delete reviewData[key as keyof typeof reviewData]
      }
    })

    console.log('📤 [ProjectAPI] 发送审核数据:', reviewData)
    const result = await backendApi.post<TaskOperationResult>(`/tasks/${id}/review`, reviewData)
    console.log('✅ [ProjectAPI] 任务审核成功:', result)
    return { data: result }
  },

  // 批量导入任务（Excel/CSV）
  importTasksFromExcel: async (file: File, projectId?: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      // 模拟Excel导入
      const newTasks: Task[] = []
      for (let i = 0; i < 5; i++) {
        const newTask: Task = {
          id: `task${Date.now()}_${i}`,
          title: `导入任务${i + 1}`,
          description: `从Excel导入的任务${i + 1}`,
          projectId: 'project1',
          projectName: '示例项目',
          status: 'pending',
          priority: 'medium',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          createdBy: 'system',
          estimatedHours: 0,
          actualHours: 0
        }
        newTasks.push(newTask)
      }
      mockTasks.unshift(...newTasks)
      return {
        data: {
          success: true,
          created: newTasks.length,
          failed: 0,
          errors: []
        }
      }
    }
    const formData = new FormData()
    formData.append('file', file)
    if (projectId) formData.append('project_id', projectId)
    return backendApi.post<BatchImportResult>('/tasks/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 导出任务
  exportTasks: async (params: TaskQueryParams) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      // 模拟导出
      return { data: 'mock_export_data' }
    }
    return http.get({
      url: '/tasks/export',
      params,
      responseType: 'blob'
    })
  },

  // 上传标注截图到 MinIO
  uploadAnnotationImages: async (taskId: string, files: File[]) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 800))
      // 模拟返回上传的URL
      const urls = files.map(
        (file, index) =>
          `http://192.168.200.20:9000/medical-annotations/annotations/${taskId}/mock_${Date.now()}_${index}_${file.name}`
      )

      return { data: { urls } }
    }

    console.log('📤 [TaskAPI] 上传标注截图到MinIO:', taskId, files.length)
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    try {
      const result = await backendApi.post<{ urls: string[] }>(
        `/tasks/${taskId}/upload-annotation-images`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      console.log('✅ [TaskAPI] 标注截图上传成功:', result)
      return { data: result }
    } catch (error) {
      console.error('❌ [TaskAPI] 标注截图上传失败:', error)
      throw error
    }
  },

  // 上传审核截图到 MinIO
  uploadReviewImages: async (taskId: string, files: File[]) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 800))
      // 模拟返回上传的URL
      const urls = files.map(
        (file, index) =>
          `http://192.168.200.20:9000/medical-annotations/reviews/${taskId}/mock_${Date.now()}_${index}_${file.name}`
      )
      return { data: { urls } }
    }

    console.log('📤 [TaskAPI] 上传审核截图到MinIO:', taskId, files.length)
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    try {
      const result = await backendApi.post<{ urls: string[] }>(
        `/tasks/${taskId}/upload-review-images`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      console.log('✅ [TaskAPI] 审核截图上传成功:', result)
      return { data: result }
    } catch (error) {
      console.error('❌ [TaskAPI] 审核截图上传失败:', error)
      throw error
    }
  },
  // 上传跳过截图到 MinIO
  uploadSkipImages: async (taskId: string, files: File[]) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 800))
      const urls = files.map(
        (file, index) =>
          `http://192.168.200.20:9000/medical-annotations/skips/${taskId}/mock_${Date.now()}_${index}_${file.name}`
      )
      return { data: { urls } }
    }

    console.log('📤 [TaskAPI] 上传跳过截图到MinIO:', taskId, files.length)
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    try {
      const result = await backendApi.post<{ urls: string[] }>(
        `/tasks/${taskId}/upload-skip-images`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      console.log('✅ [TaskAPI] 跳过截图上传成功:', result)
      return { data: result }
    } catch (error) {
      console.error('❌ [TaskAPI] 跳过截图上传失败:', error)
      throw error
    }
  },

  // 申请跳过任务
  requestSkipTask: async (taskId: string, data: { reason: string; images: string[] }) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      return { message: '跳过申请已提交', data: { status: 'skip_pending' } }
    }

    console.log('📋 [TaskAPI] 申请跳过任务:', taskId, data)
    try {
      const result = await backendApi.post(`/tasks/${taskId}/request-skip`, {
        reason: data.reason,
        images: data.images
      })
      console.log('✅ [TaskAPI] 跳过申请提交成功:', result)
      return result
    } catch (error) {
      console.error('❌ [TaskAPI] 跳过申请提交失败:', error)
      throw error
    }
  },

  // 审核跳过申请
  reviewSkipRequest: async (taskId: string, data: { approved: boolean; comment: string }) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      return {
        message: '跳过申请审核完成',
        data: { status: data.approved ? 'skipped' : 'in_progress' }
      }
    }

    console.log('📋 [TaskAPI] 审核跳过申请:', taskId, data)
    try {
      const result = await backendApi.post(`/tasks/${taskId}/review-skip`, {
        approved: data.approved,
        comment: data.comment
      })
      console.log('✅ [TaskAPI] 跳过申请审核成功:', result)
      return result
    } catch (error) {
      console.error('❌ [TaskAPI] 跳过申请审核失败:', error)
      throw error
    }
  }
}

// 用户管理
export const userApi = {
  // 获取用户列表
  getUsers: async (params: { page: number; pageSize: number; keyword?: string; role?: string }) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      let filteredUsers = [...mockUsers]

      if (params.keyword) {
        filteredUsers = filteredUsers.filter(
          (user) =>
            user.username.includes(params.keyword!) || user.realName.includes(params.keyword!)
        )
      }

      if (params.role) {
        filteredUsers = filteredUsers.filter((user) => user.role === params.role)
      }

      const start = (params.page - 1) * params.pageSize
      const end = start + params.pageSize
      const list = filteredUsers.slice(start, end)

      return {
        data: {
          list,
          total: filteredUsers.length
        }
      }
    }
    return http.get<{ list: User[]; total: number }>({ url: '/users', params })
  },

  // 获取用户详情
  getUser: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      const user = mockUsers.find((u) => u.id === id)
      if (!user) throw new Error('用户不存在')
      return { data: user }
    }
    return http.get<User>({ url: `/users/${id}` })
  },

  // 创建用户
  createUser: async (data: Partial<User>) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      const newUser: User = {
        id: `user${Date.now()}`,
        username: data.username || '',
        realName: data.realName || '',
        email: data.email || '',
        role: data.role || 'annotator',
        roles: data.roles || ['R_ANNOTATOR'],
        avatar: data.avatar || '',
        department: data.department || '',
        status: 'active',
        createdAt: new Date().toISOString()
      }
      mockUsers.push(newUser)
      return { data: newUser }
    }
    return http.post<User>({ url: '/users', data })
  },

  // 更新用户
  updateUser: async (id: string, data: Partial<User>) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      const userIndex = mockUsers.findIndex((u) => u.id === id)
      if (userIndex === -1) throw new Error('用户不存在')

      const updatedUser = { ...mockUsers[userIndex], ...data }
      mockUsers[userIndex] = updatedUser
      return { data: updatedUser }
    }
    return http.put<User>({ url: `/users/${id}`, data })
  },

  // 删除用户
  deleteUser: async (id: string) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const userIndex = mockUsers.findIndex((u) => u.id === id)
      if (userIndex === -1) throw new Error('用户不存在')
      mockUsers.splice(userIndex, 1)
      return { success: true }
    }
    return http.del({ url: `/users/${id}` })
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      // 模拟返回当前用户
      return { data: mockUsers[0] }
    }
    return http.get<User>({ url: '/users/current' })
  }
}

// 绩效管理
export const performanceApi = {
  // 获取绩效统计
  getPerformanceStats: async (params: PerformanceQueryParams) => {
    console.log('📈 [PerformanceAPI] 获取绩效统计:', params)
    const result = await http.get<{ list: PerformanceStats[]; total: number }>({
      url: '/performance/stats',
      params
    })
    console.log('✅ [PerformanceAPI] 绩效统计获取成功:', result)
    return result
  },

  // 获取个人绩效
  getPersonalPerformance: async (period: string = 'monthly') => {
    console.log('📈 [PerformanceAPI] 获取个人绩效:', period)
    const result = await http.get<{
      total_tasks: number
      completed_tasks: number
      total_score: number
      average_score: number
      completion_rate: number
    }>({ url: '/performance/personal', params: { period } })
    console.log('✅ [PerformanceAPI] 个人绩效获取成功:', result)
    return result
  },

  // 获取团队绩效
  getTeamPerformance: async (params: PerformanceQueryParams) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      return { data: mockPerformanceStats }
    }
    return http.get<PerformanceStats[]>({ url: '/performance/team', params })
  },

  // 获取绩效排行榜
  getPerformanceRanking: async (params: { period: string; date: string; limit?: number }) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      return { data: mockPerformanceStats.slice(0, params.limit || 10) }
    }
    return http.get<PerformanceStats[]>({ url: '/performance/ranking', params })
  }
}

// 仪表板数据
export const dashboardApi = {
  // 获取仪表板概览数据
  getOverview: async () => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      return {
        data: {
          totalProjects: mockProjects.length,
          activeProjects: mockProjects.filter((p) => p.status === 'active').length,
          totalTasks: mockTasks.length,
          pendingTasks: mockTasks.filter((t) => t.status === 'pending').length,
          inProgressTasks: mockTasks.filter((t) => t.status === 'in_progress').length,
          completedTasks: mockTasks.filter((t) => t.status === 'approved').length,
          totalUsers: mockUsers.length,
          activeUsers: mockUsers.filter((u) => u.status === 'active').length
        }
      }
    }
    // 使用后端的仪表板统计API，只需要ProjectDashboard权限
    try {
      const result = await backendApi.get<any>('/performance/dashboard')
      return {
        totalProjects: result.total_projects || 0,
        activeProjects: result.active_projects || 0,
        totalTasks: result.total_tasks || 0,
        pendingTasks: result.pending_tasks || 0,
        inProgressTasks: 0, // 后端API暂未返回，使用默认值
        submittedTasks: 0, // 后端API暂未返回，使用默认值
        completedTasks: result.completed_tasks || 0,
        rejectedTasks: 0, // 后端API暂未返回，使用默认值
        totalUsers: result.total_users || 0,
        activeUsers: result.total_users || 0, // 假设所有用户都是活跃的
        projectProgress: result.project_progress || []
      }
    } catch (e) {
      console.warn('⚠️ [DashboardAPI] 获取仪表板数据失败，使用回退策略:', e)
      // 回退策略：使用任务API获取基础统计，不再调用用户API
      try {
        const response: any = await backendApi.get<any>('/tasks/', {
          params: { skip: 0, limit: 1000 }
        })
        // 后端返回 {list: Array, total: number}，需要提取 list
        const tasks: any[] = response?.list || response?.data?.list || []

        // 统计任务
        const totalTasks = tasks.length
        const pendingTasks = tasks.filter((t: any) => t.status === 'pending').length
        const inProgressTasks = tasks.filter((t: any) => t.status === 'in_progress').length
        const submittedTasks = tasks.filter((t: any) => t.status === 'submitted').length
        const completedTasks = tasks.filter((t: any) => t.status === 'approved').length
        const rejectedTasks = tasks.filter((t: any) => t.status === 'rejected').length

        // 统计项目数（从任务中提取）
        const uniqueProjects = new Set(
          tasks.map((t: any) => t.project_id || t.projectId).filter(Boolean)
        )

        return {
          totalProjects: uniqueProjects.size,
          activeProjects: uniqueProjects.size,
          totalTasks,
          pendingTasks,
          inProgressTasks,
          submittedTasks,
          completedTasks,
          rejectedTasks,
          totalUsers: 5, // 默认值，不再调用用户API
          activeUsers: 5 // 默认值，不再调用用户API
        }
      } catch (fallbackError) {
        console.error('❌ [DashboardAPI] 回退策略也失败:', fallbackError)
        throw fallbackError
      }
    }
  },

  // 获取项目进度统计
  getProjectProgress: async () => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const projectStats: ProjectStats[] = mockProjects.map((project) => {
        const projectTasks = mockTasks.filter((t) => t.projectId === project.id)
        const totalTasks = projectTasks.length
        const pendingTasks = projectTasks.filter((t) => t.status === 'pending').length
        const inProgressTasks = projectTasks.filter((t) => t.status === 'in_progress').length
        const submittedTasks = projectTasks.filter((t) => t.status === 'submitted').length
        const completedTasks = projectTasks.filter((t) => t.status === 'approved').length
        const approvedTasks = projectTasks.filter((t) => t.status === 'approved').length
        const rejectedTasks = projectTasks.filter((t) => t.status === 'rejected').length

        return {
          projectId: project.id,
          projectName: project.name,
          totalTasks,
          pendingTasks,
          inProgressTasks,
          submittedTasks,
          completedTasks,
          approvedTasks,
          rejectedTasks,
          completionRate: totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0,
          averageScore: 0,
          totalHours: 0
        }
      })
      return { data: projectStats }
    }
    // 仅通过任务数据计算项目进度，避免请求不存在的项目接口
    const response: any = await backendApi.get<any>('/tasks/', {
      params: { skip: 0, limit: 1000 }
    })
    // 后端返回 {list: Array, total: number}，需要提取 list
    const tasks: any[] = response?.list || response?.data?.list || []
    const map = new Map<string, any>()
    for (const t of tasks) {
      const pid = t.project_id || t.projectId
      if (!pid) continue
      if (!map.has(pid)) {
        map.set(pid, {
          projectId: pid,
          projectName: t.project_name || t.projectName || pid,
          tasks: [] as any[]
        })
      }
      map.get(pid).tasks.push(t)
    }

    const projectProgress = Array.from(map.values()).map((p: any) => {
      const projectTasks = p.tasks
      const completedTasks = projectTasks.filter((task: any) => task.status === 'approved').length
      return {
        projectId: p.projectId,
        projectName: p.projectName,
        totalTasks: projectTasks.length,
        completedTasks,
        completionRate:
          projectTasks.length > 0 ? Math.round((completedTasks / projectTasks.length) * 100) : 0,
        pendingTasks: projectTasks.filter((task: any) => task.status === 'pending').length,
        inProgressTasks: projectTasks.filter((task: any) => task.status === 'in_progress').length,
        submittedTasks: projectTasks.filter((task: any) => task.status === 'submitted').length,
        approvedTasks: projectTasks.filter((task: any) => task.status === 'approved').length,
        rejectedTasks: projectTasks.filter((task: any) => task.status === 'rejected').length,
        averageScore: 0,
        totalHours: 0
      }
    })

    return projectProgress
  },

  // 获取任务状态分布
  getTaskStatusDistribution: async () => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      return {
        data: {
          pending: mockTasks.filter((t) => t.status === 'pending').length,
          assigned: mockTasks.filter((t) => t.status === 'assigned').length,
          inProgress: mockTasks.filter((t) => t.status === 'in_progress').length,
          submitted: mockTasks.filter((t) => t.status === 'submitted').length,
          approved: mockTasks.filter((t) => t.status === 'approved').length,
          rejected: mockTasks.filter((t) => t.status === 'rejected').length
        }
      }
    }
    return http.get<{
      pending: number
      assigned: number
      inProgress: number
      submitted: number
      approved: number
      rejected: number
    }>({ url: '/dashboard/task-status-distribution' })
  },

  // 获取用户活跃度
  getUserActivity: async (params: { days: number }) => {
    if (AppConfig.mockMode.enabled) {
      await new Promise((resolve) => setTimeout(resolve, 300))
      const activity = []
      for (let i = 0; i < params.days; i++) {
        activity.push({
          date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          activeUsers: Math.floor(Math.random() * 10) + 1,
          completedTasks: Math.floor(Math.random() * 20) + 1
        })
      }
      return { data: activity.reverse() }
    }
    return http.get<Array<{ date: string; activeUsers: number; completedTasks: number }>>({
      url: '/dashboard/user-activity',
      params
    })
  }
}
