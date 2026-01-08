<template>
  <div v-loading="loading" class="project-detail-view">
    <!-- 顶部项目概览 -->
    <div class="dashboard-header">
      <div class="project-info">
        <div class="title-row">
          <h1 class="project-title">{{ project?.name }}</h1>
          <div class="tags">
            <el-tag :type="getStatusType(project?.status)" effect="dark" class="status-tag">
              {{ getStatusText(project?.status) }}
            </el-tag>
            <el-tag :type="getPriorityType(project?.priority)" effect="plain" class="priority-tag">
              {{ getPriorityText(project?.priority) }}优先级
            </el-tag>
            <CategoryTag
              v-if="project?.category"
              :category="project.category"
              :sub-category="project.subCategory"
              size="default"
            />
          </div>
        </div>
        <p class="project-desc">{{ project?.description || '暂无项目描述' }}</p>
        <div class="project-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            创建于 {{ formatDate(project?.createdAt) }}
          </span>
          <span class="meta-item" v-if="project?.endDate">
            <el-icon><Timer /></el-icon>
            截止日期 {{ project?.endDate }}
          </span>
        </div>
      </div>
      
      <div class="header-actions">
        <el-button @click="handleExportReport" :loading="exportLoading" class="action-btn">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
        <el-button type="primary" @click="handleEdit" class="action-btn">
          <el-icon><Edit /></el-icon>
          编辑项目
        </el-button>
        <el-button 
          v-if="canDeleteProject" 
          type="danger" 
          plain 
          @click="handleDelete" 
          class="action-btn"
        >
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary-bg">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ taskStats.total }}</div>
          <div class="stat-label">总任务数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success-bg">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ taskStats.completed }}</div>
          <div class="stat-label">已完成任务</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon warning-bg">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ completionRate }}%</div>
          <div class="stat-label">整体完成率</div>
        </div>
        <el-progress 
          type="circle" 
          :percentage="completionRate" 
          :width="40" 
          :stroke-width="4"
          :show-text="false"
          class="mini-progress"
        />
      </div>

      <div class="stat-card">
        <div class="stat-icon info-bg">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ annotatorNames.length }}</div>
          <div class="stat-label">参与成员</div>
        </div>
        <div class="avatars" v-if="annotatorNames.length > 0">
          <div class="avatar-placeholder" v-for="i in Math.min(3, annotatorNames.length)" :key="i"></div>
        </div>
      </div>
    </div>

    <!-- 主要图表区域 -->
    <div class="charts-grid">
      <!-- 任务状态分布 -->
      <div class="chart-card ring-chart">
        <div class="card-header">
          <h3>任务状态分布</h3>
        </div>
        <div class="chart-body">
          <ArtRingChart
            height="300px"
            :data="taskStatusData"
            :showTooltip="true"
            :showLegend="true"
            legendPosition="right"
            :radius="['60%', '80%']"
            :colors="statusColors"
            :centerText="`${completionRate}%\n完成率`"
          />
        </div>
      </div>

      <!-- 标注员贡献分析 -->
      <div class="chart-card bar-chart">
        <div class="card-header">
          <h3>标注员贡献分析</h3>
          <span class="subtitle">Top 10 贡献榜</span>
        </div>
        <div class="chart-body">
          <ArtBarChart
            v-if="!loading && annotatorNames.length > 0"
            :key="`bar-chart-${annotatorNames.length}`"
            height="300px"
            :data="annotatorTaskData"
            :xAxisData="annotatorNames.slice(0, 10)"
            :stack="true"
            :showLegend="true"
            :showTooltip="true"
            legendPosition="top"
            :colors="barChartColors"
            barWidth="40%"
          />
          <el-empty v-else description="暂无数据" :image-size="100" />
        </div>
      </div>
    </div>

    <!-- 任务列表和进度详情 -->
    <div class="details-grid">
      <!-- 最新任务列表 -->
      <div class="chart-card task-list-card">
        <div class="card-header">
          <h3>最新任务</h3>
          <el-tag size="small" type="info">{{ projectTasks.length }} 个任务</el-tag>
        </div>
        <div class="card-body no-padding">
          <el-table :data="projectTasks.slice(0, 5)" style="width: 100%">
            <el-table-column prop="title" label="任务名称" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="task-title">{{ row.title }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getTaskStatusType(row.status)" size="small" effect="light">
                  {{ getTaskStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assignedToName" label="执行人" width="100">
              <template #default="{ row }">
                <div class="user-cell" v-if="row.assignedToName">
                  <el-avatar :size="20" class="small-avatar">{{ row.assignedToName[0] }}</el-avatar>
                  <span>{{ row.assignedToName }}</span>
                </div>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="时间" width="140">
              <template #default="{ row }">
                <span class="text-gray text-small">{{ formatDate(row.createdAt) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 项目完结操作 -->
      <div class="chart-card action-card">
        <div class="card-header">
          <h3>项目操作</h3>
        </div>
        <div class="card-body center-content">
          <div class="progress-circle-container">
            <el-progress 
              type="dashboard" 
              :percentage="completionRate" 
              :width="160"
              :color="getProgressColor(completionRate)"
            >
              <template #default="{ percentage }">
                <div class="progress-value">{{ percentage }}%</div>
                <div class="progress-text">项目进度</div>
              </template>
            </el-progress>
          </div>
          
          <div class="action-buttons">
            <el-button
              v-if="project?.status !== 'completed'"
              type="success"
              size="large"
              :disabled="completionRate < 100"
              @click="handleFinishProject"
              class="finish-btn"
            >
              <el-icon><Check /></el-icon>
              完结项目
            </el-button>

            <el-alert 
              v-else 
              type="success" 
              :closable="false" 
              show-icon
              class="completed-alert"
            >
              <template #title>
                <span class="success-text">项目已完结</span>
              </template>
              <div class="success-desc">完结于 {{ project?.endDate || '未知日期' }}</div>
            </el-alert>

            <p class="tip-text" v-if="project?.status !== 'completed' && completionRate < 100">
              需达到 100% 进度方可完结
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑项目对话框 -->
    <ProjectFormDialog v-model="showEditDialog" :project="project" @success="handleEditSuccess" />
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { 
    Edit, Check, Loading, Download, Delete, 
    Calendar, Timer, List, TrendCharts, UserFilled 
  } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import { taskApi } from '@/api/projectApi'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import CategoryTag from '@/components/project/CategoryTag.vue'
  import ProjectFormDialog from './ProjectFormDialog.vue'
  import type { Project, Task } from '@/types/project'

  defineOptions({ name: 'ProjectDetailView' })

  interface Props {
    project?: Project
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    refresh: []
    deleted: []
  }>()

  const router = useRouter()
  const projectStore = useProjectStore()
  const userStore = useUserStore()

  // State
  const loading = ref(false)
  const projectTasks = ref<any[]>([])
  const showEditDialog = ref(false)
  const exportLoading = ref(false)

  // 权限检查：是否可以删除项目
  const canDeleteProject = computed(() => {
    const role = userStore.currentUser?.role || ''
    return ['admin', 'super'].includes(role.toLowerCase())
  })

  // 加载项目任务
  const loadProjectTasks = async () => {
    if (!props.project) return

    loading.value = true
    try {
      const result = await taskApi.getTasks({
        projectId: props.project.id,
        page: 1,
        pageSize: 1000,
        includeCompletedProjects: true
      })

      console.log('🔍 [ProjectDetailView] 原始任务数据:', result)

      let taskList = []
      if (result && (result as any).list) {
        // 优先检查 result.list（新的 API 响应格式）
        taskList = (result as any).list || []
      } else if (result && (result as any).data) {
        // 然后检查 result.data.list
        taskList = ((result as any).data as any).list || []
      } else if (Array.isArray(result)) {
        // 最后检查是否直接是数组
        taskList = result
      }

      console.log('📋 [ProjectDetailView] 处理后的任务列表:', taskList.length, '条')

      projectTasks.value = (taskList as any[]).map((task: any) => ({
        ...task,
        projectName: task.projectName || task.project_name || task.project?.name || '未知项目',
        assignedTo: task.assignedTo || task.assigned_to,
        assignedToName: task.assignedToName || task.assigned_to_name,
        createdBy: task.createdBy || task.created_by,
        createdByName: task.createdByName || task.created_by_name,
        reviewedBy: task.reviewedBy || task.reviewed_by,
        reviewedByName: task.reviewedByName || task.reviewed_by_name
      }))
    } catch (error) {
      console.error('加载项目任务失败:', error)
      ElMessage.error('加载项目任务失败')
    } finally {
      loading.value = false
    }
  }

  // 监听项目变化
  watch(
    () => props.project,
    async (newProject) => {
      if (newProject) {
        await loadProjectTasks()
      }
    },
    { immediate: true }
  )

  // 任务统计
  const taskStats = computed(() => {
    const tasks = projectTasks.value
    return {
      total: tasks.length,
      pending: tasks.filter((t) => t.status === 'pending').length,
      inProgress: tasks.filter((t) => t.status === 'in_progress').length,
      submitted: tasks.filter((t) => t.status === 'submitted').length,
      completed: tasks.filter((t) => t.status === 'approved').length,
      rejected: tasks.filter((t) => t.status === 'rejected').length,
      skipped: tasks.filter((t) => t.status === 'skipped').length
    }
  })

  // 完成率
  const completionRate = computed(() => {
    if (taskStats.value.total === 0) return 0
    return Math.round((taskStats.value.completed / taskStats.value.total) * 100)
  })

  // 任务状态分布数据（带颜色映射）
  const taskStatusData = computed(() => {
    const dataWithColors = [
      { name: '待分配', value: taskStats.value.pending, color: taskStatusColorMap.pending },
      { name: '进行中', value: taskStats.value.inProgress, color: taskStatusColorMap.inProgress },
      { name: '已提交', value: taskStats.value.submitted, color: taskStatusColorMap.submitted },
      { name: '已完成', value: taskStats.value.completed, color: taskStatusColorMap.completed },
      { name: '已驳回', value: taskStats.value.rejected, color: taskStatusColorMap.rejected },
      { name: '已跳过', value: taskStats.value.skipped, color: taskStatusColorMap.skipped }
    ]

    // 过滤掉值为0的项
    return dataWithColors.filter((item) => item.value > 0)
  })

  // 标注员任务分配和完成情况（堆叠柱状图数据）
  const annotatorTaskStats = computed(() => {
    const tasks = projectTasks.value
    const annotatorMap = new Map<
      string,
      {
        completed: number
        inProgress: number
        submitted: number
        rejected: number
        skipped: number
        pending: number
      }
    >()

    tasks.forEach((t) => {
      // 过滤掉未分配的任务
      const name = t.assignedToName || t.assignedTo
      if (!name || name === '未分配' || name === 'unassigned') {
        return
      }

      if (!annotatorMap.has(name)) {
        annotatorMap.set(name, {
          completed: 0,
          inProgress: 0,
          submitted: 0,
          rejected: 0,
          skipped: 0,
          pending: 0
        })
      }

      const stats = annotatorMap.get(name)!
      if (t.status === 'approved') {
        stats.completed++
      } else if (t.status === 'in_progress') {
        stats.inProgress++
      } else if (t.status === 'submitted') {
        stats.submitted++
      } else if (t.status === 'rejected') {
        stats.rejected++
      } else if (t.status === 'skipped') {
        stats.skipped++
      } else if (t.status === 'pending' || t.status === 'assigned') {
        stats.pending++
      }
    })

    return annotatorMap
  })

  // 标注员名称列表（横轴）
  const annotatorNames = computed(() => {
    const names = Array.from(annotatorTaskStats.value.keys())
    // 按总任务数排序
    const sorted = names.sort((a, b) => {
      const statsA = annotatorTaskStats.value.get(a)!
      const statsB = annotatorTaskStats.value.get(b)!
      const totalA =
        statsA.completed +
        statsA.inProgress +
        statsA.submitted +
        statsA.rejected +
        statsA.skipped +
        statsA.pending
      const totalB =
        statsB.completed +
        statsB.inProgress +
        statsB.submitted +
        statsB.rejected +
        statsB.skipped +
        statsB.pending
      return totalB - totalA
    })
    return sorted
  })

  // 堆叠柱状图数据（按照统一的状态顺序和颜色）
  const annotatorTaskData = computed(() => {
    const names = annotatorNames.value

    const chartData = [
      {
        name: '待分配',
        data: names.map((name) => annotatorTaskStats.value.get(name)?.pending || 0),
        stack: 'total'
      },
      {
        name: '进行中',
        data: names.map((name) => annotatorTaskStats.value.get(name)?.inProgress || 0),
        stack: 'total'
      },
      {
        name: '已提交',
        data: names.map((name) => annotatorTaskStats.value.get(name)?.submitted || 0),
        stack: 'total'
      },
      {
        name: '已完成',
        data: names.map((name) => annotatorTaskStats.value.get(name)?.completed || 0),
        stack: 'total'
      },
      {
        name: '已驳回',
        data: names.map((name) => annotatorTaskStats.value.get(name)?.rejected || 0),
        stack: 'total'
      },
      {
        name: '已跳过',
        data: names.map((name) => annotatorTaskStats.value.get(name)?.skipped || 0),
        stack: 'total'
      }
    ]

    return chartData
  })

  // 统一的任务状态颜色映射
  const taskStatusColorMap = {
    pending: '#f59e0b', // 待分配 - 橙色
    inProgress: '#3b82f6', // 进行中 - 蓝色
    submitted: '#8b5cf6', // 已提交 - 紫色
    completed: '#10b981', // 已完成 - 绿色
    rejected: '#ef4444', // 已驳回 - 红色
    skipped: '#94a3b8' // 已跳过 - 灰色
  }

  // 任务状态分布图颜色（动态生成）
  const statusColors = computed(() => {
    return taskStatusData.value.map((item) => item.color)
  })

  // 标注员参与度分析柱状图颜色（固定顺序）
  const barChartColors = [
    taskStatusColorMap.pending, // 待分配
    taskStatusColorMap.inProgress, // 进行中
    taskStatusColorMap.submitted, // 已提交
    taskStatusColorMap.completed, // 已完成
    taskStatusColorMap.rejected, // 已驳回
    taskStatusColorMap.skipped // 已跳过
  ]

  // 状态类型映射函数
  const getStatusType = (status?: string): 'success' | 'warning' | 'info' | 'danger' => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
      active: 'success',
      completed: 'info',
      paused: 'warning',
      cancelled: 'danger'
    }
    return (status && map[status]) || 'info'
  }

  const getStatusText = (status?: string) => {
    const map: Record<string, string> = {
      active: '进行中',
      completed: '已完成',
      paused: '已暂停',
      cancelled: '已取消'
    }
    return (status && map[status]) || status || '-'
  }

  const getPriorityType = (priority?: string): 'success' | 'warning' | 'info' | 'danger' => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
      low: 'info',
      medium: 'success',
      high: 'warning',
      urgent: 'danger'
    }
    return (priority && map[priority]) || 'info'
  }

  const getPriorityText = (priority?: string) => {
    const map: Record<string, string> = {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '紧急'
    }
    return (priority && map[priority]) || priority || '-'
  }

  const getTaskStatusType = (status: string): 'success' | 'warning' | 'info' | 'danger' => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
      pending: 'info',
      assigned: 'primary' as any,
      in_progress: 'warning',
      submitted: 'success',
      approved: 'success',
      rejected: 'danger',
      skip_pending: 'warning',
      skipped: 'warning'
    }
    return map[status] || 'info'
  }

  const getTaskStatusText = (status: string) => {
    const map: Record<string, string> = {
      pending: '待领取',
      assigned: '已分配',
      in_progress: '进行中',
      submitted: '已提交',
      approved: '已通过',
      rejected: '已驳回',
      skip_pending: '跳过申请中',
      skipped: '已跳过'
    }
    return map[status] || status
  }

  const getProgressColor = (percentage: number) => {
    if (percentage < 30) return taskStatusColorMap.rejected // 红色
    if (percentage < 70) return taskStatusColorMap.pending // 橙色
    return taskStatusColorMap.completed // 绿色
  }

  // 格式化日期
  const formatDate = (date: string | Date | undefined) => {
    if (!date) return '-'
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  // 编辑项目
  const handleEdit = () => {
    showEditDialog.value = true
  }

  // 编辑成功
  const handleEditSuccess = () => {
    emit('refresh')
    loadProjectTasks()
  }

  // 导出项目报告
  const handleExportReport = async () => {
    if (!props.project) {
      ElMessage.error('项目信息不存在')
      return
    }

    try {
      exportLoading.value = true
      const url = `/api/performance/project/${props.project.id}/export`
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (!response.ok) throw new Error(`导出失败: ${response.statusText}`)

      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = `${props.project.name}_项目报告.pdf`
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/)
        if (filenameMatch) filename = decodeURIComponent(filenameMatch[1])
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)

      ElMessage.success('报告导出成功')
    } catch (error) {
      console.error('❌ [ProjectDetailView] 导出失败:', error)
      ElMessage.error('导出报告失败，请重试')
    } finally {
      exportLoading.value = false
    }
  }

  // 完结项目
  const handleFinishProject = async () => {
    if (completionRate.value < 100) {
      ElMessage.warning('项目进度必须达到100%才能完结')
      return
    }

    if (!props.project) {
      ElMessage.error('项目信息不存在')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要完结项目"${props.project.name}"吗？\n\n注意：完结后项目状态将变更为"已完成"。`,
        '确认完结项目',
        {
          confirmButtonText: '确定完结',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      loading.value = true
      const today = new Date().toISOString().split('T')[0]
      await projectStore.updateProject(props.project.id, {
        status: 'completed',
        endDate: today
      })

      ElMessage.success('项目已完结')
      emit('refresh')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('完结项目失败:', error)
        ElMessage.error('完结项目失败')
      }
    } finally {
      loading.value = false
    }
  }

  // 删除项目
  const handleDelete = async () => {
    if (!props.project) return

    try {
      await ElMessageBox.confirm(
        `确定要删除项目"${props.project.name}"吗？此操作不可恢复。`,
        '确认删除项目',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'error'
        }
      )

      loading.value = true
      await projectStore.deleteProject(props.project.id)
      ElMessage.success('项目删除成功')
      emit('deleted')
      emit('refresh')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除项目失败:', error)
        ElMessage.error('删除项目失败')
      }
    } finally {
      loading.value = false
    }
  }
</script>

<style lang="scss" scoped>
.project-detail-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 顶部 Header
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--art-main-bg-color);
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  .project-info {
    flex: 1;
    .title-row {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      .project-title {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        color: var(--art-text-gray-900);
      }

      .tags {
        display: flex;
        gap: 8px;
        align-items: center;
      }
    }

    .project-desc {
      color: var(--art-text-gray-600);
      margin: 0 0 16px 0;
      font-size: 14px;
      max-width: 800px;
      line-height: 1.5;
    }

    .project-meta {
      display: flex;
      gap: 24px;
      color: var(--art-text-gray-500);
      font-size: 13px;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
    flex-shrink: 0;
  }
}

// 统计卡片 Grid
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  .stat-card {
    background: var(--art-main-bg-color);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;

      &.primary-bg { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
      &.success-bg { background: rgba(16, 185, 129, 0.1); color: #10b981; }
      &.warning-bg { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
      &.info-bg { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
    }

    .stat-content {
      flex: 1;
      .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--art-text-gray-900);
        line-height: 1.2;
      }
      .stat-label {
        font-size: 13px;
        color: var(--art-text-gray-500);
        margin-top: 4px;
      }
    }

    .mini-progress {
      margin-left: auto;
    }

    .avatars {
      display: flex;
      margin-left: auto;
      
      .avatar-placeholder {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #e5e7eb;
        border: 2px solid white;
        margin-left: -8px;
        &:first-child { margin-left: 0; }
      }
    }
  }
}

// 图表 Grid
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
}

// 详情 Grid
.details-grid {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 20px;
}

// 通用卡片样式
.chart-card {
  background: var(--art-main-bg-color);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--art-card-border);
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--art-text-gray-900);
    }

    .subtitle {
      font-size: 12px;
      color: var(--art-text-gray-500);
    }
  }

  .card-body {
    padding: 20px;
    flex: 1;

    &.no-padding {
      padding: 0;
    }

    &.center-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
  }
}

// 任务列表样式
.task-list-card {
  .user-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    .small-avatar {
      background: #e0e7ff;
      color: #4338ca;
      font-size: 10px;
    }
  }
  
  .text-gray { color: var(--art-text-gray-500); }
  .text-small { font-size: 12px; }
  .task-title { font-weight: 500; color: var(--art-text-gray-800); }
}

// 操作卡片样式
.action-card {
  .progress-circle-container {
    margin-bottom: 24px;
    .progress-value { font-size: 28px; font-weight: 700; color: var(--art-text-gray-900); }
    .progress-text { font-size: 12px; color: var(--art-text-gray-500); margin-top: 4px; }
  }

  .action-buttons {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;

    .finish-btn {
      width: 100%;
      height: 44px;
      font-size: 15px;
    }

    .completed-alert {
      width: 100%;
      margin-bottom: 0;
      
      .success-text { font-weight: 600; }
      .success-desc { font-size: 12px; margin-top: 4px; }
    }

    .tip-text {
      font-size: 12px;
      color: var(--art-text-gray-400);
      margin: 0;
    }
  }
}
</style>
