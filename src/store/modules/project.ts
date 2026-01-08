import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { Project, Task, User, PerformanceStats, ProjectStats } from '@/types/project'
import { mockProjects, mockTasks, mockUsers, mockPerformanceStats } from '@/mock/project/mockData'
import { projectApi, taskApi, performanceApi, dashboardApi } from '@/api/projectApi'
import { userApi } from '@/api/userApi'
import { useUserStore } from './user'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const tasks = ref<Task[]>([])
  const users = ref<User[]>([])
  const performanceStats = ref<PerformanceStats[]>([])
  const projectStats = ref<ProjectStats[]>([])
  const loading = ref(false)
  const total = ref(0)

  // 计算属性
  const activeProjects = computed(() => projects.value.filter((p) => p.status === 'active'))
  const completedProjects = computed(() => projects.value.filter((p) => p.status === 'completed'))
  const pendingTasks = computed(() => tasks.value.filter((t) => t.status === 'pending'))
  const myTasks = computed(() => {
    const currentUserId = getCurrentUserId()
    const filtered = tasks.value.filter((t) => t.assignedTo === currentUserId)
    console.log('📋 [ProjectStore] myTasks 计算结果:', {
      currentUserId,
      totalTasks: tasks.value.length,
      myTasksCount: filtered.length,
      myTasks: filtered.map((t) => ({
        id: t.id,
        title: t.title,
        assignedTo: t.assignedTo,
        status: t.status
      }))
    })
    return filtered
  })

  // 获取当前用户ID（从用户store获取）
  const getCurrentUserId = () => {
    const userStore = useUserStore()
    return userStore.currentUser?.id || 'unknown_user'
  }

  // 初始化示例数据
  const initializeMockData = () => {
    if (projects.value.length === 0) {
      projects.value = mockProjects
    }
    if (tasks.value.length === 0) {
      tasks.value = mockTasks
    }
    if (users.value.length === 0) {
      users.value = mockUsers
    }
    // 不再初始化模拟绩效数据，保持空数组
    // if (performanceStats.value.length === 0) {
    //   performanceStats.value = mockPerformanceStats
    // }
    total.value = projects.value.length
  }

  // 项目管理
  const fetchProjects = async (params: any) => {
    loading.value = true
    try {
      const result = await projectApi.getProjects(params || ({} as any))
      const data: any = (result as any).data || result
      const list = Array.isArray(data) ? data : data.list || data.data || []
      projects.value = list
      total.value = (data.total !== undefined ? data.total : list.length) || list.length
    } catch (error) {
      console.error('获取项目列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const createProject = async (projectData: Partial<Project>) => {
    try {
      const res = await projectApi.createProject(projectData)
      const created: any = (res as any).data || res
      projects.value.unshift(created)
      return created
    } catch (error) {
      console.error('创建项目失败:', error)
      throw error
    }
  }

  const updateProject = async (id: string, projectData: Partial<Project>) => {
    try {
      console.log('📝 [ProjectStore] 更新项目:', { id, projectData })

      // ✅ 调用后端API更新项目
      const result = await projectApi.updateProject(id, projectData)
      console.log('✅ [ProjectStore] 后端更新成功:', result)

      // 更新本地状态
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        projects.value[index] = {
          ...projects.value[index],
          ...projectData,
          updatedAt: new Date().toISOString()
        }
      }

      return result
    } catch (error) {
      console.error('❌ [ProjectStore] 更新项目失败:', error)
      throw error
    }
  }

  const deleteProject = async (id: string) => {
    try {
      console.log('🗑️ [ProjectStore] 删除项目:', id)

      // 调用后端API删除项目（会自动删除关联的任务）
      await projectApi.deleteProject(id)

      // 从本地状态中移除项目
      projects.value = projects.value.filter((p) => p.id !== id)

      // 从本地状态中移除该项目的所有任务
      tasks.value = tasks.value.filter((t) => t.projectId !== id)

      console.log('✅ [ProjectStore] 项目及其任务删除成功')
    } catch (error) {
      console.error('❌ [ProjectStore] 删除项目失败:', error)
      throw error
    }
  }

  const deleteTask = async (id: string) => {
    try {
      tasks.value = tasks.value.filter((t) => t.id !== id)
    } catch (error) {
      console.error('删除任务失败:', error)
      throw error
    }
  }

  const getProjectStats = async (id: string) => {
    try {
      const project = projects.value.find((p) => p.id === id)
      if (!project) throw new Error('项目不存在')

      const projectTasks = tasks.value.filter((t) => t.projectId === id)
      const stats: ProjectStats = {
        projectId: id,
        projectName: project.name,
        totalTasks: projectTasks.length,
        pendingTasks: projectTasks.filter((t) => t.status === 'pending').length,
        inProgressTasks: projectTasks.filter((t) => t.status === 'in_progress').length,
        submittedTasks: projectTasks.filter((t) => t.status === 'submitted').length,
        completedTasks: projectTasks.filter(
          (t) => t.status === 'submitted' || t.status === 'approved'
        ).length,
        approvedTasks: projectTasks.filter((t) => t.status === 'approved').length,
        rejectedTasks: projectTasks.filter((t) => t.status === 'rejected').length,
        completionRate:
          projectTasks.length > 0
            ? (projectTasks.filter((t) => t.status === 'submitted' || t.status === 'approved')
                .length /
                projectTasks.length) *
              100
            : 0,
        averageScore: 85,
        totalHours: projectTasks.reduce((sum, t) => sum + (t.actualHours || 0), 0)
      }
      return stats
    } catch (error) {
      console.error('获取项目统计失败:', error)
      throw error
    }
  }

  // 任务管理
  const fetchTasks = async (params: any) => {
    // 确保审核员建立通知连接
    ensureReviewerNotification()
    loading.value = true
    try {
      console.log('📋 [ProjectStore] 获取任务列表:', params)

      // 调用真实API获取任务数据
      const result = await taskApi.getTasks(params)
      console.log('✅ [ProjectStore] 任务数据获取成功:', result)

      // 更新本地状态
      if (result && (result as any).data) {
        const taskList = ((result as any).data as any).list || []

        // 确保项目信息正确映射
        const processedTasks = (taskList as any[]).map((task: any) => ({
          ...task,
          // 统一项目名称字段
          projectName: task.projectName || task.project_name || task.project?.name || '未知项目',
          // 确保必要字段存在
          assignedTo: task.assignedTo || task.assigned_to,
          assignedToName: task.assignedToName || task.assigned_to_name,
          createdBy: task.createdBy || task.created_by,
          createdByName: task.createdByName || task.created_by_name,
          reviewedBy: task.reviewedBy || task.reviewed_by,
          reviewedByName: task.reviewedByName || task.reviewed_by_name,
          projectId: task.projectId || task.project_id,
          // 统一时间字段（供趋势图/时间轴使用）
          createdAt: task.createdAt || task.created_at,
          updatedAt: task.updatedAt || task.updated_at,
          submittedAt: task.submittedAt || task.submitted_at,
          reviewedAt: task.reviewedAt || task.reviewed_at,
          // 工时：兼容 annotation_data 与 annotationData
          estimatedHours:
            task.estimatedHours ??
            task.annotationData?.estimatedHours ??
            task.annotation_data?.estimated_hours ??
            0,
          // 跳过相关
          skippedAt: (task as any).skippedAt || (task as any).skipped_at,
          skipReason: (task as any).skipReason || (task as any).skip_reason,
          skipImages: (task as any).skipImages || (task as any).skip_images
        }))

        tasks.value = processedTasks
        total.value = Number(((result as any).data as any).total || 0)

        console.log('📊 [ProjectStore] 处理后的任务数据:', {
          总数: processedTasks.length,
          前5个任务: processedTasks.slice(0, 5).map((t: any) => ({
            id: t.id,
            title: t.title,
            projectName: t.projectName,
            assignedTo: t.assignedTo,
            status: t.status
          }))
        })

        // 返回处理后的数据
        return {
          ...result,
          data: {
            ...((result as any).data as any),
            list: processedTasks,
            processedTasks
          }
        }
      } else {
        // 如果 API 调用失败，使用模拟数据作为后备
        console.warn('⚠️ [ProjectStore] API调用失败，使用模拟数据')
        initializeMockData()
        return {
          data: {
            list: tasks.value,
            total: tasks.value.length
          }
        }
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 获取任务列表失败:', error)
      // 如果 API 调用失败，使用模拟数据作为后备
      console.warn('⚠️ [ProjectStore] 使用模拟数据作为后备')
      initializeMockData()
      return {
        data: {
          list: tasks.value,
          total: tasks.value.length
        }
      }
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData: Partial<Task>) => {
    try {
      const newTask: Task = {
        id: `task${Date.now()}`,
        projectId: taskData.projectId || '',
        projectName: taskData.projectName || '',
        title: taskData.title || '',
        description: taskData.description || '',
        status: taskData.status || 'pending',
        priority: taskData.priority || 'medium',
        assignedTo: taskData.assignedTo,
        createdBy: taskData.createdBy || 'user1',
        imageUrl: taskData.imageUrl,
        annotationData: taskData.annotationData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      tasks.value.unshift(newTask)
      return newTask
    } catch (error) {
      console.error('创建任务失败:', error)
      throw error
    }
  }

  const claimTask = async (id: string) => {
    try {
      console.log('🎯 [ProjectStore] 开始领取任务:', id)

      // 调用API领取任务
      const result = await taskApi.claimTask(id)
      console.log('✅ [ProjectStore] API调用成功:', result)

      // 解析API响应数据，处理不同的响应格式
      const apiResponse = (result as any).data || result
      console.log('📋 [ProjectStore] 解析的响应数据:', apiResponse)

      // 检查API调用是否成功
      if (apiResponse.success) {
        console.log('✅ [ProjectStore] 任务领取成功，刷新任务列表')

        // 刷新任务列表以同步最新状态
        await fetchTasks({ assignedTo: '', page: 1, pageSize: 100 })

        return { success: true, message: apiResponse.message || '任务领取成功' }
      } else {
        throw new Error(apiResponse.message || '任务领取失败')
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 领取任务失败:', error)
      throw error
    }
  }

  const startTask = async (id: string) => {
    try {
      console.log('🚀 [ProjectStore] 开始开始任务:', id)

      // 调用API开始任务
      const result = await taskApi.startTask(id)
      console.log('✅ [ProjectStore] API调用成功:', result)

      // 解析API响应数据
      const apiResponse = (result as any).data || result

      // 检查API调用是否成功
      if (apiResponse.success) {
        console.log('✅ [ProjectStore] 任务开始成功，刷新任务列表')

        // 刷新任务列表以同步最新状态
        await fetchTasks({ assignedTo: '', page: 1, pageSize: 100 })

        return { success: true, message: apiResponse.message || '任务开始成功' }
      } else {
        throw new Error(apiResponse.message || '任务开始失败')
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 开始任务失败:', error)
      throw error
    }
  }

  const restartTask = async (id: string) => {
    try {
      console.log('🔄 [ProjectStore] 开始重新开始驳回任务:', id)

      // 调用API重新开始任务
      const result = await taskApi.restartTask(id)
      console.log('✅ [ProjectStore] API调用成功:', result)

      // 解析API响应数据
      const apiResponse = (result as any).data || result

      // 检查API调用是否成功
      if (apiResponse.success) {
        console.log('✅ [ProjectStore] 驳回任务重新开始成功，刷新任务列表')

        // 刷新任务列表以同步最新状态
        await fetchTasks({ assignedTo: '', page: 1, pageSize: 100 })

        return { success: true, message: apiResponse.message || '任务重新开始成功' }
      } else {
        throw new Error(apiResponse.message || '任务重新开始失败')
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 重新开始任务失败:', error)
      throw error
    }
  }

  // 上传标注截图到 MinIO
  const uploadAnnotationImages = async (taskId: string, files: File[]) => {
    try {
      console.log('📤 [ProjectStore] 开始上传标注截图:', taskId, files.length)

      const result = await taskApi.uploadAnnotationImages(taskId, files)
      console.log('✅ [ProjectStore] 标注截图上传成功:', result)

      return result.data
    } catch (error) {
      console.error('❌ [ProjectStore] 标注截图上传失败:', error)
      throw error
    }
  }

  // 上传审核截图到 MinIO
  const uploadReviewImages = async (taskId: string, files: File[]) => {
    try {
      console.log('📤 [ProjectStore] 开始上传审核截图:', taskId, files.length)

      const result = await taskApi.uploadReviewImages(taskId, files)
      console.log('✅ [ProjectStore] 审核截图上传成功:', result)

      return result.data
    } catch (error) {
      console.error('❌ [ProjectStore] 审核截图上传失败:', error)
      throw error
    }
  }

  const submitTask = async (id: string, data: { annotationData: any; comment?: string }) => {
    try {
      console.log('📝 [ProjectStore] 开始提交任务:', id, data)

      // 调用API提交任务
      const result = await taskApi.submitTask(id, data)
      console.log('✅ [ProjectStore] API调用成功:', result)

      // 解析API响应数据，处理不同的响应格式
      const apiResponse = (result as any).data || result
      console.log('📋 [ProjectStore] 解析的提交响应:', apiResponse)

      // 检查API调用是否成功
      if (apiResponse.success) {
        console.log('✅ [ProjectStore] 任务提交成功，刷新任务列表')

        // 刷新任务列表以同步最新状态
        await fetchTasks({ assignedTo: '', page: 1, pageSize: 100 })

        return { success: true, message: apiResponse.message || '任务提交成功' }
      } else {
        throw new Error(apiResponse.message || '任务提交失败')
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 提交任务失败:', error)
      throw error
    }
  }

  const abandonTask = async (id: string, reason?: string) => {
    try {
      console.log('🚫 [ProjectStore] 开始放弃任务:', id, reason)

      // 调用API放弃任务
      const result = await taskApi.abandonTask(id, reason)
      console.log('✅ [ProjectStore] API调用成功:', result)

      // 解析API响应数据
      const apiResponse = (result as any).data || result

      // 检查API调用是否成功
      if (apiResponse.success) {
        console.log('✅ [ProjectStore] 任务放弃成功，刷新任务列表')

        // 刷新任务列表以同步最新状态
        await fetchTasks({ assignedTo: '', page: 1, pageSize: 100 })

        return { success: true, message: apiResponse.message || '任务放弃成功' }
      } else {
        throw new Error(apiResponse.message || '任务放弃失败')
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 放弃任务失败:', error)
      throw error
    }
  }

  const reviewTask = async (
    id: string,
    action: 'approve' | 'reject',
    comment?: string,
    score?: number,
    rejectImages?: string[]
  ) => {
    try {
      console.log('📋 [ProjectStore] 开始审核任务:', id, action, comment, score, rejectImages)

      // 调用API审核任务
      const reviewData = {
        approved: action === 'approve',
        comment: comment || '',
        score: action === 'approve' ? score || 5 : undefined, // 审核通过时才有评分
        reject_images: action === 'reject' && rejectImages ? rejectImages : undefined
      }

      console.log('📤 [ProjectStore] 发送审核数据:', reviewData)
      const result = await taskApi.reviewTask(id, reviewData)
      console.log('✅ [ProjectStore] API调用成功:', result)

      // 解析API响应数据，处理不同的响应格式
      const apiResponse = (result as any).data || result
      console.log('📋 [ProjectStore] 解析的审核响应:', apiResponse)

      // 检查API调用是否成功
      if (apiResponse.success) {
        console.log(
          `✅ [ProjectStore] 任务审核${action === 'approve' ? '通过' : '打回'}成功，刷新任务列表`
        )

        // 刷新任务列表以同步最新状态
        await fetchTasks({ assignedTo: '', page: 1, pageSize: 100 })

        // 使用后端返回的消息，包含绩效信息
        const message =
          apiResponse.message || (action === 'approve' ? '任务审核通过' : '任务已打回重标')
        return { success: true, message }
      } else {
        throw new Error(apiResponse.message || '任务审核失败')
      }
    } catch (error) {
      console.error('❌ [ProjectStore] 审核任务失败:', error)
      throw error
    }
  }

  const importTasksFromExcel = async (file: File, projectId: string) => {
    try {
      const res = await taskApi.importTasksFromExcel(file, projectId)
      // 导入后刷新任务列表
      await fetchTasks({ page: 1, pageSize: 100 })
      return (res as any).data || res
    } catch (error) {
      console.error('导入任务失败:', error)
      throw error
    }
  }

  // 用户管理
  const fetchUsers = async (params: any) => {
    try {
      console.log('👥 [ProjectStore] 获取用户列表:', params)
      const response = await userApi.getUsers({
        current: params.page || 1,
        size: params.pageSize || 100,
        role: params.role,
        status: params.status || 'active'
      })

      console.log('✅ [ProjectStore] 用户列表获取成功:', response)

      // 处理响应数据
      if (response && response.data && response.data.list) {
        users.value = response.data.list
        total.value = response.data.total || users.value.length
      } else if (Array.isArray(response)) {
        users.value = response
        total.value = response.length
      } else {
        console.warn('⚠️ [ProjectStore] 用户列表响应格式异常:', response)
        users.value = []
        total.value = 0
      }

      console.log('📊 [ProjectStore] 用户列表状态:', {
        count: users.value.length,
        total: total.value,
        role: params.role
      })
    } catch (error) {
      console.error('❌ [ProjectStore] 获取用户列表失败:', error)
      users.value = []
      total.value = 0
    }
  }

  // 绩效管理
  const fetchPerformanceStats = async (params: any) => {
    try {
      console.log('📈 [ProjectStore] 获取绩效统计:', params)
      const result = await performanceApi.getPerformanceStats(params)
      console.log('✅ [ProjectStore] 绩效统计获取成功:', result)
      return (result as any).data || result
    } catch (error) {
      console.error('❌ [ProjectStore] 获取绩效统计失败:', error)
      // 如果失败，返回空数据而不是模拟数据
      return { list: [] }
    }
  }

  const getPersonalPerformance = async (period: string = 'monthly') => {
    try {
      console.log('📈 [ProjectStore] 获取个人绩效:', period)

      // 调用绩效API
      const result = await performanceApi.getPersonalPerformance(period)
      console.log('✅ [ProjectStore] 个人绩效获取成功:', result)

      return (result as any).data || result
    } catch (error) {
      console.error('❌ [ProjectStore] 获取个人绩效失败:', error)
      // 如果失败，返回模拟数据作为后备
      const userTasks = tasks.value.filter((t) => t.assignedTo === getCurrentUserId())
      const completedTasks = userTasks.filter((t) => t.status === 'approved')

      return {
        total_tasks: userTasks.length,
        completed_tasks: completedTasks.length,
        total_score: completedTasks.length, // 每完成一个任务+1分
        average_score: completedTasks.length > 0 ? 1 : 0,
        completion_rate: userTasks.length > 0 ? (completedTasks.length / userTasks.length) * 100 : 0
      }
    }
  }

  // WebSocket 审核通知（简易客户端，仅审核员连接）
  let notifySocket: WebSocket | null = null
  const ensureReviewerNotification = () => {
    try {
      const userStore = useUserStore()
      const current: any = userStore.currentUser
      if (!current) return
      const role = (current.role || '').toLowerCase()
      if (role !== 'reviewer') return
      if (notifySocket && (notifySocket.readyState === 0 || notifySocket.readyState === 1)) return
      const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
      // 若前端有 VITE_API_URL 代理到 /api，需要与之保持一致
      const baseHost = (import.meta as any).env?.VITE_API_URL
        ? new URL((import.meta as any).env.VITE_API_URL).host
        : location.host
      const wsUrl = `${protocol}://${baseHost}/api/ws/notifications`
      notifySocket = new WebSocket(wsUrl)
      notifySocket.onopen = () => {
        try {
          notifySocket?.send(
            JSON.stringify({
              role,
              user: {
                id: current.id,
                username: current.username,
                real_name: current.realName || current.real_name
              }
            })
          )
          console.log('🔔 [WS] 审核员通知连接已建立:', wsUrl)
        } catch {}
      }
      notifySocket.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data || '{}')
          if (data && data.type === 'task_submitted') {
            setTimeout(() => {
              ElMessage.info(`${data.content}（待审核：${data.pending}）`)
            }, 100)
          }
        } catch {}
      }
      notifySocket.onerror = (e) => {
        console.warn('🔔 [WS] 通知连接出错:', e)
      }
      notifySocket.onclose = () => {
        console.warn('🔔 [WS] 通知连接已关闭')
      }
    } catch {}
  }

  // 仪表板数据（概览）
  const fetchDashboardOverview = async () => {
    try {
      console.log('📊 [ProjectStore] 获取仪表板概览数据')
      const result = await dashboardApi.getOverview()
      console.log('✅ [ProjectStore] 仪表板概览数据获取成功:', result)
      return (result as any).data || result
    } catch (error) {
      console.error('❌ [ProjectStore] 获取仪表板概览失败，尝试从其他API获取数据:', error)

      // 如果仪表板API失败，从其他API获取数据
      try {
        console.log('🔄 [ProjectStore] 从其他API获取统计数据')

        // 获取任务数据（这个API是成功的）
        const tasksResult = await taskApi.getTasks({ page: 1, pageSize: 1000 })
        const tasksList =
          (tasksResult as any)?.data?.list ||
          (tasksResult as any)?.list ||
          (tasksResult as any)?.data ||
          []

        console.log('📋 [ProjectStore] 获取到任务数据用于统计:', tasksList.length)

        // 从任务数据中提取项目信息
        const uniqueProjects = new Set<string>()
        tasksList.forEach((task: any) => {
          const projectId = task.project_id || task.projectId
          if (projectId) {
            uniqueProjects.add(projectId)
          }
        })

        // 尝试获取用户数据，如果失败就使用默认值
        let usersList: any[] = []
        try {
          const usersResult = await userApi.getUsersBasic({ status: 'active', size: 1000 })
          usersList = usersResult?.list || usersResult?.data?.list || usersResult?.data || []
        } catch (userError) {
          console.warn('⚠️ [ProjectStore] 获取用户数据失败，使用默认值')
          usersList = []
        }

        // 计算统计数据 - 修正：只有approved才算已完成
        const overviewData = {
          totalProjects: uniqueProjects.size,
          activeProjects: uniqueProjects.size, // 假设所有项目都是活跃的
          totalTasks: tasksList.length,
          pendingTasks: tasksList.filter((t: any) => t.status === 'pending').length,
          inProgressTasks: tasksList.filter((t: any) => t.status === 'in_progress').length,
          submittedTasks: tasksList.filter((t: any) => t.status === 'submitted').length,
          completedTasks: tasksList.filter((t: any) => t.status === 'approved').length, // 只有approved才是已完成
          rejectedTasks: tasksList.filter((t: any) => t.status === 'rejected').length,
          totalUsers: usersList.length || 5, // 如果获取不到用户数据，使用默认值
          activeUsers: usersList.filter((u: any) => u.status === 'active').length || 5
        }

        console.log('✅ [ProjectStore] 从其他API获取统计数据成功:', overviewData)
        return overviewData
      } catch (fallbackError) {
        console.error('❌ [ProjectStore] 从其他API获取数据也失败:', fallbackError)

        // 最后的后备方案：使用模拟数据
        initializeMockData()
        return {
          totalProjects: projects.value.length,
          activeProjects: activeProjects.value.length,
          totalTasks: tasks.value.length,
          pendingTasks: pendingTasks.value.length,
          inProgressTasks: tasks.value.filter((t) => t.status === 'in_progress').length,
          submittedTasks: tasks.value.filter((t) => t.status === 'submitted').length,
          completedTasks: tasks.value.filter((t) => t.status === 'approved').length, // 只有approved才是已完成
          rejectedTasks: tasks.value.filter((t) => t.status === 'rejected').length,
          totalUsers: users.value.length,
          activeUsers: users.value.filter((u) => u.status === 'active').length
        }
      }
    }
  }

  // 仪表板数据（项目进度数组）
  const fetchProjectProgress = async () => {
    try {
      console.log('📊 [ProjectStore] 获取项目进度数据')
      const result = await dashboardApi.getProjectProgress()
      console.log('✅ [ProjectStore] 项目进度数据获取成功:', result)

      // 处理返回的数据
      let progressData = [] as any[]
      if (Array.isArray(result)) {
        progressData = result as any[]
      } else if ((result as any)?.data && Array.isArray((result as any).data)) {
        progressData = (result as any).data
      } else if (
        (result as any)?.project_progress &&
        Array.isArray((result as any).project_progress)
      ) {
        progressData = (result as any).project_progress
      } else {
        progressData = ((result as any).data || result || []) as any[]
      }

      // 映射字段名（补充 skippedTasks）
      const mappedProgressData = progressData.map((item: any) => ({
        projectId: item.projectId || item.id || item.project_id,
        projectName: item.projectName || item.name || item.project_name,
        totalTasks: item.totalTasks || item.total_tasks || 0,
        completedTasks: item.completedTasks || item.completed_tasks || 0,
        completionRate: item.completionRate || item.completion_rate || item.progress || 0,
        pendingTasks: item.pendingTasks || item.pending_tasks || 0,
        inProgressTasks: item.inProgressTasks || item.in_progress_tasks || 0,
        submittedTasks: item.submittedTasks || item.submitted_tasks || 0,
        approvedTasks: item.approvedTasks || item.approved_tasks || 0,
        rejectedTasks: item.rejectedTasks || item.rejected_tasks || 0,
        skippedTasks: item.skippedTasks || item.skipped_tasks || 0,
        averageScore: item.averageScore || item.average_score || 0,
        totalHours: item.totalHours || item.total_hours || 0
      }))

      projectStats.value = mappedProgressData
      console.log('📊 [ProjectStore] 项目进度数据处理完成:', mappedProgressData)
      return mappedProgressData
    } catch (error) {
      console.error('❌ [ProjectStore] 获取项目进度失败，尝试从其他API计算:', error)

      // 如果API失败，从任务数据中提取项目信息计算进度
      try {
        console.log('🔄 [ProjectStore] 从任务数据计算项目进度')

        // 获取任务数据（这个API是成功的）
        const tasksResult = await taskApi.getTasks({ page: 1, pageSize: 1000 })
        const tasksList =
          (tasksResult as any)?.data?.list ||
          (tasksResult as any)?.list ||
          (tasksResult as any)?.data ||
          []

        console.log('📋 [ProjectStore] 获取到任务数据用于项目进度计算:', tasksList.length)

        // 从任务数据中提取项目信息
        const projectMap = new Map()
        tasksList.forEach((task: any) => {
          const projectId = task.project_id || task.projectId
          const projectName = task.project_name || task.projectName || '未知项目'

          if (projectId && !projectMap.has(projectId)) {
            projectMap.set(projectId, {
              projectId: projectId,
              projectName: projectName,
              tasks: []
            })
          }

          if (projectId) {
            projectMap.get(projectId).tasks.push(task)
          }
        })

        // 计算每个项目的进度 - 修正：只有approved才算已完成
        const calculatedProgress = Array.from(projectMap.values()).map((project: any) => {
          const projectTasks = project.tasks
          const completedTasks = projectTasks.filter(
            (task: any) => task.status === 'approved' // 只有approved才算已完成
          ).length

          return {
            projectId: project.projectId,
            projectName: project.projectName,
            totalTasks: projectTasks.length,
            completedTasks: completedTasks,
            completionRate:
              projectTasks.length > 0
                ? Math.round((completedTasks / projectTasks.length) * 100)
                : 0,
            pendingTasks: projectTasks.filter((task: any) => task.status === 'pending').length,
            inProgressTasks: projectTasks.filter((task: any) => task.status === 'in_progress')
              .length,
            submittedTasks: projectTasks.filter((task: any) => task.status === 'submitted').length,
            approvedTasks: projectTasks.filter((task: any) => task.status === 'approved').length,
            rejectedTasks: projectTasks.filter((task: any) => task.status === 'rejected').length,
            averageScore: 0,
            totalHours: 0
          }
        })

        projectStats.value = calculatedProgress
        console.log('✅ [ProjectStore] 从任务数据计算项目进度完成:', calculatedProgress)
        return calculatedProgress
      } catch (fallbackError) {
        console.error('❌ [ProjectStore] 从任务数据计算项目进度也失败:', fallbackError)

        // 最后的后备方案：使用模拟数据
        initializeMockData()
        const map: ProjectStats[] = projects.value.map((p) => {
          const projectTasks = tasks.value.filter((t) => t.projectId === p.id)
          const completed = projectTasks.filter((t) => t.status === 'approved').length // 只有approved才是已完成
          const completion =
            projectTasks.length > 0 ? Math.round((completed / projectTasks.length) * 100) : 0
          return {
            projectId: p.id,
            projectName: p.name,
            totalTasks: projectTasks.length,
            pendingTasks: projectTasks.filter((t) => t.status === 'pending').length,
            inProgressTasks: projectTasks.filter((t) => t.status === 'in_progress').length,
            submittedTasks: projectTasks.filter((t) => t.status === 'submitted').length,
            completedTasks: completed,
            approvedTasks: projectTasks.filter((t) => t.status === 'approved').length,
            rejectedTasks: projectTasks.filter((t) => t.status === 'rejected').length,
            completionRate: completion,
            averageScore: 85,
            totalHours: projectTasks.reduce((sum, t) => sum + (t.actualHours || 0), 0)
          }
        })
        projectStats.value = map
        return map
      }
    }
  }

  // 仪表板数据（合并）
  const fetchDashboardData = async () => {
    try {
      // 使用模拟数据
      initializeMockData()

      const dashboardData = {
        totalProjects: projects.value.length,
        activeProjects: activeProjects.value.length,
        totalTasks: tasks.value.length,
        pendingTasks: pendingTasks.value.length,
        completedTasks: tasks.value.filter(
          (t) => t.status === 'submitted' || t.status === 'approved'
        ).length,
        totalUsers: users.value.length,
        recentTasks: tasks.value.slice(0, 5),
        projectProgress: projects.value.map((p) => ({
          id: p.id,
          name: p.name,
          progress: (p.completedTasks / p.totalTasks) * 100
        }))
      }

      return dashboardData
    } catch (error) {
      console.error('获取仪表板数据失败:', error)
      throw error
    }
  }

  return {
    // 状态
    projects,
    currentProject,
    tasks,
    users,
    performanceStats,
    projectStats,
    loading,
    total,

    // 计算属性
    activeProjects,
    completedProjects,
    pendingTasks,
    myTasks,

    // 项目管理
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    deleteTask,
    getProjectStats,

    // 任务管理
    fetchTasks,
    createTask,
    claimTask,
    startTask,
    restartTask,
    submitTask,
    abandonTask,
    reviewTask,
    importTasksFromExcel,
    uploadAnnotationImages,
    uploadReviewImages,

    // 用户管理
    fetchUsers,

    // 绩效管理
    fetchPerformanceStats,
    getPersonalPerformance,

    // 仪表板
    fetchDashboardData,
    fetchDashboardOverview,
    fetchProjectProgress,

    // 初始化
    initializeMockData
  }
})
