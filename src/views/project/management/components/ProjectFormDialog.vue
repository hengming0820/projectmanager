<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑项目' : '新建项目'"
    width="650px"
    @close="handleClose"
    :close-on-click-modal="false"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="项目名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入项目名称" size="large" />
      </el-form-item>

      <el-form-item label="项目描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入项目描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="项目状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择项目状态" style="width: 100%">
              <el-option label="进行中" value="active" />
              <el-option label="已完成" value="completed" />
              <el-option label="已暂停" value="paused" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="项目分类" prop="category">
            <el-select
              v-model="form.category"
              placeholder="请选择项目分类"
              @change="handleCategoryChange"
              style="width: 100%"
            >
              <el-option label="病例" value="case" />
              <el-option label="AI标注" value="ai_annotation" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="子分类" prop="subCategory" v-if="form.category">
            <el-select v-model="form.subCategory" placeholder="请选择子分类" style="width: 100%">
              <el-option
                v-for="option in subCategoryOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="开始日期" prop="startDate">
            <el-date-picker
              v-model="form.startDate"
              type="date"
              placeholder="选择开始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="结束日期" prop="endDate">
            <el-date-picker
              v-model="form.endDate"
              type="date"
              placeholder="选择结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 仅在新建项目时显示批量导入任务选项 -->
      <template v-if="!isEdit">
        <el-divider content-position="left">
          <span style="font-size: 14px; color: #409eff">
            <el-icon style="vertical-align: middle"><Upload /></el-icon>
            批量导入任务（可选）
          </span>
        </el-divider>

        <el-form-item label="导入任务">
          <el-switch v-model="form.importTasks" />
          <span style="margin-left: 10px; font-size: 12px; color: #909399">
            创建项目的同时批量导入任务
          </span>
        </el-form-item>

        <template v-if="form.importTasks">
          <el-alert type="info" :closable="false" style="margin-bottom: 16px">
            <template #title>
              <div style="font-size: 12px; line-height: 1.6">
                <strong>支持两种导入方式：</strong><br />
                1️⃣ <strong>文件导入</strong>：上传 Excel/CSV
                文件（需包含：任务标题、任务描述、优先级、影像URL、预计工时）<br />
                2️⃣ <strong>目录导入</strong>：选择文件夹，自动将一级子文件夹名作为任务标题批量创建
              </div>
            </template>
          </el-alert>

          <el-form-item label="导入方式">
            <el-radio-group v-model="importForm.mode">
              <el-radio-button label="file">📄 文件导入</el-radio-button>
              <el-radio-button label="directory">📁 目录导入</el-radio-button>
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
              :on-remove="handleFileRemove"
            >
              <el-button type="primary" size="default">
                <el-icon style="margin-right: 4px"><DocumentAdd /></el-icon>
                选择文件
              </el-button>
              <template #tip>
                <div class="el-upload__tip"> 支持 xlsx/xls/csv 文件，最大 10MB </div>
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
            <el-button type="primary" @click="pickDirectory" size="default">
              <el-icon style="margin-right: 4px"><FolderOpened /></el-icon>
              选择目录
            </el-button>
            <div v-if="importForm.dirSummary" class="dir-summary">
              <el-icon color="#67c23a"><SuccessFilled /></el-icon>
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
                maxlength="200"
              />
            </el-form-item>
            <el-form-item label="预计工时">
              <el-input-number
                v-model="importForm.estimatedHours"
                :min="0"
                :max="100"
                :step="0.5"
                controls-position="right"
                style="width: 100%"
              />
              <span style="margin-left: 8px; font-size: 12px; color: #909399">小时</span>
            </el-form-item>
          </template>
        </template>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="handleClose" size="large">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit" size="large">
        {{ isEdit ? '保存' : form.importTasks ? '创建并导入任务' : '创建项目' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref, computed, watch, reactive } from 'vue'
  import { ElMessage } from 'element-plus'
  import { Upload, DocumentAdd, FolderOpened, SuccessFilled } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import type { Project, ProjectStatus, TaskPriority, ProjectCategory } from '@/types/project'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'ProjectFormDialog' })

  interface Props {
    modelValue: boolean
    project?: Project
  }

  interface ProjectFormData {
    name: string
    description: string
    priority: TaskPriority
    status: ProjectStatus
    category: ProjectCategory | ''
    subCategory: string
    startDate: string
    endDate: string
    importTasks: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: false,
    project: undefined
  })

  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
    success: []
  }>()

  const projectStore = useProjectStore()

  // State
  const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  const formRef = ref<FormInstance>()
  const loading = ref(false)
  const isEdit = computed(() => !!props.project)

  const form = ref<ProjectFormData>({
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

  // 子分类选项
  const subCategoryOptions = computed(() => {
    if (form.value.category === 'case') {
      return [
        { label: '临床试验', value: 'trial' },
        { label: '科研', value: 'research' },
        { label: '有偿', value: 'paid' }
      ]
    } else if (form.value.category === 'ai_annotation') {
      return [
        { label: '科研', value: 'research' },
        { label: '日常', value: 'daily' }
      ]
    }
    return []
  })

  // 表单规则
  const rules: FormRules = {
    name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
    priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
    status: [{ required: true, message: '请选择项目状态', trigger: 'change' }],
    startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
  }

  // 监听项目变化
  watch(
    () => props.project,
    (newProject) => {
      if (newProject) {
        form.value = {
          name: newProject.name,
          description: newProject.description || '',
          priority: newProject.priority,
          status: newProject.status,
          category: newProject.category || '',
          subCategory: newProject.subCategory || '',
          startDate: newProject.startDate,
          endDate: newProject.endDate || '',
          importTasks: false
        }
      }
    },
    { immediate: true }
  )

  // 分类变化
  const handleCategoryChange = () => {
    form.value.subCategory = ''
  }

  // 文件上传处理
  const handleFileChange = (file: any) => {
    importForm.file = file.raw
  }

  const handleFileRemove = () => {
    importForm.file = null
    fileList.value = []
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
  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      loading.value = true

      // 转换表单数据，处理空字符串
      const projectData: Partial<Project> = {
        name: form.value.name,
        description: form.value.description,
        priority: form.value.priority,
        status: form.value.status,
        category: form.value.category || undefined,
        subCategory: form.value.subCategory || undefined,
        startDate: form.value.startDate,
        endDate: form.value.endDate || undefined
      } as Partial<Project>

      if (isEdit.value && props.project) {
        // 编辑项目
        await projectStore.updateProject(props.project.id, projectData)
        ElMessage.success('项目更新成功')
      } else {
        // 创建新项目
        const result = await projectStore.createProject(projectData)
        const newProjectId = result.id

        // 如果需要导入任务
        if (form.value.importTasks) {
          try {
            if (importForm.mode === 'file') {
              // 文件导入
              if (!importForm.file) {
                ElMessage.warning('请选择要导入的文件')
                loading.value = false
                return
              }
              await projectStore.importTasksFromExcel(importForm.file, newProjectId)
              ElMessage.success('项目创建成功，任务导入完成')
            } else {
              // 目录导入
              if (!importForm.dirFiles || importForm.dirFiles.length === 0) {
                ElMessage.warning('请选择目录')
                loading.value = false
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
                loading.value = false
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

      emit('success')
      handleClose()
    } catch (error: any) {
      if (error !== false) {
        // 不是表单验证错误
        console.error('保存项目失败:', error)
        ElMessage.error(error.message || '保存项目失败')
      }
    } finally {
      loading.value = false
    }
  }

  // 关闭对话框
  const handleClose = () => {
    visible.value = false
    formRef.value?.resetFields()
    form.value = {
      name: '',
      description: '',
      priority: 'medium',
      status: 'active',
      category: '',
      subCategory: '',
      startDate: '',
      endDate: '',
      importTasks: false
    }
    // 重置导入表单
    importForm.mode = 'file'
    importForm.file = null
    importForm.dirFiles = []
    importForm.dirSummary = ''
    importForm.description = ''
    importForm.estimatedHours = 0
    fileList.value = []
  }
</script>

<style scoped>
  .dir-summary {
    margin-top: 8px;
    padding: 8px 12px;
    background: #f0f9ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    font-size: 13px;
    color: #3b82f6;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .el-upload__tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
</style>

<style lang="scss" scoped>
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-select),
  :deep(.el-date-picker) {
    width: 100%;
  }
</style>
