<template>
  <div v-loading="loading" class="article-list-view">
    <!-- 头部 -->
    <div class="list-header">
      <div class="header-info">
        <h3>
          <span class="icon">{{ articleType === 'meeting' ? '📋' : '🧪' }}</span>
          {{ articleType === 'meeting' ? '会议记录' : '模型测试' }}
        </h3>
        <span class="subtitle">{{ projectName }}</span>
      </div>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        {{ articleType === 'collaboration' ? '创建协作文档' : `发布${articleType === 'meeting' ? '会议记录' : '测试记录'}` }}
      </el-button>
    </div>

    <!-- 文章列表 -->
    <div class="article-list" v-if="articles.length > 0">
      <el-card
        v-for="article in articles"
        :key="article.id"
        class="article-card"
        shadow="hover"
        @click="handleViewArticle(article)"
      >
        <div class="article-content">
          <div class="article-header">
            <div class="article-title">
              {{ article.title }}
              <el-tag v-if="article.category" size="small" type="info" effect="plain">
                {{ article.category }}
              </el-tag>
            </div>
            <div class="article-meta">
              <span class="meta-item">
                <el-icon><User /></el-icon>
                {{ article.author_name }}
              </span>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatDate(article.updated_at) }}
              </span>
              <span class="meta-item">
                <el-icon><View /></el-icon>
                {{ article.view_count || 0 }}
              </span>
            </div>
          </div>

          <div v-if="article.summary" class="article-summary">
            {{ article.summary }}
          </div>

          <div class="article-footer">
            <div class="tags">
              <el-tag v-for="tag in article.tags || []" :key="tag" size="small" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
            <div class="actions">
              <el-button type="primary" size="small" text @click.stop="handleViewArticle(article)">
                查看
              </el-button>
              <el-button
                v-if="canDeleteArticle(article)"
                type="danger"
                size="small"
                text
                @click.stop="handleDelete(article)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-else :description="`暂无${articleType === 'collaboration' ? '协作文档' : (articleType === 'meeting' ? '会议记录' : '测试记录')}`">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        {{ articleType === 'collaboration' ? '创建第一个协作文档' : '发布第一条记录' }}
      </el-button>
    </el-empty>

    <!-- 分页 -->
    <div v-if="articles.length > 0" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadArticles"
        @current-change="loadArticles"
      />
    </div>

    <!-- 创建协作文档弹窗 -->
    <CreateDocumentDialog
      v-if="articleType === 'collaboration'"
      v-model="showCreateDialog"
      title="创建协作文档"
      document-type="协作文档"
      collaborator-label="协作成员"
      :show-collaborator-roles="true"
      :user-options="userOptions"
      :role-options="roleOptions"
      :tag-options="tagOptions"
      @confirm="handleCreateDocument"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, watch, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Plus, User, Clock, View } from '@element-plus/icons-vue'
  import { articlesApi } from '@/api/articlesApi'
  import { collaborationApi } from '@/api/collaborationApi'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'
  import { useUserStore } from '@/store/modules/user'
  import CreateDocumentDialog from '@/components/business/CreateDocumentDialog.vue'

  defineOptions({ name: 'ArticleListView' })

  interface Props {
    projectId: string
    articleType: string
    projectName: string
    categoryName?: string
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    refresh: [projectId: string]
  }>()

  const router = useRouter()
  const userStore = useUserStore()

  // 权限控制：判断是否可以删除某篇文章
  const canDeleteArticle = (article: any) => {
    if (!userStore.currentUser) return false
    const currentUserId = userStore.currentUser.id
    const currentUserRole = userStore.currentUser.role
    // 只有管理员和作者可以删除
    return currentUserRole === 'admin' || article.author_id === currentUserId
  }

  // State
  const loading = ref(false)
  const articles = ref<any[]>([])
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)

  // 创建弹窗（仅用于协作文档）
  const showCreateDialog = ref(false)
  const userOptions = ref<Array<{ label: string; value: string; role?: string }>>([])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])
  const tagOptions = ref<string[]>(['重要', '紧急', '设计', '开发', '测试', '会议', '方案', '总结'])

  // 加载文章列表
  const loadArticles = async () => {
    loading.value = true
    try {
      const result = await articlesApi.getArticles({
        project_id: props.projectId,
        type: props.articleType,
        page: currentPage.value,
        page_size: pageSize.value
      })

      // http.get 已经处理了响应格式，直接返回 ArticleListResponse
      articles.value = result?.items || []
      total.value = result?.total || 0
    } catch (error) {
      console.error('加载文章列表失败:', error)
      ElMessage.error('加载文章列表失败')
      articles.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // 监听属性变化
  watch(
    [() => props.projectId, () => props.articleType],
    () => {
      currentPage.value = 1
      loadArticles()
    },
    { immediate: true }
  )

  // 格式化日期
  const formatDate = (date: string | Date) => {
    const d = new Date(date)
    const now = new Date()
    const diff = now.getTime() - d.getTime()

    // 小于1小时
    if (diff < 3600000) {
      const minutes = Math.floor(diff / 60000)
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
    }

    // 小于24小时
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000)
      return `${hours}小时前`
    }

    // 小于7天
    if (diff < 604800000) {
      const days = Math.floor(diff / 86400000)
      return `${days}天前`
    }

    // 否则显示完整日期
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  // 查看文章
  const handleViewArticle = (article: any) => {
    router.push(`/articles/detail/${article.id}`)
  }

  // 加载用户和角色列表（仅用于协作文档）
  const loadUsersAndRoles = async () => {
    try {
      const res = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      const userList: any[] = res.items || res.data?.items || res.list || res.data?.list || res.data || []
      
      userOptions.value = userList.map((u: any) => ({
        label: u.real_name || u.realName || u.username || u.name,
        value: u.id || u.userId,
        role: u.role
      }))

      try {
        const roleRes: any = await roleApi.getRoles({ size: 9999 })
        const roleList: any[] = roleRes?.data?.list || roleRes?.data?.roles || []
        roleOptions.value = roleList.map((r) => ({
          label: r.name,
          value: r.role
        }))
      } catch (roleError) {
        console.error('❌ [ArticleListView] 加载角色列表失败:', roleError)
      }
    } catch (error) {
      console.error('❌ [ArticleListView] 加载用户列表失败:', error)
    }
  }

  // 创建文章 - 跳转到完整的创建页面，并携带项目ID
  const handleCreate = () => {
    // 如果是协作文档类型，打开创建弹窗
    if (props.articleType === 'collaboration') {
      showCreateDialog.value = true
      return
    }

    // 其他类型跳转到创建页面
    router.push({
      name: 'ArticleCreate',
      params: { type: props.articleType },
      query: {
        projectId: props.projectId,
        projectName: props.projectName
      }
    })
  }

  // 创建协作文档
  const handleCreateDocument = async (formData: any) => {
    try {
      console.log('📝 [ArticleListView] 创建协作文档:', formData)
      
      const newDoc = await collaborationApi.createDocument({
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        status: formData.status,
        tags: formData.tags,
        editable_user_ids: formData.editable_user_ids,
        content: '',
        project_id: props.projectId
      } as any)

      ElMessage.success('协作文档创建成功')
      showCreateDialog.value = false

      router.push({
        name: 'CollaborationDocument',
        params: { documentId: newDoc.id },
        query: {
          projectId: props.projectId,
          projectName: props.projectName
        }
      })

      loadArticles()
      emit('refresh', props.projectId)
    } catch (error) {
      console.error('❌ [ArticleListView] 创建协作文档失败:', error)
      ElMessage.error('创建协作文档失败')
    }
  }

  // 文章创建成功
  const handleArticleCreated = () => {
    loadArticles()
    emit('refresh', props.projectId)
  }

  // 删除文章
  const handleDelete = async (article: any) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除文章"${article.title}"吗？此操作不可恢复。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      loading.value = true
      await articlesApi.deleteArticle(article.id)
      ElMessage.success('删除成功')
      loadArticles()
      emit('refresh', props.projectId)
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除文章失败:', error)
        ElMessage.error('删除文章失败')
      }
    } finally {
      loading.value = false
    }
  }

  // 初始化
  onMounted(() => {
    loadArticles()
    // 如果是协作文档类型，加载用户和角色列表
    if (props.articleType === 'collaboration') {
      loadUsersAndRoles()
    }
  })

  // 不再需要 ArticleFormDialog
</script>

<style lang="scss" scoped>
  .article-list-view {
    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 2px solid #f0f0f0;

      .header-info {
        h3 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 12px;

          .icon {
            font-size: 28px;
          }
        }

        .subtitle {
          color: #909399;
          font-size: 14px;
        }
      }
    }

    .article-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .article-card {
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
      }

      :deep(.el-card__body) {
        padding: 20px;
      }
    }

    .article-content {
      .article-header {
        margin-bottom: 12px;

        .article-title {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
          gap: 8px;
          line-height: 1.5;
        }

        .article-meta {
          display: flex;
          gap: 16px;
          color: #909399;
          font-size: 12px;

          .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }

      .article-summary {
        color: #606266;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 12px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .article-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid #f0f0f0;

        .tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          flex: 1;
          min-width: 0;
        }

        .actions {
          display: flex;
          gap: 8px;
          flex-shrink: 0;
        }
      }
    }

    .pagination {
      display: flex;
      justify-content: center;
      padding: 20px 0;
    }
  }
</style>
