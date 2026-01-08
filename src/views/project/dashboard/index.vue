<template>
  <div class="project-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <ArtPageHeader
        title="项目仪表板"
        description="实时监控项目进度和团队绩效，全面掌控医学影像标注工作"
        icon="📊"
        badge="Dashboard"
        theme="purple"
      >
        <template #actions>
          <el-button type="primary" @click="refreshDashboard" round>
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </template>
      </ArtPageHeader>
    </div>

    <div class="dashboard-content">
      <!-- 核心指标卡片 -->
      <div class="metrics-grid">
        <ArtStatsCard
          :count="overview.totalProjects"
          title="总项目数"
          :description="`${overview.activeProjects} 个进行中`"
          icon="&#xe721;"
          icon-color="#3b82f6"
          class="metric-card style-blue"
        />
        <ArtStatsCard
          :count="overview.totalTasks"
          title="总任务数"
          :description="`${overview.completedTasks} 个已完成`"
          icon="&#xe7b9;"
          icon-color="#10b981"
          class="metric-card style-green"
        />
        <ArtStatsCard
          :count="overview.totalUsers"
          title="团队成员"
          :description="`${overview.activeUsers} 个活跃`"
          icon="&#xe7c3;"
          icon-color="#f97316"
          class="metric-card style-orange"
        />
        <ArtStatsCard
          :count="completionRate"
          title="整体完成率"
          :description="`${overview.pendingTasks} 个待处理`"
          icon="&#xe7c1;"
          icon-color="#8b5cf6"
          :decimals="1"
          suffix="%"
          class="metric-card style-purple"
        />
      </div>

      <!-- 主要图表区域 -->
      <div class="charts-grid">
        <!-- 项目进度概览 -->
        <div class="grid-item project-progress">
          <el-card class="dashboard-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box blue"><el-icon><DataAnalysis /></el-icon></span>
                  <span>项目进度概览</span>
                </div>
                <el-radio-group v-model="progressViewType" size="small">
                  <el-radio-button label="chart">图表</el-radio-button>
                  <el-radio-button label="list">列表</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div v-if="progressViewType === 'chart'" class="chart-content">
              <ArtBarChart
                height="350px"
                :data="projectProgressGroupedSeries"
                :xAxisData="groupedXAxisLabels"
                :showAxisLabel="true"
                :showTooltip="true"
                :showLegend="true"
                legendPosition="top"
                :stack="false"
                :colors="groupedColors"
                barWidth="16%"
                barGap="10%"
                barCategoryGap="30%"
              />
            </div>
            <div v-else class="project-progress-list custom-scrollbar">
              <div
                v-for="project in projectProgress"
                :key="project.projectId"
                class="progress-item"
              >
                <div class="project-info">
                  <span class="project-name">{{ project.projectName }}</span>
                  <span class="project-meta">{{ project.completedTasks }}/{{ project.totalTasks }} 任务</span>
                </div>
                <div class="progress-bar-wrapper">
                  <el-progress
                    :percentage="Math.round(project.completionRate)"
                    :stroke-width="10"
                    :color="getProgressColor(project.completionRate)"
                    :format="(p) => `${p}%`"
                  />
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 本月绩效排行榜 -->
        <div class="grid-item performance-rank">
          <el-card class="dashboard-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box orange"><el-icon><CaretTop /></el-icon></span>
                  <span>本月绩效榜</span>
                </div>
                <el-tag size="small" effect="plain">Top 6</el-tag>
              </div>
            </template>
            <div class="ranking-list custom-scrollbar">
              <div v-if="topPerformers.length === 0" class="empty-state">
                <el-empty description="暂无数据" :image-size="80" />
              </div>
              <div
                v-else
                v-for="(member, index) in topPerformers.slice(0, 6)"
                :key="`${member.userId}-${index}`"
                class="ranking-item"
                :class="`rank-${index + 1}`"
              >
                <div class="rank-badge">
                  <span v-if="index < 3" class="medal">{{ ['🥇', '🥈', '🥉'][index] }}</span>
                  <span v-else class="number">{{ index + 1 }}</span>
                </div>
                <div class="member-avatar">
                  <el-avatar :size="36" :src="member.avatar">
                    {{ (member.realName || member.username || '?')[0].toUpperCase() }}
                  </el-avatar>
                </div>
                <div class="member-info">
                  <div class="name">{{ member.realName || member.username }}</div>
                  <div class="score">积分: {{ member.totalScore }}</div>
                </div>
                <div class="member-stats">
                  <div class="stat-val">{{ member.completedTasks }}</div>
                  <div class="stat-label">任务</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 任务状态分布 -->
        <div class="grid-item task-status">
          <el-card class="dashboard-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box green"><el-icon><PieChart /></el-icon></span>
                  <span>任务状态分布</span>
                </div>
              </div>
            </template>
            <div class="task-status-content">
              <ArtRingChart
                height="220px"
                :data="taskStatusChartData"
                :showTooltip="true"
                :showLegend="true"
                legendPosition="right"
                :radius="['50%', '70%']"
                :colors="taskStatusChartColors"
                :centerText="overview.totalTasks.toString()"
                centerLabel="总任务"
              />
              <div class="status-bar-chart">
                 <ArtBarChart
                  height="180px"
                  :data="taskStatusBarData"
                  :xAxisData="taskStatusLabels"
                  :showTooltip="true"
                  :showLegend="false"
                  :colors="taskStatusChartColors"
                  barWidth="40%"
                />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 实时动态 -->
        <div class="grid-item recent-activity">
          <el-card class="dashboard-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box purple"><el-icon><Clock /></el-icon></span>
                  <span>实时动态</span>
                </div>
                <el-button link @click="fetchRecentActivities">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="activity-list custom-scrollbar">
              <div v-if="recentActivities.length === 0" class="empty-state">
                 <el-empty description="暂无动态" :image-size="60" />
              </div>
              <el-timeline v-else>
                <el-timeline-item
                  v-for="activity in recentActivities"
                  :key="activity.id"
                  :type="getActivityType(activity.type)"
                  :color="getActivityColor(activity.type)"
                  :timestamp="activity.timestamp"
                  placement="top"
                  hide-timestamp
                >
                  <div class="activity-card-item">
                    <div class="activity-header">
                      <span class="user">{{ activity.userName }}</span>
                      <span class="time">{{ activity.timestamp }}</span>
                    </div>
                    <div class="activity-body">
                      {{ activity.action }} <span class="target">{{ activity.target }}</span>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
        </div>

        <!-- 快速操作 -->
        <div class="grid-item quick-actions">
          <el-card class="dashboard-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box cyan"><el-icon><Tools /></el-icon></span>
                  <span>快捷操作</span>
                </div>
              </div>
            </template>
            <div class="quick-actions-list">
              <div class="action-btn primary" @click="handleQuickAction('newProject')">
                <el-icon><FolderAdd /></el-icon>
                <span>新建项目</span>
              </div>
              <div class="action-btn success" @click="handleQuickAction('importTasks')">
                <el-icon><Upload /></el-icon>
                <span>导入任务</span>
              </div>
              <div class="action-btn warning" @click="handleQuickAction('reviewTasks')">
                <el-icon><Check /></el-icon>
                <span>任务审核</span>
              </div>
              <div class="action-btn info" @click="handleQuickAction('performance')">
                <el-icon><TrendCharts /></el-icon>
                <span>团队绩效</span>
              </div>
            </div>
            <div class="today-stats">
               <div class="stat-row">
                 <span class="label">今日新增</span>
                 <span class="value">{{ todayStats.newTasks }}</span>
               </div>
               <div class="stat-row">
                 <span class="label">今日完成</span>
                 <span class="value success">{{ todayStats.completedTasks }}</span>
               </div>
               <div class="stat-row">
                 <span class="label">待审核</span>
                 <span class="value warning">{{ todayStats.pendingReview }}</span>
               </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import {
    Refresh, Folder, Document, User, CircleCheck, CaretTop, Plus, Upload, View, DataAnalysis,
    Clock, Tools, FolderAdd, Check, TrendCharts, PieChart
  } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import type { ProjectStats, PerformanceStats } from '@/types/project'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import { formatTimeAgo as formatTimeAgoUtil } from '@/utils/timeFormat'

  const projectStore = useProjectStore()
  const userStore = useUserStore()
  const router = useRouter()

  // 响应式数据
  const progressViewType = ref('chart')
  const activityDays = ref(7)
  const projectProgress = ref<ProjectStats[]>([])
  const topPerformers = ref<any[]>([])
  const recentActivities = ref<any[]>([])
  const userActivity = ref<any[]>([])

  // 概览数据
  const overview = reactive({
    totalProjects: 0,
    activeProjects: 0,
    totalTasks: 0,
    pendingTasks: 0,
    inProgressTasks: 0,
    submittedTasks: 0,
    completedTasks: 0,
    rejectedTasks: 0,
    totalUsers: 0,
    activeUsers: 0
  })

  // 今日统计
  const todayStats = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayISO = today.toISOString().split('T')[0]
    const allTasks = (projectStore.tasks || []) as any[]

    const newTasks = allTasks.filter((task: any) => {
      const createdAt = task.created_at || task.createdAt
      if (!createdAt) return false
      return new Date(createdAt).toISOString().split('T')[0] === todayISO
    }).length

    const completedTasks = allTasks.filter((task: any) => {
      if (task.status !== 'approved') return false
      const updatedAt = task.updated_at || task.updatedAt || task.approved_at || task.approvedAt
      if (!updatedAt) return false
      return new Date(updatedAt).toISOString().split('T')[0] === todayISO
    }).length

    const pendingReview = allTasks.filter((task: any) => task.status === 'submitted').length

    return { newTasks, completedTasks, pendingReview }
  })

  // 任务状态分布
  const taskStatusDistribution = reactive({
    pending: 0, in_progress: 0, submitted: 0, approved: 0, rejected: 0
  })

  // 计算完成率
  const completionRate = computed(() => {
    if (overview.totalTasks === 0) return 0
    return Math.round((overview.completedTasks / overview.totalTasks) * 100)
  })

  // 获取数据
  const fetchDashboardData = async () => {
    try {
      const overviewData = await projectStore.fetchDashboardOverview()
      const mappedOverview = {
        totalProjects: overviewData?.totalProjects || overviewData?.total_projects || 0,
        activeProjects: overviewData?.activeProjects || overviewData?.active_projects || 0,
        totalTasks: overviewData?.totalTasks || overviewData?.total_tasks || 0,
        pendingTasks: overviewData?.pendingTasks || overviewData?.pending_tasks || 0,
        inProgressTasks: overviewData?.inProgressTasks || overviewData?.in_progress_tasks || 0,
        submittedTasks: overviewData?.submittedTasks || overviewData?.submitted_tasks || 0,
        completedTasks: overviewData?.completedTasks || overviewData?.completed_tasks || 0,
        rejectedTasks: overviewData?.rejectedTasks || overviewData?.rejected_tasks || 0,
        totalUsers: overviewData?.totalUsers || overviewData?.total_users || 0,
        activeUsers: overviewData?.activeUsers || overviewData?.active_users || 0
      }
      Object.assign(overview, mappedOverview)

      // 获取项目进度
      const progressData = await projectStore.fetchProjectProgress()
      projectProgress.value = progressData.filter((project: any) => {
        return !(project.status === 'completed' || project.end_date || project.endDate || project.is_completed)
      })

      // 获取任务状态
      try {
        const result = await projectStore.fetchTasks({ page: 1, pageSize: 1000 })
        let taskList = []
        if (result?.data?.data && Array.isArray(result.data.data)) taskList = result.data.data
        else if (result?.data?.list) taskList = result.data.list
        else if (result?.data && Array.isArray(result.data)) taskList = result.data
        else if ((result as any)?.list) taskList = (result as any).list
        else if (Array.isArray(result)) taskList = result
        else if (result?.data && typeof result.data === 'object') {
           for (const k of Object.keys(result.data)) if (Array.isArray(result.data[k])) { taskList = result.data[k]; break; }
        }

        taskStatusDistribution.pending = taskList.filter((t: any) => t.status === 'pending').length
        taskStatusDistribution.in_progress = taskList.filter((t: any) => t.status === 'in_progress').length
        taskStatusDistribution.submitted = taskList.filter((t: any) => t.status === 'submitted').length
        taskStatusDistribution.approved = taskList.filter((t: any) => t.status === 'approved').length
        taskStatusDistribution.rejected = taskList.filter((t: any) => t.status === 'rejected').length
        ;(taskStatusDistribution as any).skipped = taskList.filter((t: any) => t.status === 'skipped').length
      } catch (e) {
        console.error(e)
      }

      // 获取绩效
      try {
        const result = await projectStore.fetchPerformanceStats({
          period: 'monthly',
          startDate: getMonthStart(),
          endDate: getMonthEnd(),
          page: 1, pageSize: 1000
        })
        
        if (result && (result.list || Array.isArray(result))) {
           const list = Array.isArray(result) ? result : result.list
           const mappedData = list.map((item: any) => ({
             userId: item.user_id || item.userId || 'unknown',
             username: item.username || 'unknown',
             realName: item.real_name || item.realName || '未知用户',
             avatar: item.avatar || '',
             totalTasks: item.total_tasks || 0,
             completedTasks: item.completed_tasks || 0,
             totalScore: item.total_score || 0,
           }))
           
           // 去重
           const userMap = new Map()
           mappedData.forEach((item: any) => {
             if (userMap.has(item.userId)) {
               const existing = userMap.get(item.userId)
               existing.totalTasks += item.totalTasks
               existing.completedTasks += item.completedTasks
               existing.totalScore += item.totalScore
             } else {
               userMap.set(item.userId, item)
             }
           })
           
           topPerformers.value = Array.from(userMap.values())
             .sort((a: any, b: any) => b.totalScore - a.totalScore)
             .slice(0, 8)
        }
      } catch (e) {
        console.error(e)
        topPerformers.value = []
      }

    } catch (error) {
      ElMessage.error('获取数据失败')
    }
  }

  // 获取动态
  const fetchRecentActivities = async () => {
    try {
      let allTasks = (projectStore.tasks || []) as any[]
      if (allTasks.length === 0) {
        await projectStore.fetchTasks({ page: 1, pageSize: 100 })
        allTasks = (projectStore.tasks || []) as any[]
      }
      if (allTasks.length === 0) {
        recentActivities.value = []
        return
      }

      const sortedTasks = [...allTasks].sort((a: any, b: any) => {
        const aTime = a.updated_at || a.updatedAt || a.created_at || a.createdAt || ''
        const bTime = b.updated_at || b.updatedAt || b.created_at || b.createdAt || ''
        return new Date(bTime).getTime() - new Date(aTime).getTime()
      })

      recentActivities.value = sortedTasks.slice(0, 5).map((task: any) => {
        const ts = task.updated_at || task.updatedAt || task.created_at || task.createdAt || new Date().toISOString()
        let action = '更新了任务', type = 'task_updated'
        if (task.status === 'approved') { action = '完成任务'; type = 'task_completed' }
        else if (task.status === 'submitted') { action = '提交任务'; type = 'task_submitted' }
        else if (task.status === 'in_progress') { action = '开始任务'; type = 'task_started' }
        else if (task.status === 'rejected') { action = '驳回任务'; type = 'task_rejected' }
        else if (task.status === 'pending') { action = '领取任务'; type = 'task_assigned' }

        return {
          id: task.id,
          type,
          userName: task.assigned_to_name || task.assignedToName || '用户',
          action,
          target: task.title || `任务#${task.id}`,
          timestamp: formatTimeAgoUtil(ts as string)
        }
      })
    } catch (e) {
      console.error(e)
    }
  }

  const getMonthStart = () => {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]
  }
  const getMonthEnd = () => {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0]
  }

  const refreshDashboard = () => {
    fetchDashboardData()
    fetchRecentActivities()
  }

  const handleQuickAction = (action: string) => {
    if (action === 'newProject') {
      router.push('/project/management')
    } else if (action === 'importTasks') {
      router.push('/project/management')
      ElMessage.info('请选择项目后导入')
    } else if (action === 'reviewTasks') {
      const role = userStore.currentUser?.role
      // 简单权限判断，具体以路由守卫为准
      if (role && ['admin', 'super', 'reviewer'].includes(role)) {
        router.push({ name: 'TaskReview' })
      } else {
        ElMessage.warning('您没有权限进行任务审核，请联系管理员')
      }
    } else if (action === 'performance') {
      router.push({ name: 'TeamPerformance' })
    }
  }

  const getActivityType = (type: string) => {
    const types: any = { task_completed: 'success', task_submitted: 'warning', task_rejected: 'danger', task_started: 'primary' }
    return types[type] || 'info'
  }
  
  const getActivityColor = (type: string) => {
     const colors: any = { task_completed: '#67c23a', task_submitted: '#e6a23c', task_rejected: '#f56c6c', task_started: '#409eff' }
     return colors[type] || '#909399'
  }

  const getProgressColor = (p: number) => {
    if (p >= 80) return '#67c23a'
    if (p >= 60) return '#e6a23c'
    if (p >= 40) return '#f56c6c'
    return '#909399'
  }

  // Chart Data
  const groupedXAxisLabels = computed(() => projectProgress.value.map((p) => p.projectName))
  const groupedColors = ['#a0aec0', '#409eff', '#e6a23c', '#67c23a']
  const projectProgressGroupedSeries = computed(() => {
    return [
      { name: '待分配', data: projectProgress.value.map(p => p.pendingTasks || 0) },
      { name: '进行中', data: projectProgress.value.map(p => p.inProgressTasks || 0) },
      { name: '已提交', data: projectProgress.value.map(p => p.submittedTasks || 0) },
      { name: '已完成', data: projectProgress.value.map(p => p.approvedTasks || p.completedTasks || 0) }
    ]
  })

  const taskStatusColorMap: any = {
    待分配: '#f59e0b', 进行中: '#3b82f6', 已提交: '#8b5cf6', 已完成: '#10b981', 已驳回: '#ef4444', 已跳过: '#94a3b8'
  }
  const taskStatusChartData = computed(() => [
    { name: '待分配', value: taskStatusDistribution.pending },
    { name: '进行中', value: taskStatusDistribution.in_progress },
    { name: '已提交', value: taskStatusDistribution.submitted },
    { name: '已完成', value: taskStatusDistribution.approved },
    { name: '已驳回', value: taskStatusDistribution.rejected },
    { name: '已跳过', value: (taskStatusDistribution as any).skipped }
  ].filter(i => i.value > 0))
  
  const taskStatusChartColors = computed(() => taskStatusChartData.value.map(i => taskStatusColorMap[i.name]))
  const taskStatusBarData = computed(() => taskStatusChartData.value.map(i => i.value))
  const taskStatusLabels = computed(() => taskStatusChartData.value.map(i => i.name))

  onMounted(() => {
    refreshDashboard()
  })
</script>

<style scoped lang="scss">
.project-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-header {
  margin-bottom: 4px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 1. Metrics Grid
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  .metric-card {
    background: #fff;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }

    // Minimalist Styles - Light backgrounds for icons
    &.style-blue :deep(.icon-wrapper) { background: #eff6ff; }
    &.style-green :deep(.icon-wrapper) { background: #ecfdf5; }
    &.style-orange :deep(.icon-wrapper) { background: #fff7ed; }
    &.style-purple :deep(.icon-wrapper) { background: #f5f3ff; }
    
    // Internal text colors
    :deep(.label) {
      color: #6b7280 !important;
      font-weight: 500;
    }
    :deep(.value) {
      color: #1f2937 !important;
    }
    :deep(.description) {
      color: #9ca3af !important;
    }
    :deep(.icon-wrapper) {
      border-radius: 12px;
    }
  }
}

// 2. Charts Grid
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  
  // First Row
  .project-progress {
    grid-column: span 2;
    min-height: 450px; // 确保足够高度
  }
  
  .performance-rank {
    grid-column: span 1;
    min-height: 450px;
  }
  
  // Second Row - auto placement
  .recent-activity {
    grid-column: span 1;
    min-height: 400px;
  }
  
  .quick-actions {
    grid-column: span 1;
    min-height: 400px;
  }
  
  .task-status {
    grid-column: span 1;
    min-height: 400px;
  }
}

.dashboard-card {
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); // 增加轻微阴影
  
  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #f3f4f6;
    flex-shrink: 0;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0; // 防止溢出
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
      
      .icon-box {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        
        &.blue { background: #eff6ff; color: #3b82f6; }
        &.orange { background: #fff7ed; color: #f97316; }
        &.green { background: #ecfdf5; color: #10b981; }
        &.purple { background: #f5f3ff; color: #8b5cf6; }
        &.cyan { background: #ecfeff; color: #06b6d4; }
      }
    }
  }
}

// Specific Card Styles
.project-progress-list {
  overflow-y: auto;
  flex: 1; // 撑满剩余空间
  
  .progress-item {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f3f4f6;
    
    &:last-child { border-bottom: none; margin-bottom: 0; }
    
    .project-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 14px;
      
      .project-name { font-weight: 500; color: #374151; }
      .project-meta { color: #9ca3af; font-size: 12px; }
    }
  }
}

.ranking-list {
  overflow-y: auto;
  flex: 1;
  padding-right: 4px; // 给滚动条留点空间
  
  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
  }
  
  .ranking-item {
    display: flex;
    align-items: center;
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 10px;
    background: #f9fafb;
    transition: all 0.2s;
    
    &:hover { background: #f3f4f6; }
    
    .rank-badge {
      width: 30px;
      text-align: center;
      font-weight: 700;
      font-size: 16px;
      margin-right: 10px;
      
      .number { color: #9ca3af; font-size: 14px; }
    }
    
    .member-avatar { margin-right: 12px; }
    
    .member-info {
      flex: 1;
      .name { font-size: 14px; font-weight: 600; color: #374151; }
      .score { font-size: 12px; color: #6b7280; }
    }
    
    .member-stats {
      text-align: right;
      .stat-val { font-size: 16px; font-weight: 700; color: #3b82f6; }
      .stat-label { font-size: 10px; color: #9ca3af; }
    }
    
    &.rank-1 { background: #fffbeb; border: 1px solid #fcd34d; }
    &.rank-2 { background: #f8fafc; border: 1px solid #e2e8f0; }
    &.rank-3 { background: #fff7ed; border: 1px solid #fdba74; }
  }
}

.task-status-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 20px;
  .status-bar-chart { 
    flex: 1; 
    min-height: 0; // 允许 flex items 收缩
  }
}

.activity-list {
  flex: 1;
  overflow-y: auto;
  padding-top: 10px;
  
  .activity-card-item {
    background: #f9fafb;
    padding: 10px;
    border-radius: 8px;
    
    .activity-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      font-size: 12px;
      
      .user { font-weight: 600; color: #374151; }
      .time { color: #9ca3af; }
    }
    
    .activity-body {
      font-size: 13px;
      color: #4b5563;
      .target { font-weight: 500; color: #3b82f6; }
    }
  }
}

.quick-actions-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
  flex: 1; // 占据空间
  
  .action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    font-weight: 500;
    height: 100%; // 撑满 grid cell
    
    .el-icon { font-size: 24px; margin-bottom: 4px; }
    
    &.primary { background: #eff6ff; color: #3b82f6; &:hover { background: #dbeafe; } }
    &.success { background: #ecfdf5; color: #10b981; &:hover { background: #d1fae5; } }
    &.warning { background: #fff7ed; color: #f97316; &:hover { background: #ffedd5; } }
    &.info { background: #f3f4f6; color: #6b7280; &:hover { background: #e5e7eb; } }
  }
}

.today-stats {
  border-top: 1px dashed #e5e7eb;
  padding-top: 16px;
  display: flex;
  justify-content: space-between;
  flex-shrink: 0; // 防止被挤压
  
  .stat-row {
    text-align: center;
    .label { display: block; font-size: 12px; color: #9ca3af; margin-bottom: 4px; }
    .value { font-size: 18px; font-weight: 700; color: #1f2937; }
    .value.success { color: #10b981; }
    .value.warning { color: #f97316; }
  }
}

.custom-scrollbar {
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
  &::-webkit-scrollbar-track { background: transparent; }
}

// Media Queries for Responsiveness
@media (max-width: 1400px) {
  .charts-grid {
    grid-template-columns: 1fr 1fr; // 2 columns
    
    .project-progress { grid-column: span 2; }
    .performance-rank { grid-column: span 1; }
    .task-status { grid-column: span 1; }
    .recent-activity { grid-column: span 1; }
    .quick-actions { grid-column: span 1; }
  }
}
</style>

