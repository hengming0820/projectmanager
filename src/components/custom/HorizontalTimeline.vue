<template>
  <div class="horizontal-timeline">
    <div class="timeline-container">
      <div class="timeline-line"></div>
      <div
        v-for="(event, index) in timelineEvents"
        :key="index"
        class="timeline-event"
        :class="{ active: event.isActive }"
        :style="{
          left: `${timelineEvents.length > 1 ? (index / (timelineEvents.length - 1)) * 100 : 50}%`
        }"
      >
        <!-- 时间点 -->
        <div class="timeline-dot" :class="`dot-${event.type}`">
          <el-icon>
            <component :is="getEventIcon(event.type)" />
          </el-icon>
        </div>

        <!-- 事件信息 -->
        <div
          class="timeline-content"
          :class="{ 'content-top': index % 2 === 0, 'content-bottom': index % 2 === 1 }"
        >
          <div class="event-card">
            <div class="event-title">{{ getEventTitle(event.type) }}</div>
            <div class="event-time">{{ formatTime(event.time) }}</div>
            <div class="event-user">{{ event.user_name || '系统' }}</div>
            <div v-if="event.comment" class="event-comment">{{ event.comment }}</div>
            <div v-if="event.action" class="event-action">
              <el-tag :type="event.action === 'approve' ? 'success' : 'danger'" size="small">
                {{ event.action === 'approve' ? '通过' : '驳回' }}
              </el-tag>
            </div>
            <div v-if="event.score !== undefined" class="event-score">
              <el-rate v-model="event.score" disabled size="small" show-score />
            </div>
            <div v-if="event.organ_count" class="event-detail">
              器官数：{{ event.organ_count }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import { Plus, User, VideoPlay, Upload, Check, Close, Refresh } from '@element-plus/icons-vue'

  interface TimelineEvent {
    type: string
    time: string
    user_id?: string
    user_name?: string
    comment?: string
    action?: string
    score?: number
    organ_count?: number
    isActive?: boolean
  }

  interface Props {
    timeline: TimelineEvent[]
    currentStatus?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    timeline: () => [],
    currentStatus: ''
  })

  // 处理时间轴事件，确保按时间排序并标记活跃状态
  const timelineEvents = computed(() => {
    if (!props.timeline || props.timeline.length === 0) return []

    // 按时间排序
    const sortedEvents = [...props.timeline].sort(
      (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime()
    )

    // 标记活跃状态（最后一个事件为活跃状态）
    return sortedEvents.map((event, index) => ({
      ...event,
      isActive: index === sortedEvents.length - 1
    }))
  })

  // 获取事件图标
  const getEventIcon = (type: string) => {
    const iconMap: Record<string, any> = {
      created: Plus,
      claimed: User,
      started: VideoPlay,
      submitted: Upload,
      reviewed: Check,
      restarted: Refresh
    }
    return iconMap[type] || Plus
  }

  // 获取事件标题
  const getEventTitle = (type: string) => {
    const titleMap: Record<string, string> = {
      created: '创建任务',
      claimed: '领取任务',
      started: '开始标注',
      submitted: '提交审核',
      reviewed: '审核结果',
      restarted: '重新开始'
    }
    return titleMap[type] || type
  }

  // 格式化时间
  const formatTime = (time: string) => {
    if (!time) return ''
    const date = new Date(time)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
</script>

<style scoped lang="scss">
  .horizontal-timeline {
    width: 100%;
    padding: 40px 20px;
    overflow-x: auto;

    .timeline-container {
      position: relative;
      min-width: 800px;
      height: 200px;
      margin: 0 auto;
    }

    .timeline-line {
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(to right, #e4e7ed, #409eff, #e4e7ed);
      transform: translateY(-50%);
      z-index: 1;
    }

    .timeline-event {
      position: absolute;
      top: 50%;
      transform: translateX(-50%);
      z-index: 2;

      .timeline-dot {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border: 3px solid #e4e7ed;
        color: #909399;
        font-size: 16px;
        transition: all 0.3s ease;
        transform: translateY(-50%);

        &.dot-created {
          border-color: #409eff;
          color: #409eff;
        }

        &.dot-claimed {
          border-color: #67c23a;
          color: #67c23a;
        }

        &.dot-started {
          border-color: #e6a23c;
          color: #e6a23c;
        }

        &.dot-submitted {
          border-color: #f56c6c;
          color: #f56c6c;
        }

        &.dot-reviewed {
          border-color: #409eff;
          color: #409eff;
        }

        &.dot-restarted {
          border-color: #909399;
          color: #909399;
        }
      }

      &.active .timeline-dot {
        box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
        border-color: #409eff;
        color: #409eff;
      }

      .timeline-content {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 180px;

        &.content-top {
          bottom: 60px;
        }

        &.content-bottom {
          top: 60px;
        }

        .event-card {
          background: white;
          border: 1px solid #e4e7ed;
          border-radius: 8px;
          padding: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          transition: all 0.3s ease;

          &:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
          }

          .event-title {
            font-weight: 600;
            color: #303133;
            margin-bottom: 4px;
            font-size: 14px;
          }

          .event-time {
            font-size: 12px;
            color: #909399;
            margin-bottom: 4px;
          }

          .event-user {
            font-size: 12px;
            color: #606266;
            margin-bottom: 4px;
          }

          .event-comment {
            font-size: 12px;
            color: #606266;
            margin-top: 4px;
            padding: 4px 8px;
            background: #f5f7fa;
            border-radius: 4px;
            border-left: 3px solid #409eff;
          }

          .event-action {
            margin-top: 4px;
          }

          .event-score {
            margin-top: 4px;

            :deep(.el-rate) {
              height: 16px;

              .el-rate__item {
                font-size: 12px;
              }

              .el-rate__text {
                font-size: 12px;
              }
            }
          }

          .event-detail {
            font-size: 12px;
            color: #909399;
            margin-top: 4px;
          }
        }
      }
    }
  }

  // 响应式设计
  @media (max-width: 768px) {
    .horizontal-timeline {
      padding: 20px 10px;

      .timeline-container {
        min-width: 600px;
        height: 160px;
      }

      .timeline-event {
        .timeline-dot {
          width: 32px;
          height: 32px;
          font-size: 14px;
        }

        .timeline-content {
          width: 140px;

          &.content-top {
            bottom: 50px;
          }

          &.content-bottom {
            top: 50px;
          }

          .event-card {
            padding: 8px;

            .event-title {
              font-size: 12px;
            }

            .event-time,
            .event-user,
            .event-comment,
            .event-detail {
              font-size: 11px;
            }
          }
        }
      }
    }
  }
</style>
