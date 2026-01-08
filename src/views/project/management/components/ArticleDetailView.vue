<template>
  <div class="article-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 文章内容 -->
    <div v-else-if="article" class="article-view">
      <el-card class="article-card" shadow="never">
        <template #header>
          <div class="article-header">
            <div class="header-left">
              <div class="header-info">
                <h3>{{ article.title }}</h3>
                <div class="meta-info">
                  <span class="author-info">
                    <el-icon><User /></el-icon>
                    {{ article.author_name }}
                  </span>
                  <span class="date-info">
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(article.updated_at) }}
                  </span>
                  <span class="view-info">
                    <el-icon><View /></el-icon>
                    {{ article.view_count || 0 }} 次浏览
                  </span>
                </div>
              </div>
            </div>
            <div class="header-actions">
              <template v-if="!isEditing">
                <el-button @click="loadArticle">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
                <el-dropdown trigger="click" @command="handleExportCommand">
                  <el-button>
                    <el-icon><Download /></el-icon>
                    导出
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="html">
                        <el-icon><Document /></el-icon>
                        导出为 HTML
                      </el-dropdown-item>
                      <el-dropdown-item command="pdf">
                        <el-icon><Printer /></el-icon>
                        导出为 PDF
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button @click="openMetaDialog" v-if="canEdit">
                  <el-icon><Edit /></el-icon>
                  编辑信息
                </el-button>
                <el-button @click="startEdit" v-if="canEdit">
                  <el-icon><Document /></el-icon>
                  编辑内容
                </el-button>
                <el-button @click="showHistoryDrawer">
                  <el-icon><InfoFilled /></el-icon>
                  文章信息
                </el-button>
                <el-button type="danger" @click="deleteArticle" v-if="canDelete">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
              <template v-else>
                <el-button @click="openImportMarkdown">
                  <el-icon><Upload /></el-icon>
                  导入 Markdown
                </el-button>
                <el-button @click="openImportWord">
                  <el-icon><Document /></el-icon>
                  导入 Word
                </el-button>
                <el-button @click="cancelEdit">取消</el-button>
                <el-button type="primary" @click="saveEdit" :loading="saving">保存内容</el-button>
              </template>
            </div>
          </div>
        </template>

        <div class="article-content">
          <!-- 查看模式 -->
          <template v-if="!isEditing">
            <div class="article-body">
              <ArtXnotePreview :content="article.content" height="100%" />
            </div>
          </template>

          <!-- 编辑模式 -->
          <template v-else>
            <div class="content-editor" :class="{ 'editing-active': isEditing }">
              <ArtTextbusEditor v-model="editForm.content" height="100%" />
            </div>
          </template>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="未找到文章">
        <el-button type="primary" @click="goCreatePage">
          <el-icon><Plus /></el-icon>
          发布第一篇{{ articleTypeText }}
        </el-button>
      </el-empty>
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

    <!-- 文章信息与历史抽屉 -->
    <el-drawer 
      v-model="historyDrawerVisible" 
      title="文章信息与历史" 
      direction="rtl" 
      size="550px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <div class="drawer-content">
        <!-- 文章元信息区域 -->
        <div v-if="article" class="article-meta-section">
          <el-card shadow="never" class="meta-card">
            <template #header>
              <div class="meta-card-header">
                <el-icon><InfoFilled /></el-icon>
                <span>文章元信息</span>
              </div>
            </template>

            <div class="meta-content">
              <!-- 所属项目 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><Box /></el-icon>
                  <span>所属项目</span>
                </div>
                <div class="meta-value">
                  <el-tag size="small" type="success" effect="light" class="meta-tag">
                    {{ projectName }}
                  </el-tag>
                </div>
              </div>

              <!-- 文章类型 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><Folder /></el-icon>
                  <span>类型</span>
                </div>
                <div class="meta-value">
                  <el-tag size="small" type="primary" effect="light" class="meta-tag">
                    {{ articleTypeText }}
                  </el-tag>
                </div>
              </div>

              <!-- 文章分类 -->
              <div v-if="article.category" class="meta-item">
                <div class="meta-label">
                  <el-icon><FolderOpened /></el-icon>
                  <span>分类</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    size="small"
                    :type="getCategoryTagType(article.category)"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ article.category }}
                  </el-tag>
                </div>
              </div>

              <!-- 文章简介 -->
              <div v-if="article.summary" class="meta-item summary-item">
                <div class="meta-label">
                  <el-icon><Document /></el-icon>
                  <span>简介</span>
                </div>
                <div class="meta-value summary-text">
                  {{ article.summary }}
                </div>
              </div>

              <!-- 可编辑成员 -->
              <div v-if="article.editable_user_ids?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><User /></el-icon>
                  <span>可编辑成员</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="userId in article.editable_user_ids"
                    :key="userId"
                    size="small"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ getUserRealName(userId) }}
                  </el-tag>
                  <span v-if="!article.editable_user_ids.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 可编辑角色 -->
              <div v-if="article.editable_roles?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><UserFilled /></el-icon>
                  <span>可编辑角色</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="role in article.editable_roles"
                    :key="role"
                    size="small"
                    type="success"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ getRoleName(role) }}
                  </el-tag>
                  <span v-if="!article.editable_roles.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 所属部门 -->
              <div v-if="article.departments?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><OfficeBuilding /></el-icon>
                  <span>所属部门</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="dept in article.departments"
                    :key="dept"
                    size="small"
                    type="warning"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ dept }}
                  </el-tag>
                  <span v-if="!article.departments.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 标签 -->
              <div v-if="article.tags && article.tags.length" class="meta-item">
                <div class="meta-label">
                  <span>🏷️</span>
                  <span>标签</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="tag in article.tags"
                    :key="tag"
                    size="small"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ tag }}
                  </el-tag>
                  <span v-if="!article.tags.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 提示：无元信息 -->
              <el-empty
                v-if="
                  !article.editable_user_ids?.length &&
                  !article.editable_roles?.length &&
                  !article.departments?.length &&
                  (!article.tags || !article.tags.length)
                "
                description="暂无文章元信息"
                :image-size="80"
              />
            </div>
          </el-card>
        </div>

        <!-- 编辑历史区域 -->
        <div v-loading="loading" class="history-section">
          <el-card shadow="never" class="history-card">
            <template #header>
              <div class="history-card-header">
                <el-icon><Clock /></el-icon>
                <span>编辑历史</span>
              </div>
            </template>

            <el-timeline v-if="history.length > 0">
              <el-timeline-item
                v-for="item in history"
                :key="item.id"
                :timestamp="formatDate(item.created_at)"
                placement="top"
              >
                <div class="history-item">
                  <div class="history-editor">
                    <el-icon><User /></el-icon>
                    <span>{{ item.editor_name }}</span>
                  </div>
                  <div class="history-action">
                    <el-tag :type="getActionTagType(item.action)" size="small">
                      {{ getActionLabel(item.action) }}
                    </el-tag>
                  </div>
                  <div class="history-summary" v-if="item.changes_summary">
                    {{ item.changes_summary }}
                  </div>
                  <div class="history-version" v-if="item.version_after">
                    版本: v{{ item.version_before || 0 }} → v{{ item.version_after }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无编辑历史" :image-size="80" />
          </el-card>
        </div>
      </div>
    </el-drawer>

    <!-- 元信息编辑弹窗 -->
    <el-dialog 
      v-model="metaDialogVisible" 
      title="编辑文档信息" 
      width="640px"
      :z-index="10000000"
      :modal="true"
      :append-to-body="true"
      :destroy-on-close="true"
      class="meta-edit-dialog"
    >
      <el-config-provider :z-index="10000100">
        <el-form :model="metaForm" label-width="96px">
          <el-form-item label="标题" required>
            <el-input v-model="metaForm.title" />
          </el-form-item>
          <el-form-item label="摘要">
            <el-input v-model="metaForm.summary" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="封面">
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
          </el-form-item>
          <el-form-item label="分类">
            <el-input v-model="metaForm.category" placeholder="输入或选择分类" />
          </el-form-item>
          <el-form-item label="可见">
            <el-switch v-model="metaForm.is_public" />
          </el-form-item>
          <el-form-item label="可编辑角色">
            <el-select
              v-model="metaForm.editable_roles"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="2"
              placeholder="选择可编辑角色"
              style="width: 100%"
            >
              <el-option
                v-for="role in roleOptions"
                :key="role.value"
                :label="role.label"
                :value="role.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="可编辑成员">
            <el-select
              v-model="metaForm.editable_user_ids"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="2"
              placeholder="选择人员"
              style="width: 100%"
            >
              <el-option v-for="u in userOptions" :key="u.value" :label="u.label" :value="u.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属部门">
            <el-select
              v-model="metaForm.departments"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="2"
              placeholder="选择部门"
              style="width: 100%"
            >
              <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-config-provider>
      <template #footer>
        <el-button @click="metaDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingMeta" @click="saveMeta">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
  import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus'
  import {
    User,
    Clock,
    View,
    UserFilled,
    OfficeBuilding,
    Download,
    ArrowDown,
    Document,
    Printer,
    Edit,
    Delete,
    Plus,
    Refresh,
    Upload,
    UploadFilled,
    InfoFilled
  } from '@element-plus/icons-vue'
  import { articlesApi } from '@/api/articlesApi'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '@/store/modules/user'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'
  import ArtTextbusEditor from '@/components/core/forms/art-textbus-editor/index.vue'
  import ArtXnotePreview from '@/components/core/forms/art-xnote-preview/index.vue'
  import mammoth from 'mammoth'
  import {
    markdownToHtml,
    parseMarkdownFile,
    validateMarkdownFile,
    readMarkdownFile
  } from '@/utils/markdown'

  interface Props {
    articleId: string
    projectId: string
    projectName: string
    articleType: string
    categoryName?: string
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    refresh: [projectId: string]
  }>()

  const router = useRouter()
  const userStore = useUserStore()

  const loading = ref(false)
  const article = ref<any>(null)
  const isEditing = ref(false)
  const editForm = ref({ content: '' })
  const saving = ref(false)
  const savingMeta = ref(false)
  const history = ref<any[]>([])
  const metaDialogVisible = ref(false)
  const historyDrawerVisible = ref(false)
  const showMdDialog = ref(false)
  const showWordDialog = ref(false)
  const mdFileName = ref('')
  const wordFileName = ref('')
  const wordImporting = ref(false)

  const metaForm = ref({
    title: '',
    summary: '',
    cover_url: '',
    category: '',
    is_public: true,
    editable_roles: [] as string[],
    editable_user_ids: [] as string[],
    departments: [] as string[]
  })

  const userOptions = ref<Array<{ label: string; value: string; role?: string }>>([])
  const deptOptions = ref<string[]>(['技术部', '产品部', '市场部', '运营部'])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])

  // 上传相关
  const uploadUrl = computed(() => '/api/common/upload/images')
  const uploadHeaders = computed(() => ({ Authorization: userStore.accessToken }))
  const coverList = ref<any[]>([])

  const onCoverUploaded = (res: any, file: any) => {
    const raw = res?.data?.files?.[0]?.url || res?.data?.url || res?.url
    const url =
      typeof raw === 'string'
        ? raw.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/')
        : raw
    if (url) {
      metaForm.value.cover_url = url
      coverList.value = [{ name: file.name, url }]
    }
  }

  const onCoverRemoved = () => {
    metaForm.value.cover_url = ''
    coverList.value = []
  }

  // 文章类型文本
  const articleTypeText = computed(() => {
    // 优先使用分类名称，如果没有则根据类型判断
    if (props.categoryName) {
      return props.categoryName
    }
    return props.articleType === 'meeting' ? '会议记录' : '模型测试'
  })

  // 权限判断
  const canEdit = computed(() => {
    if (!article.value) return false
    const isAdmin = userStore.currentUser?.role === 'admin'
    const isAuthor = userStore.currentUser?.id === article.value.author_id
    const uid = userStore.currentUser?.id
    const role = (userStore.currentUser?.role || '').toLowerCase()
    const byUser = !!(
      article.value.editable_user_ids &&
      uid &&
      article.value.editable_user_ids.includes(uid)
    )
    const byRole = !!(
      article.value.editable_roles &&
      role &&
      article.value.editable_roles.map((r: string) => r.toLowerCase()).includes(role)
    )
    return isAdmin || isAuthor || byUser || byRole
  })

  // 删除权限：只有管理员和作者可以删除
  const canDelete = computed(() => {
    if (!article.value || !userStore.currentUser) return false
    const currentUserId = userStore.currentUser.id
    const currentUserRole = userStore.currentUser.role
    return currentUserRole === 'admin' || article.value.author_id === currentUserId
  })

  // 工具函数
  const getCategoryColor = (category: string) => {
    const colorMap: Record<string, string> = {
      考核: '#f56c6c',
      评估: '#e6a23c',
      对外: '#409eff',
      对内: '#67c23a',
      胸肺: '#409eff',
      泌尿: '#67c23a',
      肝胆: '#e6a23c',
      盆腔: '#f56c6c'
    }
    return colorMap[category] || '#909399'
  }

  // 获取分类标签类型（用于Element Plus的tag组件）
  const getCategoryTagType = (category: string) => {
    const typeMap: Record<string, any> = {
      考核: 'danger', // 红色
      评估: 'warning', // 橙色
      对外: 'primary', // 蓝色
      对内: 'success', // 绿色
      胸肺: 'primary', // 蓝色
      泌尿: 'success', // 绿色
      肝胆: 'warning', // 橙色
      盆腔: 'danger', // 红色
      计划: 'info', // 灰色
      随笔: 'info', // 灰色
      讨论: 'warning' // 橙色
    }
    return typeMap[category] || 'info'
  }

  const getRoleName = (role: string) => {
    const roleOption = roleOptions.value.find((r) => r.value === role)
    return roleOption?.label || role
  }

  const getUserRealName = (uid: string) => {
    const user = userOptions.value.find((u) => u.value === uid)
    return user?.label || uid
  }

  // 获取操作标签类型
  const getActionTagType = (action: string) => {
    const map: Record<string, any> = {
      create: 'success',
      update: 'primary',
      publish: 'warning',
      delete: 'danger',
      edit_content: 'info'
    }
    return map[action] || 'info'
  }

  // 获取操作标签文本
  const getActionLabel = (action: string) => {
    const map: Record<string, string> = {
      create: '创建',
      update: '更新',
      publish: '发布',
      delete: '删除',
      edit_content: '编辑内容'
    }
    return map[action] || action
  }

  const formatDate = (s: string) => {
    const d = new Date(s)
    const now = new Date()
    const diff = now.getTime() - d.getTime()

    if (diff < 3600000) {
      const minutes = Math.floor(diff / 60000)
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
    }

    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000)
      return `${hours}小时前`
    }

    if (diff < 604800000) {
      const days = Math.floor(diff / 86400000)
      return `${days}天前`
    }

    return d.toLocaleString('zh-CN')
  }

  // 加载文章详情
  const loadArticle = async () => {
    if (!props.articleId) return

    loading.value = true
    try {
      article.value = await articlesApi.get(props.articleId)
      history.value = await articlesApi.history(props.articleId)

      // 更新表单数据
      if (article.value) {
        editForm.value = { content: article.value.content }
        metaForm.value = {
          title: article.value.title,
          summary: article.value.summary || '',
          cover_url: article.value.cover_url || '',
          category: article.value.category || '',
          is_public: article.value.is_public ?? true,
          editable_roles: [...(article.value.editable_roles || [])],
          editable_user_ids: [...(article.value.editable_user_ids || [])],
          departments: [...(article.value.departments || [])]
        }
        coverList.value = article.value.cover_url
          ? [{ name: 'cover', url: article.value.cover_url }]
          : []
      }
    } catch (error) {
      console.error('加载文章详情失败:', error)
      ElMessage.error('加载文章详情失败')
    } finally {
      loading.value = false
    }
  }

  // 加载用户和角色列表
  const loadUsers = async () => {
    try {
      // 使用 getUsersBasic API（包含 role 字段）
      const result: any = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      const users = result?.data?.users || result?.data?.list || []
      userOptions.value = users.map((u: any) => ({
        label: u.real_name || u.realName || u.username || u.userName || u.id,
        value: u.id,
        role: u.role
      }))

      // 获取角色列表（所有登录用户都可以访问）
      try {
        const roleRes: any = await roleApi.getRoles({ size: 9999 })
        const roleList: any[] = roleRes?.data?.list || roleRes?.data?.roles || []
        roleOptions.value = roleList.map((r) => ({
          label: r.name, // 中文显示名称
          value: r.role // 英文角色编码
        }))
      } catch (roleError) {
        console.error('[文章详情] 加载角色列表失败:', roleError)
        roleOptions.value = []
      }
    } catch (error) {
      console.error('加载用户列表失败:', error)
    }
  }

  // 发布新文章
  const goCreatePage = () => {
    router.push({
      name: 'ArticleCreate',
      params: { type: props.articleType },
      query: {
        projectId: props.projectId,
        projectName: props.projectName
      }
    })
  }

  // 编辑正文
  const startEdit = () => {
    if (!article.value) return
    
    // 如果是协作文档类型，跳转到协作文档编辑页面
    if (props.articleType === 'collaboration') {
      console.log('🤝 [ArticleDetail] 跳转到协作文档编辑页面:', article.value.id)
      router.push({
        name: 'CollaborationDocument',
        params: { documentId: article.value.id },
        query: {
          projectId: props.projectId,
          projectName: props.projectName
        }
      })
      return
    }
    
    // 普通文章在当前页面编辑
    editForm.value = { content: article.value.content }
    isEditing.value = true
  }

  const cancelEdit = () => {
    isEditing.value = false
    if (article.value) editForm.value = { content: article.value.content }
  }

  const saveEdit = async () => {
    if (!article.value) return
    try {
      saving.value = true
      await articlesApi.update(article.value.id, { content: editForm.value.content })
      ElMessage.success('已保存正文')
      isEditing.value = false
      await loadArticle()
    } catch (e) {
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  }

  // 编辑元信息
  const openMetaDialog = async () => {
    if (!article.value) return
    
    // 确保用户和角色数据已加载
    if (userOptions.value.length === 0 || roleOptions.value.length === 0) {
      await loadUsers()
    }
    
    metaForm.value = {
      title: article.value.title,
      summary: article.value.summary || '',
      cover_url: article.value.cover_url || '',
      category: article.value.category || '',
      is_public: article.value.is_public ?? true,
      editable_roles: [...(article.value.editable_roles || [])],
      editable_user_ids: [...(article.value.editable_user_ids || [])],
      departments: [...(article.value.departments || [])]
    }
    coverList.value = article.value.cover_url
      ? [{ name: 'cover', url: article.value.cover_url }]
      : []
    metaDialogVisible.value = true
  }

  const saveMeta = async () => {
    if (!article.value) return
    try {
      savingMeta.value = true
      await articlesApi.update(article.value.id, { ...metaForm.value })
      ElMessage.success('已保存其他信息')
      metaDialogVisible.value = false
      await loadArticle()
    } catch (e) {
      ElMessage.error('保存失败')
    } finally {
      savingMeta.value = false
    }
  }

  // 删除文章
  const deleteArticle = async () => {
    if (!article.value) return
    try {
      await ElMessageBox.confirm('确定删除该文章吗？', '提示', { type: 'warning' })
      await articlesApi.remove(article.value.id)
      ElMessage.success('已删除')
      emit('refresh', props.projectId)
    } catch (e) {
      // ignore cancel
    }
  }

  // 查看历史
  const showHistoryDrawer = () => {
    historyDrawerVisible.value = true
  }

  // 导出功能
  const handleExportCommand = (command: string) => {
    if (command === 'html') {
      exportHtml()
    } else if (command === 'pdf') {
      exportPdf()
    }
  }

  const exportHtml = () => {
    if (!article.value) return
    const title = (article.value.title || 'article').replace(/[/\\:*?"<>|]/g, '_')
    const escapeHtml = (str: string) =>
      str.replace(
        /[&<>"']/g,
        (m) => (({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }) as any)[m]
      )
    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(title)}</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial; margin:24px; color:#111827;}
    h1,h2,h3{margin-top:18px;}
    h1{font-size:26px;line-height:1.35;}
    h2{font-size:22px;line-height:1.4;}
    h3{font-size:18px;line-height:1.5;}
    p{margin:10px 0; line-height:1.8;}
    img{max-width:100%;height:auto;border-radius:4px;}
    pre{background:#0b1020;color:#e5e7eb;padding:12px 14px;border-radius:6px;overflow:auto;}
    code{background:#f3f4f6;padding:2px 6px;border-radius:4px;}
  </style>
</head>
<body>
  <h1>${escapeHtml(article.value.title)}</h1>
  ${article.value.content}
</body>
</html>`
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title}.html`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  }

  // 导出为 PDF（通过浏览器打印）
  const exportPdf = () => {
    if (!article.value) return

    const title = article.value.title || 'article'
    const escapeHtml = (str: string) =>
      str.replace(
        /[&<>"']/g,
        (m) => (({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }) as any)[m]
      )

    // 获取当前日期
    const now = new Date()
    const dateStr = `${now.getFullYear()}年${String(now.getMonth() + 1).padStart(2, '0')}月${String(now.getDate()).padStart(2, '0')}日`

    const html = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8" />
  <title>${escapeHtml(title)}</title>
  <style>
    @page { 
      size: A4; 
      margin: 12mm 12mm;
    }
    * {
      box-sizing: border-box;
    }
    body {
      font-family: "Microsoft YaHei", "微软雅黑", system-ui, -apple-system, sans-serif;
      color: #111827;
      margin: 0;
      padding: 0;
      position: relative;
    }
    /* 页眉样式 - 固定在顶部 */
    .page-header {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 0mm;
      border-bottom: 0.5pt solid #d1d5db;
      font-size: 9pt;
      color: #6b7280;
      background: white;
      z-index: 1000;
    }
    .page-header .company-name {
      font-weight: 600;
      color: #374151;
    }
    /* 页脚样式 - 固定在底部 */
    .page-footer {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 0mm;
      border-top: 0.5pt solid #d1d5db;
      font-size: 9pt;
      color: #6b7280;
      background: white;
      z-index: 1000;
    }
    .page-footer .company-name {
      color: #374151;
    }
    /* 内容区域 - 留出页眉页脚空间 */
    .page-content {
      margin-top: 40px;
      margin-bottom: 40px;
      padding: 0;
    }
    h1, h2, h3 { margin-top: 18px; }
    h1 { font-size: 24px; margin-bottom: 12px; }
    p { line-height: 1.8; margin: 10px 0; }
    img { max-width: 100%; height: auto; border-radius: 4px; }
    blockquote { border-left: 4px solid #e5e7eb; background: #f9fafb; padding: 10px 12px; color: #374151; margin: 10px 0; }
    pre { background: #0b1020; color: #e5e7eb; padding: 12px 14px; border-radius: 6px; overflow: auto; margin: 10px 0; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    th, td { border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }
    th { background: #f9fafb; font-weight: 600; }
  </style></head><body>
  <!-- 页眉 -->
  <div class="page-header">
    <span>${dateStr}</span>
    <span class="company-name">星像精准医疗科技（成都）有限公司</span>
  </div>
  
  <!-- 页脚 -->
  <div class="page-footer">
    <span class="company-name">星像精准医疗科技（成都）有限公司</span>
    <span class="page-number"></span>
  </div>
  
  <!-- 内容区域 -->
  <div class="page-content">
    <h1>${escapeHtml(article.value.title || '')}</h1>
    ${article.value.summary ? `<p><strong>摘要：</strong>${escapeHtml(article.value.summary)}</p>` : ''}
    <div>${article.value.content || ''}</div>
  </div>
  
  <script>
    // 自动添加页码
    window.onload = function() {
      var pageNumbers = document.querySelectorAll('.page-number');
      pageNumbers.forEach(function(el) {
        el.textContent = '第 ' + '1' + ' 页';
      });
      // 延迟打开打印对话框
      setTimeout(function() { 
        window.print(); 
      }, 300);
    };
  <\/script>
  </body></html>`

    const win = window.open('', '_blank')
    if (!win) {
      ElMessage.warning('无法打开新窗口，请检查浏览器弹窗拦截设置')
      return
    }
    win.document.open()
    win.document.write(html)
    win.document.close()
  }

  // 导入功能
  const openImportMarkdown = () => {
    showMdDialog.value = true
    mdFileName.value = ''
  }

  // Markdown 文件选择处理
  const onMdSelected = async (file: any) => {
    try {
      const raw: File = file?.raw || file
      if (!raw) return

      mdFileName.value = raw.name

      // 验证文件
      const validation = validateMarkdownFile(raw)
      if (!validation.valid) {
        ElMessage.warning(validation.error || 'Markdown 文件无效')
        return
      }

      // 读取文件内容
      const content = await readMarkdownFile(raw)

      // 解析文件（提取标题和正文）
      const { body } = parseMarkdownFile(content)

      // 转换 Markdown 为 HTML
      const html = markdownToHtml(body, {
        gfm: true,
        openLinksInNewWindow: true,
        sanitize: true
      })

      editForm.value.content = html
      showMdDialog.value = false
      ElMessage.success('Markdown 已导入')
    } catch (e: any) {
      console.error('Markdown 导入失败:', e)
      ElMessage.error(`Markdown 导入失败: ${e.message || '未知错误'}`)
    }
  }

  // 打开导入 Word 对话框
  const openImportWord = () => {
    showWordDialog.value = true
    wordFileName.value = ''
    wordImporting.value = false
  }

  // Word 文件选择处理
  const onWordSelected = async (file: any) => {
    try {
      const raw: File = file?.raw || file
      if (!raw) return

      wordFileName.value = raw.name
      wordImporting.value = true

      // 使用 mammoth 将 docx 转换为 HTML
      const arrayBuffer = await raw.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })

      if (result.value) {
        editForm.value.content = result.value
        showWordDialog.value = false
        ElMessage.success('Word 文档已导入')

        // 如果有警告信息，显示给用户
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

  // 监听 articleId 变化
  watch(
    () => props.articleId,
    () => {
      loadArticle()
    },
    { immediate: true }
  )

  // 监听元数据表单中的角色变化，自动选择该角色的所有成员
  watch(
    () => metaForm.value.editable_roles,
    (newRoles) => {
      if (!newRoles || newRoles.length === 0) {
        // 如果没有选择角色，清空成员
        metaForm.value.editable_user_ids = []
        return
      }

      // 获取所有选中角色的成员
      const selectedUserIds = userOptions.value
        .filter((u) => u.role && newRoles.includes(u.role))
        .map((u) => u.value)

      // 自动选择所有该角色的成员
      metaForm.value.editable_user_ids = selectedUserIds

      console.log('✅ [ArticleDetail] 已自动选择', selectedUserIds.length, '个成员')
    },
    { deep: true }
  )

  onMounted(() => {
    loadArticle()
    loadUsers()
  })

  // 组件卸载时解锁文章
  onBeforeUnmount(async () => {
    if (isEditing.value && article.value) {
      try {
        await articlesApi.unlock(article.value.id)
        console.log('🔓 [项目文章] 组件卸载时已解锁文章')
      } catch (error) {
        console.error('组件卸载时解锁文章失败:', error)
      }
    }
  })
</script>

<style scoped lang="scss">
  // 根容器 - 完全参照会议记录页面的 article-detail-wrapper
  .article-detail-container {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .loading-container {
    padding: 24px;
    background: var(--art-main-bg-color);
    border-radius: 12px;
  }

  .article-view {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .article-card {
    border: none !important;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
    position: relative;

    :deep(.el-card__header) {
      padding: 20px 24px;
      background: var(--art-main-bg-color);
      border-bottom: 1px solid var(--art-card-border);
      flex-shrink: 0;
      position: relative;
      z-index: 1;
    }

    :deep(.el-card__body) {
      padding: 0;
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
    }
  }

  .article-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;

    .header-left {
      flex: 1;
      min-width: 0;

      .header-info {
        h3 {
          margin: 0 0 12px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          line-height: 1.4;
        }

        .meta-info {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          align-items: center;
          font-size: 13px;
          color: var(--art-text-gray-600);

          .author-info,
          .date-info,
          .view-info {
            display: flex;
            align-items: center;
            gap: 4px;

            .el-icon {
              font-size: 14px;
            }
          }
        }
      }
    }

    .header-actions {
      display: flex;
      gap: 8px;
      flex-shrink: 0;

      .el-button {
        border-radius: 6px;
        font-weight: 500;

        .el-icon {
          font-size: 14px;
        }
      }
    }
  }

  .article-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    background: transparent;
    border: none;
    position: relative;

    // 自定义滚动条
    &::-webkit-scrollbar {
      width: 8px;
    }
    &::-webkit-scrollbar-track {
      background: transparent;
      border-radius: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--art-gray-400);
      border-radius: 4px;

      &:hover {
        background: var(--art-gray-500);
      }
    }

    // 查看模式的文章主体
    .article-body {
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
      padding: 24px;

      // 移除预览组件的所有边框和背景
      :deep(*) {
        &[class*='preview'],
        &[class*='xnote'],
        &[class*='container'],
        &[class*='wrapper'] {
          border: none !important;
          box-shadow: none !important;
          outline: none !important;
        }
      }

      // 特别处理表格边框（保留表格内部边框，但移除外部边框）
      :deep(table) {
        border: none !important;
        box-shadow: none !important;
      }

      // 移除任何可能的灰色背景或边框
      :deep(div),
      :deep(section),
      :deep(article) {
        &:not(table):not(td):not(th) {
          border-color: transparent !important;
          
          &[style*='border'] {
            border: none !important;
          }
        }
      }
    }

    // 编辑模式的编辑器样式
    .content-editor {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: var(--art-main-bg-color);
      min-height: 0;
      overflow: hidden;
      height: 100%;
      position: relative; // 确保定位上下文

      // 强制覆盖 Textbus 编辑器的根元素样式
      :deep(.art-textbus-editor),
      :deep(.textbus-editor-container) {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        width: 100% !important;
        overflow: hidden !important;
      }

      // 工具栏固定
      :deep(.textbus-toolbar-wrapper) {
        flex-shrink: 0 !important;
        z-index: 10 !important;
        background: #fff !important;
        border-bottom: 1px solid #eee !important;
      }

      // 内容区域自适应并滚动
      :deep(.textbus-container),
      :deep(.textbus-content),
      :deep(.textbus-scroller) {
        flex: 1 !important;
        height: auto !important; // 覆盖可能的固定高度
        overflow-y: auto !important;
        overflow-x: hidden !important;
        min-height: 0 !important;
      }
      
      // 修复可能存在的绝对定位导致的溢出
      :deep(.textbus-editor) {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
      }
    }

    // 编辑模式时调整外层容器
    &:has(.content-editor.editing-active) {
      padding: 0; // 移除所有 padding，让编辑器贴边
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }

  // 空状态
  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 48px 24px;
    background: var(--art-main-bg-color);
    border-radius: 12px;
  }

  .history-list {
    padding: 4px 0;
  }

  .hist-item {
    padding: 8px 0;
  }

  .hist-item .row {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--art-text-gray-900);
  }

  .hist-item .sep {
    color: #9ca3af;
  }

  .hist-item .name,
  .hist-item .ts {
    color: var(--art-text-gray-800);
  }

  .hist-item .op {
    font-weight: 600;
  }

  .hist-item .sub {
    margin-left: 28px;
    color: #4b5563;
    display: flex;
    gap: 6px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
  }

  .dot-create {
    background: #67c23a;
  }

  .dot-update {
    background: #409eff;
  }

  .dot-delete {
    background: #f56c6c;
  }

  .dot-default {
    background: #9ca3af;
  }

  // 文章信息与历史抽屉样式
  .drawer-content {
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;

    // 文章元信息区域
    .article-meta-section {
      .meta-card {
        border: 1px solid var(--el-border-color-lighter) !important;
        border-radius: 8px;
        overflow: hidden;

        :deep(.el-card__header) {
          padding: 16px 20px;
          background: var(--el-fill-color-light);
          border-bottom: 1px solid var(--el-border-color-lighter);

          .meta-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--art-text-gray-900);
            font-weight: 600;
            font-size: 15px;

            .el-icon {
              font-size: 18px;
              color: var(--el-color-primary);
            }
          }
        }

        :deep(.el-card__body) {
          padding: 20px;
        }

      }

      .meta-content {
        .meta-item {
          margin-bottom: 20px;

          &:last-child {
            margin-bottom: 0;
          }

          .meta-label {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            color: var(--art-text-gray-900);
            margin-bottom: 10px;
            font-size: 14px;

            .el-icon {
              color: #3b82f6;
              font-size: 16px;
            }
          }

          .meta-value {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding-left: 22px;

            .meta-tag {
              margin: 0;
            }

            .empty-text {
              color: var(--art-text-gray-400);
              font-size: 13px;
              font-style: italic;
            }
          }

          // 简介特殊样式
          &.summary-item {
            .summary-text {
              display: block;
              padding: 12px 16px;
              padding-left: 22px;
              background: var(--art-bg-color);
              border-radius: 6px;
              font-size: 14px;
              line-height: 1.6;
              color: var(--art-text-gray-700);
              border-left: 3px solid #3b82f6;
              white-space: pre-wrap;
              word-break: break-word;
            }
          }
        }
      }
    }

    // 编辑历史区域
    .history-section {
      flex: 1;
      min-height: 0;

      .history-card {
        border: 1px solid var(--el-border-color-lighter) !important;
        border-radius: 8px;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;

        :deep(.el-card__header) {
          padding: 16px 20px;
          background: var(--el-fill-color-light);
          border-bottom: 1px solid var(--el-border-color-lighter);

          .history-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--art-text-gray-900);
            font-weight: 600;
            font-size: 15px;

            .el-icon {
              font-size: 18px;
              color: var(--el-color-primary);
            }
          }
        }

        :deep(.el-card__body) {
          padding: 20px;
          flex: 1;
          overflow-y: auto;
        }
      }

      .history-item {
        padding: 16px;
        background: var(--art-bg-color);
        border-radius: 8px;
        margin-bottom: 16px;
        border: 1px solid var(--el-border-color-lighter);
        transition: all 0.3s ease;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          border-color: var(--el-color-primary-light-7);
        }

        .history-editor {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          margin-bottom: 8px;

          .el-icon {
            color: #3b82f6;
          }
        }

        .history-action {
          margin-bottom: 8px;
        }

        .history-summary {
          color: var(--art-text-gray-600);
          font-size: 14px;
          margin-bottom: 8px;
          line-height: 1.6;
        }

        .history-version {
          font-size: 13px;
          color: var(--art-text-gray-500);
          font-family: monospace;
          background: var(--el-fill-color-light);
          padding: 4px 8px;
          border-radius: 4px;
          display: inline-block;
        }
      }
    }
  }
</style>

<style>
/* 全局样式：提升对话框内下拉菜单的 z-index，确保在对话框和遮罩层之上 */
.high-z-index-popper {
  z-index: 99999999 !important;
}

/* 元信息编辑对话框样式优化 */
.meta-edit-dialog {
  .el-dialog__body {
    overflow: visible !important;
    max-height: 70vh;
    overflow-y: auto;
  }
  
  .el-form {
    overflow: visible !important;
  }
  
  .el-form-item {
    overflow: visible !important;
  }
  
  /* 确保 select 下拉菜单不被裁剪 */
  .el-select {
    overflow: visible !important;
  }
  
  .el-select__wrapper {
    overflow: visible !important;
  }
}

/* 确保 select 的 popper 在最上层 */
.el-popper.el-select__popper {
  z-index: 99999999 !important;
}
</style>

