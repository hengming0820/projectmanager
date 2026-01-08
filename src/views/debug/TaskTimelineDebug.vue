<template>
  <div class="timeline-debug">
    <div class="debug-header">
      <h2>任务时间轴调试页面</h2>
      <p>用于调试任务时间轴数据获取和显示问题</p>
    </div>

    <div class="debug-section">
      <h3>任务列表</h3>
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="200" />
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间轴事件数" width="120">
          <template #default="{ row }">
            {{ (row.timeline || []).length }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="debugTask(row)">调试</el-button>
            <el-button size="small" type="primary" @click="viewTimeline(row)">查看时间轴</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="selectedTask" class="debug-section">
      <h3>任务详情调试</h3>
      <div class="debug-info">
        <h4>基本信息</h4>
        <pre>{{ JSON.stringify(selectedTask, null, 2) }}</pre>

        <h4>时间轴数据</h4>
        <div v-if="selectedTask.timeline && selectedTask.timeline.length">
          <p>时间轴事件数量: {{ selectedTask.timeline.length }}</p>
          <div
            v-for="(event, index) in selectedTask.timeline"
            :key="index"
            class="timeline-event-debug"
          >
            <h5>事件 {{ index + 1 }}</h5>
            <pre>{{ JSON.stringify(event, null, 2) }}</pre>
          </div>
        </div>
        <div v-else>
          <p style="color: red">❌ 没有时间轴数据</p>
        </div>
      </div>
    </div>

    <!-- 时间轴显示测试 -->
    <el-dialog v-model="showTimelineDialog" title="时间轴显示测试" width="90%">
      <div v-if="selectedTask">
        <h4>任务: {{ selectedTask.title }}</h4>
        <div v-if="selectedTask.timeline && selectedTask.timeline.length" class="timeline-test">
          <HorizontalTimeline
            :timeline="selectedTask.timeline"
            :current-status="selectedTask.status"
          />
        </div>
        <div v-else>
          <el-empty description="没有时间轴数据" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { ElMessage } from 'element-plus'
  import { taskApi } from '@/api/projectApi'
  import { useProjectStore } from '@/store/modules/project'
  import HorizontalTimeline from '@/components/custom/HorizontalTimeline.vue'
  import type { Task } from '@/types/project'

  // 为调试扩展任务类型，增加可选的 timeline 字段
  type DebugTask = Task & { timeline?: any[] }

  const projectStore = useProjectStore()
  const tasks = ref<DebugTask[]>([])
  const selectedTask = ref<DebugTask | null>(null)
  const showTimelineDialog = ref(false)

  // 获取任务列表
  const fetchTasks = async () => {
    try {
      console.log('🔍 [Debug] 获取任务列表...')
      await projectStore.fetchTasks({})
      tasks.value = projectStore.tasks
      console.log('✅ [Debug] 任务列表获取成功:', tasks.value.length)

      // 输出每个任务的时间轴信息
      tasks.value.forEach((task) => {
        console.log(`📋 [Debug] 任务 ${task.id}:`, {
          title: task.title,
          status: task.status,
          timelineLength: (task.timeline || []).length,
          timeline: task.timeline
        })
      })
    } catch (error) {
      console.error('❌ [Debug] 获取任务列表失败:', error)
      ElMessage.error('获取任务列表失败')
    }
  }

  // 调试单个任务
  const debugTask = async (task: DebugTask) => {
    try {
      console.log('🔍 [Debug] 调试任务:', task.id)

      // 获取任务详情
      const result = await taskApi.getTask(task.id)
      const taskDetail = (result.data || result) as DebugTask

      console.log('📋 [Debug] 任务详情:', taskDetail)
      console.log('⏰ [Debug] 时间轴数据:', taskDetail.timeline)

      selectedTask.value = taskDetail

      // 显示调试信息
      ElMessage.success(`任务 ${task.title} 调试完成，请查看控制台和下方详情`)
    } catch (error) {
      console.error('❌ [Debug] 调试任务失败:', error)
      ElMessage.error('调试任务失败')
    }
  }

  // 查看时间轴
  const viewTimeline = async (task: DebugTask) => {
    await debugTask(task)
    showTimelineDialog.value = true
  }

  // 状态相关函数
  const getStatusType = (status: string): 'success' | 'danger' | 'warning' | 'info' | 'primary' => {
    const types: Record<string, 'success' | 'danger' | 'warning' | 'info' | 'primary'> = {
      pending: 'info',
      assigned: 'info',
      in_progress: 'primary',
      submitted: 'warning',
      approved: 'success',
      rejected: 'danger'
    }
    return types[status as keyof typeof types] || 'info'
  }

  const getStatusText = (status: string) => {
    const texts = {
      pending: '待分配',
      assigned: '已分配',
      in_progress: '进行中',
      submitted: '待审核',
      approved: '已通过',
      rejected: '已驳回'
    }
    return texts[status as keyof typeof texts] || status
  }

  onMounted(() => {
    fetchTasks()
  })
</script>

<style scoped lang="scss">
  .timeline-debug {
    padding: 20px;
    background: #f5f5f5;
    min-height: 100vh;

    .debug-header {
      background: white;
      padding: 24px;
      border-radius: 8px;
      margin-bottom: 20px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);

      h2 {
        margin: 0 0 8px 0;
        color: #303133;
      }

      p {
        margin: 0;
        color: #606266;
      }
    }

    .debug-section {
      background: white;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);

      h3 {
        margin: 0 0 16px 0;
        color: #303133;
        border-bottom: 2px solid #409eff;
        padding-bottom: 8px;
      }

      .debug-info {
        h4 {
          margin: 16px 0 8px 0;
          color: #606266;
        }

        pre {
          background: #f8f9fa;
          padding: 12px;
          border-radius: 4px;
          border: 1px solid #e4e7ed;
          overflow-x: auto;
          font-size: 12px;
          max-height: 300px;
        }

        .timeline-event-debug {
          margin-bottom: 16px;
          border: 1px solid #e4e7ed;
          border-radius: 4px;
          padding: 12px;

          h5 {
            margin: 0 0 8px 0;
            color: #409eff;
          }
        }
      }
    }

    .timeline-test {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      border: 1px solid #e4e7ed;
    }
  }
</style>
