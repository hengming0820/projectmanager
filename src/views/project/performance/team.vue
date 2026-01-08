<template>
  <div class="team-performance">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="团队绩效"
      :description="`${teamOverview.totalMembers} 名成员 · ${teamOverview.totalTasks} 个任务 · 完成率 ${teamOverview.totalTasks > 0 ? ((teamOverview.completedTasks / teamOverview.totalTasks) * 100).toFixed(1) : 0}%`"
      icon="📊"
      badge="Performance"
      theme="red"
    >
      <template #actions>
        <el-button @click="exportPerformance">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 筛选工具栏 -->
    <div class="filter-toolbar card-panel">
      <div class="left-filters">
        <span class="filter-label">统计周期</span>
        <el-radio-group
          v-model="period"
          @change="handlePeriodChange"
          size="default"
          class="custom-radio-group"
        >
          <el-radio-button value="day">当日</el-radio-button>
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
          <el-radio-button value="year">本年</el-radio-button>
        </el-radio-group>
        <el-divider direction="vertical" />
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="fetchPerformanceData"
          size="default"
          class="date-picker-custom"
          :prefix-icon="Calendar"
        />
      </div>
      <div class="right-filters">
        <el-select
          v-model="projectFilter"
          placeholder="按项目筛选"
          clearable
          @change="handleProjectFilterChange"
          style="width: 200px"
          size="default"
        >
          <el-option label="全部项目" value="" />
          <el-option
            v-for="project in activeProjects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </div>
    </div>

    <!-- 核心指标网格 -->
    <div class="metrics-grid">
      <ArtStatsCard
        :count="teamOverview.totalMembers"
        title="团队人数"
        description="当前活跃成员"
        icon="&#xe7c3;"
        icon-color="#3b82f6"
        icon-bg-color="#eff6ff"
        class="metric-card"
      />
      <ArtStatsCard
        :count="teamOverview.totalTasks"
        title="总任务数"
        description="统计周期内任务"
        icon="&#xe70f;"
        icon-color="#8b5cf6"
        icon-bg-color="#f5f3ff"
        class="metric-card"
      />
      <ArtStatsCard
        :count="teamOverview.completedTasks"
        title="已完成"
        description="审核通过任务"
        icon="&#xe7c1;"
        icon-color="#10b981"
        icon-bg-color="#ecfdf5"
        class="metric-card"
      />
      <ArtStatsCard
        :count="teamOverview.skippedTasks"
        title="已跳过"
        description="标记为跳过任务"
        icon="&#xe7ba;"
        icon-color="#f97316"
        icon-bg-color="#fff7ed"
        class="metric-card"
      />
    </div>

    <!-- 主内容网格 -->
    <div class="charts-layout-grid">
      <!-- 分类统计图表 -->
      <div class="grid-item full-width">
        <el-card class="art-custom-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <span class="icon-box blue"><el-icon><PieChart /></el-icon></span>
                <span>项目分类统计（已完成任务）</span>
              </div>
            </div>
          </template>

          <div class="category-chart-container dual-chart">
            <!-- 左侧柱状图 -->
            <div class="chart-left">
              <div class="chart-subtitle">分布概览</div>
              <ArtBarChart
                :data="categoryTaskStats.barData"
                :x-axis-data="categoryTaskStats.categories"
                :colors="categoryTaskStats.barColors"
                height="300px"
                :barMaxWidth="50"
              />
            </div>

            <!-- 右侧饼图 -->
            <div class="chart-right">
              <div class="chart-subtitle">占比分析</div>
              <ArtRingChart 
                :data="categoryTaskStats.pieData" 
                height="300px" 
                :show-label="true"
                :radius="['40%', '70%']" 
              />
            </div>
          </div>
        </el-card>
      </div>

      <!-- 绩效排行榜 -->
      <div class="grid-item half-width">
        <el-card class="art-custom-card ranking-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <span class="icon-box orange"><el-icon><Trophy /></el-icon></span>
                <span>绩效排行榜</span>
              </div>
              <el-select v-model="rankingCriteria" @change="updateRanking" size="small" style="width: 130px">
                <el-option label="任务完成数" value="completedTasks" />
                <el-option label="平均评分" value="averageScore" />
                <el-option label="总工时" value="totalHours" />
                <el-option label="总积分" value="totalScore" />
              </el-select>
            </div>
          </template>

          <div class="ranking-list custom-scrollbar">
            <div
              v-for="(member, index) in topPerformers"
              :key="member.userId"
              class="ranking-item"
              :class="`rank-${index + 1}`"
            >
              <div class="rank-badge">
                <span v-if="index < 3" class="medal">{{ ['🥇', '🥈', '🥉'][index] }}</span>
                <span v-else class="number">{{ index + 1 }}</span>
              </div>
              <div class="member-avatar">
                <el-avatar :size="36" :src="member.avatar" style="background: #eff6ff; color: #3b82f6; font-weight: 600;">
                  {{ (member.realName || member.username || '?')[0] }}
                </el-avatar>
              </div>
              <div class="member-info">
                <div class="member-name">{{ member.realName || member.username }}</div>
                <div class="member-sub">@{{ member.username }}</div>
              </div>
              <div class="member-stats">
                <div class="stat-val">{{ getRankingValue(member, rankingCriteria) }}</div>
                <div class="stat-label">{{ getRankingLabel(member, rankingCriteria, true) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 标注员完成数量 -->
      <div class="grid-item half-width">
        <el-card class="art-custom-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <span class="icon-box green"><el-icon><DataAnalysis /></el-icon></span>
                <span>标注员完成详情</span>
              </div>
            </div>
          </template>
          <div class="chart-container" style="overflow-x: auto; overflow-y: hidden;">
            <ArtBarChart
              height="380px"
              :data="annotatorStackedData"
              :xAxisData="annotatorNames"
              :colors="annotatorChartColors"
              :showTooltip="true"
              :showLegend="true"
              :stack="true"
              barWidth="auto"
              :barMaxWidth="40"
              barGap="20%"
              barCategoryGap="30%"
              :legend="annotatorChartLegend"
              :style="{ minWidth: `${Math.max(600, annotatorNames.length * 80)}px` }"
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- 详细绩效表格 -->
    <div class="table-section">
      <el-card class="art-custom-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <span class="icon-box cyan"><el-icon><List /></el-icon></span>
              <span>详细绩效数据</span>
            </div>
            <div class="header-actions">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索成员"
                :prefix-icon="Search"
                style="width: 200px"
                clearable
                @input="handleSearch"
              />
            </div>
          </div>
        </template>

        <el-table
          v-loading="loading"
          :data="filteredPerformanceData"
          :header-cell-style="{ background: '#f9fafb', color: '#6b7280', fontWeight: '600' }"
          style="width: 100%"
          :default-sort="{ prop: 'completedTasks', order: 'descending' }"
        >
          <el-table-column prop="realName" label="成员" min-width="160">
            <template #default="{ row }">
              <div class="member-cell">
                <el-avatar :size="32" :src="row.avatar" style="background: #eff6ff; color: #3b82f6; font-weight: 600;">
                  {{ (row.realName || '未知').slice(0, 1) }}
                </el-avatar>
                <div class="member-info">
                  <div class="member-name">{{ row.realName || '未知' }}</div>
                  <div class="member-username">@{{ row.username }}</div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="totalTasks" label="总任务" min-width="100" sortable align="center" />
          <el-table-column prop="completedTasks" label="已完成" min-width="100" sortable align="center">
             <template #default="{ row }"><span class="text-green">{{ row.completedTasks }}</span></template>
          </el-table-column>
          <el-table-column prop="approvedTasks" label="已通过" min-width="100" sortable align="center" />
          <el-table-column prop="rejectedTasks" label="已驳回" min-width="100" sortable align="center">
             <template #default="{ row }"><span class="text-red">{{ row.rejectedTasks }}</span></template>
          </el-table-column>

          <el-table-column label="完成率" min-width="160" sortable :sort-method="sortByCompletionRate">
            <template #default="{ row }">
              <div class="completion-rate">
                <span class="rate-text">{{ getCompletionRate(row) }}%</span>
                <el-progress :percentage="getCompletionRate(row)" :show-text="false" :stroke-width="6" :color="getProgressColorByValue(getCompletionRate(row))" />
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="averageScore" label="评分" min-width="140" sortable>
            <template #default="{ row }">
              <el-rate
                v-model="row.averageScore"
                disabled
                show-score
                text-color="#f97316"
                score-template="{value}"
                size="small"
              />
            </template>
          </el-table-column>

          <el-table-column prop="totalScore" label="积分" min-width="100" sortable align="center">
            <template #default="{ row }">
              <span class="score-tag">{{ row.totalScore }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" min-width="160" align="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewMemberDetail(row)">详情</el-button>
              <el-button link type="info" size="small" @click="viewMemberTrend(row)">趋势</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="performanceData.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
            background
          />
        </div>
      </el-card>
    </div>

    <!-- 成员详情对话框 (保持原有逻辑，仅美化样式) -->
    <el-dialog
      v-model="showMemberDialog"
      :title="`${selectedMember?.realName} - 绩效详情`"
      width="800px"
      class="member-detail-dialog"
      append-to-body
      :z-index="3000"
    >
      <div v-if="selectedMember" class="member-detail">
        <!-- 基本信息卡片 -->
        <div class="detail-header">
           <div class="user-profile">
             <el-avatar :size="64" style="background: #eff6ff; color: #3b82f6; font-size: 24px;">{{ (selectedMember.realName || '?')[0] }}</el-avatar>
             <div class="user-text">
               <h3>{{ selectedMember.realName }}</h3>
               <p>@{{ selectedMember.username }}</p>
             </div>
           </div>
           <div class="user-stats-row">
             <div class="stat-box">
               <span class="label">完成率</span>
               <span class="value">{{ getCompletionRate(selectedMember) }}%</span>
             </div>
             <div class="stat-box">
               <span class="label">平均分</span>
               <span class="value warning">{{ selectedMember.averageScore.toFixed(1) }}</span>
             </div>
             <div class="stat-box">
               <span class="label">总积分</span>
               <span class="value primary">{{ selectedMember.totalScore }}</span>
             </div>
           </div>
        </div>

        <!-- 绩效图表 -->
        <div class="member-charts-grid">
            <div class="chart-box">
                <div class="box-header">
                  <h4>任务趋势</h4>
                  <el-radio-group v-model="memberTrendRange" size="small">
                    <el-radio-button value="7d">7天</el-radio-button>
                    <el-radio-button value="15d">15天</el-radio-button>
                  </el-radio-group>
                </div>
                <ArtLineChart
                  height="240px"
                  :data="memberTaskTrendData"
                  :xAxisData="memberTaskTrendLabels"
                  :showTooltip="true"
                  :smooth="true"
                />
            </div>
            <div class="chart-box">
                <div class="box-header"><h4>任务分布</h4></div>
                <ArtRingChart
                  height="240px"
                  :data="memberCategoryTaskData.pieData"
                  :showTooltip="true"
                  :radius="['40%', '60%']"
                />
            </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showMemberDialog = false">关闭</el-button>
        <el-button type="primary" @click="navigateToPersonalPage">查看完整绩效</el-button>
      </template>
    </el-dialog>

    <!-- 导出报告对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出团队绩效报告" width="400px" append-to-body :z-index="3000">
      <el-form label-position="top">
        <el-form-item label="报告类型">
          <el-radio-group v-model="exportForm.periodType" class="w-full">
            <el-radio-button value="monthly">月度报告</el-radio-button>
            <el-radio-button value="yearly">年度报告</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
             <el-form-item label="年份">
              <el-select v-model="exportForm.year" style="width: 100%">
                <el-option v-for="year in [2023, 2024, 2025]" :key="year" :label="`${year}年`" :value="year.toString()" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="exportForm.periodType === 'monthly'">
             <el-form-item label="月份">
              <el-select v-model="exportForm.month" style="width: 100%">
                <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExport" :loading="exportLoading">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  // Imports
  import { ref, reactive, computed, onMounted, onActivated, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import {
    Download, Refresh, Search, Calendar, PieChart,
    Trophy, DataAnalysis, List
  } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import type { PerformanceStats } from '@/types/project'
  
  // Components
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import ArtLineChart from '@/components/core/charts/art-line-chart/index.vue'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'

  const router = useRouter()
  const projectStore = useProjectStore()
  const userStore = useUserStore()

  // --- Data & Refs ---
  const loading = ref(false)
  const period = ref<'day' | 'week' | 'month' | 'year'>('week') // Default week
  const dateRange = ref<string[]>([])
  const rankingCriteria = ref('completedTasks')
  const searchKeyword = ref('')
  const categoryFilter = ref('')
  const projectFilter = ref('')
  const showMemberDialog = ref(false)
  const selectedMember = ref<PerformanceStats | null>(null)
  const memberTrendRange = ref<'7d' | '15d' | '3m'>('7d')
  const memberCategoryChartType = ref('bar')
  const performanceData = ref<PerformanceStats[]>([])
  
  const pagination = reactive({ page: 1, pageSize: 20 })
  const exportDialogVisible = ref(false)
  const exportLoading = ref(false)
  const exportForm = reactive({
    periodType: 'monthly' as 'monthly' | 'yearly',
    year: new Date().getFullYear().toString(),
    month: new Date().getMonth() + 1
  })

  // --- Computed ---
  
  const activeProjects = computed(() => projectStore.projects.filter((p) => p.status !== 'completed'))

   // --- Helpers ---
   const getCategoryDisplayName = (c: string) => {
      const map: any = { case: '病例', ai_annotation: 'AI标注' }
      return map[c] || c
   }
   const getSubCategoryDisplayName = (c: string) => {
      const map: any = { trial: '试用', research: '科研', paid: '有偿', daily: '日常', research_ai: '科研', default: '默认' }
      return map[c] || c
   }
  const getRankingValue = (m: any, c: string) => m[c] || 0
  
  const getRankingLabel = (member: any, criteria: string, unitOnly = false) => {
     if (unitOnly) {
        const map: any = { completedTasks: '个', averageScore: '分', totalHours: 'h', totalScore: '分' }
        return map[criteria] || ''
     }
     return ''
  }

  const getProgressColorByValue = (val: number) => {
     if (val >= 80) return '#10b981'
     if (val >= 60) return '#3b82f6'
     if (val >= 40) return '#f59e0b'
     return '#ef4444'
  }
  
  const getProgressColor = (i: number) => ['#f59e0b', '#94a3b8', '#d97706'][i] || '#e5e7eb'

  const getPercentage = (m: any, c: string) => {
     // 优先使用完整数据计算最大值，若为空则降级使用当前榜单数据
     const source = performanceData.value.length > 0 ? performanceData.value : topPerformers.value
     const max = Math.max(...source.map((i: any) => Number(i[c]) || 0)) || 1
     const current = Number(m[c]) || 0
     const percent = Math.round((current / max) * 100)
     // 确保百分比在 0-100 之间
     return Math.min(100, Math.max(0, percent))
  }
  
  const getCompletionRate = (row: any) => {
     if(!row.totalTasks) return 0
     return Math.round((row.completedTasks / row.totalTasks) * 100)
  }
  const sortByCompletionRate = (a: any, b: any) => getCompletionRate(a) - getCompletionRate(b)
  const teamOverview = computed(() => {
    const calculatedData = calculatePerformanceFromTasks()
    if (!calculatedData || calculatedData.length === 0) return { totalMembers: 0, totalTasks: 0, completedTasks: 0, skippedTasks: 0 }

    const allTasks = (projectStore.tasks || []) as any[]
    let tasks = allTasks.filter((t) => {
      const project = projectStore.projects.find((p) => p.id === t.projectId)
      return project && project.status !== 'completed'
    })
    if (projectFilter.value) tasks = tasks.filter((t) => t.projectId === projectFilter.value)

    // Filter by date range for the stats cards to be consistent with charts
    const rangeCheck = getRangeCheckFn()
    tasks = tasks.filter(t => {
       const d = t.createdAt || t.created_at
       return d && rangeCheck(new Date(d))
    })

    return {
      totalMembers: calculatedData.length,
      totalTasks: tasks.length,
      completedTasks: tasks.filter((t) => t.status === 'approved').length,
      skippedTasks: tasks.filter((t) => t.status === 'skipped').length
    }
  })

  // 2. Annotator Chart
  const annotatorNames = computed(() => {
    const allTasks = (projectStore.tasks || []) as any[]
    if (!allTasks.length) return []
    const userIds = Array.from(new Set(allTasks.map((t) => t.assignedTo).filter(Boolean)))
    return userIds.map((uid) => {
      const task = allTasks.find((t) => t.assignedTo === uid && (t.assignedToName || t.assigned_to_name))
      if (task) return task.assignedToName || task.assigned_to_name
      const perf = performanceData.value.find((p) => p.userId === uid)
      if (perf && perf.realName) return perf.realName
      return `User ${String(uid).slice(-4)}`
    })
  })

  const annotatorStackedData = computed(() => {
    const allTasks = (projectStore.tasks || []) as any[]
    if (!allTasks.length) return []
    
    let filteredTasks = allTasks.filter((t) => {
      const project = projectStore.projects.find((p) => p.id === t.projectId)
      return project && project.status !== 'completed'
    })
    if (projectFilter.value) filteredTasks = filteredTasks.filter((t) => t.projectId === projectFilter.value)

    const userIds = Array.from(new Set(filteredTasks.map((t) => t.assignedTo).filter(Boolean)))
    const rangeCheck = getRangeCheckFn()

    const statusMap: any = { pending: '待分配', in_progress: '进行中', submitted: '已提交', approved: '已完成', rejected: '已驳回', skipped: '已跳过' }
    
    return Object.entries(statusMap).map(([status, name]) => {
        return {
          name: name as string,
          data: userIds.map((uid) => {
            return filteredTasks.filter(t => 
                t.assignedTo === uid && 
                t.status === status && 
                rangeCheck(new Date(t.updatedAt || t.createdAt || new Date()))
            ).length
          })
        }
    }).filter(s => s.data.some((v: number) => v > 0))
  })

  const annotatorChartColors = computed(() => {
     const map: any = { '待分配': '#f59e0b', '进行中': '#3b82f6', '已提交': '#8b5cf6', '已完成': '#10b981', '已驳回': '#ef4444', '已跳过': '#9ca3af' }
     return annotatorStackedData.value.map((s: any) => map[s.name] || '#ccc')
  })
  
  const annotatorChartLegend = computed(() => annotatorStackedData.value.map((s: any) => s.name))

  // 3. Category Stats
  const categoryTaskStats = computed(() => {
    const allTasks = (projectStore.tasks || []) as any[]
    let completedTasks = allTasks.filter(t => (t.status === 'approved' || t.status === 'rejected'))
    
    // Filter project
    if (projectFilter.value) completedTasks = completedTasks.filter(t => t.projectId === projectFilter.value)
    
    // Filter Date
    const rangeCheck = getRangeCheckFn()
    completedTasks = completedTasks.filter(t => rangeCheck(new Date(t.updatedAt || t.createdAt)))

    const map = new Map<string, number>()
    completedTasks.forEach(t => {
       const p = projectStore.projects.find(p => p.id === t.projectId)
       if (p && p.category) {
          const key = `${getCategoryDisplayName(p.category)}-${getSubCategoryDisplayName(p.subCategory || 'default')}`
          map.set(key, (map.get(key) || 0) + 1)
       }
    })
    
    const categories = Array.from(map.keys())
    const values = Array.from(map.values())
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    
    return {
       categories,
       barData: values,
       barColors: categories.map((_, i) => colors[i % colors.length]),
       pieData: categories.map((n, i) => ({ name: n, value: values[i], itemStyle: { color: colors[i % colors.length] } }))
    }
  })

  // 4. Top Performers
  const topPerformers = computed(() => {
    const data = calculatePerformanceFromTasks()
    if (!data.length) return []
    return data.sort((a: any, b: any) => Number(getRankingValue(b, rankingCriteria.value)) - Number(getRankingValue(a, rankingCriteria.value))).slice(0, 10)
  })

  // 5. Table Data
  const filteredPerformanceData = computed(() => {
    let data = performanceData.value
    if (searchKeyword.value) {
      const k = searchKeyword.value.toLowerCase()
      data = data.filter(i => (i.realName?.toLowerCase().includes(k) || i.username?.toLowerCase().includes(k)))
    }
    return data
  })

  // 6. Member Detail Charts
  const memberTaskTrendData = computed(() => {
     if (!selectedMember.value) return []
     // Mock trend data based on current stats for demo or complex calculation
     // Simulating based on range
     const days = memberTrendRange.value === '7d' ? 7 : 15
     return Array(days).fill(0).map(() => Math.floor(Math.random() * 5))
  })
  const memberTaskTrendLabels = computed(() => {
     const days = memberTrendRange.value === '7d' ? 7 : 15
     const arr = []
     for(let i=days-1; i>=0; i--) {
        const d = new Date()
        d.setDate(d.getDate() - i)
        arr.push(`${d.getMonth()+1}/${d.getDate()}`)
     }
     return arr
  })
  const memberCategoryTaskData = computed(() => {
     // Use global category stats logic but filtered for user
     // Simplified for member
     return { pieData: categoryTaskStats.value.pieData } // Reuse for now
  })


  // --- Methods ---

  function getRangeCheckFn() {
      const now = new Date()
      const [startStr, endStr] = dateRange.value.length === 2 ? dateRange.value : getDefaultDateRangeForPeriod(period.value)
      const start = new Date(startStr)
      start.setHours(0,0,0,0)
      const end = new Date(endStr)
      end.setHours(23,59,59,999)
      
      return (dt: Date) => dt >= start && dt <= end
  }

  const calculatePerformanceFromTasks = (): any[] => {
    const allTasks = (projectStore.tasks || []) as any[]
    if (!allTasks.length) return []

    let tasks = allTasks.filter(t => {
       const p = projectStore.projects.find(prj => prj.id === t.projectId)
       return p && p.status !== 'completed'
    })
    if (projectFilter.value) tasks = tasks.filter(t => t.projectId === projectFilter.value)
    
    const rangeCheck = getRangeCheckFn()
    const userIds = Array.from(new Set(tasks.map(t => t.assignedTo).filter(Boolean)))

    return userIds.map(uid => {
       const userTasks = tasks.filter(t => t.assignedTo === uid)
       const rangeTasks = userTasks.filter(t => rangeCheck(new Date(t.updatedAt || t.createdAt)))
       
       const approved = rangeTasks.filter(t => t.status === 'approved')
       
       // Calc score
       const scores = approved.map(t => Number(t.score || 0)).filter(s => s > 0)
       const avg = scores.length ? scores.reduce((a,b) => a+b,0)/scores.length : 0
       
       // Find name
       const tWithName = userTasks.find(t => t.assignedToName)
       const user = userStore.users.find((u: any) => u.id === uid)
       
       return {
          userId: uid,
          username: uid,
          realName: tWithName?.assignedToName || `User ${String(uid).slice(-4)}`,
          avatar: user?.avatar || '',
          totalTasks: rangeTasks.length,
          completedTasks: approved.length + rangeTasks.filter(t => t.status === 'rejected').length,
          approvedTasks: approved.length,
          rejectedTasks: rangeTasks.filter(t => t.status === 'rejected').length,
          averageScore: avg,
          totalScore: approved.length, // Simplified score
          totalHours: 0
       }
    }).filter(u => u.totalTasks > 0)
  }

  const getDefaultDateRangeForPeriod = (p: string) => {
    const now = new Date()
    const d = new Date(now)
    if (p === 'day') return [now.toISOString(), now.toISOString()]
    if (p === 'week') {
       const day = d.getDay() || 7
       d.setDate(d.getDate() - day + 1)
       const end = new Date(d)
       end.setDate(d.getDate() + 6)
       return [d.toISOString().split('T')[0], end.toISOString().split('T')[0]]
    }
    if (p === 'month') {
       const start = new Date(now.getFullYear(), now.getMonth(), 1)
       const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
       return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
    }
    // year
    return [`${now.getFullYear()}-01-01`, `${now.getFullYear()}-12-31`]
  }

  const handlePeriodChange = () => {
     dateRange.value = getDefaultDateRangeForPeriod(period.value)
     fetchPerformanceData()
  }
  
  const handleProjectFilterChange = () => {
     performanceData.value = calculatePerformanceFromTasks()
  }

  const fetchPerformanceData = async () => {
     loading.value = true
     await nextTick()
     // Use frontend calc for speed & demo, assuming tasks loaded
     performanceData.value = calculatePerformanceFromTasks()
     loading.value = false
  }

  const refreshData = async () => {
     loading.value = true
     try {
        await projectStore.fetchProjects({ page: 1, pageSize: 1000, forceRefresh: true })
        await projectStore.fetchTasks({ page: 1, pageSize: 2000, forceRefresh: true, assignedTo: undefined })
        fetchPerformanceData()
     } finally {
        loading.value = false
     }
  }


  // Actions
  const viewMemberDetail = (row: any) => {
     selectedMember.value = row
     showMemberDialog.value = true
  }
   const viewMemberTrend = (row: any) => {
      selectedMember.value = row
      showMemberDialog.value = true // Reuse dialog
   }
   const navigateToPersonalPage = () => {
      if(selectedMember.value) {
         router.push({ name: 'PersonalPerformance', query: { userId: selectedMember.value.userId, userName: selectedMember.value.realName } })
      }
   }
   const exportPerformance = () => { exportDialogVisible.value = true }
  const confirmExport = async () => {
     exportLoading.value = true
     await new Promise(r => setTimeout(r, 1000))
     exportLoading.value = false
     exportDialogVisible.value = false
     ElMessage.success('导出成功')
  }
  const handleSearch = () => { pagination.page = 1 }
  const handlePageChange = (p: number) => { pagination.page = p }
  const handlePageSizeChange = (s: number) => { pagination.pageSize = s; pagination.page = 1 }
  const updateRanking = () => {} // Reactive

  onMounted(() => {
     dateRange.value = getDefaultDateRangeForPeriod(period.value)
     refreshData()
  })
  onActivated(() => refreshData())

</script>

<style scoped lang="scss">
.team-performance {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 1. Filter Toolbar
.filter-toolbar {
  background: #fff;
  border-radius: 16px;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  gap: 20px; // 增加整体间距

  .left-filters {
    display: flex;
    align-items: center;
    gap: 20px; // 增加内部控件间距

    .filter-label {
      font-size: 14px;
      font-weight: 500;
      color: #374151;
      white-space: nowrap;
    }

    .custom-radio-group {
      :deep(.el-radio-button__inner) {
        padding: 8px 20px;
      }
    }

    .date-picker-custom {
      width: 260px;
    }
  }
}

// 2. Metrics Grid
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
    
    // Force row layout for stats cards to override art-custom-card column layout
    :deep(.el-card__body) {
        flex-direction: row !important; 
        align-items: center;
    }

    :deep(.value) { color: #1f2937; }
    :deep(.label) { color: #6b7280; }
  }
}

// 3. Charts Grid
.charts-layout-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;

  .grid-item {
    min-height: 400px;
    
    &.full-width {
      grid-column: span 2;
    }
    &.half-width {
      grid-column: span 1;
    }
  }
}

.art-custom-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #f3f4f6;
  }

  :deep(.el-card__body) {
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
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
        &.orange { background: #fff7ed; color: #f97316; }
        &.green { background: #ecfdf5; color: #10b981; }
        &.cyan { background: #ecfeff; color: #06b6d4; }
      }
    }
  }
}

// Specific Chart Styles
.category-chart-container.dual-chart {
  display: flex;
  gap: 24px;
  height: 100%;
  
  .chart-left {
    flex: 2;
    display: flex;
    flex-direction: column;
  }
  .chart-right {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .chart-subtitle {
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 12px;
    text-align: center;
  }
}

// Ranking List
.ranking-list {
  overflow-y: auto;
  padding-right: 4px;
  flex: 1;

  .ranking-item {
    display: flex;
    align-items: center;
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 10px;
    background: #f9fafb;
    border: 1px solid transparent;
    transition: all 0.2s;

    &:hover {
      background: #f3f4f6;
      border-color: #e5e7eb;
    }

    &.rank-1 { background: #fffbeb; border: 1px solid #fcd34d; }
    &.rank-2 { background: #f8fafc; border: 1px solid #e2e8f0; }
    &.rank-3 { background: #fff7ed; border: 1px solid #fdba74; }

    .rank-badge {
      width: 32px;
      text-align: center;
      font-weight: 700;
      font-size: 16px;
      margin-right: 10px;
      
      .number { color: #9ca3af; font-size: 14px; }
    }

    .member-avatar { margin-right: 12px; }

    .member-info {
      flex: 1;
      .member-name { font-weight: 600; color: #374151; font-size: 14px; }
      .member-sub { font-size: 12px; color: #9ca3af; }
    }

    .member-stats {
      text-align: right;
      .stat-val { font-size: 16px; font-weight: 700; color: #3b82f6; }
      .stat-label { font-size: 10px; color: #9ca3af; }
    }
  }
}

// Table Section
.table-section {
  .score-tag {
    font-weight: 600;
    color: #f59e0b;
    background: #fff7ed;
    padding: 2px 8px;
    border-radius: 4px;
  }
  
  .text-green { color: #10b981; font-weight: 600; }
  .text-red { color: #ef4444; }
  
  .completion-rate {
    display: flex;
    align-items: center;
    gap: 8px;
    .rate-text { font-size: 12px; width: 36px; text-align: right; color: #6b7280; }
    .el-progress { flex: 1; }
  }
  
  .member-cell {
    display: flex;
    align-items: center;
    gap: 10px;
    .member-name { font-weight: 600; color: #374151; }
    .member-username { font-size: 12px; color: #9ca3af; }
  }
}

// Member Detail
.member-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px dashed #e5e7eb;
    
    .user-profile {
      display: flex;
      align-items: center;
      gap: 16px;
      .user-text h3 { margin: 0 0 4px; font-size: 18px; color: #1f2937; }
      .user-text p { margin: 0; color: #6b7280; }
    }
    
    .user-stats-row {
      display: flex;
      gap: 32px;
      .stat-box {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        .label { font-size: 12px; color: #9ca3af; margin-bottom: 4px; }
        .value { font-size: 20px; font-weight: 700; color: #1f2937; }
        .value.warning { color: #f97316; }
        .value.primary { color: #3b82f6; }
      }
    }
  }
  
  .member-charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    
    .chart-box {
      background: #f9fafb;
      border-radius: 12px;
      padding: 16px;
      
      .box-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        h4 { margin: 0; font-size: 14px; color: #374151; }
      }
    }
  }
}

// Custom Scrollbar
.custom-scrollbar {
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
  &::-webkit-scrollbar-track { background: transparent; }
}
</style>