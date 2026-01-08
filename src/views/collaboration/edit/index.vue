<template>
  <div class="collaboration-edit-container" v-loading="loading">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="left-actions">
        <el-button @click="goBack" :icon="ArrowLeft" circle />
        <h2 class="page-title">编辑协作文档</h2>
        <el-tag v-if="document" :type="getStatusTagType(document.status)" size="small">
          {{ collaborationUtils.getStatusText(document.status) }}
        </el-tag>
        <el-tag v-if="projectName" type="info" size="small">
          📁 {{ projectName }}
        </el-tag>
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
      </div>
    </div>

    <!-- 主编辑区域 -->
    <div class="main-content" v-if="document">
      <!-- 左侧：设置面板 + 在线用户 -->
      <div class="settings-panel">
        <!-- 在线协作用户 -->
        <div class="panel-section">
          <div class="section-title">
            <el-icon><UserFilled /></el-icon>
            正在编辑
            <el-tag size="small" type="success" style="margin-left: 8px">
              {{ collaborationUsers.length }}
            </el-tag>
          </div>
          <div class="collaboration-users-list">
            <div v-for="user in collaborationUsers" :key="user.id" class="user-item">
              <div class="user-avatar" :style="{ borderColor: user.color }">
                <span class="avatar-text">
                  {{ user.username.charAt(0).toUpperCase() }}
                </span>
                <div class="online-indicator" :style="{ background: user.color }"></div>
              </div>
              <div class="user-info">
                <div class="user-name">
                  {{ user.username }}
                  <el-tag v-if="user.isSelf" size="small" type="primary" effect="plain">我</el-tag>
                </div>
              </div>
            </div>
            <div v-if="collaborationUsers.length === 0" class="no-users">
              <el-icon><Warning /></el-icon>
              暂无在线用户
            </div>
          </div>
        </div>

        <el-divider style="margin: 16px 0" />

        <!-- 项目提示 -->
        <el-alert
          v-if="projectName"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #title>
            <span style="font-size: 13px">正在为项目「{{ projectName }}」编辑协作文档</span>
          </template>
        </el-alert>

        <!-- 文档设置 -->
        <div class="panel-section">
          <div class="section-title">
            <el-icon><Setting /></el-icon>
            文档设置
          </div>

          <!-- 优先级 -->
          <div class="form-item">
            <label class="item-label">优先级</label>
            <el-select
              v-model="document.priority"
              placeholder="选择"
              class="item-select"
              @change="markAsModified"
            >
              <el-option label="🔵 低" value="low" />
              <el-option label="🟢 普通" value="normal" />
              <el-option label="🟡 高" value="high" />
              <el-option label="🔴 紧急" value="urgent" />
            </el-select>
          </div>

          <!-- 状态 -->
          <div class="form-item">
            <label class="item-label">状态</label>
            <el-select
              v-model="document.status"
              placeholder="选择"
              class="item-select"
              @change="markAsModified"
            >
              <el-option label="📝 草稿" value="draft" />
              <el-option label="✅ 进行中" value="active" />
              <el-option label="✔️ 已完成" value="completed" />
              <el-option label="📦 已归档" value="archived" />
            </el-select>
          </div>
        </div>

        <el-divider style="margin: 16px 0" />

        <!-- 协作角色（用于筛选） -->
        <div class="panel-section">
          <div class="section-title">
            <el-icon><UserFilled /></el-icon>
            协作角色
          </div>
          <div class="form-item">
            <el-select
              v-model="selectedRoles"
              multiple
              filterable
              placeholder="选择角色，自动添加该角色的所有成员"
              class="item-select"
              collapse-tags
              collapse-tags-tooltip
              @change="handleRoleChange"
            >
              <el-option
                v-for="role in roleOptions"
                :key="role.value"
                :label="role.label"
                :value="role.value"
              />
            </el-select>
            <div v-if="selectedRoles.length === 0" class="item-tip warning">
              💡 请先选择协作角色，系统将自动添加该角色的所有成员
            </div>
            <div v-else class="item-tip success">
              ✅ 已自动选择 {{ filteredUsersByRole.length }} 位成员（可手动调整）
            </div>
          </div>
        </div>

        <el-divider style="margin: 16px 0" />

        <!-- 协作成员 -->
        <div class="panel-section">
          <div class="section-title">
            <el-icon><User /></el-icon>
            协作成员
          </div>
          <div class="form-item">
            <el-select
              v-model="document.editable_user_ids"
              multiple
              filterable
              placeholder="选择团队成员"
              class="item-select"
              collapse-tags
              collapse-tags-tooltip
              :disabled="selectedRoles.length === 0"
              @change="markAsModified"
            >
              <el-option
                v-for="u in filteredUsersByRole"
                :key="u.value"
                :label="u.label"
                :value="u.value"
              >
                <span>{{ u.label }}</span>
                <span style="color: #8492a6; font-size: 12px; margin-left: 8px">
                  ({{ getRoleLabel(u.role) }})
                </span>
              </el-option>
            </el-select>
            <div class="item-tip"> 只有协作成员可以编辑此文档 </div>
          </div>
        </div>

        <el-divider style="margin: 16px 0" />

        <!-- 标签 -->
        <div class="panel-section">
          <div class="section-title">
            <el-icon><PriceTag /></el-icon>
            标签
          </div>
          <div class="form-item">
            <el-select
              v-model="document.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="添加标签"
              class="item-select"
              collapse-tags
              collapse-tags-tooltip
              @change="markAsModified"
            >
              <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
            </el-select>
          </div>
        </div>

        <el-divider style="margin: 16px 0" />

        <!-- 保存按钮 -->
        <div class="save-section">
          <el-button
            type="primary"
            :loading="saving"
            :disabled="!isModified"
            @click="saveDocument"
            size="large"
            style="width: 100%"
          >
            <el-icon v-if="!saving"><CircleCheck /></el-icon>
            {{ saving ? '保存中...' : isModified ? '保存更改' : '已保存' }}
          </el-button>
          <div v-if="isModified" class="save-tip">有未保存的更改</div>
          <div v-else-if="lastSaveTime" class="save-tip">
            最后保存: {{ formatDateTime(lastSaveTime) }}
          </div>
        </div>
      </div>

      <!-- 右侧：编辑器 -->
      <div class="editor-container">
        <!-- 标题输入 -->
        <div class="title-input-wrapper">
          <el-input
            v-model="document.title"
            placeholder="请输入文档标题..."
            class="title-input"
            maxlength="100"
            :show-word-limit="false"
            @input="markAsModified"
          />
        </div>

        <!-- 描述输入 -->
        <div class="description-input-wrapper">
          <el-input
            v-model="document.description"
            type="textarea"
            :rows="2"
            placeholder="添加文档描述（可选，用于卡片展示）"
            maxlength="500"
            :show-word-limit="false"
            class="description-input"
            @input="markAsModified"
          />
        </div>

        <!-- 分隔线 -->
        <el-divider style="margin: 16px 0" />

        <!-- 富文本编辑器 -->
        <div class="editor-wrapper">
          <ArtTextbusEditor
            v-model="editingContent"
            :height="editorHeight"
            placeholder="开始编写协作文档内容..."
            :collaboration-enabled="true"
            :document-id="document.id"
            :current-user="currentUserInfo"
            :auto-save="true"
            :auto-save-interval="30000"
            :show-static-toolbar="false"
            @collaboration-users-change="onCollaborationUsersChange"
          />
        </div>
      </div>
    </div>

    <!-- 导入 Markdown 对话框 -->
    <el-dialog v-model="showMdDialog" title="导入 Markdown 文档" width="520px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleMdFileChange"
        :show-file-list="false"
        accept=".md"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将 Markdown 文件拖到此处，或<em>点击选择</em>
        </div>
      </el-upload>
      <div v-if="mdFileName" class="file-selected">
        已选文件：<strong>{{ mdFileName }}</strong>
      </div>
      <template #footer>
        <el-button @click="showMdDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 导入 Word 对话框 -->
    <el-dialog v-model="showWordDialog" title="导入 Word 文档" width="520px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleWordFileChange"
        :show-file-list="false"
        accept=".docx"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将 Word 文件拖到此处，或<em>点击选择</em>
        </div>
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
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    ArrowLeft,
    Check,
    Setting,
    User,
    PriceTag,
    UserFilled,
    Warning,
    Document,
    CircleCheck,
    UploadFilled
  } from '@element-plus/icons-vue'
  import { collaborationApi, collaborationUtils } from '@/api/collaborationApi'
  import { useUserStore } from '@/store/modules/user'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'
  import ArtTextbusEditor from '@/components/core/forms/art-textbus-editor/index.vue'
  import { formatDateTime } from '@/utils/timeFormat'
  import mammoth from 'mammoth'
  import { markdownToHtml, validateMarkdownFile, readMarkdownFile } from '@/utils/markdown'

  const route = useRoute()
  const router = useRouter()
  const userStore = useUserStore()

  const documentId = computed(() => route.params.documentId as string)
  const projectId = computed(() => route.query.projectId as string | undefined)
  const projectName = computed(() => route.query.projectName as string | undefined)
  const document = ref<any>(null)
  const loading = ref(false)
  const saving = ref(false)
  const editingContent = ref('')
  const isModified = ref(false)
  const lastSaveTime = ref<string>('')

  // 导入对话框相关
  const showMdDialog = ref(false)
  const showWordDialog = ref(false)
  const mdFileName = ref('')
  const wordFileName = ref('')
  const wordImporting = ref(false)
  const collaborationUsers = ref<
    Array<{
      id: string
      username: string
      color: string
      isSelf?: boolean
    }>
  >([])

  // 用户选项
  const userOptions = ref<Array<{ label: string; value: string; role?: string }>>([])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])
  const selectedRoles = ref<string[]>([])

  // 可用标签
  const availableTags = ref<string[]>([
    '重要',
    '紧急',
    '设计',
    '开发',
    '测试',
    '会议',
    '方案',
    '总结'
  ])

  // 编辑器高度
  const editorHeight = computed(() => 'calc(100vh - 340px)')

  // 当前用户信息（用于协作）
  const currentUserInfo = computed(() => ({
    id: userStore.currentUser?.id || '',
    username: userStore.currentUser?.username || '',
    realName: userStore.currentUser?.realName || userStore.currentUser?.username || ''
  }))

  // 根据选择的角色筛选用户
  const filteredUsersByRole = computed(() => {
    if (!selectedRoles.value || selectedRoles.value.length === 0) {
      return userOptions.value
    }
    return userOptions.value.filter((user) => selectedRoles.value.includes(user.role || ''))
  })

  // 获取角色标签
  const getRoleLabel = (roleValue?: string) => {
    if (!roleValue) return ''
    const role = roleOptions.value.find((r) => r.value === roleValue)
    return role?.label || roleValue
  }

  // 角色变化时自动更新协作者列表
  const handleRoleChange = () => {
    const selectedUserIds = filteredUsersByRole.value.map((u) => u.value)
    document.value.editable_user_ids = selectedUserIds
    markAsModified()
  }

  // 加载用户列表和角色列表
  const loadUsers = async () => {
    try {
      console.log('📋 [EditPage] 开始加载用户列表')
      const res = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      console.log('📋 [EditPage] API 响应:', res)

      // 兼容不同的响应格式
      let userList: any[] = []
      if (res) {
        userList = res.items || res.data?.items || res.list || res.data?.list || res.data || []
        console.log('📋 [EditPage] 解析出的用户列表:', userList)
      }

      if (userList.length > 0) {
        userOptions.value = userList
          .filter((u: any) => u.id !== userStore.currentUser?.id)
          .map((u: any) => ({
            label: u.real_name || u.realName || u.username || u.name,
            value: u.id || u.userId,
            role: u.role
          }))
        console.log('✅ [EditPage] 用户选项已加载:', userOptions.value.length, '个用户')
      } else {
        console.warn('⚠️ [EditPage] 用户列表为空')
      }

      // 加载角色列表
      try {
        const roleRes: any = await roleApi.getRoles({ size: 9999 })
        const roleList: any[] = roleRes?.data?.list || roleRes?.data?.roles || []
        roleOptions.value = roleList.map((r) => ({
          label: r.name,
          value: r.role
        }))
        console.log('✅ [EditPage] 角色列表加载成功，数量:', roleOptions.value.length)
      } catch (roleError) {
        console.error('❌ [EditPage] 加载角色列表失败:', roleError)
      }
    } catch (error) {
      console.error('❌ [EditPage] 加载用户列表失败:', error)
    }
  }

  // 加载文档
  const loadDocument = async () => {
    try {
      loading.value = true
      console.log('📄 [EditPage] 获取协作文档详情:', documentId.value)
      const res = await collaborationApi.getDocument(documentId.value)
      document.value = res
      editingContent.value = res.content || ''
      console.log('✅ [Edit] 文档加载成功:', res.title)
    } catch (error) {
      console.error('❌ [Edit] 文档加载失败:', error)
      ElMessage.error('加载文档失败')
    } finally {
      loading.value = false
    }
  }

  // 标记为已修改
  const markAsModified = () => {
    isModified.value = true
  }

  // 保存文档
  const saveDocument = async () => {
    if (!document.value || !document.value.title.trim()) {
      ElMessage.warning('标题不能为空')
      return
    }

    try {
      saving.value = true
      await collaborationApi.updateDocument(document.value.id, {
        title: document.value.title,
        description: document.value.description,
        status: document.value.status,
        priority: document.value.priority,
        tags: document.value.tags,
        editable_user_ids: document.value.editable_user_ids,
        content: editingContent.value
      } as any)

      ElMessage.success('保存成功')
      isModified.value = false
      lastSaveTime.value = new Date().toISOString()
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  }

  // 返回
  const goBack = () => {
    if (isModified.value) {
      ElMessageBox.confirm('有未保存的更改，确定要离开吗？', '提示', {
        confirmButtonText: '离开',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          router.back()
        })
        .catch(() => {})
    } else {
      router.back()
    }
  }

  // 获取状态标签类型
  const getStatusTagType = (status: string) => {
    const map: Record<string, any> = {
      draft: 'info',
      active: 'success',
      completed: 'success',
      archived: 'warning'
    }
    return map[status] || 'info'
  }

  // 协作用户变化
  const onCollaborationUsersChange = (users: any[]) => {
    collaborationUsers.value = users
  }

  // 导入 Markdown
  const openImportMarkdown = () => {
    showMdDialog.value = true
  }

  const handleMdFileChange = async (file: any) => {
    try {
      mdFileName.value = file.name
      const content = await readMarkdownFile(file.raw)
      const html = markdownToHtml(content)
      editingContent.value = html
      markAsModified()
      ElMessage.success('Markdown 导入成功')
      showMdDialog.value = false
    } catch (error) {
      console.error('导入失败:', error)
      ElMessage.error('导入失败')
    }
  }

  // 导入 Word
  const openImportWord = () => {
    showWordDialog.value = true
  }

  const handleWordFileChange = async (file: any) => {
    try {
      wordFileName.value = file.name
      wordImporting.value = true
      const arrayBuffer = await file.raw.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })
      editingContent.value = result.value
      markAsModified()
      ElMessage.success('Word 导入成功')
      wordImporting.value = false
      showWordDialog.value = false
    } catch (error) {
      console.error('导入失败:', error)
      ElMessage.error('导入失败')
      wordImporting.value = false
    }
  }

  onMounted(() => {
    loadDocument()
    loadUsers()
  })
</script>

<style scoped lang="scss">
  .collaboration-edit-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f5f7fa;

    .top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      background: white;
      border-bottom: 1px solid #e4e7ed;

      .left-actions {
        display: flex;
        align-items: center;
        gap: 12px;

        .page-title {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }
      }

      .right-actions {
        display: flex;
        gap: 12px;
      }
    }

    .main-content {
      flex: 1;
      display: flex;
      gap: 16px;
      padding: 16px;
      overflow: hidden;

      .settings-panel {
        width: 280px;
        background: white;
        border-radius: 8px;
        padding: 16px;
        overflow-y: auto;

        .panel-section {
          .section-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #303133;
          }

          .form-item {
            margin-bottom: 16px;

            .item-label {
              display: block;
              margin-bottom: 8px;
              font-size: 14px;
              color: #606266;
            }

            .item-select {
              width: 100%;
            }

            .item-tip {
              margin-top: 6px;
              font-size: 12px;
              color: var(--art-text-gray-500);

              &.warning {
                padding: 8px 12px;
                background-color: #fef0e6;
                color: #e6a23c;
                border: 1px solid #f5dab1;
                border-radius: 4px;
              }

              &.success {
                padding: 8px 12px;
                background-color: #f0f9ff;
                color: #409eff;
                border: 1px solid #c6e2ff;
                border-radius: 4px;
              }
            }
          }
        }

        .collaboration-users-list {
          .user-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px;
            border-radius: 6px;
            margin-bottom: 8px;

            &:hover {
              background: #f5f7fa;
            }

            .user-avatar {
              position: relative;
              width: 36px;
              height: 36px;
              border-radius: 50%;
              border: 2px solid;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #ecf5ff;

              .avatar-text {
                font-weight: 600;
                color: #409eff;
              }

              .online-indicator {
                position: absolute;
                bottom: 0;
                right: 0;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                border: 2px solid white;
              }
            }

            .user-info {
              flex: 1;

              .user-name {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 14px;
              }
            }
          }

          .no-users {
            text-align: center;
            padding: 20px;
            color: #909399;
            font-size: 14px;
          }
        }

        .save-section {
          margin-top: 16px;

          .save-tip {
            text-align: center;
            margin-top: 8px;
            font-size: 12px;
            color: #909399;
          }
        }
      }

      .editor-container {
        flex: 1;
        background: white;
        border-radius: 8px;
        padding: 24px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;

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
              padding: 0;
              line-height: 1.4;

              &::placeholder {
                color: var(--art-text-gray-400);
                font-weight: 400;
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
                box-shadow: none !important;
              }
            }
          }
        }

        .editor-wrapper {
          flex: 1;
          min-height: 0;
        }
      }
    }

    .file-selected {
      margin-top: 12px;
      padding: 8px 12px;
      background: #f0f9ff;
      border-radius: 4px;
      font-size: 14px;
    }
  }
</style>
