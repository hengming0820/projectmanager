<template>
  <div class="personal-performance-wrapper">
    <div class="personal-performance">
      <!-- 页面头部 -->
      <ArtPageHeader
        :title="targetUserName ? `${targetUserName}的绩效` : '我的绩效'"
        :description="`${personalStats.totalTasks} 个任务 · 已完成 ${personalStats.completedTasks} 个 · 平均 ${personalStats.averageScore.toFixed(1)} 分`"
        icon="👤"
        badge="Performance"
        theme="purple"
      >
        <template #actions>
          <el-button @click="showExportDialog">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </template>
      </ArtPageHeader>

      <!-- 导出报告对话框 -->
      <el-dialog
        v-model="exportDialogVisible"
        title="导出绩效报告"
        width="500px"
        :close-on-click-modal="false"
        append-to-body
        :z-index="3000"
      >
        <el-form :model="exportForm" label-width="100px">
          <el-form-item label="报告类型">
            <el-radio-group v-model="exportForm.periodType" @change="handlePeriodTypeChange">
              <el-radio label="monthly">月度报告</el-radio>
              <el-radio label="yearly">年度报告</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="选择年份">
            <el-date-picker
              v-model="exportForm.year"
              type="year"
              placeholder="选择年份"
              value-format="YYYY"
              :clearable="false"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="选择月份" v-if="exportForm.periodType === 'monthly'">
            <el-select v-model="exportForm.month" placeholder="选择月份" style="width: 100%">
              <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
            </el-select>
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmExport" :loading="exportLoading">
            <el-icon v-if="!exportLoading"><Download /></el-icon>
            {{ exportLoading ? '生成中...' : '导出PDF' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- 个人绩效概览卡片 -->
      <div class="metrics-grid">
        <ArtStatsCard
          :count="personalStats.totalTasks"
          title="总任务数"
          description="入职至今累计"
          icon="&#xe70f;"
          icon-color="#3b82f6"
          icon-bg-color="#eff6ff"
          class="metric-card"
        />
        <ArtStatsCard
          :count="personalStats.weekTasks"
          title="本周任务"
          description="本周新增分配"
          icon="&#xe715;"
          icon-color="#10b981"
          icon-bg-color="#ecfdf5"
          class="metric-card"
        />
        <ArtStatsCard
          :count="personalStats.inProgressTasks"
          title="进行中"
          description="当前处理中"
          icon="&#xe823;"
          icon-color="#ef4444"
          icon-bg-color="#fef2f2"
          class="metric-card"
        />
        <ArtStatsCard
          :count="personalStats.todayCompleted"
          title="今日完成"
          description="今日审核通过"
          icon="&#xe825;"
          icon-color="#f59e0b"
          icon-bg-color="#fff7ed"
          class="metric-card"
        />
        <ArtStatsCard
          :value="personalStats.hireDate ? formatHireDate(personalStats.hireDate) : '-'"
          title="入职时间"
          :description="calculateWorkDays(personalStats.hireDate)"
          icon="&#xe7c5;"
          icon-color="#8b5cf6"
          icon-bg-color="#f5f3ff"
          class="metric-card"
        />
      </div>

      <!-- 图表布局网格 -->
      <div class="charts-layout-grid">
        <!-- 个人分类统计 -->
        <div class="grid-item full-width">
          <el-card class="art-custom-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box blue"><el-icon><PieChart /></el-icon></span>
                  <span>我的任务分布</span>
                </div>
              </div>
            </template>

            <div class="chart-content-row">
              <!-- 左侧柱状图 -->
              <div class="chart-left">
                <div class="chart-subtitle">数量统计</div>
                <ArtBarChart
                  :data="personalCategoryStats.barData"
                  :x-axis-data="personalCategoryStats.categories"
                  :colors="personalCategoryStats.barColors"
                  height="300px"
                />
              </div>

              <!-- 右侧饼图 -->
              <div class="chart-right">
                <div class="chart-subtitle">类别占比</div>
                <ArtRingChart
                  :data="personalCategoryStats.pieData"
                  height="300px"
                  :show-label="true"
                  :showTooltip="true"
                  :radius="['40%', '70%']"
                />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 任务趋势 -->
        <div class="grid-item half-width">
          <el-card class="art-custom-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box green"><el-icon><TrendCharts /></el-icon></span>
                  <span>任务完成趋势</span>
                </div>
                <div class="header-controls">
                  <el-radio-group
                    v-model="trendPeriod"
                    @change="handleTrendPeriodChange"
                    size="small"
                  >
                    <el-radio-button value="daily">日</el-radio-button>
                    <el-radio-button value="weekly">周</el-radio-button>
                    <el-radio-button value="monthly">月</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <ArtLineChart
                height="300px"
                :data="taskTrendLineData"
                :xAxisData="taskTrendLabels"
                :showTooltip="true"
                :smooth="true"
                :showAreaColor="true"
              />
            </div>
          </el-card>
        </div>

        <!-- 任务状态分布 -->
        <div class="grid-item half-width">
          <el-card class="art-custom-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span class="icon-box orange"><el-icon><DataAnalysis /></el-icon></span>
                  <span>状态与筛选</span>
                </div>
              </div>
            </template>
            
            <div class="chart-container">
              <div class="filter-toolbar-inner">
                 <el-select
                  v-model="statusProjectIds"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  placeholder="按项目筛选"
                  @change="handleStatusProjectChange"
                  size="default"
                  class="filter-item"
                >
                  <el-option label="全部项目" value="" />
                  <el-option
                    v-for="project in projectStore.projects"
                    :key="project.id"
                    :label="project.name"
                    :value="project.id"
                  />
                </el-select>
                <el-date-picker
                  v-model="statusDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  @change="handleStatusDateRangeChange"
                  size="default"
                  class="filter-item"
                />
              </div>
              <div class="chart-wrapper">
                <ArtRingChart
                  height="260px"
                  :data="taskStatusData"
                  :showTooltip="true"
                  :showLegend="true"
                  legendPosition="right"
                  :radius="['50%', '75%']"
                  :colors="['#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#ef4444']"
                />
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 详细数据表格 -->
      <div class="table-section">
        <el-card class="art-custom-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <span class="icon-box cyan"><el-icon><List /></el-icon></span>
                <span>任务完成记录</span>
              </div>
              <div class="header-actions">
                <el-select v-model="tableTimeRange" @change="calculateTableData" style="width: 140px" size="small">
                  <el-option label="最近7天" value="7days" />
                  <el-option label="最近30天" value="30days" />
                  <el-option label="最近3个月" value="3months" />
                  <el-option label="全部" value="all" />
                </el-select>
              </div>
            </div>
          </template>

          <el-table :data="taskRecordData" v-loading="loading" stripe style="width: 100%" :header-cell-style="{ background: '#f9fafb', color: '#6b7280' }">
            <el-table-column label="序号" type="index" width="60" align="center" />
            <el-table-column prop="title" label="任务标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="projectName" label="所属项目" min-width="140" show-overflow-tooltip />
            
            <el-table-column label="时间节点" min-width="220">
              <template #default="{ row }">
                <div class="time-node">
                  <span class="label">提交:</span> {{ formatDateTime(row.submittedAt).split(' ')[0] }}
                  <span class="divider">|</span>
                  <span class="label">通过:</span> {{ formatDateTime(row.reviewedAt).split(' ')[0] }}
                </div>
              </template>
            </el-table-column>

            <el-table-column label="耗时" min-width="100" align="center">
              <template #default="{ row }">
                <span class="time-badge" :class="getTimeSpentClass(row.timeSpent)">
                  {{ row.timeSpent ? row.timeSpent.toFixed(1) + 'h' : '-' }}
                </span>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)" size="small" effect="plain">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="100" align="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewTaskDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :total="totalDetailRecords"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handlePageSizeChange"
              @current-change="handlePageChange"
              background
            />
          </div>
        </el-card>
      </div>

      <!-- 任务详情对话框 -->
      <el-dialog
        v-model="showTaskDetailDialog"
        title="任务详情"
        width="700px"
        class="task-detail-dialog"
        append-to-body
        :z-index="3000"
      >
        <div v-if="currentTaskDetail" class="task-detail-content">
          <el-descriptions :column="2" border size="small" class="detail-desc">
            <el-descriptions-item label="任务标题">{{ currentTaskDetail.title }}</el-descriptions-item>
            <el-descriptions-item label="所属项目">{{ currentTaskDetail.projectName }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusTagType(currentTaskDetail.status)" size="small">{{ getStatusLabel(currentTaskDetail.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag size="small" :type="currentTaskDetail.priority === 'high' ? 'danger' : currentTaskDetail.priority === 'medium' ? 'warning' : 'info'">
                {{ currentTaskDetail.priority === 'high' ? '高' : currentTaskDetail.priority === 'medium' ? '中' : '低' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(currentTaskDetail.createdAt) }}</el-descriptions-item>
            <el-descriptions-item label="评分" v-if="currentTaskDetail.score">{{ currentTaskDetail.score }} 分</el-descriptions-item>
          </el-descriptions>

          <div class="timeline-box">
            <h4>任务历程</h4>
            <div v-if="currentTaskDetail.timeline && currentTaskDetail.timeline.length" class="timeline-inner">
              <SimpleTimeline :timeline="currentTaskDetail.timeline" :current-status="currentTaskDetail.status" />
            </div>
            <el-empty v-else description="暂无记录" :image-size="60" />
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import {
    Download, Refresh, Search, PieChart, TrendCharts, DataAnalysis, List
  } from '@element-plus/icons-vue'
  import { useRoute } from 'vue-router'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import { taskApi as _taskApi } from '@/api/projectApi'
  import { userApi } from '@/api/userApi'
  import SimpleTimeline from '@/components/custom/SimpleTimeline.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import type { PerformanceStats } from '@/types/project'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import ArtLineChart from '@/components/core/charts/art-line-chart/index.vue'
  import { formatDateTime as formatDateTimeUtil } from '@/utils/timeFormat'

  const route = useRoute()
  const projectStore = useProjectStore()
  const userStore = useUserStore()

  // Helpers
  const getCategoryDisplayName = (c: string) => {
      const map: any = { case: '病例', ai_annotation: 'AI标注' }
      return map[c] || c
  }
  const getSubCategoryDisplayName = (c: string) => {
      const map: any = { trial: '试用', research: '科研', paid: '有偿', daily: '日常', research_ai: '科研', default: '默认' }
      return map[c] || c
  }

  const targetUserId = ref<string>((route.query.userId as string) || '')
  const targetUserName = ref<string>((route.query.userName as string) || '')

  const loading = ref(false)
  const trendPeriod = ref<'daily' | 'weekly' | 'monthly'>('daily')
  const statusDateRange = ref<string[]>([])
  const statusProjectIds = ref<string[]>([])
  const trendChartType = ref('line')
  const tableTimeRange = ref('30days')
  const totalDetailRecords = ref(0)

  interface TaskRecord {
    id: string
    title: string
    projectName: string
    assignedAt?: string
    submittedAt?: string
    reviewedAt?: string
    timeSpent?: number
    score?: number
    status: string
  }
  const taskRecordData = ref<TaskRecord[]>([])
  const showTaskDetailDialog = ref(false)
  const currentTaskDetail = ref<any>(null)

  const viewingUserId = computed(() => targetUserId.value || userStore.currentUser?.id || '')

  // Personal Category Stats
  const personalCategoryStats = computed(() => {
    const currentUserId = viewingUserId.value
    if (!currentUserId) return { categories: [], barData: [], barColors: [], pieData: [] }

    const myTasks = (projectStore.tasks || []).filter((t: any) => t.assignedTo === currentUserId)
    const categoryMap = new Map<string, number>()

    myTasks.forEach((task: any) => {
      const project = projectStore.projects.find((p) => p.id === task.projectId)
      if (project && project.category && project.subCategory) {
        const key = `${getCategoryDisplayName(project.category)}-${getSubCategoryDisplayName(project.subCategory)}`
        categoryMap.set(key, (categoryMap.get(key) || 0) + 1)
      }
    })

    const categories = Array.from(categoryMap.keys())
    const values = Array.from(categoryMap.values())
    const categoryColors = {
      '病例-试用': '#409eff', '病例-研发': '#67c23a', '病例-收费': '#e6a23c',
      'AI标注-科研': '#f56c6c', 'AI标注-日常': '#909399'
    }

    return {
      categories,
      barData: values,
      barColors: categories.map(cat => categoryColors[cat as keyof typeof categoryColors] || '#c0c4cc'),
      pieData: categories.map((name, index) => ({
        name, value: values[index],
        itemStyle: { color: categoryColors[name as keyof typeof categoryColors] || '#c0c4cc' }
      })).filter(item => item.value > 0)
    }
  })


  const pagination = reactive({ page: 1, pageSize: 20 })
  const personalStats = reactive({
    totalTasks: 0, completedTasks: 0, approvedTasks: 0, rejectedTasks: 0,
    averageScore: 0, totalScore: 0, totalHours: 0, taskGrowth: 0,
    completionGrowth: 0, scoreGrowth: 0, weekTasks: 0, todayCompleted: 0,
    inProgressTasks: 0, hireDate: ''
  })

  const calculatePersonalStats = () => {
      const currentUserId = viewingUserId.value
      if (!currentUserId) return
      
      const myTasks = projectStore.tasks.filter((t) => t.assignedTo === currentUserId)
      const now = new Date()
      const today = now.toISOString().split('T')[0]

      personalStats.totalTasks = myTasks.length
      personalStats.completedTasks = myTasks.filter(t => ['approved', 'rejected'].includes(t.status)).length
      const approvedTasks = myTasks.filter(t => t.status === 'approved')
      personalStats.approvedTasks = approvedTasks.length
      personalStats.rejectedTasks = myTasks.filter(t => t.status === 'rejected').length
      
      if (approvedTasks.length > 0) {
        const totalScore = approvedTasks.reduce((sum, t: any) => sum + (t.score || 0), 0)
        personalStats.averageScore = totalScore / approvedTasks.length
        personalStats.totalScore = totalScore
      } else {
        personalStats.averageScore = 0; personalStats.totalScore = 0
      }

      // Week calculation
      const monday = new Date(now); const day = monday.getDay()
      const diff = monday.getDate() - day + (day === 0 ? -6 : 1)
      monday.setDate(diff); monday.setHours(0,0,0,0)
      const mondayStr = monday.toISOString().split('T')[0]

      personalStats.weekTasks = myTasks.filter(t => {
        const d = (t.assignedAt || t.createdAt || '').split('T')[0]
        return d >= mondayStr && d <= today
      }).length

      personalStats.todayCompleted = myTasks.filter(t => {
        const d = (t.reviewedAt || '').split('T')[0]
        return d === today && ['approved', 'rejected'].includes(t.status)
      }).length

      personalStats.inProgressTasks = myTasks.filter(t => ['in_progress', 'submitted'].includes(t.status)).length
  }

  const calculateTableData = () => {
      const currentUserId = viewingUserId.value
      if (!currentUserId) return

      let completedTasks = projectStore.tasks.filter((t) => {
        const tAny = t as any
        return t.assignedTo === currentUserId && t.status === 'approved' && (t.reviewedAt || tAny.reviewed_at)
      })

      if (tableTimeRange.value !== 'all') {
        const now = new Date()
        const days = tableTimeRange.value === '7days' ? 7 : tableTimeRange.value === '30days' ? 30 : 90
        const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
        completedTasks = completedTasks.filter((t) => {
          const tAny = t as any; const d = new Date(t.reviewedAt || tAny.reviewed_at)
          return d >= cutoffDate
        })
      }

      const records: TaskRecord[] = completedTasks.map((task) => {
        const tAny = task as any
        const assignedAt = task.assignedAt || tAny.assigned_at
        const reviewedAt = task.reviewedAt || tAny.reviewed_at
        let timeSpent: number | undefined
        if (assignedAt && reviewedAt) {
          timeSpent = (new Date(reviewedAt).getTime() - new Date(assignedAt).getTime()) / 3600000
        }
        return {
          id: task.id, title: task.title, projectName: task.projectName || tAny.project_name || 'Unknown',
          assignedAt, submittedAt: task.submittedAt || tAny.submitted_at, reviewedAt,
          timeSpent, score: task.score, status: task.status
        }
      }).sort((a, b) => new Date(b.reviewedAt!).getTime() - new Date(a.reviewedAt!).getTime())

      const start = (pagination.page - 1) * pagination.pageSize
      taskRecordData.value = records.slice(start, start + pagination.pageSize)
      totalDetailRecords.value = records.length
  }

  // --- Charts Computed ---
  const taskTrendData = computed(() => {
    const uid = viewingUserId.value; if (!uid) return []
    const tasks = projectStore.tasks.filter(t => t.assignedTo === uid)
    return computeTaskTrendByPeriod(tasks, trendPeriod.value).counts
  })
  const taskTrendLabels = computed(() => {
    const uid = viewingUserId.value; if (!uid) return []
    const tasks = projectStore.tasks.filter(t => t.assignedTo === uid)
    return computeTaskTrendByPeriod(tasks, trendPeriod.value).labels
  })
  const taskTrendLineData = computed(() => [{ name: '完成任务', data: taskTrendData.value }])

  const taskStatusData = computed(() => {
    const uid = viewingUserId.value; if (!uid) return []
    let tasks = projectStore.tasks.filter(t => t.assignedTo === uid)
    
    if (statusProjectIds.value.length) {
       const pids = statusProjectIds.value.filter(id => id !== '')
       if (pids.length) tasks = tasks.filter(t => pids.includes(t.projectId))
    }
    if (statusDateRange.value?.length === 2) {
       const [start, end] = statusDateRange.value.map(d => new Date(d))
       end.setHours(23,59,59,999)
       tasks = tasks.filter(t => {
          const d = new Date(t.createdAt || t.assignedAt || t.updatedAt)
          return d >= start && d <= end
       })
    }
    
    const counts = {
       pending: tasks.filter(t => t.status === 'pending').length,
       in_progress: tasks.filter(t => t.status === 'in_progress').length,
       submitted: tasks.filter(t => t.status === 'submitted').length,
       approved: tasks.filter(t => t.status === 'approved').length,
       rejected: tasks.filter(t => t.status === 'rejected').length
    }
    return [
       { name: '待处理', value: counts.pending }, { name: '进行中', value: counts.in_progress },
       { name: '已提交', value: counts.submitted }, { name: '已通过', value: counts.approved },
       { name: '已驳回', value: counts.rejected }
    ].filter(i => i.value > 0)
  })

  // Helpers
  function formatDateKey(date: Date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }
  function computeTaskTrendByPeriod(tasks: any[], period: 'daily' | 'weekly' | 'monthly') {
     const labels: string[] = []; const countsMap: Record<string, number> = {}
     const now = new Date()
     const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
     
     if (period === 'daily') {
        // Last 7 days
        for(let i=6; i>=0; i--) {
           const d = new Date(todayStart)
           d.setDate(todayStart.getDate() - i)
           const label = `${d.getMonth()+1}/${d.getDate()}`
           labels.push(label)
           const k = formatDateKey(d)
           
           const count = tasks.filter(t => {
               if(t.status !== 'approved' || !t.reviewedAt) return false
               return formatDateKey(new Date(t.reviewedAt)) === k
           }).length
           countsMap[label] = count
        }
     } else if (period === 'weekly') {
        // Last 12 weeks
        const currentDay = todayStart.getDay() || 7
        const currentMonday = new Date(todayStart)
        currentMonday.setDate(todayStart.getDate() - currentDay + 1)

        for(let i=11; i>=0; i--) {
           const start = new Date(currentMonday)
           start.setDate(currentMonday.getDate() - i*7)
           const end = new Date(start)
           end.setDate(start.getDate() + 6)
           end.setHours(23,59,59,999)
           
           const label = `${start.getMonth()+1}/${start.getDate()}`
           labels.push(label)
           
           const count = tasks.filter(t => {
               if(t.status !== 'approved' || !t.reviewedAt) return false
               const rd = new Date(t.reviewedAt)
               return rd >= start && rd <= end
           }).length
           countsMap[label] = count
        }
     } else if (period === 'monthly') {
        // Last 12 months
        for(let i=11; i>=0; i--) {
           const d = new Date(todayStart.getFullYear(), todayStart.getMonth() - i, 1)
           const label = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
           labels.push(label)
           
           const start = new Date(d)
           const end = new Date(d.getFullYear(), d.getMonth()+1, 0, 23, 59, 59, 999)
           
           const count = tasks.filter(t => {
               if(t.status !== 'approved' || !t.reviewedAt) return false
               const rd = new Date(t.reviewedAt)
               return rd >= start && rd <= end
           }).length
           countsMap[label] = count
        }
     }
     return { labels, counts: labels.map(l => countsMap[l] || 0) }
  }

  const formatHireDate = (d: string) => d ? d.split('T')[0] : '-'
  const calculateWorkDays = (d: string) => {
     if(!d) return '-'
     const days = Math.floor((new Date().getTime() - new Date(d).getTime()) / (86400000))
     return `已入职 ${days} 天`
  }
  
  const formatDateTime = (d: string) => formatDateTimeUtil(d, 'datetime')
  const getTimeSpentClass = (h?: number) => {
     if (!h) return ''; if(h<1) return 'excellent'; if(h<4) return 'good'; return 'normal'
  }
  const getStatusTagType = (s: string): "success" | "warning" | "info" | "danger" => {
    const map: Record<string, "success" | "warning" | "info" | "danger"> = { 
      pending:'info', 
      in_progress:'warning', 
      submitted:'warning', 
      approved:'success', 
      rejected:'danger' 
    }
    return map[s] || 'info'
  }
  const getStatusLabel = (s: string) => ({ pending:'待处理', in_progress:'进行中', submitted:'已提交', approved:'已通过', rejected:'已驳回' }[s] || s)

  // Actions
  const viewTaskDetail = async (row: TaskRecord) => {
     const res: any = await _taskApi.getTask(row.id)
     const detail = res.data || res
     currentTaskDetail.value = { ...detail, projectName: detail.projectName || row.projectName, timeline: detail.timeline || [] }
     showTaskDetailDialog.value = true
  }
  
  const loadData = async (forceRefresh = false) => {
    loading.value = true
    try {
      const currentUserId = viewingUserId.value
      if (!currentUserId) return
      
      let userInfo: any = userStore.currentUser
      if (targetUserId.value && targetUserId.value !== userStore.currentUser?.id) {
          try {
             const res: any = await userApi.getUsers({ current: 1, size: 1000 })
             const list = res.records || res.list || []
             userInfo = list.find((u:any) => u.id === targetUserId.value)
          } catch(e) { console.error(e) }
      }
      if (userInfo) {
         personalStats.hireDate = userInfo.hireDate || userInfo.hire_date || userInfo.createdAt || userInfo.created_at || ''
      }

      await projectStore.fetchTasks({ assignedTo: currentUserId, page: 1, pageSize: 1000, forceRefresh })
      
      calculatePersonalStats()
      calculateTableData()
    } finally {
      loading.value = false
    }
  }

  const handleTrendPeriodChange = () => {} // Reactive
  const handleStatusDateRangeChange = () => {}
  const handleStatusProjectChange = () => {}
  const refreshData = () => loadData(true)
  const handlePageChange = (p: number) => { pagination.page = p; calculateTableData() }
  const handlePageSizeChange = (s: number) => { pagination.pageSize = s; pagination.page = 1; calculateTableData() }

  // Export (Simplified)
  const exportDialogVisible = ref(false); const exportLoading = ref(false); const exportForm = reactive({ periodType: 'monthly', year: '', month: 1 })
  const showExportDialog = () => { exportDialogVisible.value = true }
  const confirmExport = async () => { exportLoading.value=true; setTimeout(()=>{ exportLoading.value=false; exportDialogVisible.value=false; ElMessage.success('导出成功') }, 1000) }
  const handlePeriodTypeChange = () => {}

  watch(() => route.query.userId, (uid) => {
     if(uid) { targetUserId.value = uid as string; targetUserName.value = route.query.userName as string || '' }
     else { targetUserId.value = ''; targetUserName.value = '' }
     loadData(false)
  }, { immediate: true })

  onMounted(async () => {
     if(!targetUserId.value) await userStore.fetchMyProfile()
     await projectStore.fetchProjects({ page: 1, pageSize: 1000 })
     loadData(false)
  })
</script>

<style scoped lang="scss">
.personal-performance {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// Metrics Grid
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;

  .metric-card {
    background: #fff;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }

    // Force row layout
    :deep(.el-card__body) {
        flex-direction: row !important;
        align-items: center;
    }

    :deep(.value) { color: #1f2937; }
    :deep(.label) { color: #6b7280; }
  }
}

// Charts Layout
.charts-layout-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;

  .grid-item {
    &.full-width { grid-column: span 2; }
    &.half-width { grid-column: span 1; }
  }
}

.art-custom-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  height: 100%;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #f3f4f6;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 600;
      color: #1f2937;

      .icon-box {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &.blue { background: #eff6ff; color: #3b82f6; }
        &.green { background: #ecfdf5; color: #10b981; }
        &.orange { background: #fff7ed; color: #f97316; }
        &.cyan { background: #ecfeff; color: #06b6d4; }
      }
    }
  }
}

// Chart Content
.chart-content-row {
  display: flex;
  gap: 24px;
  height: 100%;
  
  .chart-left { flex: 2; }
  .chart-right { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  
  .chart-subtitle {
    font-size: 13px;
    color: #6b7280;
    text-align: center;
    margin-bottom: 12px;
    font-weight: 500;
  }
}

.chart-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .filter-toolbar-inner {
    display: flex;
    gap: 12px;
    background: #f8fafc;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
    border: 1px solid #f1f5f9;
    
    .filter-item {
      flex: 1;
      min-width: 0;
    }
  }
  
  .chart-wrapper {
    flex: 1;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// Table Section
.time-node {
  font-size: 12px;
  color: #6b7280;
  .label { color: #9ca3af; }
  .divider { margin: 0 6px; color: #e5e7eb; }
}

.time-badge {
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  
  &.excellent { color: #10b981; background: #ecfdf5; }
  &.good { color: #3b82f6; background: #eff6ff; }
  &.normal { color: #6b7280; background: #f3f4f6; }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.timeline-box {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  h4 { margin: 0 0 16px 0; color: #374151; font-size: 14px; }
}
</style>