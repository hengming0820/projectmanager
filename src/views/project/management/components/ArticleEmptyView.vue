<template>
  <div class="article-empty-container">
    <!-- 顶部操作栏 -->
    <div class="empty-header">
      <div class="header-left">
        <h3>{{ articleTypeText }}</h3>
        <span class="project-badge">{{ projectName }}</span>
      </div>
      <div class="header-right">
        <el-button @click="goCreatePage" type="primary" size="default">
          <el-icon><Plus /></el-icon>
          发布{{ articleTypeText }}
        </el-button>
      </div>
    </div>

    <!-- 空状态内容 -->
    <div class="empty-content">
      <el-empty :description="`暂无${articleTypeText}`">
        <el-button type="primary" @click="goCreatePage" size="large">
          <el-icon><Plus /></el-icon>
          {{ articleType === 'collaboration' ? '创建第一个协作文档' : `发布第一篇${articleTypeText}` }}
        </el-button>
      </el-empty>
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
  import { ref, computed, onMounted } from 'vue'
  import { Plus } from '@element-plus/icons-vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import CreateDocumentDialog from '@/components/business/CreateDocumentDialog.vue'
  import { collaborationApi } from '@/api/collaborationApi'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'

  defineOptions({
    name: 'ArticleEmptyView'
  })

  interface Props {
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

  // 文章类型文本
  const articleTypeText = computed(() => {
    // 优先使用分类名称，如果没有则根据类型判断
    if (props.categoryName) {
      return props.categoryName
    }
    return props.articleType === 'meeting' ? '会议记录' : '模型测试'
  })

  // 创建文档/文章
  const goCreatePage = () => {
    // 如果是协作文档类型，打开创建弹窗
    if (props.articleType === 'collaboration') {
      showCreateDialog.value = true
      return
    }
    
    // 其他类型跳转到发布页面
    router.push({
      name: 'ArticleCreate',
      params: { type: props.articleType },
      query: {
        projectId: props.projectId,
        projectName: props.projectName
      }
    })
  }

  // 创建弹窗相关
  const showCreateDialog = ref(false)
  const userOptions = ref<Array<{ label: string; value: string; role?: string }>>([])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])
  const tagOptions = ref<string[]>(['重要', '紧急', '设计', '开发', '测试', '会议', '方案', '总结'])

  // 加载用户和角色列表
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
        console.error('❌ [ArticleEmptyView] 加载角色列表失败:', roleError)
      }
    } catch (error) {
      console.error('❌ [ArticleEmptyView] 加载用户列表失败:', error)
    }
  }

  // 创建协作文档
  const handleCreateDocument = async (formData: any) => {
    try {
      console.log('📝 [ArticleEmptyView] 创建协作文档:', formData)
      
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

      emit('refresh', props.projectId)
    } catch (error) {
      console.error('❌ [ArticleEmptyView] 创建协作文档失败:', error)
      ElMessage.error('创建协作文档失败')
    }
  }

  onMounted(() => {
    if (props.articleType === 'collaboration') {
      loadUsersAndRoles()
    }
  })
</script>

<style scoped>
  .article-empty-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .empty-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--art-main-bg-color);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .header-left h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--art-text-gray-900);
  }

  .project-badge {
    padding: 4px 12px;
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 500;
  }

  .header-right {
    display: flex;
    gap: 12px;
  }

  .empty-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--art-main-bg-color);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    min-height: 400px;
  }

  .empty-content :deep(.el-empty__description) {
    font-size: 16px;
    color: var(--art-text-gray-600);
  }
</style>
