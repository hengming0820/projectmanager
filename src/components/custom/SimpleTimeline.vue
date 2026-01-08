<template>
  <div class="art-timeline">
    <div v-if="!timeline || timeline.length === 0" class="no-timeline">
      <el-empty description="暂无时间轴记录" />
    </div>
    <div v-else class="timeline-container">
      <!-- 时间轴线条 -->
      <div class="timeline-line">
        <div class="timeline-line-gradient"></div>
      </div>

      <!-- 时间轴节点 -->
      <div
        v-for="(event, index) in sortedTimeline"
        :key="index"
        class="timeline-event"
        :style="{ left: `${getEventPosition(index)}%` }"
      >
        <!-- 节点圆点 -->
        <div
          class="timeline-dot"
          :class="[
            event.type === 'reviewed' && event.action
              ? `dot-reviewed-${event.action}`
              : `dot-${event.type}`,
            { 'is-last': index === sortedTimeline.length - 1 }
          ]"
          @click="showEventDetail(event)"
        >
          <span class="dot-icon">{{ getEventIcon(event.type, event.action) }}</span>
          <!-- 脉动效果（最后一个节点） -->
          <span v-if="index === sortedTimeline.length - 1" class="dot-ripple"></span>
        </div>

        <!-- 事件卡片 -->
        <div
          class="timeline-content"
          :class="{
            'content-top': index % 2 === 0,
            'content-bottom': index % 2 === 1
          }"
        >
          <div class="event-card" @click="showEventDetail(event)">
            <!-- 卡片头部：图标+标题（包含审核结果） -->
            <div class="card-header">
              <span class="card-icon">{{ getEventIcon(event.type, event.action) }}</span>
              <span
                class="card-title"
                :class="{
                  'title-approve': event.type === 'reviewed' && event.action === 'approve',
                  'title-reject': event.type === 'reviewed' && event.action === 'reject'
                }"
              >
                {{ getEventTitle(event.type, event.action) }}
              </span>
            </div>

            <!-- 时间（更显目） -->
            <div class="card-time">
              {{ formatTime(event.time) }}
            </div>

            <!-- 用户信息 -->
            <div class="card-user">
              <div class="user-avatar">
                <span>{{ getUserInitial(event.user_name) }}</span>
              </div>
              <span class="user-name">{{ event.user_name || '系统' }}</span>
            </div>

            <!-- 附加信息提示 -->
            <div v-if="event.comment || getEventImages(event).length > 0" class="card-extras">
              <span v-if="event.comment" class="extra-badge"> 💬 有备注 </span>
              <span v-if="getEventImages(event).length > 0" class="extra-badge">
                📷 {{ getEventImages(event).length }}张
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 事件详情弹窗 -->
    <teleport to="body">
      <el-dialog
        v-model="showDetailDialog"
        :title="detailEvent ? getEventTitle(detailEvent.type, detailEvent.action) : '事件详情'"
        width="600px"
        :close-on-click-modal="true"
        :z-index="9999"
        class="art-timeline-detail-dialog"
        :modal="false"
        destroy-on-close
      >
        <div v-if="detailEvent" class="event-detail-content">
          <!-- 基本信息 -->
          <div class="detail-section">
            <div class="detail-row">
              <span class="detail-label">
                <i>{{ getEventIcon(detailEvent.type, detailEvent.action) }}</i> 事件类型
              </span>
              <span class="detail-value">{{
                getEventTitle(detailEvent.type, detailEvent.action)
              }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label"> <i>⏰</i> 时间 </span>
              <span class="detail-value">{{ formatDetailTime(detailEvent.time) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label"> <i>👤</i> 操作人 </span>
              <span class="detail-value">{{ detailEvent.user_name || '系统' }}</span>
            </div>
          </div>

          <!-- 操作结果 -->
          <div v-if="detailEvent.action" class="detail-section">
            <h4 class="section-title">
              <i>{{ detailEvent.action === 'approve' ? '✓' : '✗' }}</i> 操作结果
            </h4>
            <div class="action-info">
              <el-tag
                :type="detailEvent.action === 'approve' ? 'success' : 'danger'"
                size="large"
                effect="dark"
              >
                {{ detailEvent.action === 'approve' ? '✓ 审核通过' : '✗ 审核驳回' }}
              </el-tag>
              <span v-if="detailEvent.score !== undefined" class="score-display">
                评分：<strong>{{ detailEvent.score }}</strong> 分
              </span>
            </div>
          </div>

          <!-- 备注内容 -->
          <div v-if="detailEvent.comment" class="detail-section">
            <h4 class="section-title"> <i>💭</i> 备注内容 </h4>
            <div class="comment-content">
              {{ detailEvent.comment }}
            </div>
          </div>

          <!-- 截图预览 -->
          <div v-if="detailEventImages.length" class="detail-section">
            <h4 class="section-title">
              <i>🖼</i> {{ getImagesSectionTitle(detailEvent.type) }} ({{
                detailEventImages.length
              }})
            </h4>
            <div class="images-grid">
              <el-image
                v-for="(img, idx) in detailEventImages"
                :key="img.id || img.url || idx"
                :src="getImageUrl(img)"
                :preview-src-list="detailEventImageUrls"
                :initial-index="idx"
                fit="cover"
                class="preview-image"
                lazy
              >
                <template #error>
                  <div class="image-error">
                    <i>🖼️</i>
                    <span>加载失败</span>
                  </div>
                </template>
              </el-image>
            </div>
          </div>

          <!-- 器官数量（仅在详情中显示） -->
          <div v-if="detailEvent.organ_count" class="detail-section">
            <h4 class="section-title"> <i>📊</i> 标注信息 </h4>
            <div class="detail-row">
              <span class="detail-label">标注器官数</span>
              <span class="detail-value"
                ><strong>{{ detailEvent.organ_count }}</strong> 个</span
              >
            </div>
          </div>
        </div>

        <template #footer>
          <el-button @click="showDetailDialog = false">关闭</el-button>
        </template>
      </el-dialog>
    </teleport>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, watch, nextTick } from 'vue'

  interface TimelineEvent {
    type: string
    time: string
    user_id?: string
    user_name?: string
    comment?: string
    action?: string
    score?: number
    organ_count?: number
    images?: string[] // 添加图片数组
  }

  interface Props {
    timeline: TimelineEvent[]
    currentStatus?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    timeline: () => [],
    currentStatus: ''
  })

  // 处理时间轴事件，确保按时间排序
  const sortedTimeline = computed(() => {
    if (!props.timeline || props.timeline.length === 0) return []

    // 按时间排序
    return [...props.timeline].sort(
      (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime()
    )
  })

  // 获取事件位置
  const getEventPosition = (index: number) => {
    const totalEvents = sortedTimeline.value.length
    if (totalEvents <= 1) return 50 // 单个事件居中显示

    // 为边界留出空间，避免节点被截断
    const margin = 8 // 左右各留8%的边距
    const availableWidth = 100 - margin * 2

    if (totalEvents === 2) {
      // 两个事件：在可用空间内分布
      return index === 0 ? margin + availableWidth * 0.2 : margin + availableWidth * 0.8
    }

    // 多个事件：在可用空间内均匀分布
    const position = margin + (index / (totalEvents - 1)) * availableWidth
    return position
  }

  // 获取事件图标（统一使用纯色字符）
  const getEventIcon = (type: string, action?: string) => {
    // 如果是审核事件，根据审核结果返回不同图标
    if (type === 'reviewed') {
      return action === 'approve' ? '✓' : '✗'
    }

    const iconMap: Record<string, string> = {
      created: '➕',
      claimed: '👋',
      started: '▶',
      submitted: '📤',
      reviewed: '✓',
      restarted: '↻',
      skip_requested: '⏭',
      skip_approved: '✓',
      skip_rejected: '✗'
    }
    return iconMap[type] || '•'
  }

  // 获取事件标题
  const getEventTitle = (type: string, action?: string) => {
    // 如果是审核事件，根据审核结果返回不同标题
    if (type === 'reviewed') {
      return action === 'approve' ? '审核通过' : '审核未通过'
    }

    const titleMap: Record<string, string> = {
      created: '创建任务',
      claimed: '领取任务',
      started: '开始标注',
      submitted: '提交审核',
      reviewed: '审核结果',
      restarted: '重新开始',
      skip_requested: '跳过申请',
      skip_approved: '跳过批准',
      skip_rejected: '跳过驳回'
    }
    return titleMap[type] || type
  }

  // 格式化时间（简短）
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

  // 格式化时间（详细）
  const formatDetailTime = (time: string) => {
    if (!time) return ''
    const date = new Date(time)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // 获取用户名首字母
  const getUserInitial = (userName?: string) => {
    if (!userName || userName === '系统') return '系'
    return userName.charAt(0).toUpperCase()
  }

  // 详情弹窗
  const showDetailDialog = ref(false)
  const detailEvent = ref<TimelineEvent | null>(null)

  // 缓存当前详情事件的图片列表
  const detailEventImages = computed(() => getEventImages(detailEvent.value))

  // 缓存当前详情事件的图片URL列表（用于预览）
  const detailEventImageUrls = computed(() =>
    detailEventImages.value.map((img) => getImageUrl(img))
  )

  // 显示事件详情
  const showEventDetail = (event: TimelineEvent) => {
    detailEvent.value = event
    showDetailDialog.value = true

    // 确保弹窗打开后，强制设置正确的z-index
    nextTick(() => {
      const dialogWrapper = document.querySelector('.art-timeline-detail-dialog') as HTMLElement
      if (dialogWrapper) {
        dialogWrapper.style.zIndex = '9999'
        console.log('✅ [Timeline] 设置时间轴详情弹窗z-index:', 9999)
      }
    })
  }

  // 记录是否已设置图片预览器的z-index
  let viewerZIndexSet = false
  let observer: MutationObserver | null = null

  // 监听图片预览器的出现，确保z-index正确
  watch(showDetailDialog, (newVal) => {
    if (newVal) {
      viewerZIndexSet = false

      nextTick(() => {
        // 清除之前的观察器
        if (observer) {
          observer.disconnect()
        }

        // 监听图片预览器
        observer = new MutationObserver((mutations) => {
          // 如果已经设置过了，就不再处理
          if (viewerZIndexSet) return

          const viewer = document.querySelector('.el-image-viewer__wrapper') as HTMLElement
          if (viewer) {
            // 标记为已设置，避免重复执行
            viewerZIndexSet = true

            viewer.style.zIndex = '10000'
            viewer.style.position = 'fixed'
            console.log('✅ [Timeline] 设置图片预览器z-index:', 10000)

            // 设置关闭按钮和工具栏
            const closeBtn = document.querySelector('.el-image-viewer__close') as HTMLElement
            const actions = document.querySelector('.el-image-viewer__actions') as HTMLElement
            const mask = document.querySelector('.el-image-viewer__mask') as HTMLElement

            if (closeBtn) {
              closeBtn.style.zIndex = '10001'
              closeBtn.style.position = 'fixed'
            }
            if (actions) {
              actions.style.zIndex = '10001'
              actions.style.position = 'fixed'
            }
            if (mask) {
              mask.style.zIndex = '9998'
            }

            // 断开观察器
            if (observer) {
              observer.disconnect()
              observer = null
            }
          }
        })

        observer.observe(document.body, {
          childList: true,
          subtree: false // 只监听直接子节点，减少性能消耗
        })

        // 10秒后强制断开
        setTimeout(() => {
          if (observer) {
            observer.disconnect()
            observer = null
          }
        }, 10000)
      })
    } else {
      // 弹窗关闭时，重置标记和断开观察器
      viewerZIndexSet = false
      if (observer) {
        observer.disconnect()
        observer = null
      }
    }
  })

  // 临时开关：是否启用时间范围匹配（调试用）
  const USE_TIME_RANGE_MATCHING = true

  // 获取事件的图片列表（根据时间范围匹配，避免多次提交/审核的混淆）
  const getEventImages = (event: TimelineEvent | null): any[] => {
    if (!event) return []

    // 如果已经有images字段，直接返回（去重）
    if ((event as any).images && Array.isArray((event as any).images)) {
      console.log('📷 [Timeline] 使用已有的images字段:', (event as any).images)
      // 对已有images进行去重
      const uniqueImages = Array.from(
        new Map(
          (event as any).images.map((img: any) => {
            const url = typeof img === 'string' ? img : img.url || img.file_url
            return [url, img]
          })
        ).values()
      )
      console.log(
        '✨ [Timeline] 去重后images:',
        uniqueImages.length,
        '原始:',
        (event as any).images.length
      )
      return uniqueImages
    }

    // 根据事件类型从attachments中提取对应的图片
    const attachments = (event as any).attachments || []
    if (!Array.isArray(attachments) || attachments.length === 0) {
      console.log('⚠️ [Timeline] 事件无attachments:', event.type)
      return []
    }

    console.log('📦 [Timeline] 事件attachments总数:', attachments.length, '事件类型:', event.type)
    console.log('🔧 [Timeline] 时间范围匹配:', USE_TIME_RANGE_MATCHING ? '启用' : '禁用')

    // 根据事件类型确定要查找的图片类型
    let targetType = ''
    switch (event.type) {
      case 'submitted':
        targetType = 'annotation_screenshot'
        break
      case 'reviewed':
        targetType = 'review_screenshot'
        break
      case 'skip_requested':
        targetType = 'skip_screenshot'
        break
      default:
        console.log('ℹ️ [Timeline] 事件类型无对应截图:', event.type)
        return []
    }

    console.log('🎯 [Timeline] 查找截图类型:', targetType)

    // 如果禁用时间范围匹配，直接按类型过滤（旧逻辑）
    if (!USE_TIME_RANGE_MATCHING) {
      console.log('ℹ️ [Timeline] 使用简单类型匹配（旧逻辑）')
      const images = attachments
        .filter((att: any) => att && att.attachment_type === targetType)
        .map((att: any) => ({
          url: att.file_url,
          name: att.file_name,
          id: att.id,
          created_at: att.created_at
        }))

      const uniqueImages = Array.from(new Map(images.map((img) => [img.url, img])).values())

      console.log('✅ [Timeline] 找到匹配截图（按类型）:', uniqueImages.length)
      return uniqueImages
    }

    // 获取当前事件的时间和下一个同类型事件的时间
    const currentEventTime = new Date(event.time).getTime()

    // 在timeline中找到当前事件的位置和下一个同类型事件
    const timeline = props.timeline || []

    console.log('🔎 [Timeline] 开始查找当前事件在timeline中的位置')
    console.log('📋 [Timeline] Timeline总事件数:', timeline.length)
    console.log('🎯 [Timeline] 当前事件信息:', {
      type: event.type,
      time: event.time,
      user_id: event.user_id
    })

    // 打印所有timeline事件
    timeline.forEach((e, idx) => {
      console.log(`  ${idx}. ${e.type} @ ${e.time} by ${e.user_name}`)
    })

    const currentEventIndex = timeline.findIndex(
      (e) => e.time === event.time && e.type === event.type && e.user_id === event.user_id
    )

    console.log('✅ [Timeline] 当前事件索引:', currentEventIndex)

    if (currentEventIndex === -1) {
      console.error('❌ [Timeline] 在timeline中找不到当前事件！将回退到简单匹配')
      // 回退到简单类型匹配
      const images = attachments
        .filter((att: any) => att && att.attachment_type === targetType)
        .map((att: any) => ({
          url: att.file_url,
          name: att.file_name,
          id: att.id,
          created_at: att.created_at
        }))
      return Array.from(new Map(images.map((img) => [img.url, img])).values())
    }

    // 找下一个同类型的事件作为时间上限（关键：按时间排序）
    let nextEventTime: number | null = null
    let nextEventIndex: number | null = null

    console.log('🔍 [Timeline] 开始查找下一个同类型事件，从索引', currentEventIndex + 1, '开始')

    for (let i = currentEventIndex + 1; i < timeline.length; i++) {
      console.log(`  检查事件 ${i}: ${timeline[i].type} @ ${timeline[i].time}`)
      if (timeline[i].type === event.type) {
        nextEventTime = new Date(timeline[i].time).getTime()
        nextEventIndex = i
        console.log('✅ [Timeline] 找到下一个同类型事件:', {
          index: i,
          type: timeline[i].type,
          time: timeline[i].time,
          gap: ((nextEventTime - currentEventTime) / 1000 / 60).toFixed(2) + '分钟'
        })
        break
      }
    }

    // 如果没有找到下一个同类型事件
    if (nextEventTime === null) {
      console.log('⚠️ [Timeline] 没有找到下一个同类型事件')

      // 使用下一个任意事件的时间作为保守上限
      if (currentEventIndex < timeline.length - 1) {
        nextEventTime = new Date(timeline[currentEventIndex + 1].time).getTime()
        nextEventIndex = currentEventIndex + 1
        console.log('📌 [Timeline] 使用下一个任意事件作为上限:', {
          index: nextEventIndex,
          type: timeline[nextEventIndex].type,
          time: timeline[nextEventIndex].time
        })
      } else {
        console.log('ℹ️ [Timeline] 这是最后一个事件，无上限')
      }
    }

    console.log('📅 [Timeline] 最终时间范围:', {
      事件时间: event.time,
      当前事件索引: currentEventIndex,
      下一个事件索引: nextEventIndex,
      时间下限: new Date(currentEventTime).toISOString(),
      时间上限: nextEventTime ? new Date(nextEventTime).toISOString() : '无限制',
      时间窗口: nextEventTime
        ? ((nextEventTime - currentEventTime) / 1000 / 60).toFixed(2) + '分钟'
        : '无限'
    })

    // 提取对应类型的所有图片，并计算它们与当前事件的时间差（就近匹配算法）
    const candidateImages = attachments
      .filter((att: any) => att && att.attachment_type === targetType)
      .map((att: any) => {
        // 如果attachment没有created_at字段，给一个极大的时间差（兼容旧数据，但优先级最低）
        if (!att.created_at) {
          console.warn('⚠️ [Timeline] Attachment缺少created_at字段，将以最低优先级匹配:', {
            id: att.id,
            url: att.file_url?.substring(0, 50) + '...'
          })
          return {
            attachment: att,
            time: 0,
            timeDiff: Number.MAX_SAFE_INTEGER
          }
        }

        // 处理时区问题：如果created_at没有时区后缀，强制按UTC解析
        let attTimeStr = att.created_at
        const hasTimezone =
          attTimeStr.includes('Z') || attTimeStr.includes('+') || attTimeStr.match(/\-\d{2}:\d{2}$/)

        if (!hasTimezone) {
          attTimeStr = attTimeStr + 'Z'
          console.log('🕐 [Timeline] Attachment时间缺少时区，添加Z后缀:', {
            原始: att.created_at,
            转换后: attTimeStr
          })
        }

        const attTime = new Date(attTimeStr).getTime()
        const timeDiff = Math.abs(attTime - currentEventTime) // 计算时间差的绝对值

        return {
          attachment: att,
          time: attTime,
          timeDiff: timeDiff
        }
      })

    // 按时间差排序，找到最接近的截图
    candidateImages.sort((a, b) => a.timeDiff - b.timeDiff)

    console.log(
      '🎯 [Timeline] 候选截图（按时间差排序）:',
      candidateImages.map((ci, idx) => ({
        排序: idx + 1,
        id: ci.attachment.id,
        time: ci.time ? new Date(ci.time).toISOString() : '无时间',
        timeDiff:
          ci.timeDiff === Number.MAX_SAFE_INTEGER
            ? '无限大'
            : (ci.timeDiff / 1000).toFixed(2) + '秒'
      }))
    )

    // 选择时间差最小的截图作为当前事件的截图
    // 容错时间：如果最接近的截图时间差大于60秒，则不匹配
    const tolerance = 60 * 1000 // 60秒容错
    const images = candidateImages
      .filter((ci, idx) => {
        // 必须在容错范围内
        if (ci.timeDiff > tolerance) {
          console.log(`❌ [Timeline] 截图${idx + 1}时间差过大，超过容错范围:`, {
            id: ci.attachment.id,
            时间差: (ci.timeDiff / 1000).toFixed(2) + '秒',
            容错范围: tolerance / 1000 + '秒'
          })
          return false
        }

        // 只保留时间差最小的一组（如果有多个截图时间非常接近当前事件）
        if (candidateImages.length === 0) return false
        const minDiff = candidateImages[0].timeDiff
        // 如果时间差与最小时间差的差值小于5秒，则认为是同一组
        const isSameGroup = ci.timeDiff - minDiff < 5000

        console.log('🔍 [Timeline] 检查attachment:', {
          id: ci.attachment.id,
          type: ci.attachment.attachment_type,
          created_at: ci.attachment.created_at || '❌ 缺失',
          url: ci.attachment.file_url?.substring(0, 50) + '...',
          时间对比: {
            attachment时间: ci.time ? new Date(ci.time).toISOString() : '无',
            事件时间: new Date(currentEventTime).toISOString(),
            时间差: (ci.timeDiff / 1000).toFixed(2) + '秒',
            最小时间差: (minDiff / 1000).toFixed(2) + '秒',
            与最小差值: ((ci.timeDiff - minDiff) / 1000).toFixed(2) + '秒'
          },
          匹配结果: isSameGroup ? '✅ 匹配（时间最近）' : '❌ 不匹配（时间较远）'
        })

        return isSameGroup
      })
      .map((ci) => ({
        url: ci.attachment.file_url,
        name: ci.attachment.file_name,
        id: ci.attachment.id,
        created_at: ci.attachment.created_at
      }))

    // 根据URL去重（使用Map保证唯一性）
    const uniqueImages = Array.from(new Map(images.map((img) => [img.url, img])).values())

    console.log(
      '✅ [Timeline] 找到时间范围内的截图:',
      uniqueImages.length,
      '过滤前:',
      images.length
    )

    // 如果没有找到任何图片，打印详细的诊断信息
    if (uniqueImages.length === 0) {
      console.error('❌ [Timeline] 未找到任何匹配的截图！诊断信息:', {
        事件类型: event.type,
        目标attachment类型: targetType,
        事件时间: event.time,
        时间范围: {
          下限: new Date(currentEventTime).toISOString(),
          上限: nextEventTime ? new Date(nextEventTime).toISOString() : '无限制'
        },
        attachments总数: attachments.length,
        类型匹配的数量: attachments.filter((att: any) => att && att.attachment_type === targetType)
          .length,
        有created_at的数量: attachments.filter((att: any) => att && att.created_at).length,
        建议: '请检查attachment的created_at字段是否存在，或临时设置USE_TIME_RANGE_MATCHING=false'
      })

      // 打印所有attachments的详细信息
      console.log('📋 [Timeline] 所有attachments详情:')
      attachments.forEach((att: any, idx: number) => {
        console.log(`  ${idx + 1}.`, {
          id: att.id,
          type: att.attachment_type,
          created_at: att.created_at || '❌ 缺失',
          url: att.file_url?.substring(0, 60) + '...'
        })
      })
    }

    if (uniqueImages.length !== images.length) {
      console.warn('⚠️ [Timeline] 检测到重复图片！', {
        原始数量: images.length,
        去重后数量: uniqueImages.length,
        重复图片: images.filter((img, idx, arr) => arr.findIndex((i) => i.url === img.url) !== idx)
      })
    }

    return uniqueImages
  }

  // 获取图片URL
  const getImageUrl = (img: any): string => {
    let url = ''
    if (typeof img === 'string') {
      url = img
    } else {
      url = img.url || img.file_url || ''
    }

    // 调试日志
    console.log('🖼️ [Timeline] 原始图片URL:', url)

    // 如果是MinIO直链，转换为代理URL
    if (url && url.includes('/medical-annotations/')) {
      // 将 http://192.168.200.20:9000/medical-annotations/xxx 转换为 /api/files/xxx
      const convertedUrl = url.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/')
      console.log('🔄 [Timeline] 转换后URL:', convertedUrl)
      return convertedUrl
    }

    // 如果是相对路径，保持不变
    if (url && url.startsWith('/')) {
      console.log('✅ [Timeline] 使用相对路径:', url)
      return url
    }

    console.log('⚠️ [Timeline] 未识别的URL格式:', url)
    return url
  }

  // 获取图片区域标题
  const getImagesSectionTitle = (type: string): string => {
    const titleMap: Record<string, string> = {
      submitted: '标注截图',
      reviewed: '审核截图',
      skip_requested: '跳过申请截图',
      skip_approved: '跳过审核截图',
      skip_rejected: '跳过审核截图'
    }
    return titleMap[type] || '相关截图'
  }
</script>

<style scoped lang="scss">
  .art-timeline {
    width: 100%;
    padding: 15px 10px;
    overflow-x: auto;
    overflow-y: visible;

    /* 确保内容不被裁剪 */
    min-height: 300px;

    .no-timeline {
      text-align: center;
      padding: 30px 0;
    }

    .timeline-container {
      position: relative;
      min-width: 600px;
      height: 380px;
      margin: 0 auto;
      padding-top: 15px;
      padding-bottom: 15px;
    }

    .timeline-line {
      position: absolute;
      top: 50%;
      left: 8%;
      right: 8%;
      height: 3px;
      transform: translateY(-50%);
      z-index: 1;
      border-radius: 2px;
      background: var(--art-border-color);

      .timeline-line-gradient {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(
          to right,
          transparent,
          var(--art-primary-color) 50%,
          transparent
        );
        opacity: 0.5;
        border-radius: 2px;
      }
    }

    .timeline-event {
      position: absolute;
      top: 50%;
      transform: translateX(-50%);
      z-index: 2;

      .timeline-dot {
        position: relative;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--art-main-bg-color);
        border: 3px solid var(--art-border-color);
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(-50%);
        box-shadow:
          0 2px 8px rgba(0, 0, 0, 0.1),
          0 0 0 0 rgba(var(--art-primary-rgb), 0);
        cursor: pointer;
        z-index: 3;

        .dot-icon {
          font-size: 18px;
          font-weight: 700;
          transition: transform 0.3s ease;
          filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.15));
        }

        /* 最后一个节点的脉动效果 */
        &.is-last {
          animation: dotPulse 2s ease-in-out infinite;

          .dot-ripple {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid var(--art-primary-color);
            animation: ripple 2s ease-out infinite;
          }
        }

        &:hover {
          transform: translateY(-50%) scale(1.15);
          box-shadow:
            0 4px 16px rgba(0, 0, 0, 0.15),
            0 0 0 4px rgba(var(--art-primary-rgb), 0.2);

          .dot-icon {
            transform: scale(1.1);
          }
        }

        &.dot-created {
          border-color: var(--art-primary-color);
          color: var(--art-primary-color);
          background: linear-gradient(
            135deg,
            rgba(var(--art-primary-rgb), 0.2),
            rgba(var(--art-primary-rgb), 0.05)
          );
          box-shadow: 0 3px 12px rgba(var(--art-primary-rgb), 0.35);
        }

        &.dot-claimed {
          border-color: #48bb78;
          color: #48bb78;
          background: linear-gradient(135deg, rgba(72, 187, 120, 0.2), rgba(72, 187, 120, 0.05));
          box-shadow: 0 3px 12px rgba(72, 187, 120, 0.35);
        }

        &.dot-started {
          border-color: #ed8936;
          color: #ed8936;
          background: linear-gradient(135deg, rgba(237, 137, 54, 0.2), rgba(237, 137, 54, 0.05));
          box-shadow: 0 3px 12px rgba(237, 137, 54, 0.35);
        }

        &.dot-submitted {
          border-color: #f59e0b;
          color: #f59e0b;
          background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05));
          box-shadow: 0 3px 12px rgba(245, 158, 11, 0.35);
        }

        &.dot-reviewed {
          border-color: #10b981;
          color: #10b981;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
          box-shadow: 0 3px 12px rgba(16, 185, 129, 0.35);
        }

        &.dot-reviewed-approve {
          border-color: #10b981;
          color: #10b981;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
          box-shadow: 0 3px 12px rgba(16, 185, 129, 0.35);
        }

        &.dot-reviewed-reject {
          border-color: #ef4444;
          color: #ef4444;
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05));
          box-shadow: 0 3px 12px rgba(239, 68, 68, 0.35);
        }

        &.dot-restarted {
          border-color: #8b5cf6;
          color: #8b5cf6;
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.05));
          box-shadow: 0 3px 12px rgba(139, 92, 246, 0.35);
        }

        &.dot-skip_requested {
          border-color: #f59e0b;
          color: #f59e0b;
          background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05));
          box-shadow: 0 3px 12px rgba(245, 158, 11, 0.35);
        }

        &.dot-skip_approved {
          border-color: #10b981;
          color: #10b981;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
          box-shadow: 0 3px 12px rgba(16, 185, 129, 0.35);
        }

        &.dot-skip_rejected {
          border-color: #ef4444;
          color: #ef4444;
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05));
          box-shadow: 0 3px 12px rgba(239, 68, 68, 0.35);
        }
      }

      /* 脉动动画 */
      @keyframes dotPulse {
        0%,
        100% {
          transform: translateY(-50%) scale(1);
        }
        50% {
          transform: translateY(-50%) scale(1.05);
        }
      }

      /* 涟漪动画 */
      @keyframes ripple {
        0% {
          transform: scale(1);
          opacity: 0.6;
        }
        100% {
          transform: scale(2);
          opacity: 0;
        }
      }

      .timeline-content {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 165px;
        z-index: 5;

        &.content-top {
          bottom: 55px;
        }

        &.content-bottom {
          top: 55px;
        }

        .event-card {
          background: var(--art-card-bg-color);
          border: 1px solid var(--art-card-border);
          border-radius: 8px;
          padding: 10px;
          box-shadow:
            0 2px 8px rgba(0, 0, 0, 0.08),
            0 0 0 1px rgba(var(--art-primary-rgb), 0);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          font-size: 12px;
          backdrop-filter: blur(10px);
          cursor: pointer;

          &:hover {
            box-shadow:
              0 6px 20px rgba(0, 0, 0, 0.15),
              0 0 0 2px rgba(var(--art-primary-rgb), 0.3);
            transform: translateY(-3px);
            border-color: rgba(var(--art-primary-rgb), 0.5);

            .view-detail-hint {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .card-header {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;

            .card-icon {
              font-size: 16px;
              line-height: 1;
              flex-shrink: 0;
              font-weight: 700;
              display: flex;
              align-items: center;
              justify-content: center;
              width: 20px;
              height: 20px;
              color: var(--art-text-gray-700);
            }

            &:has(.title-approve) .card-icon {
              color: #10b981;
            }

            &:has(.title-reject) .card-icon {
              color: #ef4444;
            }

            .card-title {
              font-weight: 600;
              color: var(--art-text-gray-900);
              font-size: 13px;
              flex: 1;

              &.title-approve {
                color: #10b981;
                font-weight: 700;
              }

              &.title-reject {
                color: #ef4444;
                font-weight: 700;
              }
            }
          }

          .card-time {
            font-size: 13px;
            font-weight: 800;
            color: var(--art-primary-color);
            font-family: 'Courier New', monospace;
            margin-bottom: 8px;
            padding: 4px 0;
            text-shadow: 0 0 10px rgba(var(--art-primary-rgb), 0.4);
            letter-spacing: 0.5px;
          }

          .card-user {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;

            .user-avatar {
              width: 24px;
              height: 24px;
              border-radius: 50%;
              background: linear-gradient(
                135deg,
                var(--art-primary-color),
                rgba(var(--art-primary-rgb), 0.7)
              );
              display: flex;
              align-items: center;
              justify-content: center;
              color: #ffffff !important;
              font-size: 13px;
              font-weight: 800;
              flex-shrink: 0;
              box-shadow: 0 3px 12px rgba(var(--art-primary-rgb), 0.4);
              border: 2px solid rgba(255, 255, 255, 0.95);

              span {
                color: #ffffff !important;
                text-shadow:
                  0 1px 3px rgba(0, 0, 0, 0.6),
                  0 0 6px rgba(0, 0, 0, 0.4);
                font-family:
                  -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial',
                  sans-serif;
                line-height: 1;
              }
            }

            .user-name {
              font-size: 12px;
              color: var(--art-text-gray-700);
              font-weight: 500;
              flex: 1;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }

          .card-extras {
            display: flex;
            gap: 6px;
            margin-top: 8px;
            flex-wrap: wrap;

            .extra-badge {
              font-size: 11px;
              color: var(--art-text-gray-700);
              font-weight: 500;
              padding: 3px 8px;
              background: linear-gradient(135deg, var(--art-bg-color), var(--art-main-bg-color));
              border: 1px solid var(--art-border-color);
              border-radius: 12px;
              transition: all 0.2s ease;

              &:hover {
                border-color: var(--art-primary-color);
                color: var(--art-primary-color);
                transform: translateY(-1px);
              }
            }
          }
        }
      }
    }
  }

  // 响应式设计
  @media (max-width: 768px) {
    .art-timeline {
      padding: 20px 5px;

      .timeline-container {
        min-width: 500px;
        height: 180px;
      }

      .timeline-event {
        .timeline-dot {
          width: 30px;
          height: 30px;
          font-size: 14px;

          .dot-icon {
            font-size: 12px;
          }
        }

        .timeline-content {
          width: 140px;

          &.content-top {
            bottom: 55px;
          }

          &.content-bottom {
            top: 25px;
          }

          .event-card {
            padding: 8px;

            .event-header {
              .event-title {
                font-size: 11px;
              }

              .event-time {
                font-size: 10px;
              }
            }

            .event-user {
              font-size: 10px;
            }

            .event-detail,
            .event-comment-trigger .comment-text {
              font-size: 10px;
            }

            .event-action .event-score {
              font-size: 10px;
            }
          }
        }
      }
    }
  }

  @media (max-width: 480px) {
    .art-timeline {
      .timeline-container {
        min-width: 400px;
        height: 160px;
      }

      .timeline-event {
        .timeline-dot {
          width: 28px;
          height: 28px;
        }

        .timeline-content {
          width: 110px;

          .event-card {
            padding: 6px;

            .event-header {
              .event-title {
                font-size: 10px;
              }

              .event-time {
                font-size: 9px;
              }
            }

            .event-user {
              font-size: 9px;

              .user-avatar {
                width: 16px;
                height: 16px;
                font-size: 8px;
              }
            }

            .event-detail,
            .event-comment-trigger .comment-text {
              font-size: 9px;
            }
          }
        }
      }
    }
  }

  /* 详情弹窗样式 */
  :deep(.art-timeline-detail-dialog) {
    .el-dialog__header {
      background: linear-gradient(
        135deg,
        var(--art-primary-color),
        rgba(var(--art-primary-rgb), 0.8)
      );
      color: white;
      padding: 16px 20px;
      margin: 0;
      border-radius: 8px 8px 0 0;

      .el-dialog__title {
        color: white;
        font-weight: 600;
        font-size: 16px;
      }

      .el-dialog__headerbtn {
        top: 16px;

        .el-dialog__close {
          color: white;
          font-size: 18px;

          &:hover {
            color: rgba(255, 255, 255, 0.8);
          }
        }
      }
    }

    .el-dialog__body {
      padding: 20px;
      background: var(--art-main-bg-color);
    }

    .el-dialog__footer {
      padding: 12px 20px;
      background: var(--art-bg-color);
      border-top: 1px solid var(--art-border-color);
    }
  }

  .event-detail-content {
    .detail-section {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .section-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        font-weight: 600;
        color: var(--art-text-gray-900);
        margin: 0 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--art-primary-color);

        i {
          font-size: 16px;
          font-style: normal;
          font-weight: 700;
          color: var(--art-primary-color);
        }
      }

      .detail-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        background: var(--art-card-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: 6px;
        margin-bottom: 8px;
        transition: all 0.3s ease;

        &:hover {
          background: rgba(var(--art-primary-rgb), 0.05);
          border-color: rgba(var(--art-primary-rgb), 0.3);
        }

        &:last-child {
          margin-bottom: 0;
        }

        .detail-label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: var(--art-text-gray-600);
          font-weight: 500;

          i {
            font-size: 16px;
            font-style: normal;
            font-weight: 700;
            color: var(--art-primary-color);
          }
        }

        .detail-value {
          font-size: 13px;
          color: var(--art-text-gray-900);
          font-weight: 600;
          text-align: right;

          strong {
            color: var(--art-primary-color);
            font-size: 16px;
          }
        }
      }

      .action-info {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: var(--art-card-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: 6px;

        .score-display {
          font-size: 13px;
          color: var(--art-text-gray-700);

          strong {
            color: var(--art-primary-color);
            font-size: 16px;
            margin: 0 2px;
          }
        }
      }

      .comment-content {
        padding: 12px;
        background: var(--art-card-bg-color);
        border: 1px solid var(--art-card-border);
        border-left: 3px solid var(--art-primary-color);
        border-radius: 6px;
        font-size: 13px;
        line-height: 1.6;
        color: var(--art-text-gray-800);
        white-space: pre-wrap;
        word-break: break-word;
      }

      .images-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 12px;

        .preview-image {
          width: 100%;
          height: 120px;
          border-radius: 6px;
          overflow: hidden;
          border: 2px solid var(--art-card-border);
          cursor: pointer;
          position: relative;
          z-index: 1;

          /* 简化hover效果，避免触发重绘 */
          &:hover {
            border-color: var(--art-primary-color);
          }

          :deep(img) {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .image-error {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--art-bg-color);
            color: var(--art-text-gray-500);
            font-size: 12px;
            gap: 4px;

            i {
              font-size: 24px;
              opacity: 0.5;
            }
          }
        }
      }
    }
  }
</style>

<style lang="scss">
  /* 全局tooltip样式 */
  .art-timeline-tooltip {
    max-width: 300px !important;
    padding: 8px 12px !important;
    font-size: 12px !important;
    line-height: 1.6 !important;
    border-radius: 6px !important;
    background: var(--art-text-gray-900) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;

    .el-popper__arrow::before {
      background: var(--art-text-gray-900) !important;
    }
  }

  /* 确保图片预览器在最上层，避免与dialog冲突 */
  .el-image-viewer__wrapper {
    z-index: 10000 !important;
    position: fixed !important;
    background-color: rgba(0, 0, 0, 0.3) !important;
  }

  /* Element Plus 图片查看器的关闭按钮 */
  .el-image-viewer__close {
    z-index: 10001 !important;
    position: fixed !important;
  }

  /* Element Plus 图片查看器的工具栏 */
  .el-image-viewer__actions {
    z-index: 10001 !important;
    position: fixed !important;
  }

  /* Element Plus 图片查看器的遮罩层 */
  .el-image-viewer__mask {
    z-index: 9998 !important;
    background-color: rgba(0, 0, 0, 0.3) !important;
  }

  /* 修复图片查看器显示问题 - 画布容器允许滚动 */
  .el-image-viewer__canvas {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: auto !important;

    img {
      filter: none !important;
      opacity: 1 !important;
      max-width: none !important;
      max-height: none !important;
      width: auto !important;
      height: auto !important;
      margin: auto !important;
      display: block !important;
      object-fit: contain !important;
    }
  }

  /* 修复图片容器样式 */
  .el-image-viewer__img {
    filter: none !important;
    opacity: 1 !important;
    max-width: none !important;
    max-height: none !important;
  }

  /* 滚动条样式 */
  .el-image-viewer__canvas::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  .el-image-viewer__canvas::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  .el-image-viewer__canvas::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;

    &:hover {
      background: rgba(255, 255, 255, 0.5);
    }
  }

  /* 时间轴详情弹窗样式调整 */
  .art-timeline-detail-dialog {
    z-index: 9999 !important;

    .el-dialog__wrapper {
      z-index: 9999 !important;
    }

    .el-overlay {
      display: none !important;
    }
  }

  /* 确保时间轴弹窗中的dialog wrapper有正确的z-index */
  .el-dialog__wrapper.art-timeline-detail-dialog {
    z-index: 9999 !important;
  }

  /* 禁用el-image的hover效果，避免触发z-index变化 */
  .art-timeline-detail-dialog {
    .el-image {
      z-index: auto !important;

      &:hover {
        z-index: auto !important;
      }
    }
  }
</style>
