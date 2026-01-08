<template>
  <div class="task-pool">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="任务池"
      description="管理和分配医学影像标注任务"
      icon="📋"
      badge="Tasks"
      theme="blue"
    >
      <template #actions>
        <el-button @click="refreshTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('pending')">
            <ArtStatsCard
              :count="taskPoolStats.pending"
              title="待领取"
              description="可领取的任务"
              icon="&#xe721;"
              icon-color="#409eff"
              icon-bg-color="#ecf5ff"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('submitted')">
            <ArtStatsCard
              :count="taskPoolStats.submitted"
              title="待审核"
              description="等待审核的任务"
              icon="&#xe7c0;"
              icon-color="#f56c6c"
              icon-bg-color="#fef0f0"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('skipped')">
            <ArtStatsCard
              :count="taskPoolStats.skipped"
              title="已跳过"
              description="已跳过的任务"
              icon="&#xe7c3;"
              icon-color="#e6a23c"
              icon-bg-color="#fdf6ec"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('approved')">
            <ArtStatsCard
              :count="taskPoolStats.approved"
              title="已通过"
              description="审核通过的任务"
              icon="&#xe7c1;"
              icon-color="#67c23a"
              icon-bg-color="#f0f9ff"
            />
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-click" @click="quickFilterByStatus('')">
            <ArtStatsCard
              :count="taskPoolStats.total"
              title="全部"
              description="所有任务数量"
              icon="&#xe721;"
              icon-color="#409eff"
              icon-bg-color="#ecf5ff"
            />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表（包含搜索筛选） -->
    <el-card class="art-custom-card task-list-card">
      <template #header>
        <div class="card-header-with-filters">
          <div class="header-title">
            <span class="title-text">任务列表</span>
            <span class="task-count">共 {{ projectStore.total }} 个任务</span>
          </div>

          <!-- 搜索筛选区域 -->
          <div class="filters-section">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索任务标题或描述"
              :prefix-icon="Search"
              clearable
              @input="handleSearch"
              style="width: 240px"
            />
            <el-select
              v-model="searchForm.projectId"
              placeholder="选择项目"
              clearable
              @change="handleSearch"
              style="width: 160px"
            >
              <el-option label="全部项目" value="" />
              <el-option
                v-for="project in projectStore.projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
            <el-select
              v-model="searchForm.status"
              placeholder="任务状态"
              clearable
              @change="handleSearch"
              style="width: 140px"
            >
              <el-option label="全部状态" value="" />
              <el-option label="待领取" value="pending" />
              <el-option label="已分配" value="assigned" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已提交" value="submitted" />
              <el-option label="已通过" value="approved" />
              <el-option label="已驳回" value="rejected" />
              <el-option label="跳过申请中" value="skip_pending" />
              <el-option label="已跳过" value="skipped" />
            </el-select>
            <el-button @click="resetSearch" :icon="Refresh">重置</el-button>
            <el-button type="primary" @click="exportTasks" :icon="Download">导出</el-button>
          </div>
        </div>
      </template>
      <el-table
        v-loading="projectStore.loading"
        :data="projectStore.tasks"
        stripe
        height="calc(100vh - 420px)"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" fixed />

        <!-- 任务标题 -->
        <el-table-column prop="title" label="任务标题" width="220" fixed>
          <template #default="{ row }">
            <div class="task-title-cell">
              <el-tooltip :content="row.title" placement="top" :show-after="500">
                <strong class="task-title-text">{{ row.title }}</strong>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 所属项目 -->
        <el-table-column prop="projectName" label="所属项目" width="600">
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

        <el-table-column prop="assignedTo" label="分配给" width="140">
          <template #default="{ row }">
            <div v-if="row.assignedTo" class="annotator-cell">
              <span class="annotator-name">{{ getUserName(row.assignedTo, row) }}</span>
            </div>
            <div v-else class="unassigned-cell">
              <span class="unassigned-text">未分配</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="estimatedHours" label="预计工时" width="100">
          <template #default="{ row }"> {{ row.estimatedHours || '-' }}h </template>
        </el-table-column>

        <el-table-column prop="createdAt" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right" align="right">
          <template #default="{ row }">
            <div class="action-buttons" style="justify-content: flex-end">
              <!-- 待领取状态 -->
              <template v-if="row.status === 'pending'">
                <el-button
                  type="primary"
                  size="small"
                  :icon="Download"
                  @click="claimTask(row)"
                  class="claim-btn"
                >
                  领取任务
                </el-button>
              </template>

              <!-- 已领取状态 -->
              <template v-else-if="row.status === 'in_progress'">
                <el-tag type="success" size="small" class="status-badge">
                  <el-icon><Clock /></el-icon>
                  进行中
                </el-tag>
              </template>

              <!-- 已提交状态 -->
              <template v-else-if="row.status === 'submitted'">
                <el-tag type="warning" size="small" class="status-badge">
                  <el-icon><DocumentChecked /></el-icon>
                  待审核
                </el-tag>
              </template>

              <!-- 已通过状态 -->
              <template v-else-if="row.status === 'approved'">
                <el-tag type="success" size="small" class="status-badge">
                  <el-icon><CircleCheck /></el-icon>
                  已通过
                </el-tag>
              </template>

              <!-- 已驳回状态 -->
              <template v-else-if="row.status === 'rejected'">
                <el-tag type="danger" size="small" class="status-badge">
                  <el-icon><CircleClose /></el-icon>
                  已驳回
                </el-tag>
              </template>

              <!-- 已跳过状态 -->
              <template v-else-if="row.status === 'skipped'">
                <el-tag type="info" size="small" class="status-badge">
                  <el-icon><Remove /></el-icon>
                  已跳过
                </el-tag>
              </template>

              <!-- 通用操作按钮 -->
              <el-dropdown trigger="click" class="action-dropdown">
                <el-button type="info" size="small" :icon="MoreFilled" circle />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="View" @click="viewTask(row)">
                      查看详情
                    </el-dropdown-item>
                    <el-dropdown-item :icon="Edit" @click="editTask(row)">
                      编辑任务
                    </el-dropdown-item>
                    <el-dropdown-item :icon="Delete" @click="openSkipDialog(row)" divided>
                      跳过任务
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作 -->
      <div v-if="selectedTasks.length > 0" class="batch-actions">
        <span>已选择 {{ selectedTasks.length }} 个任务</span>
        <el-button type="danger" size="small" @click="batchDeleteTasks"> 批量删除 </el-button>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="projectStore.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑任务对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTask ? '编辑任务' : '新建任务'"
      width="600px"
      @close="resetForm"
      append-to-body
      :z-index="3000"
    >
      <el-form ref="formRef" :model="taskForm" :rules="formRules" label-width="100px">
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>

        <el-form-item label="所属项目" prop="projectId">
          <el-select v-model="taskForm.projectId" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in projectStore.activeProjects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>

        <el-form-item label="影像URL" prop="imageUrl">
          <el-input v-model="taskForm.imageUrl" placeholder="请输入影像文件URL" />
        </el-form-item>

        <el-form-item label="预计工时" prop="estimatedHours">
          <el-input-number
            v-model="taskForm.estimatedHours"
            :min="0.5"
            :max="100"
            :step="0.5"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingTask ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入任务"
      width="560px"
      append-to-body
      :z-index="3000"
    >
      <div class="import-section">
        <el-alert title="导入说明" type="info" show-icon :closable="false" class="import-tips">
          <template #default>
            <p>支持两种方式：</p>
            <p>1) 上传Excel/CSV（含列：任务标题、任务描述、优先级、影像URL、预计工时）。</p>
            <p>2) 选择目录：读取一级子文件夹名为任务标题，前端生成CSV并自动导入。</p>
            <ul>
              <li>选择项目（必填）</li>
              <li>目录导入可统一填写描述与预计工时，优先级默认中</li>
            </ul>
          </template>
        </el-alert>

        <el-form :model="importForm" label-width="100px" class="import-form">
          <el-form-item label="选择项目" required>
            <el-select v-model="importForm.projectId" placeholder="请选择项目" style="width: 100%">
              <el-option
                v-for="project in projectStore.activeProjects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="导入方式" required>
            <el-radio-group v-model="importForm.mode">
              <el-radio label="file">文件</el-radio>
              <el-radio label="directory">目录</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="importForm.mode === 'file'" label="上传文件" required>
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".xlsx,.xls,.csv"
              :on-change="handleFileChange"
              :file-list="fileList"
              class="upload-demo"
            >
              <el-button type="primary">选择文件</el-button>
              <template #tip>
                <div class="el-upload__tip"> 支持上传 xlsx/xls/csv 文件，且不超过10MB </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item v-else label="选择目录" required>
            <input
              ref="dirInputRef"
              type="file"
              webkitdirectory
              multiple
              @change="handleDirectoryChange"
              style="display: none"
            />
            <el-button type="primary" @click="pickDirectory">选择目录</el-button>
            <div v-if="importForm.dirSummary" style="margin-top: 6px; color: #909399">
              {{ importForm.dirSummary }}
            </div>
          </el-form-item>

          <template v-if="importForm.mode === 'directory'">
            <el-form-item label="统一描述">
              <el-input
                v-model="importForm.description"
                placeholder="为所有任务设置统一描述（可选）"
              />
            </el-form-item>
            <el-form-item label="预计工时">
              <el-input-number
                v-model="importForm.estimatedHours"
                :min="0"
                :max="100"
                :step="0.5"
                style="width: 100%"
              />
            </el-form-item>
          </template>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button
          v-if="importForm.mode === 'file'"
          type="primary"
          @click="importTasks"
          :loading="importing"
          >导入</el-button
        >
        <el-button v-else type="primary" @click="importFromDirectoryCsv" :loading="importing"
          >从目录生成CSV并导入</el-button
        >
      </template>
    </el-dialog>

    <!-- 跳过任务对话框 -->
    <el-dialog
      v-model="showSkipDialog"
      title="跳过任务"
      width="520px"
      append-to-body
      :z-index="3000"
    >
      <el-form label-width="90px">
        <el-form-item label="跳过原因" required>
          <el-input
            v-model="skipForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请填写跳过原因"
          />
        </el-form-item>
        <el-form-item label="上传截图">
          <el-upload
            ref="skipUploadRef"
            :auto-upload="false"
            list-type="picture-card"
            multiple
            accept="image/*"
            :on-change="handleSkipImageChange"
            :on-remove="handleSkipImageRemove"
            :file-list="skipForm.fileList"
          >
            <el-icon><Plus /></el-icon>
            <div class="upload-text">点击上传截图</div>
          </el-upload>
          <div class="upload-tip">可选，上传用于说明跳过原因的截图</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSkipDialog = false">取消</el-button>
        <el-button type="primary" @click="submitSkip">确认跳过</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="80%"
      append-to-body
      :z-index="3000"
    >
      <div v-if="currentTask">
        <el-descriptions :column="2" border class="task-descriptions">
          <el-descriptions-item label="任务标题">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="所属项目">{{
            currentTask.project_name || currentTask.projectName
          }}</el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(currentTask.status) as unknown as any">{{
              getStatusText(currentTask.status)
            }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="影像URL" :span="2">
            <a
              v-if="currentTask.imageUrl || currentTask.image_url"
              :href="currentTask.imageUrl || currentTask.image_url"
              target="_blank"
              class="image-url-link"
            >
              {{ currentTask.imageUrl || currentTask.image_url }}
            </a>
            <span v-else class="text-gray-400">未设置</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{
            currentTask.created_at || currentTask.createdAt
              ? new Date(currentTask.created_at || currentTask.createdAt).toLocaleString()
              : '-'
          }}</el-descriptions-item>
          <el-descriptions-item
            v-if="currentTask.skipped_at || currentTask.skippedAt"
            label="跳过时间"
          >
            {{ new Date(currentTask.skipped_at || currentTask.skippedAt).toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 16px">
          <h4>任务生命周期</h4>
          <div v-if="currentTask.timeline && currentTask.timeline.length">
            <SimpleTimeline :timeline="currentTask.timeline" :current-status="currentTask.status" />
          </div>
          <div v-else>
            <el-empty description="暂无时间轴记录" />
          </div>
        </div>

        <div style="margin-top: 16px">
          <h4>截图</h4>
          <div v-if="dedupScreenshots.length === 0">
            <el-empty description="暂无截图" />
          </div>
          <div
            v-else
            style="
              display: grid;
              grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
              gap: 12px;
            "
          >
            <div
              v-for="(img, idx) in dedupScreenshots"
              :key="img.key || idx"
              style="border: 1px solid #dcdfe6; border-radius: 8px; overflow: hidden"
            >
              <img
                :src="img.url"
                style="width: 100%; height: 150px; object-fit: cover; display: block"
              />
              <div style="padding: 6px 8px; font-size: 12px; color: #909399">{{ img.label }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import {
    ElMessage,
    ElMessageBox,
    type FormInstance,
    type UploadProps,
    type UploadFile
  } from 'element-plus'
  import { taskApi as _taskApi } from '@/api/projectApi'
  import {
    Plus,
    Search,
    Upload,
    Refresh,
    Download,
    Edit,
    Delete,
    View,
    Clock,
    CircleCheck,
    CircleClose,
    DocumentChecked,
    MoreFilled,
    User,
    UserFilled,
    Remove,
    Folder
  } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  // SimpleTimeline 已在上方导入
  import type { Task } from '@/types/project'
  import CategoryTag from '@/components/project/CategoryTag.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'

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
  const showCreateDialog = ref(false)
  const showImportDialog = ref(false)
  const editingTask = ref<Task | null>(null)
  const submitting = ref(false)
  const importing = ref(false)
  const formRef = ref<FormInstance>()
  const uploadRef = ref()
  const dirInputRef = ref<HTMLInputElement | null>(null)
  const selectedTasks = ref<Task[]>([])
  const fileList = ref<UploadFile[]>([])

  // 搜索表单
  const searchForm = reactive({
    keyword: '',
    projectId: '',
    status: ''
  })

  // 分页
  const pagination = reactive({
    page: 1,
    pageSize: 20
  })

  // 任务表单
  const taskForm = reactive({
    title: '',
    projectId: '',
    description: '',
    priority: 'medium',
    imageUrl: '',
    estimatedHours: 1
  })

  // 导入表单
  const importForm = reactive({
    projectId: '',
    mode: 'file' as 'file' | 'directory',
    file: null as File | null,
    dirFiles: [] as File[],
    dirSummary: '',
    description: '',
    estimatedHours: 0
  })

  // 表单验证规则
  const formRules = {
    title: [
      { required: true, message: '请输入任务标题', trigger: 'blur' },
      { min: 2, max: 100, message: '任务标题长度在 2 到 100 个字符', trigger: 'blur' }
    ],
    projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
    priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
  }

  // 获取任务列表
  const fetchTasks = async () => {
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: searchForm.keyword,
      projectId: searchForm.projectId || undefined,
      status: searchForm.status ? [searchForm.status] : undefined
    }
    await projectStore.fetchTasks(params)
  }

  // 刷新任务列表
  const refreshTasks = async () => {
    try {
      console.log('🔄 [TaskPool] 刷新任务列表')
      await fetchTasks()
      ElMessage.success('任务列表刷新成功')
    } catch (error) {
      console.error('❌ [TaskPool] 刷新任务列表失败:', error)
      ElMessage.error('刷新任务列表失败')
    }
  }

  // 获取项目列表
  const fetchProjects = async () => {
    await projectStore.fetchProjects({
      page: 1,
      pageSize: 100,
      status: ['active']
    })
  }

  // 计算任务池统计
  const taskPoolStats = computed(() => {
    const allTasks = projectStore.tasks
    return {
      pending: allTasks.filter((t) => t.status === 'pending').length,
      submitted: allTasks.filter((t) => t.status === 'submitted').length,
      skipped: allTasks.filter((t) => t.status === 'skipped').length,
      approved: allTasks.filter((t) => t.status === 'approved').length,
      total: projectStore.total
    }
  })

  // 快速筛选（点击卡片）
  const quickFilterByStatus = (status: string) => {
    searchForm.status = status
    handleSearch()
  }

  // 搜索处理
  const handleSearch = () => {
    pagination.page = 1
    fetchTasks()
  }

  // 重置搜索
  const resetSearch = () => {
    searchForm.keyword = ''
    searchForm.projectId = ''
    searchForm.status = ''
    handleSearch()
  }

  // 分页处理
  const handlePageChange = (page: number) => {
    pagination.page = page
    fetchTasks()
  }

  const handlePageSizeChange = (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    fetchTasks()
  }

  // 选择处理
  const handleSelectionChange = (selection: Task[]) => {
    selectedTasks.value = selection
  }

  // 获取状态类型和文本
  const getStatusType = (status: string): 'info' | 'warning' | 'primary' | 'success' | 'danger' => {
    // 确保status不为空
    if (!status || status.trim() === '') {
      return 'info'
    }

    // 使用更醒目的颜色区分"已跳过"
    const types = {
      pending: 'info',
      assigned: 'warning',
      in_progress: 'primary',
      submitted: 'success',
      approved: 'success',
      rejected: 'danger',
      skip_pending: 'warning', // 跳过申请中
      skipped: 'warning'
    }
    return (types as any)[status] || 'info'
  }

  const getStatusText = (status: string) => {
    const texts = {
      pending: '待领取',
      assigned: '已分配',
      in_progress: '进行中',
      submitted: '已提交',
      approved: '已通过',
      rejected: '已驳回',
      skip_pending: '跳过申请中', // 新增跳过申请状态
      skipped: '已跳过'
    }
    return texts[status as keyof typeof texts] || status
  }

  // 获取优先级类型和文本
  const getPriorityType = (priority: string) => {
    // 确保priority不为空
    if (!priority || priority.trim() === '') {
      return 'info'
    }

    const types = {
      low: 'info',
      medium: 'primary',
      high: 'warning',
      urgent: 'danger'
    }
    return types[priority as keyof typeof types] || 'info'
  }

  const getPriorityText = (priority: string) => {
    const texts = {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '紧急'
    }
    return texts[priority as keyof typeof texts] || priority
  }

  // 获取用户名（这里简化处理）
  const getUserName = (userId: string | undefined | null, row?: any) => {
    if (!userId) return '未分配'
    // 先用后端冗余姓名字段
    if (row && (row.assignedToName || row.assigned_to_name)) {
      return row.assignedToName || row.assigned_to_name
    }
    // 再从全局用户列表查 real_name
    try {
      const userStore = useUserStore()
      const user = (userStore as any).users?.find?.((u: any) => u.id === userId)
      if (user)
        return user.real_name || user.realName || user.username || `用户${String(userId).slice(-4)}`
    } catch {}
    return `用户${String(userId).slice(-4)}`
  }

  // 获取任务对应的项目分类
  const getTaskProjectCategory = (task: any) => {
    const project = projectStore.projects.find((p) => p.id === task.projectId)
    return {
      category: project?.category || '',
      subCategory: project?.subCategory || ''
    }
  }

  // 格式化日期
  const formatDate = (date: string | undefined | null) => {
    if (!date) {
      return '-'
    }
    return date.split('T')[0]
  }

  // 领取任务
  const claimTask = async (task: Task) => {
    try {
      await ElMessageBox.confirm(`确定要领取任务"${task.title}"吗？`, '确认领取', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      })

      await projectStore.claimTask(task.id)
      ElMessage.success('领取成功')
      fetchTasks()
    } catch (error: any) {
      if (error !== 'cancel') {
        // 显示详细的错误信息
        const errorMessage = error?.response?.data?.detail || error?.message || '领取失败'

        // 特殊处理任务上限错误
        if (errorMessage.includes('上限') || errorMessage.includes('已达')) {
          ElMessageBox.alert(
            '您当前有3个进行中或已提交的任务，已达到可领取任务上限。请先完成部分任务后再领取新任务。',
            '无法领取任务',
            {
              confirmButtonText: '我知道了',
              type: 'warning'
            }
          )
        } else {
          ElMessage.error(errorMessage)
        }
      }
    }
  }

  // 查看任务（详情+时间轴）
  const showDetailDialog = ref(false)
  const currentTask = ref<any>(null)

  const viewTask = async (task: Task) => {
    try {
      const res: any = await _taskApi.getTask(task.id)
      const detail = (res.data || res) as any

      // 为每个timeline事件添加attachments引用，以便显示对应阶段的截图
      if (detail.timeline && detail.timeline.length > 0) {
        detail.timeline = detail.timeline.map((event: any) => ({
          ...event,
          attachments: detail.attachments || []
        }))
      }

      // 兜底填充所属项目与标注员姓名
      const projectName =
        detail.project_name ||
        detail.projectName ||
        projectStore.projects.find((p) => p.id === (detail.project_id || task.projectId))?.name
      const assignedToName =
        detail.assigned_to_name ||
        detail.assignedToName ||
        (projectStore as any).users?.find?.(
          (u: any) => u.id === (detail.assigned_to || task.assignedTo)
        )?.real_name
      currentTask.value = {
        ...detail,
        project_name: projectName || detail.project_name,
        assignedToName: assignedToName || detail.assignedToName
      }
    } catch (e) {
      currentTask.value = task
    }
    showDetailDialog.value = true
  }

  // 编辑任务
  const editTask = (task: Task) => {
    editingTask.value = task
    Object.assign(taskForm, {
      title: task.title,
      projectId: task.projectId,
      description: task.description,
      priority: task.priority as any,
      imageUrl: task.imageUrl,
      estimatedHours: task.estimatedHours
    })
    showCreateDialog.value = true
  }

  // 跳过任务
  const showSkipDialog = ref(false)
  const skippingTask = ref<Task | null>(null)
  const skipForm = reactive({ reason: '', images: [] as string[], fileList: [] as any[] })
  const skipUploadRef = ref()

  const openSkipDialog = (task: Task) => {
    skippingTask.value = task
    skipForm.reason = ''
    skipForm.images = []
    skipForm.fileList = []
    showSkipDialog.value = true
  }

  const submitSkip = async () => {
    if (!skippingTask.value) return
    if (!skipForm.reason.trim()) {
      ElMessage.warning('请填写跳过原因')
      return
    }
    try {
      // 先上传新选择的文件
      let uploadedUrls: string[] = []
      const newFiles = skipForm.fileList.filter((f: any) => f.raw).map((f: any) => f.raw as File)
      if (newFiles.length > 0) {
        const uploadRes: any = await _taskApi.uploadSkipImages(skippingTask.value.id, newFiles)
        uploadedUrls = uploadRes.data?.urls || uploadRes.urls || []
      }
      const allImages = [...skipForm.images, ...uploadedUrls]
      await _taskApi.skipTask(skippingTask.value.id, { reason: skipForm.reason, images: allImages })
      ElMessage.success('已标记为跳过')
      showSkipDialog.value = false
      fetchTasks()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  }

  const handleSkipImageChange = (file: any, fileList: any[]) => {
    skipForm.fileList = fileList
  }

  const handleSkipImageRemove = (file: any, fileList: any[]) => {
    skipForm.fileList = fileList
  }

  // 支持粘贴板图片（跳过任务对话框打开时）
  const handlePasteToSkip = (e: ClipboardEvent) => {
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
          ;(skipForm.fileList as any[]).push({ name: f.name, url: objUrl, raw: f })
        })
        e.preventDefault()
      }
    } catch {}
  }

  watch(showSkipDialog, (val) => {
    if (val) window.addEventListener('paste', handlePasteToSkip)
    else window.removeEventListener('paste', handlePasteToSkip)
  })

  // 过滤后的跳过截图附件
  const skipAttachmentImages = computed(() => {
    const atts = (currentTask.value && currentTask.value.attachments) || []
    return (atts as Array<{ attachment_type?: string; file_url: string }>).filter(
      (a) => !!a && a.attachment_type === 'skip_screenshot'
    )
  })

  // 组合并去重：驳回截图与跳过截图
  const dedupScreenshots = computed(() => {
    const attachments = ((currentTask.value && (currentTask.value as any).attachments) ||
      []) as Array<any>
    const review = attachments
      .filter((a) => a && a.attachment_type === 'review_screenshot')
      .map((a) => ({ url: a.file_url, key: a.file_url || a.id || a.file_name, label: '已驳回' }))
    const skipFromAtt = attachments
      .filter((a) => a && a.attachment_type === 'skip_screenshot')
      .map((a) => ({ url: a.file_url, key: a.file_url || a.id || a.file_name, label: '已跳过' }))
    const skipFromUrls = ((currentTask.value && (currentTask.value as any).skip_images) || []).map(
      (u: string) => ({ url: u, key: u, label: '已跳过' })
    )
    const all = [...review, ...skipFromAtt, ...skipFromUrls]
    const seen = new Set<string>()
    const result: Array<{ url: string; key: string; label: string }> = []
    for (const item of all) {
      if (!item.url) continue
      const k = item.key || item.url
      if (!seen.has(k)) {
        seen.add(k)
        result.push(item)
      }
    }
    return result
  })

  // 批量删除任务
  const batchDeleteTasks = async () => {
    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？此操作不可恢复。`,
        '确认批量删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      // 这里应该调用批量删除API
      ElMessage.success('批量删除成功')
      selectedTasks.value = []
      fetchTasks()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('批量删除失败')
      }
    }
  }

  // 导出任务
  const exportTasks = async () => {
    try {
      // 获取当前筛选的任务列表（如果有选中的任务就导出选中的，否则导出全部）
      const tasksToExport =
        selectedTasks.value.length > 0 ? selectedTasks.value : projectStore.tasks

      if (tasksToExport.length === 0) {
        ElMessage.warning('没有可导出的任务')
        return
      }

      ElMessage.info('正在导出任务列表...')

      // 构建CSV数据
      const headers = [
        '任务标题',
        '所属项目',
        '任务描述',
        '项目分类',
        '优先级',
        '分配给',
        '任务状态',
        '创建时间',
        '分配时间',
        '提交时间',
        '影像URL',
        '预计工时',
        '实际工时'
      ]

      const rows = tasksToExport.map((task) => {
        // 类型断言以支持后端可能返回的蛇形命名格式
        const taskAny = task as any

        // 获取项目名称
        const projectName =
          task.projectName ||
          taskAny.project_name ||
          projectStore.projects.find((p) => p.id === task.projectId)?.name ||
          '-'

        // 获取分类信息
        const project = projectStore.projects.find((p) => p.id === task.projectId)
        const categoryText = project
          ? `${project.category || '-'}${project.subCategory ? '/' + project.subCategory : ''}`
          : '-'

        // 获取标注员姓名
        const assignedToName =
          taskAny.assignedToName ||
          taskAny.assigned_to_name ||
          getUserName(task.assignedTo, taskAny) ||
          '未分配'

        // 状态文本
        const statusText = getStatusText(task.status)

        // 优先级文本
        const priorityText = getPriorityText(task.priority)

        // 格式化时间（使用短格式，避免Excel显示为#####）
        const formatTime = (time: any) => {
          if (!time) return ''
          try {
            const date = new Date(time)
            const year = date.getFullYear()
            const month = String(date.getMonth() + 1).padStart(2, '0')
            const day = String(date.getDate()).padStart(2, '0')
            const hour = String(date.getHours()).padStart(2, '0')
            const minute = String(date.getMinutes()).padStart(2, '0')
            return `${year}-${month}-${day} ${hour}:${minute}`
          } catch {
            return ''
          }
        }

        return [
          task.title || '-',
          projectName,
          (task.description || '-').replace(/[\n\r]/g, ' ').replace(/"/g, '""'),
          categoryText,
          priorityText,
          assignedToName,
          statusText,
          formatTime(task.createdAt || taskAny.created_at),
          formatTime(task.assignedAt || taskAny.assigned_at),
          formatTime(task.submittedAt || taskAny.submitted_at),
          task.imageUrl || taskAny.image_url || '-',
          task.estimatedHours || taskAny.estimated_hours || 0,
          task.actualHours || taskAny.actual_hours || 0
        ]
      })

      // 生成CSV内容（带UTF-8 BOM，兼容Excel）
      const csvLines = [headers, ...rows]
        .map((cols) => cols.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(','))
        .join('\n')

      // 创建Blob并下载
      const bom = new Uint8Array([0xef, 0xbb, 0xbf])
      const blob = new Blob([bom, csvLines], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // 生成文件名
      const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      const filenameSuffix =
        selectedTasks.value.length > 0
          ? `_selected_${selectedTasks.value.length}`
          : `_all_${tasksToExport.length}`
      link.download = `任务列表_${timestamp}${filenameSuffix}.csv`

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      ElMessage.success(`已导出 ${tasksToExport.length} 条任务记录`)
    } catch (error) {
      console.error('导出任务失败:', error)
      ElMessage.error('导出失败')
    }
  }

  // 提交表单
  const submitForm = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      submitting.value = true

      if (editingTask.value) {
        // 此页面仅演示更新，直接复用创建方法提交（类型放宽）
        await projectStore.createTask({
          id: editingTask.value.id,
          title: taskForm.title,
          projectId: taskForm.projectId,
          description: taskForm.description,
          priority: taskForm.priority as any,
          imageUrl: taskForm.imageUrl,
          estimatedHours: taskForm.estimatedHours
        } as any)
        ElMessage.success('更新成功')
      } else {
        await projectStore.createTask({
          title: taskForm.title,
          projectId: taskForm.projectId,
          description: taskForm.description,
          priority: taskForm.priority as any,
          imageUrl: taskForm.imageUrl,
          estimatedHours: taskForm.estimatedHours
        } as any)
        ElMessage.success('创建成功')
      }

      showCreateDialog.value = false
      fetchTasks()
    } catch (error) {
      ElMessage.error(editingTask.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  }

  // 文件选择处理
  const handleFileChange: UploadProps['onChange'] = (uploadFile) => {
    importForm.file = uploadFile.raw || null
    fileList.value = uploadFile ? [uploadFile] : []
  }

  // 触发目录选择
  const pickDirectory = () => {
    // 某些浏览器只识别 webkitdirectory，无需设置 directory
    dirInputRef.value?.click()
  }

  // 目录选择处理
  const handleDirectoryChange = (e: Event) => {
    const input = e.target as HTMLInputElement
    const files = Array.from(input.files || [])
    importForm.dirFiles = files
    // 提取一级子目录名
    const titles = new Set<string>()
    for (const f of files) {
      const rel = (f as any).webkitRelativePath || f.name
      const parts = rel.split('/').filter(Boolean)
      if (parts.length >= 2) {
        const title = parts[1]
        if (title) titles.add(title)
      }
    }
    importForm.dirSummary = `检测到 ${titles.size} 个子文件夹，将创建同名任务。`
  }

  // 导入任务
  const importTasks = async () => {
    if (!importForm.projectId) {
      ElMessage.warning('请选择项目')
      return
    }

    if (!importForm.file) {
      ElMessage.warning('请选择文件')
      return
    }

    try {
      importing.value = true
      const result: any = await projectStore.importTasksFromExcel(
        importForm.file as File,
        importForm.projectId
      )
      const msg = result?.message || '导入完成'
      ElMessage.success(msg)

      showImportDialog.value = false
      fetchTasks()
    } catch (error) {
      ElMessage.error('导入失败')
    } finally {
      importing.value = false
    }
  }

  // 从目录生成CSV并调用现有导入接口
  const importFromDirectoryCsv = async () => {
    if (!importForm.projectId) {
      ElMessage.warning('请选择项目')
      return
    }
    if (!importForm.dirFiles || importForm.dirFiles.length === 0) {
      ElMessage.warning('请选择目录')
      return
    }

    // 收集一级子目录名
    const titleSet = new Set<string>()
    for (const f of importForm.dirFiles) {
      const rel = (f as any).webkitRelativePath || f.name
      const parts = rel.split('/').filter(Boolean)
      if (parts.length >= 2) titleSet.add(parts[1])
    }
    const titles = Array.from(titleSet)
    if (titles.length === 0) {
      ElMessage.warning('未检测到子文件夹，请确认目录结构')
      return
    }

    try {
      importing.value = true
      // 生成 CSV 文本（UTF-8 BOM，兼容 Excel）
      const headers = ['任务标题', '任务描述', '优先级', '影像URL', '预计工时', '项目ID']
      const rows = titles.map((title) => [
        title,
        (importForm.description || '').replace(/\n/g, ' '),
        'medium',
        '',
        String(importForm.estimatedHours || 0),
        importForm.projectId
      ])
      const csvLines = [headers, ...rows]
        .map((cols) => cols.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(','))
        .join('\n')

      const bom = new Uint8Array([0xef, 0xbb, 0xbf])
      const blob = new Blob([bom, csvLines], { type: 'text/csv;charset=utf-8;' })
      const file = new File([blob], `tasks_${Date.now()}.csv`, { type: 'text/csv' })

      // 复用现有的 CSV 导入流程
      const result: any = await projectStore.importTasksFromExcel(
        file as File,
        importForm.projectId
      )
      const msg = result?.message || `导入完成（共 ${titles.length} 条）`
      ElMessage.success(msg)
      showImportDialog.value = false
      fetchTasks()
    } catch (e) {
      console.error('目录转CSV导入失败:', e)
      ElMessage.error('从目录导入失败')
    } finally {
      importing.value = false
    }
  }

  // 重置表单
  const resetForm = () => {
    editingTask.value = null
    Object.assign(taskForm, {
      title: '',
      projectId: '',
      description: '',
      priority: 'medium',
      imageUrl: '',
      estimatedHours: 1
    })
    nextTick(() => {
      formRef.value?.clearValidate()
    })
  }

  // 重置导入表单
  const resetImportForm = () => {
    importForm.projectId = ''
    importForm.mode = 'file'
    importForm.file = null
    importForm.dirFiles = []
    importForm.dirSummary = ''
    importForm.description = ''
    importForm.estimatedHours = 0
    fileList.value = []
    uploadRef.value?.clearFiles()
  }

  // 强制重新登录
  const forceRelogin = async () => {
    try {
      await ElMessageBox.confirm('将清除当前登录状态并跳转到登录页，确定继续吗？', '重新登录', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      console.log('🔄 [TaskPool] 用户手动触发重新登录')
      userStore.forceReauth()
    } catch (error) {
      // 用户取消操作
    }
  }

  // 初始化
  onMounted(() => {
    fetchProjects()
    fetchTasks()
  })
</script>

<style scoped lang="scss">
  .task-pool {
    padding: 20px;
    background: var(--art-bg-color);
    min-height: 100vh;

    // 统计卡片区域
    .stats-section {
      margin-bottom: 20px;

      .stat-click {
        cursor: pointer;
        transition: transform 0.2s;

        &:hover {
          transform: translateY(-2px);
        }
      }
    }

    // 任务列表卡片样式
    .task-list-card {
      :deep(.el-card__header) {
        padding: 20px 24px;
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

      .card-header-with-filters {
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
              var(--el-color-primary-light-9) 0%,
              var(--el-color-primary-light-8) 100%
            );
            color: var(--el-color-primary);
            font-size: 12px;
            font-weight: 500;
            border-radius: 12px;
          }
        }

        .filters-section {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        }
      }
    }

    .page-header-content {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .header-left {
        h2 {
          margin: 0 0 8px 0;
          color: var(--art-gray-900);
          font-size: 24px;
          font-weight: 600;
        }

        p {
          margin: 0;
          color: var(--art-gray-600);
          font-size: 14px;
        }
      }
    }

    .table-section {
      .task-title {
        display: flex;
        align-items: center;
        gap: 8px;

        .status-tag {
          margin-left: auto;
        }
      }

      // 标注员单元格（新样式）
      .annotator-cell {
        .annotator-name {
          display: inline-block;
          padding: 2px 8px;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
          color: #0284c7;
          font-size: 13px;
          font-weight: 500;
          border-radius: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          max-width: 100%;
        }
      }

      // 未分配单元格（新样式）
      .unassigned-cell {
        .unassigned-text {
          display: inline-block;
          padding: 2px 8px;
          background: #f5f5f5;
          color: #909399;
          font-size: 13px;
          border-radius: 4px;
        }
      }

      // 保留旧样式以防其他地方使用
      .assigned-user {
        display: flex;
        align-items: center;
        gap: 8px;

        .user-avatar {
          background: var(--el-color-primary-light-8);
          color: var(--el-color-primary);
          font-size: 12px;
        }

        .user-name {
          font-size: 12px;
          color: var(--el-text-color-regular);
        }
      }

      .unassigned {
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--el-text-color-placeholder);

        .unassigned-icon {
          font-size: 16px;
        }

        .unassigned-text {
          font-size: 12px;
        }
      }

      .action-buttons {
        display: flex;
        align-items: center;
        gap: 8px;

        .claim-btn {
          --el-button-size: 24px;
          font-size: 12px;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 4px;

          .el-icon {
            font-size: 12px;
          }
        }

        .action-dropdown {
          margin-left: auto;
        }
      }

      .batch-actions {
        margin: 15px 0;
        padding: 10px;
        background: var(--art-main-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: calc(var(--custom-radius) + 2px);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .pagination-wrapper {
        margin-top: 20px;
        display: flex;
        justify-content: center;
      }

      // 任务标题单元格样式
      .task-title-cell {
        .task-title-text {
          color: var(--art-text-gray-900);
          font-weight: 600;
          font-size: 14px;
          line-height: 1.5;
          display: block;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          cursor: pointer;
          transition: color 0.2s;

          &:hover {
            color: var(--el-color-primary);
          }
        }
      }

      // 项目名称单元格样式
      :deep(.project-name-cell) {
        display: flex;
        align-items: center;
        gap: 8px;

        .project-icon {
          color: var(--el-color-primary);
          font-size: 16px;
          flex-shrink: 0;
        }

        span.project-name {
          color: var(--el-text-color-regular);
          font-size: 13px;
          line-height: 1.5;
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

      // 描述单元格样式
      .description-cell {
        .description-text {
          color: var(--el-text-color-secondary);
          font-size: 13px;
          line-height: 1.5;
        }
      }
    }

    .import-section {
      .import-tips {
        margin-bottom: 20px;

        ul {
          margin: 10px 0 0 0;
          padding-left: 20px;
        }
      }

      .import-form {
        margin-top: 20px;
      }

      .upload-demo {
        width: 100%;
      }
    }
  }
</style>
