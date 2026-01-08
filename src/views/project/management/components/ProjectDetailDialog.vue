<template>
  <el-dialog
    v-model="visible"
    :title="`项目详情 - ${currentProject?.name || ''}`"
    width="1200px"
    :before-close="handleClose"
    destroy-on-close
  >
    <div v-loading="loading" class="project-detail">
      <!-- 项目基本信息 -->
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="24">
          <el-card class="art-custom-card">
            <template #header>
              <span>项目信息</span>
            </template>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="项目名称">{{
                currentProject?.name
              }}</el-descriptions-item>
              <el-descriptions-item label="项目状态">
                <el-tag :type="getStatusType(currentProject?.status)">
                  {{ getStatusText(currentProject?.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityType(currentProject?.priority)">
                  {{ getPriorityText(currentProject?.priority) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="开始日期">{{
                currentProject?.startDate
              }}</el-descriptions-item>
              <el-descriptions-item label="结束日期">{{
                currentProject?.endDate
              }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{
                formatDate(currentProject?.createdAt)
              }}</el-descriptions-item>
              <el-descriptions-item label="项目描述" :span="3">{{
                currentProject?.description
              }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表和进度 -->
      <el-row :gutter="20">
        <!-- 任务状态分布饼图 -->
        <el-col :span="8">
          <el-card class="art-custom-card">
            <template #header>
              <span>任务状态分布</span>
            </template>
            <div class="chart-container">
              <ArtRingChart
                height="300px"
                :data="taskStatusData"
                :showTooltip="true"
                :showLegend="true"
                legendPosition="bottom"
                :radius="['45%', '75%']"
                :colors="statusColors"
                :centerText="`总任务数\n${taskStats.total}`"
              />
            </div>
          </el-card>
        </el-col>

        <!-- 标注员完成数量饼图 -->
        <el-col :span="8">
          <el-card class="art-custom-card">
            <template #header>
              <span>标注员完成情况</span>
            </template>
            <div class="chart-container">
              <ArtRingChart
                height="300px"
                :data="annotatorData"
                :showTooltip="true"
                :showLegend="true"
                legendPosition="bottom"
                :radius="['45%', '75%']"
                :colors="annotatorColors"
                :centerText="`已完成\n${taskStats.completed}`"
              />
            </div>
          </el-card>
        </el-col>

        <!-- 项目进度和操作 -->
        <el-col :span="8">
          <el-card class="art-custom-card">
            <template #header>
              <span>项目进度</span>
            </template>
            <div class="progress-container">
              <div class="progress-stats">
                <div class="stat-item">
                  <span class="label">总任务数：</span>
                  <span class="value">{{ taskStats.total }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">已完成：</span>
                  <span class="value success">{{ taskStats.completed }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">进行中：</span>
                  <span class="value warning">{{ taskStats.inProgress }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">待分配：</span>
                  <span class="value info">{{ taskStats.pending }}</span>
                </div>
              </div>

              <div class="progress-bar">
                <el-progress
                  :percentage="completionRate"
                  :stroke-width="20"
                  :color="getProgressColor(completionRate)"
                  :show-text="true"
                  :format="(percentage) => `${percentage}%`"
                />
              </div>

              <div class="project-actions">
                <!-- 只有进行中的项目才显示完结按钮 -->
                <el-button
                  v-if="currentProject?.status !== 'completed'"
                  type="success"
                  size="large"
                  :disabled="completionRate < 100"
                  @click="handleFinishProject"
                  style="width: 100%; margin-top: 20px"
                >
                  <el-icon><Check /></el-icon>
                  完结项目
                </el-button>

                <!-- 已完结的项目显示完结信息 -->
                <el-alert
                  v-else
                  type="success"
                  :closable="false"
                  show-icon
                  style="margin-top: 20px"
                >
                  <template #title>
                    <div style="font-size: 14px; font-weight: 600"> ✅ 项目已完结 </div>
                  </template>
                  <div style="font-size: 13px; margin-top: 8px; color: #67c23a">
                    完结日期：{{ currentProject?.endDate || '未知' }}
                  </div>
                </el-alert>

                <p
                  class="finish-tip"
                  v-if="currentProject?.status !== 'completed' && completionRate < 100"
                >
                  项目进度达到100%后可完结
                </p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 任务详细列表 -->
      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card class="art-custom-card">
            <template #header>
              <span>任务列表</span>
            </template>
            <el-table :data="projectTasks" stripe max-height="400">
              <el-table-column prop="title" label="任务名称" min-width="200" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTaskStatusType(row.status)" size="small">
                    {{ getTaskStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assignedToName" label="标注员" width="120" />
              <el-table-column prop="priority" label="优先级" width="100">
                <template #default="{ row }">
                  <el-tag :type="getPriorityType(row.priority)" size="small">
                    {{ getPriorityText(row.priority) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="创建时间" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.createdAt) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref, computed, watch } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Check } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { taskApi } from '@/api/projectApi'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import type { Project, Task } from '@/types/project'

  defineOptions({ name: 'ProjectDetailDialog' })

  // Props
  interface Props {
    modelValue: boolean
    project?: Project
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: false,
    project: undefined
  })

  // Emits
  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
    refresh: []
  }>()

  // Store
  const projectStore = useProjectStore()

  // State
  const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  const loading = ref(false)
  const currentProject = ref<Project>()
  const projectTasks = ref<any[]>([])

  // 监听项目变化
  watch(
    () => props.project,
    async (newProject) => {
      if (newProject && visible.value) {
        currentProject.value = newProject
        await loadProjectTasks()
      }
    },
    { immediate: true }
  )

  // 监听对话框显示状态
  watch(visible, async (newVisible) => {
    if (newVisible && props.project) {
      currentProject.value = props.project
      await loadProjectTasks()
    }
  })

  // 加载项目任务
  const loadProjectTasks = async () => {
    if (!currentProject.value) return

    loading.value = true
    try {
      // 直接调用API获取项目任务，包含完结项目的任务（用于历史查看）
      const result = await taskApi.getTasks({
        projectId: currentProject.value.id,
        page: 1,
        pageSize: 1000, // 获取所有任务
        includeCompletedProjects: true // ✅ 包含完结项目的任务
      })

      // 提取任务列表数据
      let taskList = []
      if (result && (result as any).data) {
        taskList = ((result as any).data as any).list || []
      } else if (Array.isArray(result)) {
        taskList = result
      }

      // 处理任务数据映射
      projectTasks.value = (taskList as any[]).map((task: any) => ({
        ...task,
        projectName: task.projectName || task.project_name || task.project?.name || '未知项目',
        assignedTo: task.assignedTo || task.assigned_to,
        assignedToName: task.assignedToName || task.assigned_to_name,
        createdBy: task.createdBy || task.created_by,
        createdByName: task.createdByName || task.created_by_name,
        reviewedBy: task.reviewedBy || task.reviewed_by,
        reviewedByName: task.reviewedByName || task.reviewed_by_name,
        estimatedHours: Number(task.estimatedHours || task.estimated_hours || 0),
        skippedAt: task.skippedAt || task.skipped_at,
        skipReason: task.skipReason || task.skip_reason,
        skipImages: task.skipImages || task.skip_images
      }))

      console.log('📊 [ProjectDetailDialog] 项目任务加载成功:', {
        项目ID: currentProject.value.id,
        任务数量: projectTasks.value.length
      })
    } catch (error) {
      console.error('加载项目任务失败:', error)
      ElMessage.error('加载项目任务失败')
    } finally {
      loading.value = false
    }
  }

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

  // 任务状态分布数据
  const taskStatusData = computed(() =>
    [
      { name: '待分配', value: taskStats.value.pending },
      { name: '进行中', value: taskStats.value.inProgress },
      { name: '已提交', value: taskStats.value.submitted },
      { name: '已完成', value: taskStats.value.completed },
      { name: '已驳回', value: taskStats.value.rejected },
      { name: '已跳过', value: taskStats.value.skipped }
    ].filter((item) => item.value > 0)
  )

  // 标注员完成数据
  const annotatorData = computed(() => {
    const completedTasks = projectTasks.value.filter((t) => t.status === 'approved')
    const annotatorStats = new Map<string, number>()

    completedTasks.forEach((task) => {
      const name = task.assignedToName || task.assignedTo || '未知用户'
      annotatorStats.set(name, (annotatorStats.get(name) || 0) + 1)
    })

    return Array.from(annotatorStats.entries())
      .map(([name, count]) => ({ name, value: count }))
      .sort((a, b) => b.value - a.value)
  })

  // 颜色配置
  const statusColors = ['#a0aec0', '#409eff', '#e6a23c', '#67c23a', '#f56c6c', '#8b8f98']
  const annotatorColors = [
    '#409eff',
    '#67c23a',
    '#e6a23c',
    '#f56c6c',
    '#909399',
    '#9c27b0',
    '#ff9800',
    '#4caf50'
  ]

  // 状态类型映射
  const getStatusType = (
    status?: string
  ): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
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

  const getPriorityType = (
    priority?: string
  ): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
      low: 'info',
      medium: 'primary',
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

  const getTaskStatusType = (
    status: string
  ): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
      pending: 'info',
      assigned: 'primary',
      in_progress: 'warning',
      submitted: 'success',
      approved: 'success',
      rejected: 'danger',
      skip_pending: 'warning', // 跳过申请中
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
      skip_pending: '跳过申请中', // 新增跳过申请状态
      skipped: '已跳过'
    }
    return map[status] || status
  }

  const getProgressColor = (percentage: number) => {
    if (percentage < 30) return '#f56c6c'
    if (percentage < 70) return '#e6a23c'
    return '#67c23a'
  }

  // 格式化日期
  const formatDate = (date: string | Date | undefined) => {
    if (!date) return '-'
    return new Date(date).toLocaleDateString('zh-CN')
  }

  // 完结项目
  const handleFinishProject = async () => {
    if (completionRate.value < 100) {
      ElMessage.warning('项目进度必须达到100%才能完结')
      return
    }

    if (!currentProject.value) {
      ElMessage.error('项目信息不存在')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要完结项目"${currentProject.value.name}"吗？
      
⚠️ 注意：
• 完结后，该项目的所有任务将不再显示在任务池中
• 项目状态将变更为"已完成"
• 此操作可以撤销（通过编辑项目重新激活）

请确认是否继续？`,
        '确认完结项目',
        {
          confirmButtonText: '确定完结',
          cancelButtonText: '取消',
          type: 'warning',
          dangerouslyUseHTMLString: true
        }
      )

      // ✅ 调用更新项目API，将状态改为 completed，并设置结束日期
      loading.value = true
      const today = new Date().toISOString().split('T')[0] // YYYY-MM-DD
      await projectStore.updateProject(currentProject.value.id, {
        status: 'completed',
        endDate: today // ✅ 自动设置结束日期为今天
      })

      ElMessage.success('项目已完结')

      // 刷新项目列表（通知父组件）
      emit('refresh')

      handleClose()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('完结项目失败:', error)
        ElMessage.error('完结项目失败')
      }
    } finally {
      loading.value = false
    }
  }

  // 关闭对话框
  const handleClose = () => {
    visible.value = false
    currentProject.value = undefined
    projectTasks.value = []
  }
</script>

<style lang="scss" scoped>
  .project-detail {
    .chart-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 300px;
    }

    .progress-container {
      padding: 20px;

      .progress-stats {
        margin-bottom: 30px;

        .stat-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 15px;

          .label {
            color: var(--el-text-color-regular);
            font-size: 14px;
          }

          .value {
            font-weight: 600;
            font-size: 16px;

            &.success {
              color: var(--el-color-success);
            }
            &.warning {
              color: var(--el-color-warning);
            }
            &.info {
              color: var(--el-color-info);
            }
          }
        }
      }

      .progress-bar {
        margin-bottom: 20px;
      }

      .project-actions {
        text-align: center;

        .finish-tip {
          margin-top: 10px;
          font-size: 12px;
          color: var(--el-text-color-placeholder);
        }
      }
    }
  }
</style>
