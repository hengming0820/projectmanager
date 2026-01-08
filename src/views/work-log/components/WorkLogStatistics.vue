<template>
  <div class="work-log-statistics" v-loading="loading">
    <div v-if="statistics">
      <!-- 整体统计概览 -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-card">
              <div class="icon-wrapper users">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.overall_stats.total_users }}</div>
                <div class="stat-label">参与人数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="icon-wrapper planned">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ calculateTotalPlannedHours() }}</div>
                <div class="stat-label">计划工时 (h)</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="icon-wrapper actual">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.overall_stats.total_actual_hours }}</div>
                <div class="stat-label">实际工时 (h)</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="icon-wrapper efficiency">
                <el-icon><Trophy /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ calculateWorkEfficiency() }}%</div>
                <div class="stat-label">工时完成率</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 图表展示 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <!-- 按工作类型统计 -->
          <el-col :xs="24" :lg="12">
            <el-card class="chart-card" shadow="hover">
              <template #header>
                <div class="chart-header">
                  <div class="header-title">
                    <el-icon><PieChart /></el-icon>
                    <span>员工工作类型工时统计</span>
                  </div>
                  <span class="chart-subtitle">按工作类型堆叠展示</span>
                </div>
              </template>
              <div class="chart-container">
                <div ref="workTypeChartRef" style="width: 100%; height: 350px"></div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 计划工时 vs 实际工时 -->
          <el-col :xs="24" :lg="12">
            <el-card class="chart-card" shadow="hover">
              <template #header>
                <div class="chart-header">
                  <div class="header-title">
                    <el-icon><TrendCharts /></el-icon>
                    <span>计划 vs 实际工时对比</span>
                  </div>
                  <span class="chart-subtitle">基准：40小时/周</span>
                </div>
              </template>
              <div class="chart-container">
                <div ref="hoursCompareChartRef" style="width: 100%; height: 350px"></div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 用户详细统计表格 -->
      <div class="table-section">
        <el-card shadow="hover">
          <template #header>
            <div class="table-header">
              <el-icon><List /></el-icon>
              <span>用户详细统计数据</span>
            </div>
          </template>

          <el-table :data="statistics.user_summaries" stripe border :header-cell-style="{ background: '#f5f7fa' }">
            <el-table-column prop="user_name" label="姓名" width="120" fixed="left">
              <template #default="{ row }">
                <div class="user-cell">
                  <div class="user-avatar">{{ row.user_name.charAt(0) }}</div>
                  <span class="user-name">{{ row.user_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="计划工时" width="120" align="center">
              <template #default>
                <span class="hours-text planned">40h</span>
              </template>
            </el-table-column>
            <el-table-column label="实际工时" width="120" align="center">
              <template #default="{ row }">
                <span class="hours-text actual">{{ row.total_actual_hours }}h</span>
              </template>
            </el-table-column>
            <el-table-column label="工时完成率" width="180" align="center">
              <template #default="{ row }">
                <div class="efficiency-cell">
                  <el-progress 
                    :percentage="Math.min(Number(getEfficiencyRate(row.total_actual_hours, 40)), 100)"
                    :color="getEfficiencyColor(row.total_actual_hours, 40)"
                    :stroke-width="8"
                  />
                  <span class="percentage-text">{{ getEfficiencyRate(row.total_actual_hours, 40) }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="工作类型分布" min-width="300">
              <template #default="{ row }">
                <div class="work-type-distribution">
                  <template v-for="(hours, workType) in getWorkTypeHours(row)" :key="workType">
                    <el-tooltip :content="`${workType}: ${hours}小时`" placement="top">
                      <el-tag
                        v-if="hours > 0"
                        :color="getWorkTypeColor(workType)"
                        effect="dark"
                        size="small"
                        class="type-tag"
                      >
                        {{ workType }}
                      </el-tag>
                    </el-tooltip>
                  </template>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="日志条目" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="info" effect="plain" round>{{ getEntriesCount(row) }} 条</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
  import { ElMessage } from 'element-plus'
  import { 
    User, 
    Timer, 
    CircleCheck, 
    Trophy,
    PieChart,
    TrendCharts,
    List
  } from '@element-plus/icons-vue'
  import { workWeekApi } from '@/api/workLogApi'
  import type { WorkWeekStatistics } from '@/types/work-log'
  import * as echarts from 'echarts'
  import type { EChartsOption } from 'echarts'

  interface Props {
    workWeekId: string
  }

  const props = defineProps<Props>()

  // 响应式数据
  const loading = ref(false)
  const statistics = ref<WorkWeekStatistics | null>(null)
  const workTypeChartRef = ref<HTMLDivElement | null>(null)
  const hoursCompareChartRef = ref<HTMLDivElement | null>(null)
  let workTypeChart: echarts.ECharts | null = null
  let hoursCompareChart: echarts.ECharts | null = null

  // 工作类型颜色映射
  const workTypeColorMap: Record<string, string> = {
    开发: '#409eff',
    测试: '#67c23a',
    标注: '#17a2b8',
    审核: '#ff9800',
    培训: '#9c27b0',
    会议: '#f56c6c',
    文档: '#909399',
    设计: '#e6a23c',
    请假: '#f59e0b',
    病假: '#ef4444',
    年假: '#10b981'
  }

  // 方法
  const fetchStatistics = async () => {
    loading.value = true
    try {
      const response = await workWeekApi.getWorkWeekStatistics(props.workWeekId)
      const data = (response as any).data || response
      statistics.value = data as WorkWeekStatistics

      await nextTick()
      initCharts()
    } catch (error) {
      console.error('获取统计数据失败:', error)
      ElMessage.error('获取统计数据失败')
    } finally {
      loading.value = false
    }
  }

  // 初始化图表
  const initCharts = () => {
    if (!statistics.value) return
    initWorkTypeChart()
    initHoursCompareChart()
  }

  // 初始化工作类型堆叠柱状图
  const initWorkTypeChart = () => {
    if (!workTypeChartRef.value || !statistics.value) return
    if (!workTypeChart) workTypeChart = echarts.init(workTypeChartRef.value)

    const users = (statistics.value as any).user_summaries as any[]
    const userNames = users.map((u: any) => u.user_name)
    const workTypeData: Record<string, number[]> = {}

    users.forEach((user: any) => {
      const workTypeHours = getWorkTypeHours(user)
      Object.entries(workTypeHours).forEach(([workType, hours]) => {
        if (!workTypeData[workType]) {
          workTypeData[workType] = new Array(users.length).fill(0)
        }
        const userIndex = users.findIndex((u: any) => u.user_name === user.user_name)
        workTypeData[workType][userIndex] = hours as number
      })
    })

    const series = Object.entries(workTypeData).map(([workType, data]) => ({
      name: workType,
      type: 'bar' as const,
      stack: 'total',
      data: data,
      itemStyle: { color: getWorkTypeColor(workType) },
      emphasis: { focus: 'series' as const }
    }))

    const option: EChartsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const result = [`<b>${params[0].axisValue}</b>`]
          let total = 0
          params.forEach((item: any) => {
            if (item.value > 0) {
              result.push(`${item.marker}${item.seriesName}: ${item.value}h`)
              total += item.value
            }
          })
          result.push(`<b>总计: ${total}h</b>`)
          return result.join('<br/>')
        }
      },
      legend: {
        data: Object.keys(workTypeData),
        top: 0,
        left: 'center',
        type: 'scroll'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 40,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: userNames,
        axisLabel: { rotate: userNames.length > 8 ? 45 : 0, interval: 0 }
      },
      yAxis: {
        type: 'value',
        name: '工时',
        splitLine: { lineStyle: { type: 'dashed' } }
      },
      series: series
    }

    workTypeChart.setOption(option)
  }

  // 初始化计划工时 vs 实际工时对比图
  const initHoursCompareChart = () => {
    if (!hoursCompareChartRef.value || !statistics.value) return
    if (!hoursCompareChart) hoursCompareChart = echarts.init(hoursCompareChartRef.value)

    const users = (statistics.value as any).user_summaries as any[]
    const userNames = users.map((u: any) => u.user_name)
    const plannedHours = users.map(() => 40)
    const actualHours = users.map((u: any) => u.total_actual_hours || 0)

    const option: EChartsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const result = [`<b>${params[0].axisValue}</b>`]
          params.forEach((item: any) => {
            result.push(`${item.marker}${item.seriesName}: ${item.value}h`)
          })
          const planned = params[0].value
          const actual = params[1].value
          const rate = planned > 0 ? ((actual / planned) * 100).toFixed(1) : '0.0'
          result.push(`<b>完成率: ${rate}%</b>`)
          return result.join('<br/>')
        }
      },
      legend: { data: ['计划工时', '实际工时'], top: 0 },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 40,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: userNames,
        axisLabel: { rotate: userNames.length > 8 ? 45 : 0, interval: 0 }
      },
      yAxis: {
        type: 'value',
        name: '工时',
        splitLine: { lineStyle: { type: 'dashed' } }
      },
      series: [
        {
          name: '计划工时',
          type: 'bar',
          data: plannedHours,
          itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
          barGap: '20%'
        },
        {
          name: '实际工时',
          type: 'bar',
          data: actualHours,
          itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] }
        }
      ]
    }

    hoursCompareChart.setOption(option)
  }

  const calculateTotalPlannedHours = () => {
    if (!statistics.value) return 0
    const users = (statistics.value as any).user_summaries || []
    return users.length * 40
  }

  const calculateWorkEfficiency = () => {
    if (!statistics.value) return '0.0'
    const totalPlanned = calculateTotalPlannedHours()
    const totalActual = statistics.value.overall_stats?.total_actual_hours || 0
    if (totalPlanned === 0) return '0.0'
    return ((totalActual / totalPlanned) * 100).toFixed(1)
  }

  const getEfficiencyRate = (actual: number, planned: number) => {
    if (!planned || planned <= 0) return '0.0'
    return ((actual / planned) * 100).toFixed(1)
  }

  const getEfficiencyColor = (actual: number, planned: number) => {
    const rate = actual / planned
    if (rate < 0.8) return '#f56c6c'
    if (rate < 0.95) return '#e6a23c'
    if (rate <= 1.1) return '#67c23a'
    return '#409eff' // Overload
  }

  const getWorkTypeColor = (workType: string) => workTypeColorMap[workType] || '#909399'

  const getWorkTypeHours = (user: any): Record<string, number> => user.work_type_hours || {}

  const getEntriesCount = (user: any): number => user.total_entries || 0

  const handleResize = () => {
    workTypeChart?.resize()
    hoursCompareChart?.resize()
  }

  const destroyCharts = () => {
    workTypeChart?.dispose()
    hoursCompareChart?.dispose()
    workTypeChart = null
    hoursCompareChart = null
  }

  onMounted(() => {
    fetchStatistics()
    window.addEventListener('resize', handleResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    destroyCharts()
  })
</script>

<style lang="scss" scoped>
.work-log-statistics {
  padding: 10px;

  .overview-section {
    margin-bottom: 24px;

    .stat-card {
      display: flex;
      align-items: center;
      padding: 20px;
      background: var(--art-bg-color);
      border: 1px solid var(--art-card-border);
      border-radius: 12px;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
      }

      .icon-wrapper {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        font-size: 24px;
        flex-shrink: 0;

        &.users { background: rgba(64, 158, 255, 0.1); color: #409eff; }
        &.planned { background: rgba(230, 162, 60, 0.1); color: #e6a23c; }
        &.actual { background: rgba(103, 194, 58, 0.1); color: #67c23a; }
        &.efficiency { background: rgba(144, 147, 153, 0.1); color: #909399; }
      }

      .stat-info {
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: var(--art-text-gray-900);
          line-height: 1.2;
          margin-bottom: 4px;
        }
        .stat-label {
          font-size: 13px;
          color: var(--art-text-gray-500);
        }
      }
    }
  }

  .charts-section {
    margin-bottom: 24px;

    .chart-card {
      height: 100%;
      
      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .header-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 600;
          color: var(--art-text-gray-900);
        }

        .chart-subtitle {
          font-size: 12px;
          color: var(--art-text-gray-500);
        }
      }

      .chart-container {
        padding: 10px 0;
      }
    }
  }

  .table-section {
    .table-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: var(--art-text-gray-900);
    }

    .user-cell {
      display: flex;
      align-items: center;
      gap: 10px;

      .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
      }

      .user-name {
        font-weight: 500;
        color: var(--art-text-gray-900);
      }
    }

    .hours-text {
      font-weight: 600;
      &.planned { color: var(--art-text-gray-500); }
      &.actual { color: var(--art-text-gray-900); font-size: 15px; }
    }

    .efficiency-cell {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .el-progress {
        flex: 1;
      }
      
      .percentage-text {
        font-size: 12px;
        width: 40px;
        text-align: right;
        color: var(--art-text-gray-600);
      }
    }

    .work-type-distribution {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;

      .type-tag {
        border: none;
        cursor: default;
      }
    }
  }
}

// 移动端适配
@media screen and (max-width: 768px) {
  .work-log-statistics {
    .overview-section {
      .el-col {
        margin-bottom: 16px;
      }
    }
    
    .charts-section {
      .el-col {
        margin-bottom: 16px;
      }
    }
  }
}
</style>
