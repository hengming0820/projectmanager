<template>
  <div class="article-create-container">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="left-actions">
        <el-button @click="goBack" :icon="ArrowLeft" circle />
        <h2 class="page-title">{{ pageTitle }}</h2>
      </div>
      <div class="right-actions">
        <el-button @click="openImportMarkdown">
          <el-icon><Document /></el-icon>
          导入 Markdown
        </el-button>
        <el-button @click="openImportWord">
          <el-icon><Document /></el-icon>
          导入 Word
        </el-button>
        <el-button type="primary" :loading="submitting" @click="submit">
          <el-icon v-if="!submitting"><Check /></el-icon>
          发布文章
        </el-button>
      </div>
    </div>

    <!-- 主编辑区域 -->
    <div class="main-content">
      <!-- 左侧：设置面板 -->
      <div class="settings-panel">
        <!-- 项目提示 -->
        <el-alert
          v-if="projectName"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #title>
            <span style="font-size: 13px">正在为项目「{{ projectName }}」创建文章</span>
          </template>
        </el-alert>

        <!-- 工作记录说明 -->
        <el-alert
          v-if="isWorkRecord"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <div style="font-size: 13px; line-height: 1.8">
            <strong style="font-size: 14px; margin-bottom: 8px; display: block"
              >📝 工作记录说明</strong
            >
            <span style="color: #606266"
              >工作记录为个人记录，自动归属到您所在的部门。只有您本人和管理员可以编辑/删除，所有人可以查看。</span
            >
          </div>
        </el-alert>

        <!-- 基础设置 -->
        <div class="panel-section">
          <div class="section-title">
            <el-icon><Setting /></el-icon>
            基础设置
          </div>

          <!-- 分类 -->
          <div v-if="!isWorkRecord" class="form-item">
            <label class="item-label">文章类型</label>
            <el-select v-model="form.category" placeholder="选择文章类型" class="item-select">
              <el-option
                v-for="opt in categoryOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>

          <!-- 可见性 -->
          <div v-if="!isWorkRecord" class="form-item">
            <label class="item-label">可见性</label>
            <el-switch v-model="form.is_public" active-text="公开" inactive-text="私有" />
          </div>
        </div>

        <el-divider v-if="!isWorkRecord" style="margin: 16px 0" />

        <!-- 权限设置 -->
        <div v-if="!isWorkRecord" class="panel-section">
          <div class="section-title">
            <el-icon><User /></el-icon>
            权限设置
          </div>

          <!-- 可编辑角色 -->
          <div class="form-item">
            <label class="item-label">可编辑角色</label>
            <el-select
              v-model="form.editable_roles"
              multiple
              filterable
              placeholder="选择可编辑角色"
              class="item-select"
              collapse-tags
              collapse-tags-tooltip
              :loading="rolesLoading"
              popper-class="high-z-index-popper"
            >
              <el-option
                v-for="role in roleOptions"
                :key="role.value"
                :label="role.label"
                :value="role.value"
              />
            </el-select>
          </div>

          <!-- 可编辑成员 -->
          <div class="form-item">
            <label class="item-label">可编辑成员</label>
            <el-select
              v-model="form.editable_user_ids"
              multiple
              filterable
              placeholder="选择人员"
              class="item-select"
              collapse-tags
              collapse-tags-tooltip
              :disabled="form.editable_roles.length === 0"
              popper-class="high-z-index-popper"
            >
              <el-option
                v-for="u in filteredUserOptions"
                :key="u.value"
                :label="u.label"
                :value="u.value"
              >
                <span>{{ u.label }}</span>
                <span style="color: #8492a6; font-size: 12px; margin-left: 8px">
                  ({{ roleOptions.find((r) => r.value === u.role)?.label || u.role }})
                </span>
              </el-option>
            </el-select>
            <div v-if="form.editable_roles.length === 0" class="item-tip" style="color: #e6a23c">
              请先选择可编辑角色，系统将自动选择该角色的所有成员
            </div>
            <div v-else class="item-tip">
              已自动选择 {{ form.editable_user_ids.length }} 人（可手动调整）
            </div>
          </div>

          <!-- 所属部门 -->
          <div class="form-item">
            <label class="item-label">所属部门</label>
            <el-select
              v-model="form.departments"
              multiple
              filterable
              placeholder="选择部门"
              class="item-select"
              collapse-tags
              collapse-tags-tooltip
              popper-class="high-z-index-popper"
            >
              <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
            </el-select>
          </div>
        </div>

        <el-divider v-if="!isWorkRecord" style="margin: 16px 0" />

        <!-- 归属项目 -->
        <div v-if="!isWorkRecord" class="panel-section">
          <div class="section-title">
            <el-icon><Box /></el-icon>
            归属项目
          </div>
          <div class="form-item">
            <el-select
              v-model="form.project_id"
              filterable
              clearable
              placeholder="选择项目（可选）"
              class="item-select"
              :disabled="!!projectId"
              v-loading="loadingProjects"
            >
              <el-option
                v-for="proj in projectOptions"
                :key="proj.id"
                :label="proj.name"
                :value="proj.id"
              />
            </el-select>
            <div class="item-tip"> 选择项目后，文章可在项目管理中查看 </div>
          </div>
        </div>

        <el-divider v-if="!isWorkRecord" style="margin: 16px 0" />

        <!-- 封面设置 -->
        <div v-if="!isWorkRecord" class="panel-section">
          <div class="section-title">
            <el-icon><Picture /></el-icon>
            封面设置
          </div>
          <div class="form-item">
            <el-upload
              list-type="picture-card"
              v-model:file-list="coverList"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :on-success="onCoverUploaded"
              :on-remove="onCoverRemoved"
              accept="image/*"
              :limit="1"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <div class="item-tip">建议尺寸 16:9，jpg/png 格式</div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="panel-section stats-section">
          <el-divider style="margin: 16px 0 12px 0" />
          <div class="stat-item">
            <span class="stat-label">标题字数</span>
            <span class="stat-value">{{ form.title.length }} / 100</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">摘要字数</span>
            <span class="stat-value">{{ form.summary.length }} / 500</span>
          </div>
        </div>
      </div>

      <!-- 右侧：编辑器 -->
      <div class="editor-section">
        <!-- 标题输入 -->
        <div class="title-input-wrapper">
          <el-input
            v-model="form.title"
            placeholder="请输入文章标题..."
            class="title-input"
            maxlength="100"
            :show-word-limit="false"
          />
        </div>

        <!-- 摘要输入 -->
        <div v-if="!isWorkRecord" class="description-input-wrapper">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="2"
            placeholder="添加文章摘要（可选，用于卡片展示）"
            maxlength="500"
            :show-word-limit="false"
            class="description-input"
          />
        </div>

        <!-- 分隔线 -->
        <el-divider style="margin: 16px 0" />

        <!-- 富文本编辑器 -->
        <div class="editor-wrapper">
          <ArtTextbusEditor
            ref="editorRef"
            v-model="form.content"
            :height="editorHeight"
            placeholder="开始编写你的文章..."
          />
        </div>
      </div>
    </div>

    <!-- 导入 Markdown 对话框 -->
    <el-dialog 
      v-model="showMdDialog" 
      title="导入 Markdown 文档" 
      width="520px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <p class="dialog-tip">
        选择一个 .md/.markdown 文件，第一行作为标题，其余内容将转换为正文。
      </p>
      <el-upload
        :auto-upload="false"
        :show-file-list="false"
        accept=".md,.markdown,text/markdown,text/plain"
        :on-change="onMdSelected"
        drag
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">点击或拖拽 Markdown 文件到此处</div>
      </el-upload>
      <div v-if="mdFileName" class="file-selected">
        已选择：<strong>{{ mdFileName }}</strong>
      </div>
      <template #footer>
        <el-button @click="showMdDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 导入 Word 对话框 -->
    <el-dialog 
      v-model="showWordDialog" 
      title="导入 Word 文档" 
      width="520px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <p class="dialog-tip">
        选择一个 .docx 文件（Word 2007及以上版本），内容将自动转换为HTML格式。
      </p>
      <el-upload
        :auto-upload="false"
        :show-file-list="false"
        accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        :on-change="onWordSelected"
        drag
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">点击或拖拽 Word 文件到此处</div>
      </el-upload>
      <div v-if="wordFileName" class="file-selected">
        已选文件：<strong>{{ wordFileName }}</strong>
      </div>
      <el-alert
        v-if="wordImporting"
        title="正在导入，请稍候..."
        type="info"
        :closable="false"
        style="margin-top: 12px"
      />
      <template #footer>
        <el-button @click="showWordDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import {
    ArrowLeft,
    Check,
    Document,
    Setting,
    User,
    Plus,
    Picture,
    UploadFilled,
    Box
  } from '@element-plus/icons-vue'
  import ArtTextbusEditor from '@/components/core/forms/art-textbus-editor/index.vue'
  import { useUserStore } from '@/store/modules/user'
  import { articlesApi } from '@/api/articlesApi'
  import { userApi } from '@/api/userApi'
  import { projectApi } from '@/api/projectApi'
  import { roleApi } from '@/api/roleApi'
  import mammoth from 'mammoth'
  import {
    markdownToHtml,
    parseMarkdownFile,
    validateMarkdownFile,
    readMarkdownFile
  } from '@/utils/markdown'

  const route = useRoute()
  const router = useRouter()
  const userStore = useUserStore()

  // 编辑器引用
  const editorRef = ref<any>(null)

  // 从路由获取参数
  const articleType = computed(() => route.params.type as string)
  const projectId = computed(() => (route.query.projectId as string) || '')
  const projectName = computed(() => (route.query.projectName as string) || '')

  // 页面标题
  const pageTitle = computed(() => {
    if (isWorkRecord.value) return '创建工作记录'
    if (articleType.value === 'meeting') return '创建会议记录'
    if (articleType.value === 'model_test') return '创建模型测试'
    return '创建文章'
  })

  // 是否为工作记录
  const isWorkRecord = computed(() => articleType.value === 'work_record')

  // 表单数据
  const form = ref({
    title: '',
    summary: '',
    content: '',
    category: '',
    is_public: true,
    cover_url: '',
    editable_roles: [] as string[],
    editable_user_ids: [] as string[],
    departments: [] as string[],
    project_id: (projectId.value && projectId.value.trim()) ? String(projectId.value).trim() : undefined,
    type: articleType.value // 后端期望的是 type 字段
  })

  // 监听路由参数变化，更新 form 中的 project_id
  watch(
    () => projectId.value,
    (newProjectId) => {
      console.log('👀 [ArticleCreate] 路由 projectId 变化:', {
        old: form.value.project_id,
        new: newProjectId,
        trimmed: newProjectId && newProjectId.trim() ? String(newProjectId).trim() : undefined
      })
      if (newProjectId && newProjectId.trim()) {
        form.value.project_id = String(newProjectId).trim()
      } else {
        form.value.project_id = undefined
      }
    },
    { immediate: true }
  )

  const submitting = ref(false)
  const rolesLoading = ref(false)
  const loadingProjects = ref(false)

  // 选项数据
  const userOptions = ref<Array<{ label: string; value: string; role: string }>>([])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])
  const deptOptions = ref<string[]>([]) // 从用户数据中动态获取
  const projectOptions = ref<Array<{ id: string; name: string }>>([])
  const coverList = ref<any[]>([])

  // 分类选项
  const categoryOptions = computed(() => {
    if (articleType.value === 'meeting') {
      return [
        { label: '周会', value: '周会' },
        { label: '月会', value: '月会' },
        { label: '项目会', value: '项目会' },
        { label: '需求评审', value: '需求评审' },
        { label: '技术分享', value: '技术分享' },
        { label: '其他', value: '其他' }
      ]
    } else if (articleType.value === 'model_test') {
      return [
        { label: '胸肺', value: '胸肺' },
        { label: '泌尿', value: '泌尿' },
        { label: '肝胆', value: '肝胆' },
        { label: '盆腔', value: '盆腔' },
        { label: '其他', value: '其他' }
      ]
    }
    return [
      { label: '技术', value: '技术' },
      { label: '产品', value: '产品' },
      { label: '设计', value: '设计' },
      { label: '运营', value: '运营' },
      { label: '其他', value: '其他' }
    ]
  })

  // 根据选中的角色筛选用户
  const filteredUserOptions = computed(() => {
    if (form.value.editable_roles.length === 0) {
      return []
    }
    return userOptions.value.filter((u) => u.role && form.value.editable_roles.includes(u.role))
  })

  // 上传相关
  const uploadUrl = computed(() => '/api/common/upload/images')
  const uploadHeaders = computed(() => ({ Authorization: userStore.accessToken }))

  const onCoverUploaded = (res: any, file: any) => {
    const raw = res?.data?.files?.[0]?.url || res?.data?.url || res?.url
    const url =
      typeof raw === 'string'
        ? raw.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/')
        : raw
    if (url) {
      form.value.cover_url = url
      coverList.value = [{ name: file.name, url }]
    }
  }

  const onCoverRemoved = () => {
    form.value.cover_url = ''
    coverList.value = []
  }

  // 计算编辑器高度
  const editorHeight = computed(() => {
    return isWorkRecord.value ? 'calc(100vh - 360px)' : 'calc(100vh - 420px)'
  })

  // 监听角色变化，自动选择该角色的所有成员
  watch(
    () => form.value.editable_roles,
    (newRoles, oldRoles) => {
      if (!newRoles || newRoles.length === 0) {
        // 如果没有选择角色，清空成员
        form.value.editable_user_ids = []
        return
      }

      // 获取所有选中角色的成员
      const selectedUserIds = userOptions.value
        .filter((u) => u.role && newRoles.includes(u.role))
        .map((u) => u.value)

      // 自动选择所有该角色的成员
      form.value.editable_user_ids = selectedUserIds
    },
    { deep: true }
  )

  // 加载数据
  onMounted(() => {
    console.log('🚀 [ArticleCreate] 页面挂载，路由参数:', {
      articleType: articleType.value,
      projectId: projectId.value,
      projectName: projectName.value,
      routeQuery: route.query,
      formProjectId: form.value.project_id
    })
    loadUsersAndRoles()
    loadProjects()
  })

  const loadUsersAndRoles = async () => {
    try {
      rolesLoading.value = true

      // 加载用户列表 - 使用 getUsersBasic (包含 role 字段，所有用户可访问)
      const result: any = await userApi.getUsersBasic({ status: 'active', size: 9999 })

      // 兼容多种返回格式
      const users = result?.data?.users || result?.data?.list || []

      userOptions.value = users.map((u: any) => ({
        label: u.real_name || u.realName || u.username || u.userName || u.id,
        value: u.id,
        role: u.role
      }))

      // 从用户列表中提取部门列表
      const deptSet = new Set<string>()
      users.forEach((u: any) => {
        if (u.department && u.department.trim()) {
          deptSet.add(u.department.trim())
        }
      })
      deptOptions.value = Array.from(deptSet).sort()
      console.log('✅ [ArticleCreate] 加载了', deptOptions.value.length, '个部门:', deptOptions.value)

      // 获取角色列表（所有登录用户都可以访问）
      try {
        const roleRes: any = await roleApi.getRoles({ size: 9999 })
        const roleList: any[] = roleRes?.data?.list || roleRes?.data?.roles || []
        roleOptions.value = roleList.map((r) => ({
          label: r.name, // 中文显示名称
          value: r.role // 英文角色编码
        }))
        console.log('✅ [ArticleCreate] 角色列表加载成功，数量:', roleOptions.value.length)
      } catch (roleError) {
        console.error('❌ [ArticleCreate] 加载角色列表失败:', roleError)
        roleOptions.value = []
      }
    } catch (e) {
      console.error('加载用户和角色列表失败:', e)
      ElMessage.warning('加载用户列表失败，部分功能可能受限')
    } finally {
      rolesLoading.value = false
    }
  }

  const loadProjects = async () => {
    try {
      loadingProjects.value = true
      console.log('🔄 [ArticleCreate] 开始加载项目列表，当前 projectId:', projectId.value)
      
      const projects: any = await projectApi.getProjects({ page: 1, pageSize: 9999 })
      const projectList = Array.isArray(projects) ? projects : []
      projectOptions.value = projectList.map((p: any) => ({ id: String(p.id), name: p.name }))
      
      console.log('✅ [ArticleCreate] 加载了', projectOptions.value.length, '个项目')
      console.log('📋 [ArticleCreate] 项目列表前5项:', projectOptions.value.slice(0, 5))
      
      // 项目列表加载完成后，如果路由参数中有 projectId，确保 form.project_id 被正确设置
      if (projectId.value && projectId.value.trim()) {
        const routeProjectId = String(projectId.value).trim()
        console.log('🔍 [ArticleCreate] 尝试在项目列表中查找项目ID:', routeProjectId)
        
        // 检查项目列表中是否存在该项目
        const foundProject = projectOptions.value.find((p) => String(p.id) === routeProjectId)
        
        if (foundProject) {
          form.value.project_id = routeProjectId
          console.log('✅ [ArticleCreate] 自动选中项目:', {
            id: foundProject.id,
            name: foundProject.name,
            formProjectId: form.value.project_id
          })
        } else {
          console.warn('⚠️ [ArticleCreate] 路由参数中的项目ID未在项目列表中找到')
          console.warn('⚠️ [ArticleCreate] 期望的项目ID:', routeProjectId)
          console.warn('⚠️ [ArticleCreate] 可用的项目ID:', projectOptions.value.map(p => p.id))
        }
      } else {
        console.log('ℹ️ [ArticleCreate] 无路由 projectId，不自动选择项目')
      }
    } catch (e) {
      console.error('❌ [ArticleCreate] 加载项目列表失败:', e)
      projectOptions.value = []
    } finally {
      loadingProjects.value = false
      console.log('🏁 [ArticleCreate] 项目列表加载完成，最终 form.project_id:', form.value.project_id)
    }
  }

  // 提交
  const submit = async () => {
    if (!form.value.title.trim()) {
      ElMessage.warning('请输入文章标题')
      return
    }

    if (!form.value.content.trim()) {
      ElMessage.warning('请输入文章内容')
      return
    }

    try {
      submitting.value = true

      const submitData: any = {
        ...form.value,
        type: articleType.value // 确保使用正确的 type 字段
      }

      // 清理空值：将空字符串转为 undefined
      if (!submitData.project_id) {
        submitData.project_id = undefined
      }
      if (!submitData.summary) {
        submitData.summary = undefined
      }
      if (!submitData.category) {
        submitData.category = undefined
      }
      if (!submitData.cover_url) {
        submitData.cover_url = undefined
      }

      console.log('📤 [ArticleCreate] 提交数据:', submitData)

      const response: any = await articlesApi.create(submitData)
      
      // 获取新创建的文章ID
      const newArticle = response?.data || response
      const newArticleId = newArticle?.id
      
      console.log('✅ [ArticleCreate] 文章创建成功:', {
        articleId: newArticleId,
        article: newArticle
      })
      
      ElMessage.success('文章发布成功')

      // 跳转回列表或项目页面
      // 优先检查 form 中的 project_id（可能从项目选择器中选择），其次检查路由参数
      const finalProjectId = submitData.project_id || projectId.value
      const hasProjectId = finalProjectId && String(finalProjectId).trim() !== ''
      
      console.log('🔍 [ArticleCreate] 跳转判断:', {
        routeProjectId: projectId.value,
        formProjectId: submitData.project_id,
        finalProjectId,
        hasProjectId,
        articleType: articleType.value,
        projectName: projectName.value,
        newArticleId: newArticleId,
        routeQuery: route.query
      })
      
      if (hasProjectId) {
        // 如果有项目ID和文章ID，跳转回项目列表页面并自动定位到新发布的文章
        if (newArticleId) {
          console.log('✅ [ArticleCreate] 跳转到项目列表并定位到新文章，projectId:', finalProjectId, 'articleId:', newArticleId)
          router.replace({ 
            name: 'ProjectManagement',
            query: { 
              projectId: String(finalProjectId),
              articleId: String(newArticleId)
            }
          })
        } else {
          // 没有文章ID，只跳转到项目（会刷新文章列表）
          console.log('✅ [ArticleCreate] 跳转到项目列表页面，projectId:', finalProjectId)
          router.replace({ 
            name: 'ProjectManagement',
            query: { projectId: String(finalProjectId) }
          })
        }
      } else if (articleType.value === 'meeting') {
        // 如果没有项目ID，且是会议记录，跳转到知识与文章下的会议记录页面
        console.log('✅ [ArticleCreate] 跳转到会议记录页面（无项目ID）')
        router.replace({ name: 'MeetingNotes' })
      } else if (articleType.value === 'model_test') {
        // 如果没有项目ID，且是模型测试，跳转到知识与文章下的模型测试页面
        console.log('✅ [ArticleCreate] 跳转到模型测试页面（无项目ID）')
        router.replace({ name: 'ModelTests' })
      } else {
        // 其他情况返回上一页
        console.log('✅ [ArticleCreate] 返回上一页')
        router.back()
      }
    } catch (e: any) {
      console.error('发布文章失败:', e)
      ElMessage.error('发布文章失败')
    } finally {
      submitting.value = false
    }
  }

  const goBack = () => {
    router.back()
  }

  // ============ 导入 Markdown ============
  const showMdDialog = ref(false)
  const mdFileName = ref('')
  const openImportMarkdown = () => {
    showMdDialog.value = true
    mdFileName.value = ''
  }

  const onMdSelected = async (file: any) => {
    try {
      const raw: File = file?.raw || file
      if (!raw) return

      mdFileName.value = raw.name

      const validation = validateMarkdownFile(raw)
      if (!validation.valid) {
        ElMessage.warning(validation.error || 'Markdown 文件无效')
        return
      }

      const content = await readMarkdownFile(raw)
      const { title, body } = parseMarkdownFile(content)
      const html = markdownToHtml(body, {
        gfm: true,
        openLinksInNewWindow: true,
        sanitize: true
      })

      if (title && !form.value.title) {
        form.value.title = title
      }

      form.value.content = html
      showMdDialog.value = false
      ElMessage.success('Markdown 已导入')
    } catch (e: any) {
      console.error('Markdown 导入失败:', e)
      ElMessage.error(`Markdown 导入失败: ${e.message || '未知错误'}`)
    }
  }

  // ============ 导入 Word ============
  const showWordDialog = ref(false)
  const wordFileName = ref('')
  const wordImporting = ref(false)
  const openImportWord = () => {
    showWordDialog.value = true
    wordFileName.value = ''
    wordImporting.value = false
  }

  const onWordSelected = async (file: any) => {
    try {
      const raw: File = file?.raw || file
      if (!raw) return

      wordFileName.value = raw.name
      wordImporting.value = true

      const arrayBuffer = await raw.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })

      if (result.value) {
        form.value.content = result.value
        showWordDialog.value = false
        ElMessage.success('Word 文档已导入')

        if (result.messages && result.messages.length > 0) {
          const warnings = result.messages.filter((m: any) => m.type === 'warning')
          if (warnings.length > 0) {
            console.warn('Word导入警告:', warnings)
          }
        }
      } else {
        ElMessage.warning('Word 文档内容为空')
      }
    } catch (e: any) {
      console.error('Word 导入失败:', e)
      ElMessage.error(`Word 导入失败: ${e.message || '未知错误'}`)
    } finally {
      wordImporting.value = false
    }
  }
</script>

<style scoped lang="scss">
  .article-create-container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--art-bg-color);
    overflow: auto;
  }

  /* 顶部操作栏 */
  .top-bar {
    height: 64px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--art-main-bg-color);
    border-bottom: 1px solid var(--art-card-border);
    flex-shrink: 0;

    .left-actions {
      display: flex;
      align-items: center;
      gap: 16px;

      .page-title {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--art-text-gray-900);
      }
    }

    .right-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }

  /* 主内容区 */
  .main-content {
    flex: 1;
    display: flex;
    gap: 24px;
    padding: 24px;
    overflow: visible;
    position: relative;
  }

  /* 左侧设置面板 */
  .settings-panel {
    width: 320px;
    flex-shrink: 0;
    background: var(--art-main-bg-color);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    height: fit-content;
    max-height: calc(100vh - 112px);
    overflow-y: auto;
    overflow-x: hidden;

    /* 自定义滚动条 */
    &::-webkit-scrollbar {
      width: 6px;
    }
    &::-webkit-scrollbar-track {
      background: var(--art-bg-color);
      border-radius: 3px;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--art-gray-400);
      border-radius: 3px;

      &:hover {
        background: var(--art-gray-500);
      }
    }
  }

  /* 右侧编辑器区域 */
  .editor-section {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    background: var(--art-main-bg-color);
    border-radius: 12px;
    padding: 32px;
    overflow: visible;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    position: relative;
  }

  .title-input-wrapper {
    margin-bottom: 16px;

    :deep(.title-input) {
      .el-input__wrapper {
        box-shadow: none !important;
        padding: 0;
        background: transparent;
      }

      .el-input__inner {
        font-size: 32px;
        font-weight: 700;
        color: var(--art-text-gray-900);
        height: 48px;
        line-height: 48px;

        &::placeholder {
          color: var(--art-text-gray-400);
        }
      }
    }
  }

  .description-input-wrapper {
    margin-bottom: 8px;

    :deep(.description-input) {
      .el-textarea__inner {
        font-size: 15px;
        color: var(--art-text-gray-600);
        border: none;
        box-shadow: none !important;
        padding: 0;
        resize: none;
        background: transparent;

        &::placeholder {
          color: var(--art-text-gray-400);
        }

        &:focus {
          border: none;
        }
      }
    }
  }

  .editor-wrapper {
    flex: 1;
    overflow: visible;
    min-height: 0;
  }

  /* 设置面板样式 */
  .settings-panel {
    .panel-section {
      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 15px;
        font-weight: 600;
        color: var(--art-text-gray-900);
        margin-bottom: 16px;

        .el-icon {
          font-size: 18px;
          color: var(--art-text-gray-600);
        }
      }

      .form-item {
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .item-label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: var(--art-text-gray-600);
          margin-bottom: 8px;
        }

        .item-select {
          width: 100%;
        }

        .item-tip {
          margin-top: 6px;
          font-size: 12px;
          color: var(--art-text-gray-500);
        }
      }
    }

    .stats-section {
      .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        font-size: 13px;

        .stat-label {
          color: var(--art-text-gray-600);
        }

        .stat-value {
          color: var(--art-text-gray-900);
          font-weight: 500;
        }
      }
    }
  }

  /* 对话框样式 */
  .dialog-tip {
    color: var(--art-text-gray-600);
    margin-bottom: 16px;
    font-size: 14px;
    line-height: 1.6;
  }

  .upload-icon {
    font-size: 48px;
    color: #409eff;
    margin-bottom: 12px;
  }

  .upload-text {
    font-size: 14px;
    color: var(--art-text-gray-600);
  }

  .file-selected {
    margin-top: 16px;
    padding: 12px;
    background: var(--art-bg-color);
    border-radius: 6px;
    font-size: 13px;
    color: var(--art-text-gray-700);

    strong {
      color: var(--art-text-gray-900);
    }
  }

  /* 响应式调整 */
  @media (max-width: 1200px) {
    .settings-panel {
      width: 280px;
    }
  }

  @media (max-width: 992px) {
    .main-content {
      flex-direction: column;
    }

    .settings-panel {
      width: 100%;
      max-height: 400px;
    }
  }
</style>

<style>
/* 全局样式：提升下拉菜单的 z-index，确保在对话框和遮罩层之上 */
.high-z-index-popper {
  z-index: 99999999 !important;
}
</style>
