<template>
  <div class="project-management">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="项目管理"
      description="管理医学影像标注项目，创建和维护项目信息"
      icon="📁"
      badge="Projects"
      theme="cyan"
    >
      <template #actions>
        <el-button @click="refreshAllData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建项目
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 搜索和筛选 -->
    <el-card class="art-custom-card">
      <template #header>
        <div class="card-header">
          <span>搜索筛选</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索项目名称或描述"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="searchForm.status"
            placeholder="项目状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="searchForm.priority"
            placeholder="优先级"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-button @click="resetSearch">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 项目列表 -->
    <el-card class="art-custom-card">
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
        </div>
      </template>
      <el-table
        v-loading="projectStore.loading"
        :data="projectStore.projects"
        stripe
        height="calc(100vh - 320px)"
      >
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-name">
              <strong>{{ row.name }}</strong>
              <el-tag :type="getStatusType(row.status) as any" size="small" class="status-tag">
                {{ getStatusText(row.status) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />

        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority) as any" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="分类" width="140">
          <template #default="{ row }">
            <CategoryTag :category="row.category" :sub-category="row.subCategory" size="small" />
          </template>
        </el-table-column>

        <el-table-column label="进度" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="getProgress(row)"
              :stroke-width="8"
              :format="(percentage) => `${percentage}%`"
            />
          </template>
        </el-table-column>

        <el-table-column label="任务统计" width="120">
          <template #default="{ row }">
            <div class="task-stats">
              <span>{{ getTaskStats(row).completed }}/{{ getTaskStats(row).total }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="startDate" label="开始日期" width="120" />
        <el-table-column prop="endDate" label="结束日期" width="120" />

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="viewProject(row)"> 查看 </el-button>
            <el-button type="warning" size="small" text @click="editProject(row)"> 编辑 </el-button>
            <el-button type="danger" size="small" text @click="deleteProject(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 新建/编辑项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '编辑项目' : '新建项目'"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="projectForm" :rules="formRules" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>

        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="projectForm.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>

        <el-form-item label="项目状态" prop="status">
          <el-select v-model="projectForm.status" placeholder="请选择项目状态">
            <el-option label="进行中" value="active" />
            <el-option label="已暂停" value="paused" />
          </el-select>
        </el-form-item>

        <el-form-item label="项目分类" prop="category">
          <el-select
            v-model="projectForm.category"
            placeholder="请选择项目分类"
            @change="handleCategoryChange"
          >
            <el-option label="病例" value="case" />
            <el-option label="AI标注" value="ai_annotation" />
          </el-select>
        </el-form-item>

        <el-form-item label="子分类" prop="subCategory" v-if="projectForm.category">
          <el-select v-model="projectForm.subCategory" placeholder="请选择子分类">
            <el-option
              v-for="option in getSubCategoryOptions()"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="开始日期" prop="startDate">
          <el-date-picker
            v-model="projectForm.startDate"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="结束日期" prop="endDate">
          <el-date-picker
            v-model="projectForm.endDate"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <!-- 仅在新建项目时显示批量导入任务选项 -->
        <template v-if="!editingProject">
          <el-divider content-position="left">批量导入任务（可选）</el-divider>

          <el-form-item label="是否导入任务">
            <el-switch v-model="projectForm.importTasks" />
            <span style="margin-left: 10px; font-size: 12px; color: #909399">
              创建项目的同时批量导入任务
            </span>
          </el-form-item>

          <template v-if="projectForm.importTasks">
            <el-form-item label="导入方式">
              <el-radio-group v-model="importForm.mode">
                <el-radio label="file">文件</el-radio>
                <el-radio label="directory">目录</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="importForm.mode === 'file'" label="上传文件">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                accept=".xlsx,.xls,.csv"
                :on-change="handleFileChange"
                :file-list="fileList"
              >
                <el-button size="small">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 xlsx/xls/csv（含列：任务标题、任务描述、优先级、影像URL、预计工时）
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item v-else label="选择目录">
              <input
                ref="dirInputRef"
                type="file"
                webkitdirectory
                multiple
                @change="handleDirectoryChange"
                style="display: none"
              />
              <el-button size="small" @click="pickDirectory">选择目录</el-button>
              <div
                v-if="importForm.dirSummary"
                style="margin-top: 6px; color: #909399; font-size: 12px"
              >
                {{ importForm.dirSummary }}
              </div>
            </el-form-item>

            <template v-if="importForm.mode === 'directory'">
              <el-form-item label="统一描述">
                <el-input
                  v-model="importForm.description"
                  placeholder="为所有任务设置统一描述（可选）"
                  type="textarea"
                  :rows="2"
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
          </template>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingProject ? '保存' : projectForm.importTasks ? '创建并导入' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 项目详情对话框 -->
    <ProjectDetailDialog
      v-model="showDetailDialog"
      :project="currentDetailProject"
      @refresh="fetchProjects"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, nextTick } from 'vue'
  import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
  import { Plus, Search, Refresh } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import type { Project } from '@/types/project'
  import ProjectDetailDialog from './components/ProjectDetailDialog.vue'
  import CategoryTag from '@/components/project/CategoryTag.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'

  const projectStore = useProjectStore()

  // 响应式数据
  const showCreateDialog = ref(false)
  const editingProject = ref<Project | null>(null)
  const submitting = ref(false)
  const formRef = ref<FormInstance>()

  // 搜索表单
  const searchForm = reactive({
    keyword: '',
    status: '',
    priority: '',
    dateRange: [] as string[]
  })

  // 分页
  const pagination = reactive({
    page: 1,
    pageSize: 20
  })

  // 项目表单
  const projectForm = reactive({
    name: '',
    description: '',
    priority: 'medium',
    status: 'active',
    category: '',
    subCategory: '',
    startDate: '',
    endDate: '',
    importTasks: false // 是否批量导入任务
  })

  // 导入任务表单
  const importForm = reactive({
    mode: 'file' as 'file' | 'directory',
    file: null as File | null,
    dirFiles: [] as File[],
    dirSummary: '',
    description: '',
    estimatedHours: 0
  })

  // 文件列表和引用
  const fileList = ref<any[]>([])
  const uploadRef = ref()
  const dirInputRef = ref<HTMLInputElement | null>(null)

  // 表单验证规则
  const formRules = {
    name: [
      { required: true, message: '请输入项目名称', trigger: 'blur' },
      { min: 2, max: 50, message: '项目名称长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
    status: [{ required: true, message: '请选择项目状态', trigger: 'change' }],
    category: [{ required: true, message: '请选择项目分类', trigger: 'change' }],
    subCategory: [{ required: true, message: '请选择子分类', trigger: 'change' }],
    startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
  }

  // 获取项目列表
  const fetchProjects = async () => {
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: searchForm.keyword,
      status: searchForm.status ? [searchForm.status] : undefined,
      priority: searchForm.priority ? [searchForm.priority] : undefined,
      startDate: searchForm.dateRange[0] || undefined,
      endDate: searchForm.dateRange[1] || undefined
    }
    await projectStore.fetchProjects(params)
  }

  // 搜索处理
  const handleSearch = () => {
    pagination.page = 1
    fetchProjects()
  }

  // 重置搜索
  const resetSearch = () => {
    searchForm.keyword = ''
    searchForm.status = ''
    searchForm.priority = ''
    searchForm.dateRange = []
    handleSearch()
  }

  // 分页处理
  const handlePageChange = (page: number) => {
    pagination.page = page
    fetchProjects()
  }

  const handlePageSizeChange = (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    fetchProjects()
  }

  // 获取状态类型
  const getStatusType = (status: string) => {
    // 确保status不为空
    if (!status || status.trim() === '') {
      return 'info'
    }

    const types = {
      active: 'success',
      completed: 'info',
      paused: 'warning',
      cancelled: 'danger'
    }
    return types[status as keyof typeof types] || 'info'
  }

  // 获取状态文本
  const getStatusText = (status: string) => {
    const texts = {
      active: '进行中',
      completed: '已完成',
      paused: '已暂停',
      cancelled: '已取消'
    }
    return texts[status as keyof typeof texts] || status
  }

  // 获取优先级类型
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

  // 获取优先级文本
  const getPriorityText = (priority: string) => {
    const texts = {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '紧急'
    }
    return texts[priority as keyof typeof texts] || priority
  }

  // ✅ 使用项目本身的统计字段（不受任务过滤影响）
  // 获取实时进度
  const getProgress = (project: Project) => {
    const total = project.totalTasks || 0
    const completed = project.completedTasks || 0
    if (total === 0) return 0
    return Math.max(0, Math.min(100, Math.round((completed / total) * 100)))
  }

  // 获取实时任务统计
  const getTaskStats = (project: Project) => {
    const total = project.totalTasks || 0
    const completed = project.completedTasks || 0
    return { completed, total }
  }

  // 查看项目
  const showDetailDialog = ref(false)
  const currentDetailProject = ref<Project>()

  const viewProject = (project: Project) => {
    currentDetailProject.value = project
    showDetailDialog.value = true
  }

  // 编辑项目
  const editProject = (project: Project) => {
    editingProject.value = project
    Object.assign(projectForm, {
      name: project.name,
      description: project.description,
      priority: project.priority,
      status: project.status,
      category: project.category || '',
      subCategory: project.subCategory || '',
      startDate: project.startDate,
      endDate: project.endDate
    })
    showCreateDialog.value = true
  }

  // 删除项目
  const deleteProject = async (project: Project) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除项目"${project.name}"吗？
      
⚠️ 警告：此操作将会：
• 删除该项目下的所有任务
• 删除相关的标注数据
• 此操作不可恢复

请确认是否继续？`,
        '确认删除项目',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          dangerouslyUseHTMLString: true
        }
      )

      await projectStore.deleteProject(project.id)
      ElMessage.success('删除成功')
      fetchProjects()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }

  // 分类处理函数
  const handleCategoryChange = () => {
    // 当主分类改变时，清空子分类
    projectForm.subCategory = ''
  }

  const getSubCategoryOptions = () => {
    if (projectForm.category === 'case') {
      return [
        { label: '试用', value: 'trial' },
        { label: '研发', value: 'research' },
        { label: '收费', value: 'paid' }
      ]
    } else if (projectForm.category === 'ai_annotation') {
      return [
        { label: '科研', value: 'research_ai' }, // 更新为新的值避免歧义
        { label: '日常', value: 'daily' }
      ]
    }
    return []
  }

  // 文件上传处理
  const handleFileChange = (file: any) => {
    importForm.file = file.raw
  }

  // 目录选择处理
  const pickDirectory = () => {
    dirInputRef.value?.click()
  }

  const handleDirectoryChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
      importForm.dirFiles = Array.from(target.files)

      // 收集一级子目录名
      const titleSet = new Set<string>()
      for (const f of importForm.dirFiles) {
        const rel = (f as any).webkitRelativePath || f.name
        const parts = rel.split('/').filter(Boolean)
        if (parts.length >= 2) titleSet.add(parts[1])
      }
      importForm.dirSummary = `检测到 ${titleSet.size} 个子文件夹`
    }
  }

  // 提交表单
  const submitForm = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      submitting.value = true

      if (editingProject.value) {
        // 编辑项目
        await projectStore.updateProject(editingProject.value.id, projectForm as any)
        ElMessage.success('更新成功')
      } else {
        // 创建新项目
        const result = await projectStore.createProject(projectForm as any)
        const newProjectId = result.id

        // 如果需要导入任务
        if (projectForm.importTasks) {
          try {
            if (importForm.mode === 'file') {
              // 文件导入
              if (!importForm.file) {
                ElMessage.warning('请选择要导入的文件')
                submitting.value = false
                return
              }
              await projectStore.importTasksFromExcel(importForm.file, newProjectId)
              ElMessage.success('项目创建成功，任务导入完成')
            } else {
              // 目录导入
              if (!importForm.dirFiles || importForm.dirFiles.length === 0) {
                ElMessage.warning('请选择目录')
                submitting.value = false
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
                submitting.value = false
                return
              }

              // 生成 CSV 文本（UTF-8 BOM，兼容 Excel）
              const headers = ['任务标题', '任务描述', '优先级', '影像URL', '预计工时', '项目ID']
              const rows = titles.map((title) => [
                title,
                (importForm.description || '').replace(/\n/g, ' '),
                'medium',
                '',
                String(importForm.estimatedHours || 0),
                newProjectId
              ])
              const csvLines = [headers, ...rows]
                .map((cols) => cols.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(','))
                .join('\n')

              const bom = new Uint8Array([0xef, 0xbb, 0xbf])
              const blob = new Blob([bom, csvLines], { type: 'text/csv;charset=utf-8;' })
              const file = new File([blob], `tasks_${Date.now()}.csv`, { type: 'text/csv' })

              await projectStore.importTasksFromExcel(file, newProjectId)
              ElMessage.success(`项目创建成功，已导入 ${titles.length} 个任务`)
            }
          } catch (error) {
            console.error('导入任务失败:', error)
            ElMessage.warning('项目创建成功，但任务导入失败')
          }
        } else {
          ElMessage.success('项目创建成功')
        }
      }

      showCreateDialog.value = false
      fetchProjects()
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(editingProject.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  }

  // 重置表单
  const resetForm = () => {
    editingProject.value = null
    Object.assign(projectForm, {
      name: '',
      description: '',
      priority: 'medium',
      status: 'active',
      category: '',
      subCategory: '',
      startDate: '',
      endDate: '',
      importTasks: false
    })
    // 重置导入表单
    Object.assign(importForm, {
      mode: 'file',
      file: null,
      dirFiles: [],
      dirSummary: '',
      description: '',
      estimatedHours: 0
    })
    fileList.value = []
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
    nextTick(() => {
      formRef.value?.clearValidate()
    })
  }

  // 刷新所有数据
  const refreshAllData = async () => {
    // 并行加载项目列表和所有任务数据
    await Promise.all([
      fetchProjects(),
      projectStore.fetchTasks({ page: 1, pageSize: 10000 }) // 获取所有任务用于计算进度
    ])
  }

  // 初始化
  onMounted(async () => {
    await refreshAllData()
  })

  // 暴露刷新方法供其他组件使用
  defineExpose({
    refreshAllData
  })
</script>

<style scoped lang="scss">
  .project-management {
    padding: 20px;
    background: var(--art-bg-color);
    min-height: 100vh;

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
      .project-name {
        display: flex;
        align-items: center;
        gap: 8px;

        .status-tag {
          margin-left: auto;
        }
      }

      .task-stats {
        font-weight: 500;
        color: var(--art-primary-color);
      }

      .pagination-wrapper {
        margin-top: 20px;
        display: flex;
        justify-content: center;
      }
    }
  }
</style>
