<template>
  <div class="work-log-entry-cell">
    <!-- 多个条目显示 -->
    <div v-if="displayEntries.length > 0" class="entries-wrapper">
      <div
        v-for="(entry, index) in displayEntries"
        :key="entry.id"
        class="entry-card"
        :style="{
          '--type-color': getWorkTypeColor(entry.work_type || '').border,
          '--type-bg': getWorkTypeColor(entry.work_type || '').background
        }"
      >
        <!-- 左侧装饰条 -->
        <div class="entry-accent-bar"></div>

        <div class="entry-main">
          <!-- 头部：索引、标题、工时、操作 -->
          <div class="entry-header">
            <div class="header-left">
              <span v-if="displayEntries.length > 1" class="index-badge">{{ index + 1 }}</span>
              <span class="work-subject" :title="getWorkSubjectFromContent(entry.work_content)">
                {{ getWorkSubjectFromContent(entry.work_content) }}
              </span>
            </div>
            <div class="header-right">
              <span 
                v-if="entry.actual_hours || entry.planned_hours" 
                class="hours-badge"
              >
                {{ formatHours(entry.actual_hours || entry.planned_hours) }}
              </span>
              
              <div v-if="canEditEntry" class="action-trigger" @click.stop>
                <el-dropdown
                  trigger="click"
                  @command="(cmd) => handleActionCommand(cmd, entry)"
                  placement="bottom-end"
                >
                  <div class="more-btn">
                    <el-icon><MoreFilled /></el-icon>
                  </div>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit" :icon="Edit">编辑</el-dropdown-item>
                      <el-dropdown-item command="delete" :icon="Delete" divided class="danger-item">删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>

          <!-- 内容区域 - 直接显示全部内容 -->
          <div class="entry-body">
            <div
              class="content-text"
              v-html="formatContentWithLinks(getMainContentFromContent(entry.work_content))"
            ></div>
          </div>

          <!-- 底部状态图标栏 (仅当有特殊信息时显示) -->
          <div class="entry-footer" v-if="entry.difficulties || entry.next_day_plan || hasAttachments(entry)">
            <div class="footer-tags">
              <el-tooltip v-if="entry.difficulties" :content="'困难: ' + entry.difficulties" placement="top" :show-after="500">
                <div class="mini-tag warning">
                  <el-icon><WarningFilled /></el-icon>
                  <span>困难</span>
                </div>
              </el-tooltip>
              <el-tooltip v-if="entry.next_day_plan" :content="'计划: ' + entry.next_day_plan" placement="top" :show-after="500">
                <div class="mini-tag plan">
                  <el-icon><Calendar /></el-icon>
                  <span>计划</span>
                </div>
              </el-tooltip>
              <div v-if="hasAttachments(entry)" class="mini-tag link">
                <el-icon><Link /></el-icon>
                <span>关联</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 (点击添加) -->
    <div v-else class="empty-slot" :class="{ 'clickable': canEditEntry }" @click="canEditEntry && createEntry()">
      <template v-if="canEditEntry">
        <div class="add-btn-inner">
          <el-icon class="add-icon"><Plus /></el-icon>
          <span class="add-text">添加日志</span>
        </div>
      </template>
      <div v-else class="no-data-slot">
        <span class="no-data-text">暂无日志</span>
      </div>
    </div>

    <!-- 添加更多按钮 (仅在已有条目且有权限时显示) -->
    <div v-if="canAddMoreWorkItems" class="append-btn" @click.stop="createEntry">
      <el-icon><Plus /></el-icon>
    </div>

    <!-- 编辑/创建对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="editingEntry ? '✏️ 编辑工作日志' : '📝 创建工作日志'"
      width="720px"
      :close-on-click-modal="false"
      :z-index="3000"
      append-to-body
      class="work-item-dialog-new"
      top="5vh"
    >
      <div class="dialog-content">
        <!-- 工作类型和基本信息区域 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon class="section-icon"><Document /></el-icon>
            <div>
              <h3>工作信息</h3>
              <p>设置工作类型、标题和工作时长</p>
            </div>
          </div>

          <el-form
            ref="entryFormRef"
            :model="entryForm"
            :rules="entryFormRules"
            label-width="80px"
            class="work-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="工作类型" prop="workType" required>
                  <el-select
                    v-model="entryForm.workType"
                    placeholder="请选择工作类型"
                    style="width: 100%"
                    popper-class="work-type-popper"
                  >
                    <el-option
                      v-for="option in workTypeOptions"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    >
                      <div class="work-type-option">
                        <span class="type-dot" :style="{ backgroundColor: option.color }"></span>
                        <span class="type-label">{{ option.label }}</span>
                      </div>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工作时间" prop="actualHours" required>
                  <el-input-number
                    v-model="entryForm.actualHours"
                    :min="0.5"
                    :max="12"
                    :step="0.5"
                    placeholder="请输入工作时长"
                    style="width: 100%"
                    :controls-position="'right'"
                  >
                    <template #suffix>
                      <span style="color: #909399; font-size: 13px; margin-right: 8px">小时</span>
                    </template>
                  </el-input-number>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="工作标题" prop="workSubject" required>
              <!-- 标题类型切换 -->
              <div class="subject-type-switch">
                <el-radio-group
                  v-model="subjectType"
                  size="small"
                  @change="handleSubjectTypeChange"
                >
                  <el-radio-button label="tag">
                    <el-icon><CollectionTag /></el-icon>
                    常用标签
                  </el-radio-button>
                  <el-radio-button label="project">
                    <el-icon><FolderOpened /></el-icon>
                    关联项目
                  </el-radio-button>
                </el-radio-group>
              </div>

              <!-- 常用标签选择 -->
              <el-select
                v-if="subjectType === 'tag'"
                v-model="entryForm.workSubject"
                filterable
                allow-create
                default-first-option
                placeholder="选择或输入常用标签"
                style="width: 100%; margin-top: 12px"
                popper-class="work-subject-popper"
              >
                <el-option
                  v-for="tag in commonSubjectTags"
                  :key="tag.value"
                  :label="tag.label"
                  :value="tag.value"
                >
                  <div class="subject-option">
                    <div class="tag-icon-wrapper" :style="{ backgroundColor: tag.color + '15' }">
                      <span class="tag-icon" :style="{ color: tag.color }">{{ tag.icon }}</span>
                    </div>
                    <div class="tag-info">
                      <span class="tag-label">{{ tag.label }}</span>
                      <span v-if="tag.desc" class="tag-desc">{{ tag.desc }}</span>
                    </div>
                  </div>
                </el-option>
              </el-select>

              <!-- 项目任务选择 -->
              <el-select
                v-else
                v-model="entryForm.workSubject"
                filterable
                allow-create
                default-first-option
                placeholder="选择或输入项目名称"
                style="width: 100%; margin-top: 12px"
                popper-class="work-subject-popper"
              >
                <el-option
                  v-for="project in projectsList"
                  :key="project.id"
                  :label="project.name"
                  :value="project.name"
                >
                  <div class="subject-option project-option">
                    <el-icon class="project-icon"><FolderOpened /></el-icon>
                    <span class="project-name">{{ project.name }}</span>
                  </div>
                </el-option>
              </el-select>

              <div class="subject-hint">
                <el-icon><InfoFilled /></el-icon>
                <span v-if="subjectType === 'tag'">从常用标签中选择，也可自定义输入</span>
                <span v-else>从关联项目中选择，也可自定义输入</span>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 工作内容区域 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon class="section-icon"><EditPen /></el-icon>
            <div>
              <h3>工作内容</h3>
              <p>详细描述具体的工作内容和完成情况</p>
            </div>
          </div>

          <el-form :model="entryForm" label-width="80px">
            <!-- 关联文章搜索 -->
            <el-form-item label="关联文章">
              <el-select
                v-model="selectedArticleId"
                filterable
                remote
                reserve-keyword
                placeholder="搜索项目文章、会议记录、模型测试或团队文档"
                :remote-method="searchArticles"
                :loading="articlesLoading"
                @change="handleArticleSelect"
                clearable
                style="width: 100%"
                popper-class="article-popper"
              >
                <el-option
                  v-for="article in articlesList"
                  :key="article.id"
                  :label="`${getArticleTypeLabel(article.type)} - ${article.title}`"
                  :value="article.id"
                >
                  <div class="article-option">
                    <el-tag :type="getArticleTagType(article.type)" size="small" effect="light">
                      {{ getArticleTypeLabel(article.type) }}
                    </el-tag>
                    <span class="article-title">{{ article.title }}</span>
                  </div>
                </el-option>
              </el-select>
              <div class="article-hint">
                <el-icon><InfoFilled /></el-icon>
                <span>搜索所有类型的文章，选择后会自动在工作内容中插入文章链接</span>
              </div>
            </el-form-item>

            <el-form-item label="详细内容" prop="workContent" required>
              <el-input
                v-model="entryForm.workContent"
                type="textarea"
                :rows="5"
                placeholder="请详细描述具体工作内容，包括：&#10;• 完成了哪些具体任务&#10;• 解决了什么问题&#10;• 取得了什么成果&#10;• 遇到的困难和解决方案等"
                maxlength="300"
                show-word-limit
                resize="none"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <div class="footer-left">
            <el-button 
              v-if="editingEntry" 
              type="danger" 
              text 
              bg
              size="default"
              @click="deleteEntry(editingEntry)"
            >
              <el-icon><Delete /></el-icon>
              删除日志
            </el-button>
          </div>
          <div class="footer-right">
            <el-button @click="showEditDialog = false" size="default">
              <el-icon><Close /></el-icon>
              取消
            </el-button>
            <el-button type="primary" @click="saveEntry" :loading="saving" size="default">
              <el-icon><Check /></el-icon>
              {{ editingEntry ? '更新' : '保存' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Plus,
    Edit,
    Check,
    MoreFilled,
    Delete,
    Document,
    EditPen,
    Close,
    WarningFilled,
    Calendar,
    InfoFilled,
    FolderOpened,
    CollectionTag,
    Link,
  } from '@element-plus/icons-vue'
  import { workLogEntryApi, workLogTypeApi, workLogUtils } from '@/api/workLogApi'
  import type {
    WorkLogEntry,
    WorkLogEntryCreate,
    WorkLogEntryUpdate,
    WorkLogType
  } from '@/types/work-log'
  import { articlesApi } from '@/api/articlesApi'
  import { collaborationApi } from '@/api/collaborationApi'
  import { useUserStore } from '@/store/modules/user'
  import { projectApi } from '@/api/projectApi'

  const userStore = useUserStore()

  interface Props {
    entry?: WorkLogEntry
    entries?: WorkLogEntry[] // 支持多个条目
    workDate: string
    dayName: string
    userId: string
    workWeekId: string
    canEdit: boolean
  }

  interface Emits {
    (e: 'entry-updated', entry: WorkLogEntry): void
    (e: 'entry-submitted', entry: WorkLogEntry): void
    (e: 'entry-deleted', entryId: string): void
  }

  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // 响应式数据
  const saving = ref(false)
  const showEditDialog = ref(false)
  const editingEntry = ref<WorkLogEntry | null>(null)
  const workLogTypes = ref<WorkLogType[]>([])

  // 正在编辑的工作项ID
  const editingWorkItemId = ref<string | null>(null)

  // 工作标题类型：tag(常用标签) 或 project(关联项目)
  const subjectType = ref<'tag' | 'project'>('tag')

  // 表单数据 - 简化为核心字段
  const entryForm = reactive({
    workType: '', // 工作类型 - 不设置默认值，强制用户选择
    workSubject: '', // 工作标题
    workContent: '', // 工作内容
    actualHours: undefined as number | undefined // 工作时间 - 不设置默认值，强制用户输入
  })

  const entryFormRef = ref()

  // 文章搜索相关
  const selectedArticleId = ref<string>('')
  const articlesList = ref<any[]>([])
  const articlesLoading = ref(false)

  // 工作类型选项
  const workTypeOptions = [
    { label: '开发工作', value: '开发', color: '#409eff', isLeave: false },
    { label: '测试工作', value: '测试', color: '#67c23a', isLeave: false },
    { label: '标注工作', value: '标注', color: '#17a2b8', isLeave: false },
    { label: '审核工作', value: '审核', color: '#ff9800', isLeave: false },
    { label: '培训学习', value: '培训', color: '#9c27b0', isLeave: false },
    { label: '会议沟通', value: '会议', color: '#f56c6c', isLeave: false },
    { label: '文档编写', value: '文档', color: '#909399', isLeave: false },
    { label: '设计工作', value: '设计', color: '#e6a23c', isLeave: false },
    { label: '请假', value: '请假', color: '#f59e0b', isLeave: true },
    { label: '病假', value: '病假', color: '#ef4444', isLeave: true },
    { label: '年假', value: '年假', color: '#10b981', isLeave: true }
  ]

  // 根据用户角色获取默认工作类型
  const getDefaultWorkType = () => {
    const user = userStore.currentUser
    if (!user) return '开发'

    const role = user.role?.toLowerCase() || ''

    // 根据角色映射默认类型
    if (role.includes('annotator') || role.includes('标注')) {
      return '标注'
    } else if (role.includes('reviewer') || role.includes('审核')) {
      return '审核'
    } else if (role.includes('algorithm') || role.includes('算法')) {
      return '开发'
    } else if (role.includes('development') || role.includes('开发')) {
      return '开发'
    }

    return '开发' // 默认返回开发
  }

  // 工作标题快捷选项
  const workSubjectOptions = ref<Array<{ label: string; value: string }>>([])

  // 常用标题标签
  const commonSubjectTags = [
    // 日常工作
    { label: '日常标注', value: '日常标注工作', icon: '📋', color: '#409eff', desc: '标注任务' },
    { label: '算法研发', value: '算法研发与优化', icon: '🧪', color: '#67c23a', desc: '算法优化' },
    { label: '模型训练', value: '模型训练与调优', icon: '🎯', color: '#e6a23c', desc: '模型训练' },
    { label: '模型测试', value: '模型测试与验证', icon: '✅', color: '#67c23a', desc: '模型验证' },
    { label: '数据处理', value: '数据处理与分析', icon: '📊', color: '#409eff', desc: '数据分析' },
    { label: '代码开发', value: '功能开发与实现', icon: '💻', color: '#409eff', desc: '功能实现' },
    { label: 'Bug修复', value: 'Bug修复与优化', icon: '🐛', color: '#f56c6c', desc: '问题修复' },
    { label: '需求评审', value: '需求评审与讨论', icon: '📝', color: '#909399', desc: '需求讨论' },

    // 会议相关
    { label: '会议', value: '会议', icon: '👥', color: '#909399', desc: '各类会议' },
    { label: '招聘面试', value: '招聘面试', icon: '🤝', color: '#e6a23c', desc: '面试候选人' },
    { label: '客户沟通', value: '客户沟通', icon: '📞', color: '#409eff', desc: '客户交流' },

    // 外出相关
    { label: '出差', value: '出差', icon: '✈️', color: '#f56c6c', desc: '外地出差' },
    { label: '外出', value: '外出', icon: '🚗', color: '#e6a23c', desc: '外出办事' },
    { label: '培训学习', value: '培训学习', icon: '📚', color: '#67c23a', desc: '学习培训' },

    // 其他
    { label: '文档编写', value: '文档编写', icon: '📄', color: '#909399', desc: '编写文档' },
    { label: '技术调研', value: '技术调研', icon: '🔍', color: '#409eff', desc: '技术研究' },
    { label: '项目部署', value: '项目部署', icon: '🚀', color: '#67c23a', desc: '部署上线' },
    { label: '日常维护', value: '日常维护', icon: '🔧', color: '#909399', desc: '系统维护' }
  ]

  // 项目列表
  const projectsList = ref<any[]>([])

  // 根据工作类型获取颜色
  const getWorkTypeColor = (workType: string) => {
    const option = workTypeOptions.find((opt) => opt.value === workType)
    return {
      background: option ? `${option.color}12` : '#f5f7fa', // 降低到12%透明度
      border: option ? option.color : '#e4e7ed',
      text: option ? option.color : '#606266'
    }
  }

  // 表单验证规则
  const entryFormRules = {
    workType: [{ required: true, message: '请选择工作类型', trigger: 'change' }],
    workSubject: [
      { required: true, message: '请输入工作标题', trigger: 'blur' },
      { min: 2, max: 50, message: '工作标题长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    workContent: [
      { required: true, message: '请输入工作内容', trigger: 'blur' },
      { min: 5, max: 300, message: '工作内容长度在 5 到 300 个字符', trigger: 'blur' }
    ],
    actualHours: [
      { required: true, message: '请输入工作时间', trigger: 'blur' },
      {
        validator: (rule: any, value: any, callback: any) => {
          if (value === null || value === undefined || value === '') {
            callback(new Error('请输入工作时间'))
          } else if (isNaN(Number(value))) {
            callback(new Error('工作时间必须是数字'))
          } else if (Number(value) < 0.5 || Number(value) > 12) {
            callback(new Error('工作时间应在0.5-12小时之间'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }

  // 监听工作类型变化，自动设置请假标题
  watch(
    () => entryForm.workType,
    (newType) => {
      if (['请假', '病假', '年假'].includes(newType)) {
        // 如果是请假类型，自动设置标题为假期类型
        entryForm.workSubject = newType
      }
    }
  )

  // 方法
  const fetchWorkLogTypes = async () => {
    try {
      const response = await workLogTypeApi.getWorkLogTypes(true)
      // backendApi 返回的是完整响应对象 { code, msg, data: [...] }
      const data = (response as any).data || response
      workLogTypes.value = Array.isArray(data) ? data : []
    } catch (error) {
      console.error('获取工作类型失败:', error)
    }
  }

  // 处理标题类型切换
  const handleSubjectTypeChange = (newType: string | number | boolean | undefined) => {
    // 类型守卫：确保是有效的类型
    if (newType !== 'tag' && newType !== 'project') {
      console.warn('⚠️ [WorkLogEntryCell] 无效的标题类型:', newType)
      return
    }

    console.log('🔄 [WorkLogEntryCell] 切换标题类型:', newType)

    // 清空当前选择的工作标题
    entryForm.workSubject = ''

    // 如果切换到项目模式，加载项目列表
    if (newType === 'project') {
      loadProjects()
    }
  }

  const createEntry = () => {
    console.log('➕ [WorkLogEntryCell] 创建新的工作项')
    editingEntry.value = null
    resetForm()

    // 设置默认工作类型（根据用户角色）
    entryForm.workType = getDefaultWorkType()

    // 重置为常用标签模式
    subjectType.value = 'tag'

    // 加载项目列表（虽然默认不显示，但预加载可以提升体验）
    loadProjects()

    showEditDialog.value = true
  }

  // 加载项目列表
  const loadProjects = async () => {
    try {
      console.log('🔄 [WorkLogEntryCell] 加载项目列表...')
      const response = await projectApi.getProjects({
        page: 1,
        pageSize: 50
      })
      // projectApi.getProjects 直接返回数组，不是 { list: [] } 格式
      const allProjects = Array.isArray(response) ? response : []

      // 过滤出非完结项目
      projectsList.value = allProjects.filter((p: any) => p.status !== 'completed')
      console.log('✅ [WorkLogEntryCell] 加载了', projectsList.value.length, '个活跃项目')
    } catch (error) {
      console.error('❌ [WorkLogEntryCell] 加载项目列表失败:', error)
      projectsList.value = []
    }
  }

  const editEntry = async (entry?: WorkLogEntry) => {
    const targetEntry = entry || props.entry
    if (!targetEntry) return

    editingEntry.value = targetEntry

    // 解析工作内容
    const workSubject = getWorkSubjectFromContent(targetEntry.work_content)
    const workContent = getMainContentFromContent(targetEntry.work_content)

    entryForm.workType = targetEntry.work_type || '开发'
    entryForm.workSubject = workSubject === '工作' ? '' : workSubject
    entryForm.workContent = workContent === '暂无工作内容' ? '' : workContent
    entryForm.actualHours = targetEntry.actual_hours || undefined

    // 加载项目列表
    await loadProjects()

    // 智能判断标题类型
    // 如果标题在常用标签中，则设置为 tag 模式
    const isCommonTag = commonSubjectTags.some(
      (tag) => tag.value === entryForm.workSubject || tag.label === entryForm.workSubject
    )

    // 如果标题在项目列表中，则设置为 project 模式
    const isProject = projectsList.value.some((project) => project.name === entryForm.workSubject)

    if (isProject) {
      subjectType.value = 'project'
    } else {
      // 默认使用 tag 模式（包括常用标签和自定义输入）
      subjectType.value = 'tag'
    }

    showEditDialog.value = true
  }

  const deleteEntry = async (entry: WorkLogEntry) => {
    try {
      await ElMessageBox.confirm('确定要删除这个工作日志条目吗？删除后无法恢复。', '删除确认', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      })

      console.log('🗑️ [WorkLogEntryCell] 开始删除工作日志条目:', entry.id)

      // 调用删除API
      await workLogEntryApi.deleteWorkLogEntry(entry.id)

      // 通知父组件更新
      emit('entry-deleted', entry.id)

      ElMessage.success('工作日志已删除')
      
      // 如果是在编辑对话框中删除，则关闭对话框
      if (showEditDialog.value) {
        showEditDialog.value = false
      }
    } catch (error: any) {
      if (error === 'cancel') return
      console.error('❌ [WorkLogEntryCell] 删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }

  // 处理下拉菜单操作命令
  const handleActionCommand = (command: string | number | object, entry: WorkLogEntry) => {
    switch (command) {
      case 'edit':
        editEntry(entry)
        break
      case 'delete':
        deleteEntry(entry)
        break
    }
  }

  const resetForm = () => {
    entryForm.workType = '' // 不设置默认值，强制用户选择
    entryForm.workSubject = ''
    entryForm.workContent = ''
    entryForm.actualHours = undefined // 不设置默认值，强制用户输入

    // 清除文章选择
    selectedArticleId.value = ''
    articlesList.value = []

    // 清除编辑状态
    editingWorkItemId.value = null
  }

  // 搜索文章
  const searchArticles = async (query: string) => {
    if (!query || query.trim().length < 2) {
      articlesList.value = []
      return
    }

    try {
      articlesLoading.value = true

      // 并行搜索所有类型的文章和团队文档
      const [allArticlesRes, collabRes] = await Promise.all([
        // 不指定 type，搜索所有类型的文章
        articlesApi.list({ search: query, page: 1, page_size: 20 }).catch(() => ({ items: [] })),
        // 团队协作文档
        collaborationApi
          .getDocuments({ search: query, page: 1, page_size: 10 })
          .catch(() => ({ items: [] }))
      ])

      // 合并结果
      const articles: any[] = []

      // 所有类型的文章
      if (allArticlesRes?.items) {
        articles.push(...allArticlesRes.items)
      }

      // 团队协作文档
      if (collabRes?.items) {
        articles.push(...collabRes.items.map((item: any) => ({ ...item, type: 'collaboration' })))
      }

      articlesList.value = articles
    } catch (error) {
      console.error('搜索文章失败:', error)
      articlesList.value = []
    } finally {
      articlesLoading.value = false
    }
  }

  // 选择文章后插入链接
  const handleArticleSelect = (articleId: string) => {
    if (!articleId) return

    const article = articlesList.value.find((a) => a.id === articleId)
    if (!article) return

    // 构建文章链接
    let articleUrl = ''
    const baseUrl = window.location.origin

    // 根据文章类型生成对应的链接
    if (article.type === 'collaboration') {
      articleUrl = `${baseUrl}/login#/collaboration?articleId=${article.id}`
    } else if (article.type === 'work_record') {
      articleUrl = `${baseUrl}/login#/work-log/records?articleId=${article.id}`
    } else if (article.type === 'meeting') {
      articleUrl = `${baseUrl}/login#/articles/meeting?articleId=${article.id}`
    } else if (article.type === 'model_test') {
      articleUrl = `${baseUrl}/login#/articles/model-test?articleId=${article.id}`
    } else if (article.project_id) {
      articleUrl = `${baseUrl}/login#/project/management?projectId=${article.project_id}&articleId=${article.id}`
    } else {
      const typeRoute = article.type
      articleUrl = `${baseUrl}/login#/articles/${typeRoute}?articleId=${article.id}`
    }

    // 插入链接到工作内容
    const linkText = `\n相关文章：${article.title}\n链接：${articleUrl}\n`

    if (entryForm.workContent) {
      entryForm.workContent += linkText
    } else {
      entryForm.workContent = linkText.trim()
    }

    ElMessage.success(`已插入文章链接：${article.title}`)

    // 清除选择
    selectedArticleId.value = ''
  }

  // 获取文章类型标签
  const getArticleTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      meeting: '会议记录',
      model_test: '模型测试',
      collaboration: '团队文档',
      requirement: '需求文档',
      design: '设计文档',
      tech: '技术文档',
      report: '报告文档',
      plan: '计划文档',
      summary: '总结文档'
    }
    return labels[type] || type
  }

  // 获取文章标签类型
  const getArticleTagType = (type: string) => {
    const types: Record<string, any> = {
      meeting: 'danger',
      model_test: 'warning',
      collaboration: 'primary',
      requirement: 'success',
      design: 'info',
      tech: '',
      report: 'warning',
      plan: 'primary',
      summary: 'success'
    }
    return types[type] || 'info'
  }

  const saveEntry = async (): Promise<WorkLogEntry | null> => {
    try {
      // 表单验证
      const isValid = await entryFormRef.value.validate().catch((error: any) => {
        const firstError = Object.values(error)[0]
        if (Array.isArray(firstError) && firstError.length > 0) {
          ElMessage.error(firstError[0].message || '表单验证失败')
        } else {
          ElMessage.error('请检查表单输入')
        }
        return false
      })

      if (!isValid) {
        return null
      }

      saving.value = true
      let savedEntry: WorkLogEntry | null = null

      if (editingEntry.value) {
        // 更新现有条目
        const updateData: WorkLogEntryUpdate = {
          work_content: `${entryForm.workSubject}|${entryForm.workContent}`,
          work_type: entryForm.workType,
          priority: 'normal',
          planned_hours: Math.ceil(entryForm.actualHours || 0),
          actual_hours: Math.ceil(entryForm.actualHours || 0),
          completion_rate: 100,
          difficulties: '',
          next_day_plan: '',
          remarks: ''
        }

        const response = await workLogEntryApi.updateWorkLogEntry(editingEntry.value.id, updateData)
        const data = (response as any).data || response
        savedEntry = data as WorkLogEntry
        emit('entry-updated', savedEntry)

        ElMessage.success('工作日志已更新')
      } else {
        // 创建新条目
        const createData: WorkLogEntryCreate = {
          work_week_id: props.workWeekId,
          work_date: props.workDate,
          work_content: `${entryForm.workSubject}|${entryForm.workContent}`,
          work_type: entryForm.workType,
          priority: 'normal',
          planned_hours: Math.ceil(entryForm.actualHours || 0),
          actual_hours: Math.ceil(entryForm.actualHours || 0),
          completion_rate: 100,
          difficulties: '',
          next_day_plan: '',
          remarks: ''
        }

        try {
          const response = await workLogEntryApi.createWorkLogEntry(createData)
          const data = (response as any).data || response
          savedEntry = data as WorkLogEntry
          emit('entry-updated', savedEntry)
          ElMessage.success('工作日志已保存')
        } catch (apiError: any) {
          console.error('❌ [WorkLogEntryCell] API调用失败:', apiError)
          throw apiError
        }
      }

      showEditDialog.value = false
      return savedEntry
    } catch (error: any) {
      console.error('❌ [WorkLogEntryCell] 保存失败:', error)
      if (error.status === 400) {
        ElMessage.error(`创建工作日志失败：${error.message || '请求参数有误'}`)
      } else {
        ElMessage.error('保存失败，请检查网络连接或联系管理员')
      }
      return null
    } finally {
      saving.value = false
    }
  }

  // 计算属性
  const displayEntries = computed(() => {
    if (props.entries && props.entries.length > 0) {
      return props.entries
    } else if (props.entry) {
      return [props.entry]
    }
    return []
  })

  const canEditEntry = computed(() => {
    return props.canEdit
  })

  const canAddMoreWorkItems = computed(() => {
    return canEditEntry.value && displayEntries.value.length > 0
  })

  // 检查是否有附件/链接
  const hasAttachments = (entry: WorkLogEntry) => {
    if (!entry.work_content) return false
    return entry.work_content.includes('相关文章：') && entry.work_content.includes('链接：')
  }

  // 工具方法
  const formatHours = (hours: number | undefined): string => {
    if (!hours || hours === 0) return '0h'
    return `${hours}h`
  }

  const formatContentWithLinks = (text: string | undefined): string => {
    if (!text) return ''
    const escapeHtml = (str: string) => {
      const div = document.createElement('div')
      div.textContent = str
      return div.innerHTML
    }
    const escapedText = escapeHtml(text)
    let formattedText = escapedText.replace(/\n/g, '<br>')
    const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+)/gi
    formattedText = formattedText.replace(urlRegex, (url) => {
      let cleanUrl = url
      const punctuation = /[。，、；：！？）】》」,.;:!?)}\]>]+$/
      const match = url.match(punctuation)
      let trailing = ''
      if (match) {
        trailing = match[0]
        cleanUrl = url.slice(0, -trailing.length)
      }
      return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="content-link" onclick="event.stopPropagation()">${cleanUrl}</a>${trailing}`
    })
    return formattedText
  }

  const getWorkSubjectFromContent = (content?: string): string => {
    if (!content) return '工作'
    const parts = content.split('|')
    return parts[0] || '工作'
  }

  const getMainContentFromContent = (content?: string): string => {
    if (!content) return '暂无工作内容'
    const parts = content.split('|')
    return parts[1] || content
  }

  onMounted(() => {
    fetchWorkLogTypes()
  })
</script>

<style lang="scss" scoped>
.work-log-entry-cell {
  width: 100%;
  min-height: 100%; /* 填满单元格 */
  
  .entries-wrapper {
    display: flex;
    flex-direction: column;
    gap: 6px; /* 增加条目间距 */
  }

  /* 卡片样式 - 更紧凑、现代化 */
  .entry-card {
    position: relative;
    display: flex;
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* 轻微阴影 */
    border: 1px solid transparent;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    cursor: pointer; /* 保持手型，虽然不触发详情，但表示可交互（如下拉菜单） */
    border-left: 3px solid var(--type-color); /* 左侧颜色条 */
    background: linear-gradient(to right, var(--type-bg), rgba(255, 255, 255, 0) 30%); /* 渐变背景 */

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      border-color: var(--type-color);
      
      .action-trigger {
        opacity: 1;
      }
    }

    /* 主要内容区域 */
    .entry-main {
      flex: 1;
      padding: 8px 10px; /* 紧凑内边距 */
      min-width: 0; /* 防止flex子项溢出 */
    }

    /* 头部 */
    .entry-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 6px;
      line-height: 1.2;

      .header-left {
        flex: 1;
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 6px;
        
        .index-badge {
          background: rgba(0, 0, 0, 0.05);
          color: #606266;
          font-size: 10px;
          padding: 1px 4px;
          border-radius: 4px;
          font-weight: 700;
        }

        .work-subject {
          font-weight: 700;
          font-size: 13px;
          color: #303133;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .header-right {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-left: 8px;
        flex-shrink: 0;

        .hours-badge {
          background: #f0f2f5;
          color: #606266;
          font-size: 11px;
          padding: 1px 6px;
          border-radius: 10px;
          font-weight: 600;
        }

        .action-trigger {
          opacity: 1; /* 常驻显示 */
          transition: all 0.2s;
          
          .more-btn {
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            color: #c0c4cc;
            cursor: pointer;
            
            &:hover {
              background: rgba(0, 0, 0, 0.05);
              color: #606266;
            }
          }
        }
      }
    }

    /* 内容摘要 */
    .entry-body {
      .content-text {
        font-size: 12px;
        color: #606266;
        line-height: 1.5;
        white-space: pre-wrap; /* 保留换行 */
        word-break: break-word;
        /* 移除 line-clamp，显示全部内容 */
        
        /* 链接样式优化 */
        :deep(.content-link) {
          color: #409eff;
          text-decoration: none;
          &:hover { text-decoration: underline; }
        }
      }
    }

    /* 底部标签 */
    .entry-footer {
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px dashed rgba(0, 0, 0, 0.05);
      
      .footer-tags {
        display: flex;
        gap: 4px;
        
        .mini-tag {
          display: flex;
          align-items: center;
          gap: 2px;
          font-size: 10px;
          padding: 1px 4px;
          border-radius: 3px;
          
          &.warning { background: #fdf6ec; color: #e6a23c; }
          &.plan { background: #ecf5ff; color: #409eff; }
          &.link { background: #f0f9ff; color: #0ea5e9; }
          
          .el-icon { font-size: 11px; }
        }
      }
    }
  }

  /* 空状态 - 更像是一个待填写的槽位 */
  .empty-slot {
    height: 100%;
    min-height: 100px; /* 保证足够点击区域 */
    border: 1px dashed #e4e7ed;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    background: #fff; /* 改为白色背景，更干净 */

    /* 可点击状态（添加日志） */
    &.clickable {
      cursor: pointer;
      border-color: #dcdfe6; /* 默认边框稍微加深 */
      color: #606266; /* 默认文字颜色加深 */
      background: #fafafa; /* 默认微灰色背景 */

      &:hover {
        border-color: #409eff;
        color: #409eff;
        background: #ecf5ff;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15); /* 悬停增加阴影 */
        transform: translateY(-1px); /* 悬停轻微上浮 */
        
        .add-btn-inner {
          transform: scale(1.05); /* 内部元素轻微放大 */
        }
      }
      
      .add-btn-inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        transition: transform 0.2s;
        
        .add-icon { 
          font-size: 24px; /* 加大图标 */
          font-weight: bold;
        }
        
        .add-text { 
          font-size: 13px; 
          font-weight: 500;
        }
      }
    }

    /* 不可点击状态（暂无数据） */
    .no-data-slot {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      
      .no-data-text { 
        font-size: 13px; 
        color: #909399; /* 浅灰色文字 */
        background: #f5f7fa; /* 浅灰色背景块 */
        padding: 4px 12px;
        border-radius: 12px;
      }
    }
  }

  /* 添加更多按钮 - 紧凑型 */
  .append-btn {
    margin-top: 4px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px dashed #dcdfe6;
    border-radius: 4px;
    color: #909399;
    cursor: pointer;
    transition: all 0.2s;
    background: rgba(255, 255, 255, 0.8); /* 增加背景不透明度 */

    &:hover {
      border-color: #409eff;
      color: #409eff;
      background: #ecf5ff;
      transform: translateY(-1px); /* 悬停轻微上浮 */
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 悬停增加阴影 */
    }
    
    .el-icon { font-size: 12px; }
  }
}

/* Dialog 内部样式保持不变，仅优化细节 */
.work-item-dialog-new {
  .form-section {
    padding: 24px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .section-header {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      
      .section-icon { 
        font-size: 20px; 
        color: #409eff; 
        background: #ecf5ff;
        padding: 8px;
        border-radius: 8px;
        box-sizing: content-box;
      }
      
      h3 { margin: 0 0 4px 0; font-size: 16px; color: #303133; }
      p { margin: 0; font-size: 13px; color: #909399; }
    }
  }

  .dialog-footer {
    padding: 20px 28px;
    background: var(--art-bg-color);
    border-top: 1px solid var(--art-card-border);
    display: flex;
    justify-content: space-between; /* 改为两端对齐 */
    align-items: center;
    margin: 0;

    .footer-left {
      .el-button {
        padding: 8px 16px;
        color: #f56c6c;
        
        &:hover {
          background-color: #fef0f0;
        }
      }
    }

    .footer-right {
      display: flex;
      gap: 12px;
    }

    .el-button {
      font-weight: 500;
    }
  }
}

.work-type-option, .subject-option, .article-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-dot { width: 8px; height: 8px; border-radius: 50%; }
</style>

<!-- 全局样式，用于自定义 Select 下拉菜单 -->
<style lang="scss">
/* 修复下拉菜单被弹窗遮挡的问题，强制提升层级 */
.work-type-popper,
.work-subject-popper,
.article-popper {
  z-index: 3100 !important; /* 大于弹窗的 3000 */
}

.work-subject-popper {
  .el-select-dropdown__item {
    height: auto !important;
    padding: 10px 12px;
    line-height: normal !important;
    min-height: 50px;
    display: flex;
    align-items: center;
    
    &.selected {
      color: #409eff;
      font-weight: normal;
      background-color: #f5f7fa;
    }
  }

  .subject-option {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding-right: 12px; /* 增加右侧内边距，防止文字贴边 */
    
    .tag-icon-wrapper {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
    }
    
    .tag-info {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;
      
      .tag-label {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        line-height: 1.4;
      }
      
      .tag-desc {
        font-size: 12px;
        color: #909399;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    /* 项目选项特殊样式 */
    &.project-option {
      align-items: center;
      
      .project-icon {
        font-size: 18px;
        color: #409eff;
        background: #ecf5ff;
        padding: 6px;
        border-radius: 6px;
        box-sizing: content-box;
      }
      
      .project-name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
    }
  }
}

.article-popper {
  .article-option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    
    .article-title {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: #303133;
    }
  }
}
</style>
