<template>
  <div class="my-workspace">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="我的工作台"
      description="管理我的标注任务，提交审核和查看进度"
      icon="💼"
      badge="Workspace"
      theme="green"
    >
      <template #actions>
        <el-button type="success" @click="refreshTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="5">
          <div class="stat-click" @click="quickFilter('in_progress')">
            <ArtStatsCard
              :count="taskStats.inProgress"
              title="进行中"
              description="正在标注的任务"
              icon="&#xe7b9;"
              icon-color="#e6a23c"
              icon-bg-color="#fdf6ec"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilter('submitted')">
            <ArtStatsCard
              :count="taskStats.submitted"
              title="待审核"
              description="等待审核的任务"
              icon="&#xe7c0;"
              icon-color="#f56c6c"
              icon-bg-color="#fef0f0"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilter('approved')">
            <ArtStatsCard
              :count="taskStats.completed"
              title="已完成"
              description="审核通过的任务"
              icon="&#xe7c1;"
              icon-color="#67c23a"
              icon-bg-color="#f0f9ff"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilter('rejected')">
            <ArtStatsCard
              :count="taskStats.rejected"
              title="已驳回"
              description="需要修订的任务"
              icon="&#xe7c2;"
              icon-color="#f56c6c"
              icon-bg-color="#fef0f0"
            />
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-click" @click="quickFilter('all')">
            <ArtStatsCard
              :count="taskStats.total"
              title="总计"
              description="所有任务数量"
              icon="&#xe721;"
              icon-color="#409eff"
              icon-bg-color="#ecf5ff"
            />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表（包含筛选） -->
    <el-card class="art-custom-card task-list-card">
      <template #header>
        <div class="card-header-with-tabs">
          <div class="header-title">
            <span class="title-text">我的任务</span>
            <span class="task-count">共 {{ filteredTasks.length }} 个任务</span>
          </div>

          <!-- 任务筛选标签 -->
          <div class="tabs-section">
            <el-tabs v-model="activeTab" @tab-change="handleTabChange">
              <el-tab-pane label="进行中" name="in_progress" />
              <el-tab-pane label="待审核" name="submitted" />
              <el-tab-pane label="已完成" name="approved" />
              <el-tab-pane label="已驳回" name="rejected" />
              <el-tab-pane label="全部" name="all" />
            </el-tabs>
          </div>
        </div>
      </template>
      <el-table
        v-loading="projectStore.loading"
        :data="filteredTasks"
        stripe
        height="calc(100vh - 520px)"
      >
        <!-- 任务标题 -->
        <el-table-column prop="title" label="任务标题" min-width="220" fixed>
          <template #default="{ row }">
            <div class="task-title-cell">
              <el-tooltip :content="row.title" placement="top" :show-after="500">
                <strong class="task-title-text">{{ row.title }}</strong>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 所属项目 -->
        <el-table-column prop="projectName" label="所属项目" min-width="200">
          <template #default="{ row }">
            <div class="project-name-cell">
              <el-icon class="project-icon"><Folder /></el-icon>
              <span
                v-if="row.projectName || row.project_name"
                class="project-name clickable"
                @click="navigateToProject(row)"
                style="
                  cursor: pointer;
                  color: #606266;
                  font-weight: 500;
                  text-decoration: underline;
                  text-decoration-color: rgba(0, 0, 0, 0.3);
                  text-underline-offset: 2px;
                "
              >
                {{ row.projectName || row.project_name }}
              </span>
              <span v-else class="text-gray-400">未指定项目</span>
            </div>
          </template>
        </el-table-column>

        <!-- 任务描述 -->
        <el-table-column prop="description" label="任务描述" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="description-cell">
              <span class="description-text">{{ row.description || '暂无描述' }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- 影像URL -->
        <el-table-column prop="imageUrl" label="影像URL" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.imageUrl || row.image_url" class="image-url-cell">
              <a :href="row.imageUrl || row.image_url" target="_blank" class="image-url-link">
                {{ row.imageUrl || row.image_url }}
              </a>
            </div>
            <span v-else class="text-gray-400">未设置</span>
          </template>
        </el-table-column>

        <!-- 项目分类 -->
        <el-table-column prop="category" label="项目分类" width="140">
          <template #default="{ row }">
            <CategoryTag
              :category="getTaskProjectCategory(row).category"
              :sub-category="getTaskProjectCategory(row).subCategory"
              size="small"
            />
          </template>
        </el-table-column>

        <!-- 任务状态 -->
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status) as any" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <!-- 主要操作按钮 -->
              <div class="primary-actions">
                <!-- 待分配状态 -->
                <template v-if="row.status === 'pending'">
                  <el-button type="primary" size="small" @click="startTask(row)">
                    领取任务
                  </el-button>
                </template>

                <!-- 已分配状态 -->
                <template v-else-if="row.status === 'assigned'">
                  <el-button type="primary" size="small" @click="startTask(row)">
                    开始标注
                  </el-button>
                </template>

                <!-- 进行中状态 -->
                <template v-else-if="row.status === 'in_progress'">
                  <el-button type="success" size="small" @click="submitTask(row)">
                    提交审核
                  </el-button>
                  <el-button
                    type="warning"
                    size="small"
                    @click="requestSkipTask(row)"
                    style="margin-left: 8px"
                  >
                    申请跳过
                  </el-button>
                </template>

                <!-- 已提交状态 -->
                <template v-else-if="row.status === 'submitted'">
                  <el-tag type="warning" size="small">
                    <el-icon><Clock /></el-icon>
                    待审核
                  </el-tag>
                </template>

                <!-- 已通过状态 -->
                <template v-else-if="row.status === 'approved'">
                  <el-tag type="success" size="small">
                    <el-icon><CircleCheck /></el-icon>
                    已完成
                  </el-tag>
                </template>

                <!-- 已驳回状态 -->
                <template v-else-if="row.status === 'rejected'">
                  <el-button type="warning" size="small" @click="viewRejectReason(row)">
                    查看原因
                  </el-button>
                  <el-button type="primary" size="small" @click="submitTask(row)">
                    重新提交
                  </el-button>
                </template>

                <!-- 跳过申请待审核状态 -->
                <template v-else-if="row.status === 'skip_pending'">
                  <el-tag type="warning" size="small">
                    <el-icon><Clock /></el-icon>
                    跳过审核中
                  </el-tag>
                </template>
              </div>

              <!-- 通用查看详情按钮 - 始终显示 -->
              <div class="secondary-actions">
                <el-button type="info" size="small" text @click="viewTaskDetail(row)">
                  查看详情
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 查看驳回原因对话框 -->
    <el-dialog
      v-model="showRejectDialog"
      width="700px"
      :z-index="2000"
      :append-to-body="true"
      :close-on-click-modal="false"
      class="art-reject-dialog"
      :show-close="false"
    >
      <!-- 自定义标题栏 -->
      <template #header>
        <div class="reject-dialog-header">
          <div class="header-left">
            <span class="header-icon">❌</span>
            <div class="header-info">
              <h3 class="header-title">{{ currentTask?.title || '任务驳回记录' }}</h3>
              <p class="header-hint"
                >共 {{ groupedRejectScreenshots.length }} 次驳回，请根据原因修改后重新提交</p
              >
            </div>
          </div>
          <el-button type="info" text circle @click="showRejectDialog = false" class="header-close">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </template>

      <div v-if="currentTask" class="reject-content">
        <!-- 驳回记录列表 -->
        <div v-if="groupedRejectScreenshots.length > 0" class="reject-timeline">
          <div
            v-for="(group, idx) in groupedRejectScreenshots"
            :key="'reject-' + idx"
            class="reject-group"
          >
            <!-- 紧凑型驳回卡片 -->
            <div class="reject-card">
              <!-- 卡片头部：次数 + 时间 -->
              <div class="card-header">
                <div class="reject-badge">第 {{ group.rejectCount }} 次</div>
                <div class="reject-time">{{ formatRejectTime(group.rejectTime) }}</div>
              </div>

              <!-- 卡片内容 -->
              <div class="card-content">
                <!-- 审核人 -->
                <div class="info-item">
                  <span class="info-icon">👤</span>
                  <span class="info-text">{{ group.reviewerName }}</span>
                </div>

                <!-- 驳回原因 -->
                <div class="reason-box">
                  <div class="reason-label">
                    <span class="reason-icon">💭</span>
                    <span>驳回原因</span>
                  </div>
                  <div class="reason-content">{{ group.comment }}</div>
                </div>

                <!-- 截图预览 -->
                <div v-if="group.screenshots.length > 0" class="images-box">
                  <div class="images-label">
                    <span class="images-icon">🖼</span>
                    <span>审核截图 ({{ group.screenshots.length }})</span>
                  </div>
                  <div class="images-grid">
                    <el-image
                      v-for="(att, attIdx) in group.screenshots"
                      :key="att.id || att.file_url || 'att-' + attIdx"
                      :src="rewriteFileUrl(att.file_url)"
                      fit="cover"
                      lazy
                      :preview-src-list="
                        group.screenshots
                          .map((i) => rewriteFileUrl(i.file_url) || '')
                          .filter(Boolean) as string[]
                      "
                      :initial-index="attIdx"
                      :preview-teleported="true"
                      :z-index="5000"
                      :hide-on-click-modal="true"
                      class="image-item"
                    >
                      <template #error>
                        <div class="image-error">
                          <el-icon><Picture /></el-icon>
                        </div>
                      </template>
                    </el-image>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 无驳回记录提示 -->
        <el-empty v-else description="暂无驳回记录" :image-size="80" />
      </div>

      <template #footer>
        <div class="reject-dialog-footer">
          <el-button @click="showRejectDialog = false"> 关闭 </el-button>
          <el-button type="primary" @click="handleResubmitFromDialog">
            <el-icon><Upload /></el-icon>
            重新提交
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="1200px"
      :close-on-click-modal="false"
    >
      <div v-if="currentTask" class="task-detail-content">
        <!-- 基本信息 -->
        <el-descriptions :column="2" border class="task-descriptions">
          <el-descriptions-item label="任务标题">
            {{ currentTask.title }}
          </el-descriptions-item>
          <el-descriptions-item label="所属项目">
            {{ (currentTask as any).projectName || (currentTask as any).project_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(currentTask.status) as any">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="影像URL" :span="2">
            <a
              v-if="(currentTask as any).imageUrl || (currentTask as any).image_url"
              :href="(currentTask as any).imageUrl || (currentTask as any).image_url"
              target="_blank"
              class="image-url-link"
            >
              {{ (currentTask as any).imageUrl || (currentTask as any).image_url }}
            </a>
            <span v-else class="text-gray-400">未设置</span>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(currentTask.priority) as any">
              {{ getPriorityText(currentTask.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime((currentTask as any).createdAt || (currentTask as any).created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="分配时间">
            {{
              (currentTask as any).assignedAt || (currentTask as any).assigned_at
                ? formatDateTime(
                    (currentTask as any).assignedAt || (currentTask as any).assigned_at
                  )
                : '-'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{
              (currentTask as any).submittedAt || (currentTask as any).submitted_at
                ? formatDateTime(
                    (currentTask as any).submittedAt || (currentTask as any).submitted_at
                  )
                : '-'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="审核时间">
            {{
              (currentTask as any).reviewedAt || (currentTask as any).reviewed_at
                ? formatDateTime(
                    (currentTask as any).reviewedAt || (currentTask as any).reviewed_at
                  )
                : '-'
            }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="(currentTask as any).reviewedBy || (currentTask as any).reviewed_by_name"
            label="审核人"
          >
            {{
              (currentTask as any).reviewedByName ||
              (currentTask as any).reviewed_by_name ||
              getUserName((currentTask as any).reviewedBy)
            }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="currentTask.score && currentTask.status === 'approved'"
            label="任务评分"
          >
            <el-rate v-model="currentTask.score" disabled show-score text-color="#ff9900" />
          </el-descriptions-item>
          <el-descriptions-item label="任务描述" :span="2">
            {{ currentTask.description || '无描述' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="currentTask.reviewComment" label="审核意见" :span="2">
            <div class="review-comment">{{ currentTask.reviewComment }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 横向时间轴 -->
        <div class="timeline-section">
          <h4>任务生命周期</h4>
          <div
            v-if="(currentTask as any).timeline && (currentTask as any).timeline.length"
            class="timeline-wrapper"
          >
            <SimpleTimeline
              :timeline="(currentTask as any).timeline"
              :current-status="currentTask.status"
            />
          </div>
          <div v-else class="no-timeline">
            <el-empty description="暂无时间轴记录" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 标注对话框 -->
    <el-dialog
      v-model="showAnnotationDialog"
      :title="`${currentTask?.status === 'rejected' ? '重新提交任务' : '标注任务'}：${currentTask?.title}`"
      width="90%"
      :close-on-click-modal="false"
    >
      <div v-if="currentTask" class="annotation-container">
        <!-- 如果是驳回的任务，显示驳回原因 -->
        <div v-if="currentTask.status === 'rejected'" class="reject-notice">
          <el-alert
            :title="'此任务已被驳回，请根据以下原因进行修改后重新提交'"
            type="warning"
            :description="currentTask.reviewComment || '无具体原因'"
            show-icon
            :closable="false"
          />
        </div>
        <!-- 任务信息 -->
        <div class="task-info-section">
          <h4>任务信息</h4>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="任务标题">{{ currentTask.title }}</el-descriptions-item>
            <el-descriptions-item label="所属项目">{{
              (currentTask as any).projectName || (currentTask as any).project_name || '-'
            }}</el-descriptions-item>
            <el-descriptions-item label="任务描述" :span="3">{{
              currentTask.description || '无描述'
            }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 医学影像 -->
        <div class="image-section">
          <h4>医学影像</h4>
          <div class="image-viewer">
            <div v-if="currentTask.imageUrl" class="medical-image">
              <img :src="currentTask.imageUrl" alt="医学影像" />
            </div>
            <div v-else class="no-image">
              <el-icon><Picture /></el-icon>
              <span>暂无影像文件</span>
            </div>
          </div>
        </div>

        <!-- 标注表单 -->
        <div class="annotation-section">
          <h4>标注结果</h4>
          <el-form
            :model="annotationForm"
            :rules="annotationRules"
            ref="annotationFormRef"
            label-width="120px"
          >
            <el-form-item label="器官数量" prop="organCount">
              <el-input-number
                v-model="annotationForm.organCount"
                :min="1"
                :max="100"
                controls-position="right"
                style="width: 200px"
              />
              <span class="form-tip">请输入在影像中标注的器官数量</span>
            </el-form-item>

            <el-form-item label="标注说明">
              <el-input
                v-model="annotationForm.comment"
                type="textarea"
                :rows="4"
                placeholder="标注说明（可选）"
                maxlength="500"
                show-word-limit
              />
              <span class="form-tip">选填，如有需要可以补充说明</span>
            </el-form-item>

            <el-form-item label="上传截图" prop="images">
              <el-upload
                ref="uploadRef"
                :action="uploadAction"
                :auto-upload="false"
                :on-change="handleImageChange"
                :on-remove="handleImageRemove"
                :file-list="annotationForm.images"
                list-type="picture-card"
                multiple
                accept="image/*"
                :limit="10"
              >
                <el-icon><Plus /></el-icon>
                <div class="upload-text">点击上传截图</div>
              </el-upload>
              <div class="upload-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>请上传标注过程的截图，最多10张，支持jpg/png格式</span>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="showAnnotationDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitAnnotation"
          :disabled="!canSubmit"
          :loading="submitting"
        >
          {{ currentTask?.status === 'rejected' ? '重新提交' : '提交审核' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 申请跳过对话框 -->
    <el-dialog
      v-model="showSkipRequestDialog"
      title="申请跳过任务"
      width="720px"
      :close-on-click-modal="false"
    >
      <div class="skip-request-content">
        <el-form
          ref="skipRequestFormRef"
          :model="skipRequestForm"
          :rules="skipRequestRules"
          label-width="100px"
        >
          <el-form-item label="任务信息">
            <el-descriptions :column="1" border size="small" class="skip-desc">
              <el-descriptions-item label="任务标题">
                {{ currentSkipTask?.title }}
              </el-descriptions-item>
              <el-descriptions-item label="所属项目">
                {{
                  (currentSkipTask as any)?.projectName ||
                  (currentSkipTask as any)?.project_name ||
                  '-'
                }}
              </el-descriptions-item>
            </el-descriptions>
          </el-form-item>

          <el-form-item label="跳过原因" prop="reason" required>
            <el-input
              v-model="skipRequestForm.reason"
              type="textarea"
              :rows="4"
              placeholder="请详细说明申请跳过此任务的原因...（支持 Ctrl+V 粘贴文字/截图）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="相关截图" prop="images">
            <el-upload
              v-model:file-list="skipRequestForm.images"
              :auto-upload="false"
              list-type="picture-card"
              :on-change="handleSkipImageChange"
              :on-remove="handleSkipImageRemove"
              multiple
              accept="image/*"
              :limit="5"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <div class="upload-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>支持粘贴板图片（Ctrl+V）直接添加，或点击上方卡片上传，最多5张。</span>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showSkipRequestDialog = false">取消</el-button>
        <el-button type="primary" @click="submitSkipRequest" :loading="skipRequestSubmitting">
          提交申请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, type FormInstance } from 'element-plus'
  import {
    Refresh,
    Clock,
    CircleCheck,
    CircleClose,
    Plus,
    InfoFilled,
    Picture,
    Folder,
    Close,
    Upload
  } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import type { Task } from '@/types/project'
  import SimpleTimeline from '@/components/custom/SimpleTimeline.vue'
  import { taskApi } from '@/api/projectApi'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'
  import CategoryTag from '@/components/project/CategoryTag.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import { formatDateTime as formatDateTimeUtil } from '@/utils/timeFormat'

  // 组件定义
  defineOptions({
    name: 'MyWorkspace'
  })

  const projectStore = useProjectStore()
  const userStore = useUserStore()
  const router = useRouter()

  // 跳转到项目管理
  const navigateToProject = (row: any) => {
    const projectId = row.projectId || row.project_id
    if (projectId) {
      router.push({
        path: '/project/management',
        query: { projectId }
      })
    } else {
      ElMessage.warning('项目ID不存在')
    }
  }

  // 响应式数据
  const activeTab = ref('in_progress')
  const showRejectDialog = ref(false)
  const showAnnotationDialog = ref(false)
  const showDetailDialog = ref(false)
  const currentTask = ref<Task | null>(null)
  const submitting = ref(false)
  const annotationFormRef = ref<FormInstance>()
  const uploadRef = ref()
  const uploadAction = '#'

  // 跳过申请相关
  const showSkipRequestDialog = ref(false)
  const currentSkipTask = ref<Task | null>(null)
  const skipRequestSubmitting = ref(false)
  const skipRequestFormRef = ref<FormInstance>()

  // 标注表单
  const annotationForm = reactive({
    organCount: 1,
    comment: '',
    images: [] as any[]
  })

  // 跳过申请表单
  const skipRequestForm = reactive({
    reason: '',
    images: [] as any[]
  })

  // 表单验证规则
  const annotationRules: any = {
    organCount: [
      { required: true, message: '请输入器官数量', trigger: 'blur' },
      { type: 'number' as any, min: 1, message: '器官数量不能小于1', trigger: 'blur' }
    ]
    // ✅ 审核意见改为非必填，已删除验证规则
  }

  // 跳过申请表单验证规则
  const skipRequestRules = {
    reason: [
      { required: true, message: '请输入跳过原因', trigger: 'blur' },
      { min: 10, message: '跳过原因至少需要10个字符', trigger: 'blur' }
    ]
  }

  // 计算是否可以提交
  const canSubmit = computed(() => {
    // ✅ 审核意见改为可选，只需要器官数量大于0即可提交
    return annotationForm.organCount > 0
  })

  // 计算任务统计
  const taskStats = computed(() => {
    const myTasks = projectStore.myTasks
    return {
      inProgress: myTasks.filter((t) => t.status === 'in_progress').length,
      submitted: myTasks.filter((t) => t.status === 'submitted').length,
      completed: myTasks.filter((t) => t.status === 'approved').length,
      rejected: myTasks.filter((t) => t.status === 'rejected').length,
      total: myTasks.length
    }
  })

  // 过滤任务
  const filteredTasks = computed(() => {
    const myTasks = projectStore.myTasks
    if (activeTab.value === 'all') {
      return myTasks
    }
    return myTasks.filter((task) => task.status === activeTab.value)
  })

  // 刷新任务
  const refreshTasks = async () => {
    try {
      const userId = userStore.currentUser?.id
      if (!userId) {
        ElMessage.error('用户信息缺失，无法获取任务')
        return
      }

      await projectStore.fetchTasks({
        assignedTo: userId,
        page: 1,
        pageSize: 100
      })

      console.log('✅ [MyWorkspace] 任务列表刷新完成')
    } catch (error) {
      console.error('❌ [MyWorkspace] 刷新任务列表失败:', error)
      ElMessage.error('刷新任务列表失败')
    }
  }

  // 标签切换
  const handleTabChange = (tabName: any) => {
    activeTab.value = String(tabName)
  }

  // 统计卡片快速筛选
  const quickFilter = (status: string) => {
    activeTab.value = status
  }

  // 获取状态类型和文本
  const getStatusType = (status: string) => {
    // 确保status不为空
    if (!status || status.trim() === '') {
      return 'info'
    }

    const types = {
      assigned: 'info',
      in_progress: 'primary',
      submitted: 'warning',
      approved: 'success',
      rejected: 'danger',
      skip_pending: 'warning',
      skipped: 'info'
    }
    return types[status as keyof typeof types] || 'info'
  }

  const getStatusText = (status: string) => {
    const texts = {
      assigned: '已分配',
      in_progress: '进行中',
      submitted: '已提交',
      approved: '已通过',
      rejected: '已驳回',
      skip_pending: '跳过审核中',
      skipped: '已跳过'
    }
    return texts[status as keyof typeof texts] || status
  }

  // 格式化日期时间（修复UTC时间8小时时差问题）
  const formatDateTime = (date: string) => {
    return formatDateTimeUtil(date, 'datetime')
  }

  // 格式化驳回时间（更友好的显示）
  const formatRejectTime = (date: string | null | undefined) => {
    if (!date) return '-'

    try {
      // 使用时间工具修复并格式化
      const formatted = formatDateTimeUtil(date, 'datetime')

      // 检查是否格式化成功
      if (!formatted || formatted === '-') {
        console.warn('⚠️ [MyWorkspace] 时间格式化失败:', date)
        return '时间格式错误'
      }

      return formatted
    } catch (error) {
      console.error('❌ [MyWorkspace] 格式化驳回时间失败:', error, date)
      return '时间格式错误'
    }
  }

  // 获取任务对应的项目分类
  const getTaskProjectCategory = (task: any) => {
    const project = projectStore.projects.find((p) => p.id === task.projectId)
    return {
      category: project?.category || '',
      subCategory: project?.subCategory || ''
    }
  }

  // 获取用户名
  const getUserName = (userId?: string) => {
    if (!userId) return '-'
    return `用户${userId.slice(-4)}`
  }

  // 开始任务
  const startTask = async (task: Task) => {
    try {
      if (task.status === 'assigned') {
        // 如果任务已分配，直接开始
        await projectStore.startTask(task.id)
        ElMessage.success('任务已开始')
      } else if (task.status === 'pending') {
        // 如果任务未分配，先领取
        await projectStore.claimTask(task.id)
        ElMessage.success('任务已领取并开始')
      } else {
        ElMessage.warning('任务状态不允许开始')
        return
      }

      refreshTasks()
    } catch (error) {
      console.error('开始任务失败:', error)
      ElMessage.error('开始任务失败')
    }
  }

  // 提交任务 - 打开标注对话框
  const submitTask = async (task: Task) => {
    currentTask.value = task

    // 重置表单，如果是驳回的任务，尝试填入之前的数据
    if (task.status === 'rejected' && task.annotationData) {
      // 从之前的标注数据中恢复
      annotationForm.organCount = task.annotationData.organ_count || 1
      annotationForm.comment = task.annotationData.comment || ''
      annotationForm.images = task.annotationData.images || []
    } else {
      // 新任务，重置表单
      annotationForm.organCount = 1
      annotationForm.comment = '' // ✅ 可以为空
      annotationForm.images = []
    }

    showAnnotationDialog.value = true
  }

  // 提交标注
  const submitAnnotation = async () => {
    if (!annotationFormRef.value || !currentTask.value) return

    try {
      await annotationFormRef.value.validate()
      submitting.value = true

      // 先上传图片到 MinIO
      let uploadedImageUrls: string[] = []
      if (annotationForm.images.length > 0) {
        try {
          console.log('📤 [MyWorkspace] 开始上传标注截图到MinIO:', annotationForm.images.length)
          const imageFiles = annotationForm.images
            .filter((img) => img.raw) // 只上传新的文件
            .map((img) => img.raw as File)

          if (imageFiles.length > 0) {
            const uploadResult = await projectStore.uploadAnnotationImages(
              currentTask.value.id,
              imageFiles
            )
            uploadedImageUrls = uploadResult.urls || []
            console.log('✅ [MyWorkspace] 图片上传成功:', uploadedImageUrls)
          }
        } catch (uploadError) {
          console.error('❌ [MyWorkspace] 图片上传失败:', uploadError)
          ElMessage.error('图片上传失败，请重试')
          return
        }
      }

      // 准备标注数据 - 确保格式匹配后端TaskSubmit模式
      const annotationData = {
        comment: annotationForm.comment,
        organ_count: annotationForm.organCount,
        uploaded_images: uploadedImageUrls, // MinIO上传后的URL
        timestamp: new Date().toISOString(),
        screenshot_count: uploadedImageUrls.length
      }

      console.log('📝 [MyWorkspace] 准备提交标注数据:', {
        taskId: currentTask.value.id,
        organCount: annotationForm.organCount,
        comment: annotationForm.comment,
        imageCount: uploadedImageUrls.length,
        uploadedUrls: uploadedImageUrls,
        annotationData
      })

      // ✅ 标注说明可以为空
      await projectStore.submitTask(currentTask.value.id, {
        annotationData,
        comment: annotationForm.comment.trim()
      } as any)

      ElMessage.success('任务已提交审核，请等待管理员审核')
      showAnnotationDialog.value = false

      // 重置表单
      annotationForm.organCount = 1
      annotationForm.comment = '' // ✅ 重置为空
      annotationForm.images = []

      refreshTasks()
    } catch (error: any) {
      console.error('❌ [MyWorkspace] 提交标注失败:', error)
      const errorMessage = error?.message || '提交标注失败，请检查网络连接和数据格式'
      ElMessage.error(errorMessage)
    } finally {
      submitting.value = false
    }
  }

  // 处理图片上传
  const handleImageChange = (file: any, fileList: any[]) => {
    annotationForm.images = fileList
  }

  // 处理图片删除
  const handleImageRemove = (file: any, fileList: any[]) => {
    annotationForm.images = fileList
  }

  // 申请跳过任务
  const requestSkipTask = (task: Task) => {
    currentSkipTask.value = task
    skipRequestForm.reason = ''
    skipRequestForm.images = []
    showSkipRequestDialog.value = true
  }

  // 提交跳过申请
  const submitSkipRequest = async () => {
    if (!skipRequestFormRef.value) return

    try {
      await skipRequestFormRef.value.validate()
    } catch (error) {
      console.log('❌ [MyWorkspace] 跳过申请表单验证失败:', error)
      return
    }

    if (!currentSkipTask.value) {
      ElMessage.error('未选择任务')
      return
    }

    skipRequestSubmitting.value = true

    try {
      // 上传图片
      let uploadedImageUrls: string[] = []
      if (skipRequestForm.images.length > 0) {
        try {
          const uploadResult = await taskApi.uploadSkipImages(
            currentSkipTask.value.id,
            skipRequestForm.images.map((item) => item.raw)
          )
          uploadedImageUrls = uploadResult.data?.urls || []
          console.log('✅ [MyWorkspace] 跳过申请图片上传成功:', uploadedImageUrls)
        } catch (uploadError) {
          console.error('❌ [MyWorkspace] 跳过申请图片上传失败:', uploadError)
          ElMessage.error('图片上传失败，请重试')
          return
        }
      }

      // 提交跳过申请
      await taskApi.requestSkipTask(currentSkipTask.value.id, {
        reason: skipRequestForm.reason,
        images: uploadedImageUrls
      })

      ElMessage.success('跳过申请已提交，请等待审核')
      showSkipRequestDialog.value = false

      // 重置表单
      skipRequestForm.reason = ''
      skipRequestForm.images = []

      refreshTasks()
    } catch (error: any) {
      console.error('❌ [MyWorkspace] 提交跳过申请失败:', error)
      const errorMessage = error?.message || '提交跳过申请失败，请重试'
      ElMessage.error(errorMessage)
    } finally {
      skipRequestSubmitting.value = false
    }
  }

  // 处理跳过申请图片变化
  const handleSkipImageChange = (file: any, fileList: any[]) => {
    skipRequestForm.images = fileList
  }

  // 处理跳过申请图片移除
  const handleSkipImageRemove = (file: any, fileList: any[]) => {
    skipRequestForm.images = fileList
  }

  // 支持粘贴板图片到“申请跳过”对话框
  const handlePasteToSkipRequest = (e: ClipboardEvent) => {
    try {
      if (!showSkipRequestDialog.value) return
      const items = e.clipboardData?.items
      if (!items || items.length === 0) return
      const files: File[] = []
      for (const it of items as any) {
        if (it.type && it.type.startsWith('image/')) {
          const blob = it.getAsFile?.() as File
          if (blob) {
            const file = new File([blob], `paste_${Date.now()}.png`, {
              type: blob.type || 'image/png'
            })
            files.push(file)
          }
        }
      }
      if (files.length > 0) {
        files.forEach((f) => {
          const objUrl = URL.createObjectURL(f)
          ;(skipRequestForm.images as any[]).push({ name: f.name, url: objUrl, raw: f })
        })
        e.preventDefault()
      }
    } catch {}
  }

  watch(showSkipRequestDialog, (val) => {
    if (val) window.addEventListener('paste', handlePasteToSkipRequest)
    else window.removeEventListener('paste', handlePasteToSkipRequest)
  })

  // 支持粘贴板截图到标注上传
  const handlePasteToAnnotation = (e: ClipboardEvent) => {
    try {
      const items = e.clipboardData?.items
      if (!items || items.length === 0) return
      const files: File[] = []
      for (const it of items as any) {
        if (it.type && it.type.startsWith('image/')) {
          const blob = it.getAsFile?.() as File
          if (blob) {
            const file = new File([blob], `paste_${Date.now()}.png`, {
              type: blob.type || 'image/png'
            })
            files.push(file)
          }
        }
      }
      if (files.length > 0) {
        files.forEach((f) => {
          const objUrl = URL.createObjectURL(f)
          ;(annotationForm.images as any[]).push({ name: f.name, url: objUrl, raw: f })
        })
        e.preventDefault()
      }
    } catch {}
  }

  watch(showAnnotationDialog, (val) => {
    if (val) window.addEventListener('paste', handlePasteToAnnotation)
    else window.removeEventListener('paste', handlePasteToAnnotation)
  })

  // 查看驳回原因
  const viewRejectReason = async (task: Task) => {
    try {
      // 获取最新详情并做字段映射（包含timeline）
      const res: any = await taskApi.getTask(task.id)
      const detail: any = (res && res.data) || res || {}
      const projectName =
        detail.projectName ||
        detail.project_name ||
        projectStore.projects.find((p) => p.id === (detail.project_id || task.projectId))?.name

      // 获取驳回时间（后端可能返回 reviewedAt 或 reviewed_at）
      const reviewedAt =
        detail.reviewedAt ||
        detail.reviewed_at ||
        (task as any).reviewedAt ||
        (task as any).reviewed_at

      // 调试日志：查看原始时间数据
      console.log('📋 [MyWorkspace] 驳回原因数据:', {
        taskId: task.id,
        reviewedAt_raw: reviewedAt,
        reviewedAt_formatted: reviewedAt ? formatRejectTime(reviewedAt) : '无',
        hasTimeline: !!detail.timeline,
        timelineLength: detail.timeline?.length || 0,
        detail_keys: Object.keys(detail),
        has_reviewedAt: 'reviewedAt' in detail,
        has_reviewed_at: 'reviewed_at' in detail
      })

      currentTask.value = {
        ...task,
        ...detail,
        projectName,
        assignedTo: detail.assignedTo || detail.assigned_to || (task as any).assignedTo,
        assignedToName:
          detail.assignedToName || detail.assigned_to_name || (task as any).assignedToName,
        createdAt: detail.createdAt || detail.created_at || (task as any).createdAt,
        assignedAt: detail.assignedAt || detail.assigned_at || (task as any).assignedAt,
        submittedAt: detail.submittedAt || detail.submitted_at || (task as any).submittedAt,
        reviewedAt: reviewedAt,
        reviewedBy: detail.reviewedBy || detail.reviewed_by || (task as any).reviewedBy,
        reviewedByName:
          detail.reviewedByName || detail.reviewed_by_name || (task as any).reviewedByName,
        reviewComment: detail.reviewComment || detail.review_comment || (task as any).reviewComment,
        attachments: Array.isArray(detail.attachments)
          ? detail.attachments
          : (task as any).attachments || [],
        timeline: Array.isArray(detail.timeline) ? detail.timeline : []
      } as any
    } catch (e) {
      console.error('❌ [MyWorkspace] 获取驳回原因失败:', e)
      // 回退到行数据
      currentTask.value = task
    }
    showRejectDialog.value = true
  }

  // 查看任务详情
  const viewTaskDetail = async (task: Task) => {
    try {
      console.log('🔍 [MyWorkspace] 查看任务详情:', task.id)

      // 获取完整的任务详情，包括timeline
      const result = await taskApi.getTask(task.id)
      const taskDetail: any = (result as any).data || result

      console.log('📋 [MyWorkspace] 任务详情获取成功:', taskDetail)
      console.log('⏰ [MyWorkspace] 时间轴数据:', taskDetail.timeline)
      console.log('📊 [MyWorkspace] Timeline事件数量:', taskDetail.timeline?.length || 0)

      // 为每个timeline事件添加attachments引用，以便显示对应阶段的截图
      if (taskDetail.timeline && taskDetail.timeline.length > 0) {
        taskDetail.timeline = taskDetail.timeline.map((event: any) => ({
          ...event,
          attachments: taskDetail.attachments || []
        }))

        taskDetail.timeline.forEach((event: any, index: number) => {
          console.log(`📅 [MyWorkspace] Timeline事件 ${index + 1}:`, {
            type: event.type,
            time: event.time,
            user_name: event.user_name,
            comment: event.comment,
            attachments_count: event.attachments?.length || 0
          })
        })
      } else {
        console.warn('⚠️ [MyWorkspace] Timeline数据为空或未定义')
      }

      const projectName =
        taskDetail.projectName ||
        taskDetail.project_name ||
        projectStore.projects.find(
          (p) => p.id === (taskDetail.project_id || (task as any).projectId)
        )?.name
      currentTask.value = {
        ...task,
        ...taskDetail,
        projectName,
        assignedTo: taskDetail.assignedTo || taskDetail.assigned_to || (task as any).assignedTo,
        assignedToName:
          taskDetail.assignedToName || taskDetail.assigned_to_name || (task as any).assignedToName,
        createdAt: taskDetail.createdAt || taskDetail.created_at || (task as any).createdAt,
        assignedAt: taskDetail.assignedAt || taskDetail.assigned_at || (task as any).assignedAt,
        submittedAt: taskDetail.submittedAt || taskDetail.submitted_at || (task as any).submittedAt,
        reviewedAt: taskDetail.reviewedAt || taskDetail.reviewed_at || (task as any).reviewedAt,
        reviewedBy: taskDetail.reviewedBy || taskDetail.reviewed_by || (task as any).reviewedBy,
        reviewedByName:
          taskDetail.reviewedByName || taskDetail.reviewed_by_name || (task as any).reviewedByName,
        reviewComment:
          taskDetail.reviewComment || taskDetail.review_comment || (task as any).reviewComment,
        attachments: Array.isArray(taskDetail.attachments)
          ? taskDetail.attachments
          : (task as any).attachments || []
      } as any
      showDetailDialog.value = true
    } catch (error) {
      console.error('❌ [MyWorkspace] 获取任务详情失败:', error)
      ElMessage.error('获取任务详情失败')
      // 如果获取详情失败，使用原有数据
      currentTask.value = task
      showDetailDialog.value = true
    }
  }

  // 从驳回原因对话框重新提交任务
  const handleResubmitFromDialog = async () => {
    if (!currentTask.value) return

    showRejectDialog.value = false
    // 直接打开标注对话框，不改变任务状态
    await submitTask(currentTask.value)
  }

  // 获取优先级类型和文本
  const getPriorityType = (priority: string) => {
    // 确保priority不为空
    if (!priority || priority.trim() === '') {
      return 'info'
    }

    const types = {
      low: 'info',
      medium: 'warning',
      high: 'danger'
    }
    return types[priority as keyof typeof types] || 'info'
  }

  const getPriorityText = (priority: string) => {
    const texts = {
      low: '低',
      medium: '中',
      high: '高'
    }
    return texts[priority as keyof typeof texts] || priority
  }

  // 时间轴相关函数
  const getTimelineType = (type: string) => {
    const types = {
      created: 'primary',
      claimed: 'success',
      started: 'info',
      submitted: 'warning',
      reviewed: 'primary',
      restarted: 'info',
      skip_requested: 'warning',
      skip_approved: 'success',
      skip_rejected: 'danger'
    }
    return types[type as keyof typeof types] || 'primary'
  }

  const getTimelineTitle = (type: string) => {
    const map: Record<string, string> = {
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
    return map[type] || type
  }

  // 初始化
  onMounted(async () => {
    try {
      console.log('🚀 [MyWorkspace] 开始初始化个人工作台')

      if (!userStore.isLogin) {
        console.warn('⚠️ [MyWorkspace] 用户未登录')
        ElMessage.warning('请先登录')
        return
      }

      // 预取项目用于显示项目名称
      try {
        await projectStore.fetchProjects({ page: 1, pageSize: 200 })
      } catch {}
      await refreshTasks()
      console.log('✅ [MyWorkspace] 个人工作台初始化完成')
    } catch (error) {
      console.error('❌ [MyWorkspace] 初始化失败:', error)
      ElMessage.error('个人工作台初始化失败')
    }
  })

  // 计算 - 打回截图去重
  const rejectScreenshots = computed(() => {
    const list = ((currentTask.value as any)?.attachments || []).filter(
      (a: any) => a && a.attachment_type === 'review_screenshot'
    )
    const seen = new Set<string>()
    const unique: any[] = []
    for (const a of list) {
      const key = a.file_url || a.file_name || a.id
      if (key && !seen.has(key)) {
        seen.add(key)
        unique.push(a)
      }
    }
    return unique
  })

  // 计算 - 按驳回次数分组截图
  interface RejectGroup {
    rejectCount: number
    rejectTime: string
    reviewerName: string
    comment: string
    screenshots: any[]
  }

  const groupedRejectScreenshots = computed<RejectGroup[]>(() => {
    const task = currentTask.value as any
    if (!task || !task.timeline) {
      // 如果没有timeline，返回单组（兼容旧逻辑）
      return rejectScreenshots.value.length > 0
        ? [
            {
              rejectCount: 1,
              rejectTime: task?.reviewedAt || task?.reviewed_at || '',
              reviewerName: task?.reviewedByName || task?.reviewed_by_name || '未知',
              comment: task?.reviewComment || task?.review_comment || '无具体原因',
              screenshots: rejectScreenshots.value
            }
          ]
        : []
    }

    // 从timeline中找到所有驳回事件（降序：最新的在前）
    const rejectEvents = task.timeline
      .filter((event: any) => event.type === 'reviewed' && event.action === 'reject')
      .sort((a: any, b: any) => new Date(b.time).getTime() - new Date(a.time).getTime())

    if (rejectEvents.length === 0) {
      return []
    }

    // 为每个驳回事件匹配截图（使用时间最接近的策略）
    const totalRejects = rejectEvents.length
    const groups: RejectGroup[] = rejectEvents.map((event: any, index: number) => {
      const eventTime = new Date(event.time).getTime()
      const tolerance = 60 * 1000 // 60秒容差

      // 找到与该事件时间最接近的截图
      const matchedScreenshots = (task.attachments || [])
        .filter((att: any) => {
          if (att.attachment_type !== 'review_screenshot') return false
          if (!att.created_at) return false

          let attCreatedAt = att.created_at
          // 处理时区问题
          if (
            !attCreatedAt.includes('Z') &&
            !attCreatedAt.includes('+') &&
            !attCreatedAt.match(/-\d{2}:\d{2}$/)
          ) {
            attCreatedAt += 'Z'
          }

          const attTime = new Date(attCreatedAt).getTime()
          const timeDiff = Math.abs(attTime - eventTime)

          return timeDiff <= tolerance
        })
        .sort((a: any, b: any) => {
          // 按与事件时间的接近程度排序
          let aTime = a.created_at
          let bTime = b.created_at
          if (!aTime.includes('Z') && !aTime.includes('+') && !aTime.match(/-\d{2}:\d{2}$/))
            aTime += 'Z'
          if (!bTime.includes('Z') && !bTime.includes('+') && !bTime.match(/-\d{2}:\d{2}$/))
            bTime += 'Z'

          const aDiff = Math.abs(new Date(aTime).getTime() - eventTime)
          const bDiff = Math.abs(new Date(bTime).getTime() - eventTime)
          return aDiff - bDiff
        })

      // 去重
      const seen = new Set<string>()
      const uniqueScreenshots = matchedScreenshots.filter((att: any) => {
        const key = att.file_url || att.file_name || att.id
        if (key && !seen.has(key)) {
          seen.add(key)
          return true
        }
        return false
      })

      return {
        rejectCount: totalRejects - index, // 降序后第一个是最新的，应该显示最大的次数
        rejectTime: event.time,
        reviewerName: event.user_name || '未知',
        comment: event.comment || '无具体原因',
        screenshots: uniqueScreenshots
      }
    })

    return groups
  })

  // URL 规范化：将 MinIO 直链改为后端代理路径，保持与文章预览一致
  const rewriteFileUrl = (u?: string) =>
    u ? u.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/') : u
</script>

<style scoped lang="scss">
  .my-workspace {
    padding: 10px;
    background: var(--art-bg-color);
    min-height: 100vh;

    // ✅ 头部样式已移至 ArtPageHeader 组件

    /* 申请跳过美化 */
    .skip-request-content {
      .skip-desc {
        margin-bottom: 8px;
      }
      .upload-hint {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #909399;
        margin-top: 6px;
        font-size: 12px;
      }
    }

    // 任务列表卡片样式
    .task-list-card {
      :deep(.el-card__header) {
        padding: 15px 18px;
        border-bottom: 1px solid var(--el-border-color-lighter);
      }

      // 影像URL单元格样式
      .image-url-cell {
        .image-url-link {
          color: var(--art-primary-color);
          text-decoration: none;
          word-break: break-all;

          &:hover {
            text-decoration: underline;
          }
        }
      }

      .card-header-with-tabs {
        display: flex;
        flex-direction: column;
        gap: 16px;

        .header-title {
          display: flex;
          align-items: center;
          gap: 12px;

          .title-text {
            font-size: 16px;
            font-weight: 600;
            color: var(--art-text-gray-900);
          }

          .task-count {
            display: inline-flex;
            align-items: center;
            padding: 2px 10px;
            background: linear-gradient(
              135deg,
              var(--el-color-success-light-9) 0%,
              var(--el-color-success-light-8) 100%
            );
            color: var(--el-color-success);
            font-size: 12px;
            font-weight: 500;
            border-radius: 12px;
          }
        }

        .tabs-section {
          :deep(.el-tabs) {
            .el-tabs__header {
              margin: 0;
            }

            .el-tabs__nav-wrap::after {
              display: none;
            }
          }
        }
      }
    }

    .table-section {
      // 任务标题单元格
      .task-title-cell {
        .task-title-text {
          display: block;
          font-weight: 600;
          color: var(--art-text-gray-900);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          cursor: pointer;

          &:hover {
            color: var(--art-primary-color);
          }
        }
      }

      // 项目名称单元格
      :deep(.project-name-cell) {
        display: flex;
        align-items: center;
        gap: 6px;

        .project-icon {
          color: var(--el-color-warning);
          font-size: 16px;
        }

        span.project-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      // 可点击的项目名称 hover 效果
      :deep(.project-name-cell .project-name.clickable:hover) {
        color: #409eff !important;
        text-decoration-color: #409eff !important;
      }

      // 描述单元格
      .description-cell {
        .description-text {
          color: var(--el-text-color-secondary);
          font-size: 13px;
        }
      }

      .task-title {
        display: flex;
        align-items: center;
        gap: 8px;

        .status-tag {
          margin-left: auto;
        }
      }

      .action-buttons {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: stretch;

        .primary-actions {
          display: flex;
          gap: 8px;
          align-items: center;
          flex-wrap: wrap;
          justify-content: center;
        }

        .secondary-actions {
          display: flex;
          justify-content: center;
        }
      }
    }

    .reject-content {
      .el-descriptions {
        margin-bottom: 20px;
      }

      h4 {
        font-size: 15px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;

        &::before {
          content: '📷';
          font-size: 18px;
        }
      }

      // 截图网格样式
      .screenshot-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 12px;
      }

      // 单个截图容器
      .screenshot-item {
        border: 1px solid #dcdfe6;
        border-radius: 6px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
          transform: translateY(-2px);
        }

        &::after {
          content: '🔍';
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 24px;
          opacity: 0;
          transition: opacity 0.3s ease;
          pointer-events: none;
        }

        &:hover::after {
          opacity: 0.8;
        }
      }
    }

    // 标注对话框样式
    .annotation-container {
      max-height: 80vh;
      overflow-y: auto;

      .reject-notice {
        margin-bottom: 20px;
      }

      .task-info-section {
        margin-bottom: 20px;

        h4 {
          margin: 0 0 12px 0;
          color: #303133;
          font-size: 16px;
          font-weight: 600;
          border-bottom: 2px solid #e4e7ed;
          padding-bottom: 8px;
        }
      }

      .image-section {
        margin-bottom: 20px;

        h4 {
          margin: 0 0 12px 0;
          color: #303133;
          font-size: 16px;
          font-weight: 600;
          border-bottom: 2px solid #e4e7ed;
          padding-bottom: 8px;
        }

        .image-viewer {
          border: 1px solid var(--art-card-border);
          border-radius: calc(var(--custom-radius) + 2px);
          padding: 20px;
          background: var(--art-main-bg-color);

          .medical-image {
            text-align: center;

            img {
              max-width: 100%;
              max-height: 400px;
              border-radius: 4px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
          }

          .no-image {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px;
            color: #909399;

            .el-icon {
              font-size: 48px;
              margin-bottom: 12px;
            }
          }
        }
      }

      .annotation-section {
        h4 {
          margin: 0 0 12px 0;
          color: #303133;
          font-size: 16px;
          font-weight: 600;
          border-bottom: 2px solid #e4e7ed;
          padding-bottom: 8px;
        }

        .form-tip {
          margin-left: 12px;
          color: #909399;
          font-size: 12px;
        }

        .upload-tip {
          display: flex;
          align-items: center;
          margin-top: 8px;
          padding: 8px 12px;
          background: var(--art-main-bg-color);
          border: 1px solid var(--art-primary-color);
          border-radius: calc(var(--custom-radius) + 2px);
          color: var(--art-primary-color);
          font-size: 12px;

          .el-icon {
            margin-right: 6px;
          }
        }

        .upload-text {
          margin-top: 4px;
          font-size: 12px;
          color: #999;
        }

        :deep(.el-upload--picture-card) {
          width: 100px;
          height: 100px;
          line-height: 100px;

          .el-icon {
            font-size: 24px;
            color: #8c939d;
          }
        }

        :deep(.el-upload-list--picture-card) {
          .el-upload-list__item {
            width: 100px;
            height: 100px;
          }
        }
      }
    }

    .task-detail-content {
      .task-descriptions {
        margin-bottom: 24px;
      }

      .timeline-section {
        margin-top: 24px;

        h4 {
          margin-bottom: 16px;
          color: #303133;
          font-weight: 600;
        }

        .timeline-wrapper {
          background: var(--art-main-bg-color);
          border-radius: calc(var(--custom-radius) + 4px);
          padding: 20px;
          border: 1px solid var(--art-card-border);
        }

        .timeline-item {
          .timeline-meta {
            margin-top: 5px;
            display: flex;
            flex-direction: column;
            gap: 4px;

            span {
              font-size: 12px;
              color: #909399;
            }
          }
        }
      }

      .no-timeline {
        margin-top: 24px;
        text-align: center;
        padding: 40px 0;
      }

      .review-comment {
        padding: 8px 12px;
        background: var(--art-main-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: calc(var(--custom-radius) + 2px);
        border-left: 4px solid #409eff;
        color: var(--art-gray-600);
      }
    }
  }
</style>

<style lang="scss">
  // 驳回原因对话框样式（全局样式，不使用 scoped）
  .art-reject-dialog {
    .el-dialog__header {
      padding: 0;
      margin: 0;
      border-bottom: none;
    }

    .el-dialog__body {
      padding: 0;
      background: var(--art-main-bg-color);
    }

    .el-dialog__footer {
      padding: 12px 20px;
      background: var(--art-bg-color);
      border-top: 1px solid var(--art-card-border);
    }

    // 自定义标题栏
    .reject-dialog-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      background: var(--art-card-bg-color);
      border-bottom: 2px solid var(--art-card-border);

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
        min-width: 0;

        .header-icon {
          flex-shrink: 0;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          background: linear-gradient(
            135deg,
            rgba(var(--art-primary-rgb), 0.12),
            rgba(var(--art-primary-rgb), 0.05)
          );
          border: 2px solid rgba(var(--art-primary-rgb), 0.25);
          border-radius: 10px;
        }

        .header-info {
          flex: 1;
          min-width: 0;

          .header-title {
            font-size: 15px;
            font-weight: 700;
            color: var(--art-text-gray-900);
            margin: 0 0 4px 0;
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .header-hint {
            font-size: 12px;
            color: var(--art-text-gray-600);
            margin: 0;
            line-height: 1.4;
          }
        }
      }

      .header-close {
        flex-shrink: 0;
        margin-left: 12px;

        &:hover {
          color: var(--art-primary-color);
          background: rgba(var(--art-primary-rgb), 0.1);
        }
      }
    }

    // 驳回内容区域
    .reject-content {
      max-height: 65vh;
      overflow-y: auto;

      // 驳回时间线
      .reject-timeline {
        padding: 16px;

        .reject-group {
          margin-bottom: 14px;

          &:last-child {
            margin-bottom: 0;
          }

          // 紧凑型驳回卡片
          .reject-card {
            background: var(--art-card-bg-color);
            border: 1px solid var(--art-card-border);
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s ease;

            &:hover {
              border-color: rgba(var(--art-primary-rgb), 0.4);
              box-shadow: 0 2px 12px rgba(var(--art-primary-rgb), 0.12);
            }

            // 卡片头部
            .card-header {
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 10px 14px;
              background: linear-gradient(
                135deg,
                rgba(var(--art-primary-rgb), 0.08) 0%,
                rgba(var(--art-primary-rgb), 0.03) 100%
              );
              border-bottom: 1px solid var(--art-card-border);

              .reject-badge {
                display: inline-flex;
                align-items: center;
                padding: 4px 12px;
                font-size: 13px;
                font-weight: 700;
                color: var(--art-primary-color);
                background: rgba(var(--art-primary-rgb), 0.15);
                border-radius: 12px;
              }

              .reject-time {
                font-size: 12px;
                font-weight: 600;
                color: var(--art-text-gray-600);
                font-family: 'Courier New', monospace;
              }
            }

            // 卡片内容
            .card-content {
              padding: 14px;

              // 审核人
              .info-item {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
                padding: 8px 10px;
                background: var(--art-main-bg-color);
                border-radius: 6px;

                .info-icon {
                  font-size: 16px;
                }

                .info-text {
                  font-size: 13px;
                  font-weight: 500;
                  color: var(--art-text-gray-900);
                }
              }

              // 驳回原因盒子
              .reason-box {
                margin-bottom: 12px;

                &:last-child {
                  margin-bottom: 0;
                }

                .reason-label {
                  display: flex;
                  align-items: center;
                  gap: 6px;
                  margin-bottom: 8px;
                  font-size: 12px;
                  font-weight: 600;
                  color: var(--art-text-gray-700);

                  .reason-icon {
                    font-size: 14px;
                  }
                }

                .reason-content {
                  padding: 10px 12px;
                  font-size: 13px;
                  font-weight: 500;
                  line-height: 1.6;
                  color: #ef4444;
                  background: rgba(239, 68, 68, 0.05);
                  border-left: 3px solid #ef4444;
                  border-radius: 6px;
                }
              }

              // 截图盒子
              .images-box {
                &:last-child {
                  margin-bottom: 0;
                }

                .images-label {
                  display: flex;
                  align-items: center;
                  gap: 6px;
                  margin-bottom: 8px;
                  font-size: 12px;
                  font-weight: 600;
                  color: var(--art-text-gray-700);

                  .images-icon {
                    font-size: 14px;
                  }
                }

                .images-grid {
                  display: grid;
                  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                  gap: 8px;

                  .image-item {
                    width: 100%;
                    height: 100px;
                    border: 1px solid var(--art-card-border);
                    border-radius: 6px;
                    overflow: hidden;
                    cursor: zoom-in;
                    transition: all 0.3s ease;

                    &:hover {
                      border-color: var(--art-primary-color);
                      box-shadow: 0 2px 8px rgba(var(--art-primary-rgb), 0.25);
                      transform: scale(1.03);
                    }

                    :deep(.el-image__inner) {
                      width: 100%;
                      height: 100%;
                      object-fit: cover;
                    }

                    .image-error {
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      width: 100%;
                      height: 100%;
                      background: var(--art-main-bg-color);
                      color: var(--art-text-gray-400);
                      font-size: 24px;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

    // 底部按钮区域
    .reject-dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 10px;

      .el-button {
        .el-icon {
          margin-right: 4px;
        }
      }
    }

    // 图片查看器 z-index 提升
    .el-image-viewer__wrapper {
      z-index: 5000 !important;
      background-color: rgba(0, 0, 0, 0.3) !important;
    }

    .el-image-viewer__mask {
      z-index: 4999 !important;
      background-color: rgba(0, 0, 0, 0.3) !important;
    }

    .el-image-viewer__close,
    .el-image-viewer__actions {
      z-index: 5001 !important;
    }

    // 画布容器 - 允许滚动
    .el-image-viewer__canvas {
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

    // 修复图片容器样式
    .el-image-viewer__img {
      filter: none !important;
      opacity: 1 !important;
      max-width: none !important;
      max-height: none !important;
    }

    // 滚动条样式
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
  }
</style>
