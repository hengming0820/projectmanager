<template>
  <div class="collaboration-page">
    <!-- 顶部标题栏 -->
    <ArtPageHeader
      title="团队协作文档"
      description="跨团队协作记录，实时编辑，高效沟通"
      icon="🤝"
      badge="Collaboration"
      theme="blue"
    >
      <template #actions>
        <el-button v-if="canCreateDocument" type="primary" @click="createDocument">
          <el-icon><Plus /></el-icon>
          创建文档
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </template>
    </ArtPageHeader>

    <el-container class="page-container">
      <el-container class="page-body">
        <!-- 左侧导航栏 -->
        <el-aside class="sidebar" v-if="navReady">
          <div class="nav-panel">
            <!-- 筛选器区域 -->
            <div class="filter-section">
              <!-- 搜索框 -->
              <div class="filter-search">
                <el-input
                  v-model="filterSearch"
                  placeholder="🔍 搜索文档标题..."
                  clearable
                  size="default"
                  :prefix-icon="Search"
                />
              </div>

              <!-- 筛选控件组 -->
              <div class="filter-controls">
                <!-- 我的相关开关 -->
                <div class="filter-item switch-item">
                  <div class="filter-item-content">
                    <el-icon class="filter-icon"><User /></el-icon>
                    <span class="filter-label">仅显示与我相关</span>
                  </div>
                  <el-switch v-model="showMyRelated" size="default" @change="onFilterChange" />
                </div>

                <!-- 分隔线 -->
                <div class="filter-divider"></div>

                <!-- 按协作者筛选 -->
                <div class="filter-item select-item">
                  <div class="filter-item-header">
                    <el-icon class="filter-icon"><Users /></el-icon>
                    <span class="filter-label">按协作者筛选</span>
                  </div>
                  <el-select
                    v-model="selectedCollaborators"
                    multiple
                    collapse-tags
                    collapse-tags-tooltip
                    :max-collapse-tags="2"
                    placeholder="选择协作者"
                    size="default"
                    clearable
                    @change="onFilterChange"
                  >
                    <el-option
                      v-for="user in allCollaborators"
                      :key="user.value"
                      :label="user.label"
                      :value="user.value"
                    >
                      <div class="user-option">
                        <el-icon><User /></el-icon>
                        <span>{{ user.label }}</span>
                      </div>
                    </el-option>
                  </el-select>
                </div>
              </div>
            </div>

            <!-- 文档分类树 -->
            <el-tree
              ref="treeRef"
              :data="treeData"
              node-key="key"
              :highlight-current="true"
              :current-node-key="currentDocId"
              :expand-on-click-node="true"
              :default-expanded-keys="expandedKeys"
              :filter-node-method="filterNode"
              @node-click="onNodeClick"
            >
              <template #default="{ data }">
                <div
                  :class="[
                    'tree-node',
                    data.isLeaf ? 'tree-leaf' : 'tree-group',
                    data.level ? `level-${data.level}` : ''
                  ]"
                  @contextmenu.prevent="data.isLeaf ? handleNodeRightClick($event, data) : null"
                >
                  <!-- 叶子节点（文档）显示完整信息 -->
                  <template v-if="data.isLeaf">
                    <!-- 文档图标 -->
                    <el-icon class="node-icon">
                      <Document />
                    </el-icon>
                    <el-tooltip
                      :content="data.label"
                      placement="right"
                      :disabled="data.label.length <= 20"
                      :show-after="300"
                    >
                      <span class="leaf-title">{{ data.label }}</span>
                    </el-tooltip>
                  </template>

                  <!-- 分组节点（日期）直接显示 -->
                  <span v-else class="node-label">{{ data.label }}</span>
                </div>
              </template>
            </el-tree>
          </div>
        </el-aside>

        <!-- 右侧主内容区 - 文档详情 -->
        <el-main class="main-col">
          <div v-if="currentDocId && currentDocument" class="document-detail-wrapper">
            <!-- 文档详情卡片 -->
            <el-card class="document-card">
              <template #header>
                <div class="document-header">
                  <div class="header-left">
                    <div class="header-info">
                      <h3>{{ currentDocument.title }}</h3>
                      <span class="meta-info">
                        <span class="meta-text">
                          <el-icon><User /></el-icon>
                          {{ currentDocument.owner_name }}
                        </span>
                        <span class="meta-text">
                          <el-icon><Calendar /></el-icon>
                          {{ formatDate(currentDocument.updated_at) }}
                        </span>
                      </span>
                    </div>
                  </div>
                  <div class="header-actions">
                    <template v-if="!isEditing">
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
                      <el-button @click="openMetaDialog" v-if="canEditDocument(currentDocument)">
                        <el-icon><Edit /></el-icon>
                        编辑信息
                      </el-button>
                      <el-button @click="startEdit" v-if="canEditDocument(currentDocument)">
                        <el-icon><Document /></el-icon>
                        编辑内容
                      </el-button>
                      <el-button @click="showDocumentInfoDrawer">
                        <el-icon><InfoFilled /></el-icon>
                        文档信息
                      </el-button>
                      <el-button
                        type="danger"
                        @click="deleteDocument"
                        v-if="canDeleteDocument(currentDocument)"
                      >
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </template>
                    <template v-else>
                      <el-button @click="openImportMarkdown" size="default">
                        <el-icon><Upload /></el-icon>
                        导入 Markdown
                      </el-button>
                      <el-button @click="openImportWord" size="default">
                        <el-icon><Document /></el-icon>
                        导入 Word
                      </el-button>
                      <el-button @click="cancelEdit">取消</el-button>
                      <el-button type="primary" @click="saveEdit" :loading="saving"
                        >保存内容</el-button
                      >
                    </template>
                  </div>
                </div>
              </template>

              <div class="document-content">
                <!-- 查看模式 -->
                <template v-if="!isEditing">
                  <!-- 文档内容 -->
                  <div class="document-body">
                    <ArtXnotePreview :content="currentDocument.content" height="100%" />
                  </div>
                </template>

                <!-- 编辑模式（仅编辑内容） -->
                <template v-else>
                  <div class="content-editor" :class="{ 'editing-active': isEditing }">
                    <ArtTextbusEditor
                      v-if="isEditing && currentDocument"
                      :key="`editor-${currentDocument.id}-${isEditing}`"
                      v-model="editForm.content"
                      :height="editorHeight"
                      :collaboration-url="
                        currentDocument ? collaborationWsUrl(currentDocument.id) : ''
                      "
                      :current-user="currentUserInfo"
                    />
                  </div>
                </template>
              </div>
            </el-card>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="请从左侧选择一个文档查看详情" :image-size="200">
            <el-button type="primary" @click="createDocument" v-if="canCreateDocument">
              创建第一个文档
            </el-button>
          </el-empty>
        </el-main>
      </el-container>
    </el-container>

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

    <!-- 编辑元数据对话框 -->
    <el-dialog
      v-model="showMetaDialog"
      :close-on-click-modal="false"
      width="600px"
      class="meta-dialog"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <template #header>
        <div class="dialog-header">
          <div class="dialog-icon">
            <el-icon><Edit /></el-icon>
          </div>
          <div class="dialog-title">
            <h3>编辑文档信息</h3>
            <p>修改文档的标题、描述、状态等元数据</p>
          </div>
        </div>
      </template>

      <el-form :model="metaForm" label-width="90px" class="meta-form">
        <el-form-item label="标题" required>
          <el-input v-model="metaForm.title" placeholder="请输入文档标题" size="large" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="metaForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入文档描述"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="metaForm.status" placeholder="选择状态" size="large">
            <el-option label="📝 草稿" value="draft">
              <span class="status-option">
                <span class="emoji">📝</span>
                <span>草稿</span>
              </span>
            </el-option>
            <el-option label="🔄 进行中" value="active">
              <span class="status-option">
                <span class="emoji">🔄</span>
                <span>进行中</span>
              </span>
            </el-option>
            <el-option label="✅ 已完成" value="completed">
              <span class="status-option">
                <span class="emoji">✅</span>
                <span>已完成</span>
              </span>
            </el-option>
            <el-option label="📦 已归档" value="archived">
              <span class="status-option">
                <span class="emoji">📦</span>
                <span>已归档</span>
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-radio-group v-model="metaForm.priority" size="large" class="priority-group">
            <el-radio-button value="low">
              <span class="priority-option low">低</span>
            </el-radio-button>
            <el-radio-button value="normal">
              <span class="priority-option normal">普通</span>
            </el-radio-button>
            <el-radio-button value="high">
              <span class="priority-option high">高</span>
            </el-radio-button>
            <el-radio-button value="urgent">
              <span class="priority-option urgent">紧急</span>
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="metaForm.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签"
            size="large"
            class="tags-select"
          >
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>

        <el-form-item label="可编辑角色">
          <el-select
            v-model="metaForm.editable_roles"
            multiple
            filterable
            placeholder="选择可编辑角色"
            size="large"
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
            placeholder="选择人员"
            size="large"
          >
            <el-option v-for="u in userOptions" :key="u.value" :label="u.label" :value="u.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="所属部门">
          <el-select
            v-model="metaForm.departments"
            multiple
            filterable
            placeholder="选择部门"
            size="large"
          >
            <el-option v-for="d in deptOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showMetaDialog = false" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="saveMeta"
            :loading="saving"
            size="large"
            class="save-btn"
          >
            <el-icon v-if="!saving"><Check /></el-icon>
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <teleport to="body">
      <div
        v-if="contextMenuVisible"
        class="context-menu"
        :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }"
        @click.stop
      >
        <div class="menu-item" @click="copyDocumentLink">
          <el-icon><Link /></el-icon>
          <span>复制文档链接</span>
        </div>
      </div>
    </teleport>

    <!-- 文档信息抽屉 -->
    <el-drawer 
      v-model="documentInfoDrawerVisible" 
      title="文档信息" 
      direction="rtl" 
      size="550px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <div class="drawer-content" v-if="currentDocument">
        <!-- 文档元信息区域 -->
        <div class="document-meta-section">
          <el-card shadow="never" class="meta-card">
            <template #header>
              <div class="meta-card-header">
                <el-icon><InfoFilled /></el-icon>
                <span>文档元信息</span>
              </div>
            </template>

            <div class="meta-content">
              <!-- 文档描述 -->
              <div v-if="currentDocument.description" class="meta-item summary-item">
                <div class="meta-label">
                  <el-icon><Document /></el-icon>
                  <span>描述</span>
                </div>
                <div class="meta-value summary-text">
                  {{ currentDocument.description }}
                </div>
              </div>

              <!-- 协作成员 -->
              <div v-if="currentDocument.collaborators?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><User /></el-icon>
                  <span>协作成员</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="collaborator in currentDocument.collaborators"
                    :key="collaborator.id"
                    :type="isUserEditing(collaborator.user_id) ? 'success' : undefined"
                    :effect="isUserEditing(collaborator.user_id) ? 'dark' : 'plain'"
                    size="small"
                    class="meta-tag"
                  >
                    <el-icon v-if="isUserEditing(collaborator.user_id)" style="margin-right: 4px">
                      <Edit />
                    </el-icon>
                    {{ collaborator.user_name }}
                  </el-tag>
                  <span v-if="!currentDocument.collaborators.length" class="empty-text"
                    >无协作成员</span
                  >
                </div>
              </div>

              <!-- 可编辑成员 -->
              <div v-if="currentDocument.editable_user_ids?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><User /></el-icon>
                  <span>可编辑成员</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="userId in currentDocument.editable_user_ids"
                    :key="userId"
                    size="small"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ getUserDisplayName(userId) }}
                  </el-tag>
                  <span v-if="!currentDocument.editable_user_ids.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 可编辑角色 -->
              <div v-if="currentDocument.editable_roles?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><UserFilled /></el-icon>
                  <span>可编辑角色</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="role in currentDocument.editable_roles"
                    :key="role"
                    size="small"
                    type="success"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ getRoleName(role) }}
                  </el-tag>
                  <span v-if="!currentDocument.editable_roles.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 所属部门 -->
              <div v-if="currentDocument.departments?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><OfficeBuilding /></el-icon>
                  <span>所属部门</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="dept in currentDocument.departments"
                    :key="dept"
                    size="small"
                    type="warning"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ dept }}
                  </el-tag>
                  <span v-if="!currentDocument.departments.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 标签 -->
              <div v-if="currentDocument.tags && currentDocument.tags.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><PriceTag /></el-icon>
                  <span>标签</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="tag in currentDocument.tags"
                    :key="tag"
                    size="small"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ tag }}
                  </el-tag>
                  <span v-if="!currentDocument.tags.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 优先级 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><Flag /></el-icon>
                  <span>优先级</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    :color="collaborationUtils.getPriorityInfo(currentDocument.priority).color"
                    effect="light"
                    size="small"
                  >
                    {{ collaborationUtils.getPriorityInfo(currentDocument.priority).text }}
                  </el-tag>
                </div>
              </div>

              <!-- 状态 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><Clock /></el-icon>
                  <span>状态</span>
                </div>
                <div class="meta-value">
                  <el-tag :type="getStatusTagType(currentDocument.status)" size="small">
                    {{ collaborationUtils.getStatusText(currentDocument.status) }}
                  </el-tag>
                </div>
              </div>

              <!-- 所有者 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><User /></el-icon>
                  <span>所有者</span>
                </div>
                <div class="meta-value">
                  {{ currentDocument.owner_name || '未知' }}
                </div>
              </div>

              <!-- 创建时间 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><Calendar /></el-icon>
                  <span>创建时间</span>
                </div>
                <div class="meta-value">
                  {{ formatDate(currentDocument.created_at) }}
                </div>
              </div>

              <!-- 更新时间 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><Clock /></el-icon>
                  <span>更新时间</span>
                </div>
                <div class="meta-value">
                  {{ formatDate(currentDocument.updated_at) }}
                </div>
              </div>

              <!-- 查看次数 -->
              <div class="meta-item">
                <div class="meta-label">
                  <el-icon><View /></el-icon>
                  <span>查看次数</span>
                </div>
                <div class="meta-value"> {{ currentDocument.view_count || 0 }} 次 </div>
              </div>

              <!-- 提示：无元信息 -->
              <el-empty
                v-if="
                  !currentDocument.description &&
                  !currentDocument.collaborators?.length &&
                  (!currentDocument.tags || !currentDocument.tags.length)
                "
                description="暂无文档元信息"
                :image-size="80"
              />
            </div>
          </el-card>
        </div>
      </div>
    </el-drawer>

    <!-- 创建文档对话框 -->
    <CreateDocumentDialog
      v-model="createDialogVisible"
      title="创建协作文档"
      description-label="文档描述"
      collaborator-label="协作者"
      document-type="文档"
      submit-button-text="创建并编辑"
      :show-priority="true"
      :show-roles="false"
      :show-departments="false"
      :available-tags="availableTags"
      :user-options="userOptions"
      :role-options="roleOptions"
      @submit="handleCreateDocument"
      @cancel="handleCancelCreate"
      ref="createDialogRef"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onActivated, onBeforeUnmount, watch, nextTick } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Plus,
    Refresh,
    Search,
    Edit,
    Delete,
    User,
    Calendar,
    View,
    Document,
    Clock,
    Grid,
    List,
    Check,
    Download,
    ArrowDown,
    Printer,
    Upload,
    Link,
    PriceTag,
    InfoFilled,
    Flag,
    UserFilled,
    OfficeBuilding,
    UploadFilled
  } from '@element-plus/icons-vue'
  import { useUserStore } from '@/store/modules/user'
  import { collaborationApi, collaborationUtils } from '@/api/collaborationApi'
  import type {
    CollaborationDocument,
    CollaborationStatistics,
    CollaborationStatus,
    CollaborationPriority
  } from '@/types/collaboration'
  import ArtTextbusEditor from '@/components/core/forms/art-textbus-editor/index.vue'
  import ArtXnotePreview from '@/components/core/forms/art-xnote-preview/index.vue'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'
  import mammoth from 'mammoth'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import { markdownToHtml, validateMarkdownFile, readMarkdownFile } from '@/utils/markdown'
  import CreateDocumentDialog from '@/components/business/CreateDocumentDialog.vue'

  const route = useRoute()
  const router = useRouter()
  const userStore = useUserStore()
  // 允许所有登录用户创建协作文档
  const canCreateDocument = computed(() => !!userStore.currentUser?.id)

  // 协作 WebSocket URL（TextBus XNote 使用）
  const collaborationWsUrl = (documentId: string) => {
    if (!documentId) return ''
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    return `${protocol}://${location.host}/api/collaboration/ws/${documentId}`
  }

  // 当前用户信息（TextBus XNote 需要）
  const currentUserInfo = computed(() => {
    const user = userStore.currentUser || (userStore.users.length > 0 ? userStore.users[0] : null)
    return {
      id: user?.id || '',
      username: user?.username || '',
      realName: user?.realName || user?.username || '用户',
      avatar: user?.avatar || ''
    }
  })

  // 当前选中的文档
  const currentDocId = ref<string>('')
  const currentDocument = ref<CollaborationDocument | null>(null)

  // 导航栏数据
  const navReady = ref(false)
  const treeData = ref<any[]>([])
  const expandedKeys = ref<string[]>([])
  const treeRef = ref()
  const filterSearch = ref('')

  // 文档列表数据
  const documents = ref<CollaborationDocument[]>([])
  const statistics = ref<CollaborationStatistics>({
    total_documents: 0,
    active_documents: 0,
    total_collaborators: 0,
    documents_by_status: {
      draft: 0,
      active: 0,
      completed: 0,
      archived: 0
    },
    documents_by_priority: {
      low: 0,
      normal: 0,
      high: 0,
      urgent: 0
    },
    recent_activities: []
  })

  // 编辑模式相关（仅内容）
  const isEditing = ref(false)
  const saving = ref(false)

  // 文档信息抽屉
  const documentInfoDrawerVisible = ref(false)
  const editForm = ref({
    content: ''
  })

  // 编辑器高度计算（使用 calc 计算可用高度）
  const editorHeight = computed(() => {
    // 计算可用高度：视口高度 - 头部 - 卡片头部 - 按钮栏等
    // 大约留出 300px 给头部和其他元素
    return 'calc(100vh - 300px)'
  })

  // 右键菜单相关
  const contextMenuVisible = ref(false)
  const contextMenuPosition = ref({ x: 0, y: 0 })
  const rightClickedDocument = ref<any>(null)

  // Markdown 导入相关
  const showMdDialog = ref(false)
  const mdFileName = ref('')

  // Word 导入相关
  const showWordDialog = ref(false)
  const wordFileName = ref('')
  const wordImporting = ref(false)

  // 元数据编辑对话框
  const showMetaDialog = ref(false)
  const metaForm = ref({
    title: '',
    description: '',
    status: 'draft' as CollaborationStatus,
    priority: 'normal' as CollaborationPriority,
    tags: [] as string[],
    editable_roles: [] as string[],
    editable_user_ids: [] as string[],
    departments: [] as string[]
  })

  // 用户、部门和角色选项
  const userOptions = ref<Array<{ label: string; value: string; role?: string }>>([])
  const deptOptions = ref<Array<{ label: string; value: string }>>([])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])

  // 可用标签列表
  const availableTags = ref<string[]>([])

  // 筛选控件
  const showMyRelated = ref(false) // 仅显示与我相关
  const selectedCollaborators = ref<string[]>([]) // 选中的协作者

  // 所有协作者列表（计算属性）
  const allCollaborators = computed(() => {
    const collaboratorMap = new Map<string, string>()

    documents.value.forEach((doc) => {
      // 添加创建者
      if (doc.owner_id) {
        const user = userStore.users.find((u) => u.id === doc.owner_id)
        const realName = user ? (user as any).real_name : null
        const displayName =
          realName && realName.trim() ? realName : user?.username || doc.owner_name || '未知用户'
        collaboratorMap.set(doc.owner_id, displayName)
      }

      // 添加所有协作者
      doc.collaborators.forEach((collab) => {
        const user = userStore.users.find((u) => u.id === collab.user_id)
        const realName = user ? (user as any).real_name : null
        const displayName =
          realName && realName.trim() ? realName : user?.username || collab.user_name || '未知用户'
        collaboratorMap.set(collab.user_id, displayName)
      })
    })

    // 转换为选项数组，按名称排序
    return Array.from(collaboratorMap.entries())
      .map(([value, label]) => ({ value, label }))
      .sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
  })

  // 筛选变化处理
  const onFilterChange = () => {
    buildTree()
  }

  // 加载文档列表
  const loadDocuments = async () => {
    try {
      const response = await collaborationApi.getDocuments({ page: 1, page_size: 100 })
      documents.value = (response as any).items || []

      // 调试：查看文档数据中的用户名字段
      if (documents.value.length > 0) {
        const firstDoc = documents.value[0]
        console.log('🔍 [Collaboration] 文档数据示例:', {
          owner_id: firstDoc.owner_id,
          owner_name: firstDoc.owner_name,
          collaborators: firstDoc.collaborators.map((c: any) => ({
            user_id: c.user_id,
            user_name: c.user_name
          }))
        })
      }

      buildTree()

      // 加载统计信息
      const stats = await collaborationApi.getStatistics()
      statistics.value = stats
    } catch (error) {
      console.error('加载文档列表失败:', error)
      ElMessage.error('加载文档列表失败')
    }
  }

  // 构建树形数据结构（日期 -> 文档）
  const buildTree = () => {
    const currentUserId = userStore.currentUser?.id || ''

    // 应用筛选条件
    let filteredDocs = [...documents.value]

    // 筛选1: 仅显示与我相关
    if (showMyRelated.value && currentUserId) {
      filteredDocs = filteredDocs.filter((doc) => {
        // 是创建者
        if (doc.owner_id === currentUserId) return true
        // 是协作者
        return doc.collaborators.some((c) => c.user_id === currentUserId)
      })
    }

    // 筛选2: 按协作者筛选
    if (selectedCollaborators.value.length > 0) {
      filteredDocs = filteredDocs.filter((doc) => {
        // 创建者在筛选列表中
        if (selectedCollaborators.value.includes(doc.owner_id)) return true
        // 协作者在筛选列表中
        return doc.collaborators.some((c) => selectedCollaborators.value.includes(c.user_id))
      })
    }

    // 按创建时间倒序排序
    const sortedDocs = filteredDocs.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )

    // 按日期分组
    const dateGroups: Record<string, CollaborationDocument[]> = {}

    sortedDocs.forEach((doc) => {
      const date = new Date(doc.created_at)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const yearMonth = `${year}-${String(month).padStart(2, '0')}`

      if (!dateGroups[yearMonth]) {
        dateGroups[yearMonth] = []
      }
      dateGroups[yearMonth].push(doc)
    })

    // 按时间倒序排序月份
    const months = Object.keys(dateGroups).sort((a, b) => b.localeCompare(a))

    // 构建树结构
    treeData.value = months.map((yearMonth) => {
      const [year, month] = yearMonth.split('-')
      const formattedLabel = `📅 ${year}年${parseInt(month)}月`

      // 第二层：文档列表
      const docChildren = dateGroups[yearMonth].map((doc) => ({
        key: doc.id,
        label: doc.title,
        isLeaf: true,
        level: 2,
        statusText: collaborationUtils.getStatusText(doc.status),
        statusType: getStatusTagType(doc.status),
        priority: collaborationUtils.getPriorityInfo(doc.priority).text,
        created_at: doc.created_at,
        document: doc
      }))

      return {
        key: `date-${yearMonth}`,
        label: `${formattedLabel} (${docChildren.length})`,
        level: 1,
        children: docChildren
      }
    })

    // 默认展开前3个月份
    if (expandedKeys.value.length === 0 && treeData.value.length > 0) {
      expandedKeys.value = treeData.value.slice(0, 3).map((node: any) => node.key)
    }

    // 如果还没有选中文档，选中第一个
    if (!currentDocId.value && filteredDocs.length > 0) {
      currentDocId.value = filteredDocs[0].id
      currentDocument.value = filteredDocs[0]
    }

    navReady.value = true
  }

  // 树节点点击
  const onNodeClick = (node: any) => {
    // 只处理叶子节点（文档节点）的点击
    // 分组节点的展开/收起由 el-tree 的 expand-on-click-node 自动处理
    if (!node || !node.isLeaf) {
      return
    }

    if (node.key !== currentDocId.value) {
      currentDocId.value = node.key
      currentDocument.value = node.document
    }
  }

  // 处理右键点击
  const handleNodeRightClick = (event: MouseEvent, data: any) => {
    if (!data.document) return

    rightClickedDocument.value = data.document
    contextMenuPosition.value = {
      x: event.clientX,
      y: event.clientY
    }
    contextMenuVisible.value = true
  }

  // 复制文档链接
  const copyDocumentLink = async () => {
    if (!rightClickedDocument.value) return

    const baseUrl = window.location.origin
    const docUrl = `${baseUrl}/login#/collaboration?articleId=${rightClickedDocument.value.id}`

    try {
      await navigator.clipboard.writeText(docUrl)
      ElMessage.success('文档链接已复制到剪贴板')
    } catch (error) {
      // 降级方案：使用传统的复制方法
      const textarea = document.createElement('textarea')
      textarea.value = docUrl
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('文档链接已复制到剪贴板')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      }
      document.body.removeChild(textarea)
    }

    contextMenuVisible.value = false
  }

  // 树节点过滤
  const filterNode = (value: string, data: any) => {
    if (!value) return true
    return data.label.toLowerCase().includes(value.toLowerCase())
  }

  // 监听搜索框变化
  watch(filterSearch, (val) => {
    treeRef.value?.filter(val)
  })

  // 监听元数据对话框关闭，如果关闭则解锁
  watch(showMetaDialog, async (newVal, oldVal) => {
    if (oldVal && !newVal && currentDocument.value) {
      // 对话框从打开变为关闭
      try {
        await collaborationApi.unlockDocument(currentDocument.value.id)
      } catch (error) {
        console.error('解锁失败:', error)
      }
    }
  })

  // 状态标签类型
  const getStatusTagType = (status: string): 'success' | 'info' | 'warning' | 'danger' => {
    const typeMap: Record<string, 'success' | 'info' | 'warning' | 'danger'> = {
      draft: 'info',
      active: 'warning',
      completed: 'success',
      archived: 'info'
    }
    return typeMap[status] || 'info'
  }

  // 根据角色名称获取显示名称
  const getRoleName = (role: string) => {
    const roleOption = roleOptions.value.find((r) => r.value === role)
    return roleOption?.label || role
  }

  // 根据用户ID获取用户显示名称
  const getUserDisplayName = (userId: string) => {
    const user = userStore.users.find((u) => u.id === userId)
    return user?.realName || user?.username || userId
  }

  // 格式化日期
  const formatDate = (date: string) => {
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  // 权限检查
  const canEditDocument = (doc: CollaborationDocument) => {
    const currentUserId = userStore.currentUser?.id
    if (!currentUserId) return false

    // 1. 管理员可以编辑所有文档
    if (userStore.currentUser?.role === 'admin') return true

    // 2. 文档所有者可以编辑
    if (currentUserId === doc.owner_id) return true

    // 3. 协作者可以编辑
    const isCollaborator = doc.collaborators?.some((c) => c.user_id === currentUserId)
    if (isCollaborator) return true

    return false
  }

  const canDeleteDocument = (doc: CollaborationDocument) => {
    return userStore.currentUser?.id === doc.owner_id || userStore.currentUser?.role === 'admin'
  }

  // 判断用户是否正在编辑当前文档
  const isUserEditing = (userId: string) => {
    if (!currentDocument.value) return false

    // 检查文档是否被锁定，且锁定者是该用户
    return currentDocument.value.is_locked && currentDocument.value.locked_by === userId
  }

  // 获取锁定者的真实姓名
  const getLockedByUserName = (userId?: string) => {
    if (!userId || !currentDocument.value) return '其他用户'

    // 1. 先检查是否是文档所有者
    if (currentDocument.value.owner_id === userId) {
      return currentDocument.value.owner_name
    }

    // 2. 从协作者列表中查找
    const collaborator = currentDocument.value.collaborators.find((c) => c.user_id === userId)
    if (collaborator) {
      return collaborator.user_name
    }

    // 3. 从用户选项中查找（如果有加载）
    const userOption = userOptions.value.find((u) => u.value === userId)
    if (userOption) {
      return userOption.label.split(' (')[0] // 提取真实姓名部分
    }

    // 4. 默认返回
    return '其他用户'
  }

  // 创建文档对话框
  const createDialogVisible = ref(false)
  const createDialogRef = ref()

  // 创建文档（显示对话框）
  const createDocument = () => {
    createDialogVisible.value = true
  }

  // 处理创建文档提交
  const handleCreateDocument = async (formData: any) => {
    createDialogRef.value?.setSubmitting(true)

    try {
      // 1. 创建文档（不包含协作者）
      const data = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        content: '', // 创建时内容为空
        status: 'draft' as const,
        priority: formData.priority,
        tags: formData.tags
      }

      console.log('➕ [Collaboration] 创建文档数据:', data)
      const result = await collaborationApi.createDocument(data)
      console.log('✅ [Collaboration] 文档创建成功:', result.id)

      // 2. 添加协作者（通过关联表）
      if (formData.editable_user_ids.length > 0) {
        console.log('👥 [Collaboration] 添加协作者:', formData.editable_user_ids)
        for (const userId of formData.editable_user_ids) {
          try {
            await collaborationApi.addCollaborator(result.id, userId, 'editor')
            console.log('✅ [Collaboration] 已添加协作者:', userId)
          } catch (error) {
            console.error('❌ [Collaboration] 添加协作者失败:', userId, error)
          }
        }
      }

      ElMessage.success('文档创建成功！正在跳转到编辑页面...')

      // 延迟关闭对话框，让用户看到成功提示
      setTimeout(() => {
        createDialogRef.value?.close()
    router.push({
      name: 'CollaborationDocument',
          params: { documentId: result.id }
    })
      }, 500)
    } catch (error: any) {
      console.error('❌ [Collaboration] 创建文档失败:', error)
      ElMessage.error(error.message || '创建文档失败')
    } finally {
      createDialogRef.value?.setSubmitting(false)
    }
  }

  // 取消创建
  const handleCancelCreate = () => {
    createDialogVisible.value = false
  }

  // 打开元数据编辑对话框
  const openMetaDialog = async () => {
    if (!currentDocument.value) return

    // 先刷新文档状态，获取最新的锁定信息
    try {
      console.log('🔄 [Collaboration] 打开编辑信息前刷新文档状态')
      await loadDocuments()
      const refreshedDoc = documents.value.find((d) => d.id === currentDocument.value!.id)
      if (refreshedDoc) {
        currentDocument.value = refreshedDoc
        console.log(
          '✅ [Collaboration] 文档状态已刷新，is_locked:',
          refreshedDoc.is_locked,
          'locked_by:',
          refreshedDoc.locked_by
        )
      }
    } catch (error) {
      console.error('刷新文档状态失败:', error)
    }

    // 检查文档是否被锁定
    if (
      currentDocument.value.is_locked &&
      currentDocument.value.locked_by !== userStore.currentUser?.id
    ) {
      // 获取锁定者的真实姓名
      const lockedByUser = getLockedByUserName(currentDocument.value.locked_by)
      ElMessage.warning({
        message: `文档正被 ${lockedByUser} 编辑中，无法修改信息`,
        duration: 3000
      })
      return
    }

    // 尝试锁定文档
    try {
      console.log('🔒 [Collaboration] 尝试锁定文档（编辑信息）:', currentDocument.value.id)
      await collaborationApi.lockDocument(currentDocument.value.id)

      const doc = currentDocument.value as any
      metaForm.value = {
        title: doc.title,
        description: doc.description || '',
        status: doc.status,
        priority: doc.priority,
        tags: doc.tags || [],
        editable_roles: doc.editable_roles || [],
        editable_user_ids: doc.editable_user_ids || [],
        departments: doc.departments || []
      }
      showMetaDialog.value = true
    } catch (error: any) {
      if (error.response?.status === 423) {
        ElMessage.warning({
          message: '文档正在被其他用户编辑中，无法修改信息',
          duration: 3000
        })
      } else {
        ElMessage.error('打开编辑失败')
      }
    }
  }

  // 保存元数据
  const saveMeta = async () => {
    if (!currentDocument.value || !metaForm.value.title.trim()) {
      ElMessage.warning('标题不能为空')
      return
    }

    try {
      saving.value = true
      await collaborationApi.updateDocument(currentDocument.value.id, {
        title: metaForm.value.title,
        description: metaForm.value.description,
        status: metaForm.value.status,
        priority: metaForm.value.priority,
        tags: metaForm.value.tags,
        editable_roles: metaForm.value.editable_roles,
        editable_user_ids: metaForm.value.editable_user_ids,
        departments: metaForm.value.departments,
        content: currentDocument.value.content // 保持内容不变
      } as any)

      ElMessage.success('文档信息更新成功')
      showMetaDialog.value = false

      // 解锁文档
      try {
        await collaborationApi.unlockDocument(currentDocument.value.id)
      } catch (error) {
        console.error('解锁失败:', error)
      }

      await loadDocuments()

      // 重新选中当前文档
      currentDocument.value =
        documents.value.find((d) => d.id === currentDocument.value!.id) || null
    } catch (error) {
      console.error('更新文档信息失败:', error)
      ElMessage.error('更新文档信息失败')
    } finally {
      saving.value = false
    }
  }

  // 开始编辑内容（跳转到编辑页面）
  const startEdit = async () => {
    if (!currentDocument.value) {
      ElMessage.error('请先选择一个文档')
      return
    }

    console.log('🔍 [Collaboration] 准备编辑文档:', {
      id: currentDocument.value.id,
      title: currentDocument.value.title,
      routeName: 'CollaborationDocument'
    })

    router
      .push({
        name: 'CollaborationDocument',
        params: { documentId: currentDocument.value.id }
      })
      .catch((err) => {
        console.error('❌ [Collaboration] 路由跳转失败:', err)
        ElMessage.error('跳转失败，请重试')
      })
  }

  // 取消编辑
  const cancelEdit = async () => {
    if (currentDocument.value) {
      try {
        console.log('🔓 [Collaboration] 取消编辑，解锁文档:', currentDocument.value.id)
        await collaborationApi.unlockDocument(currentDocument.value.id)

        // 刷新文档列表以更新锁定状态
        await loadDocuments()

        // 重新选中当前文档（使用最新数据）
        const refreshedDoc = documents.value.find((d) => d.id === currentDocument.value!.id)
        if (refreshedDoc) {
          currentDocument.value = refreshedDoc
          console.log('✅ [Collaboration] 文档状态已刷新，is_locked:', refreshedDoc.is_locked)
        }
      } catch (error) {
        console.error('解锁失败:', error)
      }
    }
    isEditing.value = false
    editForm.value = {
      content: ''
    }
  }

  // 保存编辑内容
  const saveEdit = async () => {
    if (!currentDocument.value || !editForm.value.content.trim()) {
      ElMessage.warning('内容不能为空')
      return
    }

    try {
      saving.value = true

      await collaborationApi.updateDocument(currentDocument.value.id, {
        content: editForm.value.content,
        // 保持其他字段不变
        title: currentDocument.value.title,
        description: currentDocument.value.description,
        status: currentDocument.value.status,
        priority: currentDocument.value.priority,
        tags: currentDocument.value.tags
      })

      ElMessage.success('文档内容更新成功')
      isEditing.value = false

      // 解锁文档
      try {
        await collaborationApi.unlockDocument(currentDocument.value.id)
      } catch (error) {
        console.error('解锁失败:', error)
      }

      await loadDocuments()

      // 重新选中当前文档
      currentDocument.value =
        documents.value.find((d) => d.id === currentDocument.value!.id) || null
    } catch (error) {
      console.error('保存文档失败:', error)
      ElMessage.error('保存文档失败')
    } finally {
      saving.value = false
    }
  }

  // 删除文档
  // 显示文档信息抽屉
  const showDocumentInfoDrawer = () => {
    if (!currentDocument.value) {
      ElMessage.warning('请先选择一个文档')
      return
    }
    documentInfoDrawerVisible.value = true
  }

  const deleteDocument = async () => {
    if (!currentDocument.value) return

    try {
      await ElMessageBox.confirm('确定要删除这个文档吗？', '确认删除', {
        type: 'warning'
      })

      await collaborationApi.deleteDocument(currentDocument.value.id)
      ElMessage.success('文档删除成功')

      currentDocId.value = ''
      currentDocument.value = null
      await loadDocuments()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除文档失败:', error)
        ElMessage.error('删除文档失败')
      }
    }
  }

  // 刷新数据
  const refreshData = async () => {
    await loadUsersAndDepts() // 先加载用户数据
    await loadDocuments()
    ElMessage.success('数据已刷新')
  }

  // 打开导入 Markdown 对话框
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

      if (!content.trim()) {
        ElMessage.warning('Markdown 文件内容为空')
        return
      }

      // 转换 Markdown 为 HTML
      const html = markdownToHtml(content, {
        gfm: true,
        openLinksInNewWindow: true,
        sanitize: true
      })

      editForm.value.content = html
      showMdDialog.value = false
      ElMessage.success('Markdown 文档已导入')
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

  // 导出命令处理
  const handleExportCommand = (command: string) => {
    if (command === 'html') {
      exportHtml()
    } else if (command === 'pdf') {
      exportPdf()
    }
  }

  // 导出为 HTML
  const exportHtml = () => {
    if (!currentDocument.value) return
    const title = (currentDocument.value.title || 'document').replace(/[/\\:*?"<>|]/g, '_')
    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(title)}</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial; margin:24px; color:#111827;}
    h1,h2,h3{margin-top:18px}
    p{line-height:1.8;margin:10px 0}
    img{max-width:100%;height:auto;border-radius:4px}
    blockquote{border-left:4px solid #e5e7eb;background:#f9fafb;padding:10px 12px;color:#374151}
    pre{background:#0b1020;color:#e5e7eb;padding:12px 14px;border-radius:6px;overflow:auto}
    code{background:#f3f4f6;padding:2px 6px;border-radius:4px}
    table{width:100%;border-collapse:collapse;margin:10px 0}
    th,td{border:1px solid #e5e7eb;padding:8px 10px;text-align:left}
  </style>
</head>
<body>
  <h1>${escapeHtml(currentDocument.value.title || '')}</h1>
  ${currentDocument.value.description ? `<p>${escapeHtml(currentDocument.value.description)}</p>` : ''}
  <div>${currentDocument.value.content || ''}</div>
</body>
</html>`
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('HTML 导出成功')
  }

  // HTML 转义函数
  function escapeHtml(s: string) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }

  // 导出为 PDF（通过浏览器打印）
  const exportPdf = () => {
    if (!currentDocument.value) return
    const title = currentDocument.value.title || 'document'
    const html = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8" />
  <title>${escapeHtml(title)}</title>
  <style>
    @page { size: A4; margin: 14mm; }
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial; color:#111827;}
    h1,h2,h3{margin-top:18px}
    p{line-height:1.8;margin:10px 0}
    img{max-width:100%;height:auto;border-radius:4px}
    blockquote{border-left:4px solid #e5e7eb;background:#f9fafb;padding:10px 12px;color:#374151}
    pre{background:#0b1020;color:#e5e7eb;padding:12px 14px;border-radius:6px;overflow:auto}
    code{background:#f3f4f6;padding:2px 6px;border-radius:4px}
    table{width:100%;border-collapse:collapse;margin:10px 0}
    th,td{border:1px solid #e5e7eb;padding:8px 10px;text-align:left}
  </style></head><body>
  <h1>${escapeHtml(currentDocument.value.title || '')}</h1>
  ${currentDocument.value.description ? `<p>${escapeHtml(currentDocument.value.description)}</p>` : ''}
  <div>${currentDocument.value.content || ''}</div>
  <script>window.onload = function(){ setTimeout(function(){ window.print(); }, 300); }<\/script>
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

  // 加载用户、部门和角色选项
  const loadUsersAndDepts = async () => {
    try {
      console.log('🔍 [Collaboration] 当前登录用户:', {
        id: userStore.currentUser?.id,
        username: userStore.currentUser?.username,
        role: userStore.currentUser?.role
      })

      // 尝试加载用户列表（管理员有权限，其他角色可能会失败）
      try {
        await userStore.fetchUsers({ status: 'active', limit: 500 })
        console.log('✅ [Collaboration] 用户列表加载成功，数量:', userStore.users.length)
      } catch (error: any) {
        // 403 权限不足是正常的，非管理员没有权限访问用户列表
        if (error.message?.includes('Not authorized') || error.message?.includes('403')) {
          console.log(
            'ℹ️ [Collaboration] 当前用户无权限访问用户列表（正常），将使用文档数据中的用户名'
          )
        } else {
          console.warn('⚠️ [Collaboration] 加载用户列表失败:', error)
        }
      }

      // 从 userStore.users 构建选项（如果有权限的话）
      if (userStore.users.length > 0) {
        userOptions.value = userStore.users.map((u: any) => ({
          label: `${u.real_name || u.username} (${u.username})`,
          value: u.id,
          role: u.role // 添加角色信息，用于筛选
        }))

        // 获取所有唯一部门
        const depts = new Set<string>()
        userStore.users.forEach((u: any) => {
          if (u.department) depts.add(u.department)
        })
        deptOptions.value = Array.from(depts)
          .sort()
          .map((dept) => ({ label: dept, value: dept }))
      }

      // 获取角色列表（所有登录用户都可以访问）
      try {
        const roleRes: any = await roleApi.getRoles({ size: 9999 })
        const roleList: any[] = roleRes?.data?.list || roleRes?.data?.roles || []
        roleOptions.value = roleList.map((r) => ({
          label: r.name, // 中文显示名称
          value: r.role // 英文角色编码
        }))
        console.log('✅ [Collaboration] 角色列表加载成功，数量:', roleOptions.value.length)
      } catch (error: any) {
        console.error('❌ [Collaboration] 加载角色列表失败:', error)
        roleOptions.value = []
      }
    } catch (error) {
      console.error('加载数据失败:', error)
    }
  }

  // 页面关闭时解锁文档
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (isEditing.value && currentDocument.value) {
      console.log('⚠️ [Collaboration] 页面即将关闭，正在编辑，尝试解锁文档')
      // 使用 sendBeacon 发送异步请求，即使页面关闭也能完成
      const url = `/api/collaboration/documents/${currentDocument.value.id}/unlock`
      const token = userStore.accessToken

      if (navigator.sendBeacon) {
        // 使用 sendBeacon 发送解锁请求（更可靠）
        const blob = new Blob([JSON.stringify({})], { type: 'application/json' })
        navigator.sendBeacon(url, blob)
        console.log('✅ [Collaboration] 已通过 sendBeacon 发送解锁请求')
      } else {
        // 降级方案：同步 XHR
        try {
          const xhr = new XMLHttpRequest()
          xhr.open('POST', url, false) // 同步请求
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
          xhr.send()
          console.log('✅ [Collaboration] 已通过同步XHR发送解锁请求')
        } catch (error) {
          console.error('❌ [Collaboration] 解锁请求失败:', error)
        }
      }
    }
  }

  // 生命周期
  onMounted(async () => {
    // 先加载用户数据，确保 userStore.users 有数据
    await loadUsersAndDepts()
    // 再加载文档并构建树
    await loadDocuments()

    // 检查URL参数，如果有 articleId，自动跳转到该文档
    const articleIdFromUrl = route.query.articleId as string
    if (articleIdFromUrl && documents.value.length > 0) {
      const targetDoc = documents.value.find((d) => d.id === articleIdFromUrl)
      if (targetDoc) {
        currentDocId.value = targetDoc.id
        currentDocument.value = targetDoc
        ElMessage.success(`已定位到文档：${targetDoc.title}`)

        // 清除URL参数
        router.replace({ query: {} })
      }
    }

    // 添加全局点击事件，用于关闭右键菜单
    document.addEventListener('click', () => {
      if (contextMenuVisible.value) {
        contextMenuVisible.value = false
      }
    })

    // 监听页面关闭事件
    window.addEventListener('beforeunload', handleBeforeUnload)
  })

  // 当组件被激活时（从其他页面返回时）自动刷新
  onActivated(async () => {
    console.log('📄 [Collaboration] 页面激活，刷新文档列表')
    await loadUsersAndDepts() // 先加载用户数据
    await loadDocuments()
  })

  // 组件卸载时清理
  onBeforeUnmount(async () => {
    console.log('🧹 [Collaboration] 组件卸载，清理资源')

    // 如果正在编辑，尝试解锁
    if (isEditing.value && currentDocument.value) {
      try {
        console.log('🔓 [Collaboration] 组件卸载时解锁文档:', currentDocument.value.id)
        await collaborationApi.unlockDocument(currentDocument.value.id)
      } catch (error) {
        console.error('❌ [Collaboration] 组件卸载时解锁失败:', error)
      }
    }

    // 移除事件监听
    window.removeEventListener('beforeunload', handleBeforeUnload)
  })

  // 监听路由变化，支持动态跳转到文档
  watch(
    () => route.query.articleId,
    async (newArticleId) => {
      if (newArticleId && typeof newArticleId === 'string') {
        // 如果文档列表还没加载，先加载
        if (documents.value.length === 0) {
          await loadDocuments()
        }

        const targetDoc = documents.value.find((d) => d.id === newArticleId)
        if (targetDoc) {
          currentDocId.value = targetDoc.id
          currentDocument.value = targetDoc
          ElMessage.success(`已定位到文档：${targetDoc.title}`)

          // 清除URL参数
          router.replace({ query: {} })
        } else {
          ElMessage.warning('未找到指定的文档')
        }
      }
    }
  )

  // 监听路由路径变化，从编辑页返回时自动刷新
  watch(
    () => route.path,
    async (newPath, oldPath) => {
      // 如果从编辑页（/collaboration/document/:id）返回到列表页（/collaboration）
      if (oldPath && oldPath.includes('/collaboration/document/') && newPath === '/collaboration') {
        console.log('📄 [Collaboration] 从编辑页返回，刷新文档列表')
        await loadUsersAndDepts() // 先加载用户数据
        await loadDocuments()
      }
    }
  )
</script>

<style lang="scss" scoped>
  .collaboration-page {
    padding: 10px;
    background: var(--art-bg-color);
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .page-container {
      display: flex;
      flex-direction: column;
      flex: 1;
      min-height: 0;
      overflow: hidden;
      position: relative; /* 确保 z-index 生效 */
      z-index: 1; /* 设置较低的 z-index，确保抽屉遮罩层能覆盖 */
    }

    .page-body {
      flex: 1;
      overflow: hidden;
      gap: 16px;
    }

    /* 左侧导航栏 */
    .sidebar {
      width: 280px;
      padding: 0;
      background: transparent;
      display: flex;
      flex-direction: column;
    }

    .nav-panel {
      flex: 0.93;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 16px;
      background: var(--art-main-bg-color);
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

      .filter-section {
        margin-bottom: 20px;

        .filter-search {
          margin-bottom: 16px;

          :deep(.el-input) {
            .el-input__wrapper {
              border-radius: 10px;
              padding: 8px 12px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
              transition: all 0.3s ease;
              background: var(--art-main-bg-color);

              &:hover {
                box-shadow: 0 2px 12px rgba(59, 130, 246, 0.15);
              }

              &.is-focus {
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
              }
            }

            .el-input__inner {
              font-size: 14px;
              color: var(--art-text-gray-800);

              &::placeholder {
                color: var(--art-text-gray-400);
                font-weight: 400;
              }
            }
          }
        }

        .filter-controls {
          display: flex;
          flex-direction: column;
          gap: 0;
          background: var(--art-main-bg-color);
          border-radius: 10px;
          padding: 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

          .filter-item {
            padding: 12px 12px;
            border-radius: 8px;
            transition: background 0.2s ease;

            &:hover {
              background: var(--art-bg-color);
            }

            &.switch-item {
              display: flex;
              align-items: center;
              justify-content: space-between;

              .filter-item-content {
                display: flex;
                align-items: center;
                gap: 10px;
                flex: 1;

                .filter-icon {
                  font-size: 16px;
                  color: #3b82f6;
                }

                .filter-label {
                  font-size: 14px;
                  font-weight: 500;
                  color: var(--art-text-gray-700);
                }
              }

              :deep(.el-switch) {
                --el-switch-on-color: #3b82f6;
                --el-switch-off-color: #d1d5db;
              }
            }

            &.select-item {
              display: flex;
              flex-direction: column;
              gap: 10px;

              .filter-item-header {
                display: flex;
                align-items: center;
                gap: 10px;

                .filter-icon {
                  font-size: 16px;
                  color: #3b82f6;
                }

                .filter-label {
                  font-size: 14px;
                  font-weight: 500;
                  color: var(--art-text-gray-700);
                }
              }

              :deep(.el-select) {
                width: 100%;

                .el-select__wrapper {
                  border-radius: 8px;
                  padding: 6px 12px;
                  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
                  transition: all 0.2s ease;
                  background: var(--art-bg-color);
                  border: 1px solid transparent;

                  &:hover {
                    border-color: #3b82f6;
                    box-shadow: 0 1px 6px rgba(59, 130, 246, 0.15);
                  }

                  &.is-focused {
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
                  }
                }

                .el-select__placeholder {
                  color: var(--art-text-gray-400);
                  font-size: 13px;
                }

                .el-select__tags-text {
                  font-size: 13px;
                  color: var(--art-text-gray-700);
                }

                .el-tag {
                  background: #dbeafe;
                  border-color: #bfdbfe;
                  color: #1e40af;
                  border-radius: 6px;
                  padding: 0 8px;
                  height: 24px;
                  line-height: 22px;
                  font-size: 12px;
                }
              }
            }
          }

          .filter-divider {
            height: 1px;
            background: linear-gradient(
              90deg,
              transparent 0%,
              var(--art-border-color) 20%,
              var(--art-border-color) 80%,
              transparent 100%
            );
            margin: 4px 8px;
          }
        }

        // 下拉选项样式
        .user-option {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 4px 0;

          .el-icon {
            font-size: 14px;
            color: #6b7280;
          }

          span {
            font-size: 14px;
            color: var(--art-text-gray-700);
          }
        }
      }

      .stats-mini {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid #f3f4f6;

        .stat-item {
          flex: 1;
          padding: 12px 8px;
          background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
          border-radius: 10px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          border: 1px solid #93c5fd;

          .stat-label {
            font-size: 11px;
            color: #1e40af;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .stat-value {
            font-size: 22px;
            font-weight: 700;
            color: #2563eb;

            &.active {
              color: #3b82f6;
            }
          }
        }
      }
    }

    /* 美化滚动条 */
    .nav-panel::-webkit-scrollbar {
      width: 6px;
    }

    .nav-panel::-webkit-scrollbar-track {
      background: transparent;
      border-radius: 3px;
    }

    .nav-panel::-webkit-scrollbar-thumb {
      background: var(--art-gray-400);
      border-radius: 3px;
    }

    .nav-panel::-webkit-scrollbar-thumb:hover {
      background: var(--art-gray-500);
    }

    // 导航树节点通用样式（与会议记录保持一致）
    .tree-node {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 8px;

      .node-icon {
        font-size: 14px;
        color: var(--art-text-gray-600);
        transition: all 0.2s;
      }

      .node-label {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 13px;
        color: var(--art-text-gray-900);
        text-align: left;
        min-width: 0;
      }
    }

    .tree-group {
      font-weight: 600;
      color: var(--art-text-gray-800);
      user-select: none;
    }

    .tree-leaf {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      gap: 8px;

      .leaf-title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
        min-width: 0;
      }

      .leaf-tag {
        flex-shrink: 0;
        margin-left: auto;
      }
    }

    // Element Plus Tree 节点样式
    :deep(.el-tree-node) {
      margin-bottom: 4px;
    }

    :deep(.el-tree-node__content) {
      height: auto;
      min-height: 36px;
      padding: 4px 8px !important;
      border-radius: 8px;
      transition: all 0.2s ease;

      &:hover {
        background: var(--art-bg-color);
      }
    }

    // 选中状态样式 - 与会议记录保持一致（使用蓝色主题）
    :deep(.el-tree-node.is-current > .el-tree-node__content) {
      background: rgba(59, 130, 246, 0.1) !important;
      border-left: 3px solid #3b82f6 !important;
      padding-left: 5px !important;
      box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
      font-weight: 600;

      .tree-node {
        color: #3b82f6;

        .node-icon {
          color: #3b82f6;
          transform: scale(1.1);
        }

        .node-label {
          color: #3b82f6;
          font-weight: 600;
        }
      }

      .tree-leaf {
        .leaf-title {
          color: #3b82f6 !important;
          font-weight: 600;
        }

        .leaf-tag {
          font-weight: 600;
        }
      }
    }

    :deep(.el-tree-node__expand-icon) {
      font-size: 14px;
      color: var(--art-text-gray-600);
      margin-right: 4px;

      &.is-leaf {
        color: transparent;
      }
    }

    // 调整缩进大小（与会议记录保持一致）
    :deep(.el-tree-node__children) {
      .el-tree-node__content {
        padding-left: 18px !important;
      }
    }

    /* 右侧主内容区 */
    .main-col {
      flex: 1;
      min-width: 0;
      min-height: 0;
      padding: 0;
      background: transparent;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .document-detail-wrapper {
        flex: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        min-height: 0;
      }

      :deep(.el-empty) {
        padding: 80px 0;

        .el-empty__description {
          font-size: 15px;
          color: var(--art-text-gray-600);
        }
      }
    }

    .document-card {
      flex: 0.93;
      display: flex;
      flex-direction: column;
      min-height: 0;
      background: var(--art-main-bg-color);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      border: 1px solid var(--art-card-border);

      :deep(.el-card__header) {
        padding: 18px 24px;
        border-bottom: 1px solid var(--art-card-border);
        background: var(--art-main-bg-color);
      }

      :deep(.el-card__body) {
        flex: 1;
        overflow: hidden;
        padding: 0;
        display: flex;
        flex-direction: column;
      }

      .document-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;

        .header-left {
          flex: 1;
          min-width: 0;

          .header-info {
            h3 {
              margin: 0 0 8px 0;
              color: var(--art-text-gray-900);
              font-size: 19px;
              font-weight: 600;
              line-height: 1.4;
              letter-spacing: 0.3px;
            }

            .meta-info {
              color: var(--art-text-gray-600);
              font-size: 14px;
              display: flex;
              align-items: center;
              flex-wrap: wrap;
              gap: 8px;

              .meta-text {
                display: flex;
                align-items: center;
                gap: 4px;
              }

              :deep(.el-tag) {
                border-radius: 6px;
                padding: 0 10px;
                height: 24px;
                line-height: 24px;
              }

              // 协作者标签样式
              .collaborators-inline {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 8px;
                flex-wrap: wrap;

                .collaborators-label {
                  display: flex;
                  align-items: center;
                  gap: 4px;
                  color: var(--art-text-gray-600);
                  font-size: 13px;
                  font-weight: 500;
                }

                .collaborator-tag-inline {
                  display: inline-flex;
                  align-items: center;
                  gap: 4px;
                  border-radius: 12px;
                  padding: 2px 10px;
                  font-size: 12px;
                  transition: all 0.3s ease;

                  .editing-icon {
                    animation: pulse 1.5s ease-in-out infinite;
                  }

                  .editing-text {
                    margin-left: 2px;
                    font-size: 11px;
                    opacity: 0.9;
                  }
                }

                // 正在编辑的标签（绿色）
                :deep(.el-tag--success.el-tag--dark) {
                  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                  border-color: #10b981;
                  color: white;
                  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);

                  .editing-icon {
                    color: white;
                  }
                }
              }
            }
          }
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-shrink: 0;

          :deep(.el-button) {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;

            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
          }
        }
      }

      .document-content {
        padding: 24px;
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        display: flex;
        flex-direction: column;

        // 自定义滚动条
        &::-webkit-scrollbar {
          width: 8px;
        }
        &::-webkit-scrollbar-track {
          background: var(--art-bg-color);
          border-radius: 4px;
        }
        &::-webkit-scrollbar-thumb {
          background: var(--art-gray-400);
          border-radius: 4px;

          &:hover {
            background: var(--art-gray-500);
          }
        }

        h4 {
          margin: 0 0 12px 0;
          color: var(--art-text-gray-800);
          font-size: 15px;
          font-weight: 600;
        }

        .document-description {
          margin-bottom: 24px;
          padding: 16px;
          background: var(--art-bg-color);
          border-radius: 8px;
          border-left: 3px solid #3b82f6;

          p {
            margin: 0;
            color: #4b5563;
            line-height: 1.6;
          }
        }

        .document-body {
          flex: 1;
          min-height: 0;
          display: flex;
          flex-direction: column;
          overflow: hidden;

          // 确保预览组件占据所有可用空间
          :deep(.art-wang-preview) {
            flex: 1;
            overflow: auto;
          }

          .content-html {
            padding: 16px;
            background: var(--art-main-bg-color);
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            min-height: 200px;
            line-height: 1.8;
            color: var(--art-text-gray-800);

            :deep(img) {
              max-width: 100%;
              height: auto;
            }

            :deep(table) {
              border-collapse: collapse;
              width: 100%;
              margin: 16px 0;

              th,
              td {
                border: 1px solid #e5e7eb;
                padding: 8px 12px;
              }

              th {
                background: var(--art-bg-color);
                font-weight: 600;
              }
            }
          }
        }

        .document-collaborators {
          margin-bottom: 24px;

          .collaborators-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;

            .collaborator-tag {
              display: flex;
              align-items: center;
              padding: 6px 12px;
              border-radius: 8px;

              .collaborator-role {
                margin-left: 4px;
                font-size: 12px;
                color: var(--art-text-gray-600);
              }
            }
          }
        }

        .document-tags {
          .tags-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;

            :deep(.el-tag) {
              border-radius: 6px;
            }
          }
        }

        // 编辑模式的编辑器样式
        .content-editor {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: var(--art-main-bg-color);
          min-height: 600px;
          height: calc(100vh - 300px);
          overflow: hidden;

          :deep(.w-e-toolbar) {
            flex-shrink: 0;
            position: sticky;
            top: 0;
            z-index: 10;
            background: var(--art-main-bg-color);
            border-bottom: 1px solid var(--art-card-border);
          }

          :deep(.w-e-text-container) {
            flex: 1;
            overflow-y: auto !important;
            overflow-x: hidden !important;

            [data-slate-editor] {
              min-height: 100%;
            }

            // 自定义编辑器内部滚动条
            &::-webkit-scrollbar {
              width: 8px;
            }
            &::-webkit-scrollbar-track {
              background: var(--art-bg-color);
              border-radius: 4px;
            }
            &::-webkit-scrollbar-thumb {
              background: var(--art-gray-400);
              border-radius: 4px;

              &:hover {
                background: var(--art-gray-500);
              }
            }
          }
        }

        // 当存在编辑器时，禁用document-content的滚动并去除padding
        &:has(.content-editor.editing-active) {
          padding: 0;
          overflow: hidden;
        }
      }
    }
  }

  // 元数据编辑对话框样式
  .meta-dialog {
    :deep(.el-dialog__header) {
      padding: 0;
      margin: 0;
      border-bottom: 1px solid #e5e7eb;
    }

    .dialog-header {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      padding: 24px 24px 20px 24px;

      .dialog-icon {
        flex-shrink: 0;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);

        .el-icon {
          font-size: 24px;
          color: white;
        }
      }

      .dialog-title {
        flex: 1;

        h3 {
          margin: 0 0 6px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          letter-spacing: 0.3px;
        }

        p {
          margin: 0;
          font-size: 13px;
          color: var(--art-text-gray-600);
          line-height: 1.5;
        }
      }
    }

    :deep(.el-dialog__body) {
      padding: 28px 24px;
    }

    .meta-form {
      :deep(.el-form-item) {
        margin-bottom: 24px;

        &:last-child {
          margin-bottom: 0;
        }
      }

      :deep(.el-form-item__label) {
        font-weight: 600;
        color: #374151;
        font-size: 14px;
        line-height: 32px;
      }

      :deep(.el-input__wrapper) {
        box-shadow: 0 0 0 1px #d1d5db inset;
        transition: all 0.2s;

        &:hover {
          box-shadow: 0 0 0 1px #9ca3af inset;
        }

        &.is-focus {
          box-shadow: 0 0 0 1px #3b82f6 inset;
        }
      }

      :deep(.el-textarea__inner) {
        box-shadow: 0 0 0 1px #d1d5db inset;
        transition: all 0.2s;

        &:hover {
          box-shadow: 0 0 0 1px #9ca3af inset;
        }

        &:focus {
          box-shadow: 0 0 0 1px #3b82f6 inset;
        }
      }

      // 状态选择器样式
      .status-option {
        display: flex;
        align-items: center;
        gap: 8px;

        .emoji {
          font-size: 16px;
        }
      }

      // 优先级按钮组样式
      .priority-group {
        display: flex;
        width: 100%;

        :deep(.el-radio-button) {
          flex: 1;

          .el-radio-button__inner {
            width: 100%;
            border-radius: 0;

            &:hover {
              color: #3b82f6;
            }
          }

          &:first-child .el-radio-button__inner {
            border-radius: 8px 0 0 8px;
          }

          &:last-child .el-radio-button__inner {
            border-radius: 0 8px 8px 0;
          }

          &.is-active .el-radio-button__inner {
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            border-color: #3b82f6;
            color: white;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
          }
        }

        .priority-option {
          font-weight: 500;

          &.low {
            color: #6b7280;
          }
          &.normal {
            color: #3b82f6;
          }
          &.high {
            color: #f59e0b;
          }
          &.urgent {
            color: #ef4444;
          }
        }
      }

      // 标签选择器样式
      .tags-select {
        width: 100%;

        :deep(.el-select__tags) {
          max-height: 120px;
          overflow-y: auto;
        }
      }
    }

    :deep(.el-dialog__footer) {
      padding: 16px 24px 24px 24px;
      border-top: 1px solid #e5e7eb;
    }

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .el-button {
        min-width: 100px;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.2s;

        &:not(.save-btn) {
          border-color: #d1d5db;
          color: var(--art-text-gray-600);

          &:hover {
            border-color: #9ca3af;
            color: var(--art-text-gray-800);
            background: var(--art-bg-color);
          }
        }
      }

      .save-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

        &:hover {
          box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
          transform: translateY(-1px);
        }

        &:active {
          transform: translateY(0);
        }

        .el-icon {
          margin-right: 4px;
        }
      }
    }
  }

  // 创建对话框样式优化
  .create-dialog {
    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .el-button {
        min-width: 100px;
        font-weight: 500;
        border-radius: 8px;
      }
    }
  }

  // 右键菜单样式
  .context-menu {
    position: fixed;
    z-index: 1999; /* 低于 el-drawer 的遮罩层 (2000) */
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    min-width: 180px;
    border: 1px solid #e4e7ed;

    .menu-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px 16px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
      color: #303133;
      white-space: nowrap;

      .el-icon {
        font-size: 16px;
        color: #606266;
      }

      &:hover {
        background: #f5f7fa;
        color: #409eff;

        .el-icon {
          color: #409eff;
        }
      }

      &:active {
        background: #e6f7ff;
      }
    }
  }

  // 脉冲动画（正在编辑的图标）
  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.6;
      transform: scale(0.95);
    }
  }

  // 文档信息抽屉样式
  .drawer-content {
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;

    // 文档元信息区域
    .document-meta-section {
      .meta-card {
        border: 1px solid var(--el-border-color-lighter) !important;
        border-radius: 8px;
        overflow: hidden;

        :deep(.el-card__header) {
          padding: 16px 20px;
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          border-bottom: none;

          .meta-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            font-weight: 600;
            font-size: 15px;

            .el-icon {
              font-size: 18px;
              color: white;
            }
          }
        }

        :deep(.el-card__body) {
          padding: 0;
        }

        .meta-content {
          padding: 20px;

          .meta-item {
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid var(--el-border-color-lighter);

            &:last-child {
              border-bottom: none;
            }

            .meta-label {
              display: flex;
              align-items: center;
              gap: 6px;
              min-width: 100px;
              color: var(--art-text-gray-600);
              font-size: 14px;
              font-weight: 500;

              .el-icon {
                font-size: 16px;
                color: var(--el-color-primary);
              }
            }

            .meta-value {
              flex: 1;
              color: var(--art-text-gray-900);
              font-size: 14px;
              display: flex;
              flex-wrap: wrap;
              align-items: center;
              gap: 6px;

              .meta-tag {
                margin-right: 8px;
                margin-bottom: 8px;
              }

              .empty-text {
                color: var(--art-text-gray-500);
                font-size: 13px;
                font-style: italic;
              }
            }

            &.summary-item {
              flex-direction: column;

              .meta-label {
                margin-bottom: 8px;
              }

              .summary-text {
                padding: 12px;
                background: var(--el-fill-color-lighter);
                border-radius: 6px;
                color: var(--art-text-gray-700);
                line-height: 1.6;
                white-space: pre-wrap;
                word-break: break-word;
              }
            }
          }
        }
      }
    }
  }

  // ===== 暗色模式适配 =====
  html.dark {
    .collaboration-page {
      .nav-panel {
        .filter-section {
          // 搜索框暗色模式
          .filter-search {
            :deep(.el-input) {
              .el-input__wrapper {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);

                &:hover {
                  box-shadow: 0 2px 12px rgba(96, 165, 250, 0.2);
                  border-color: rgba(96, 165, 250, 0.3);
                }

                &.is-focus {
                  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.3);
                  border-color: #60a5fa;
                }
              }

              .el-input__inner {
                color: #e5e7eb;

                &::placeholder {
                  color: #9ca3af;
                }
              }

              .el-input__prefix {
                color: #9ca3af;
              }
            }
          }

          // 筛选控件组暗色模式
          .filter-controls {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);

            .filter-item {
              &:hover {
                background: rgba(255, 255, 255, 0.08);
              }

              // 开关项暗色模式
              &.switch-item {
                .filter-item-content {
                  .filter-icon {
                    color: #60a5fa;
                  }

                  .filter-label {
                    color: #e5e7eb;
                    font-weight: 500;
                  }
                }

                :deep(.el-switch) {
                  --el-switch-on-color: #60a5fa;
                  --el-switch-off-color: #4b5563;
                }
              }

              // 下拉项暗色模式
              &.select-item {
                .filter-item-header {
                  .filter-icon {
                    color: #60a5fa;
                  }

                  .filter-label {
                    color: #e5e7eb;
                    font-weight: 500;
                  }
                }

                :deep(.el-select) {
                  .el-select__wrapper {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);

                    &:hover {
                      border-color: #60a5fa;
                      box-shadow: 0 1px 6px rgba(96, 165, 250, 0.2);
                    }

                    &.is-focused {
                      border-color: #60a5fa;
                      box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
                    }
                  }

                  .el-select__placeholder {
                    color: #9ca3af;
                  }

                  .el-select__input {
                    color: #e5e7eb;
                  }

                  .el-select__selected-item {
                    color: #e5e7eb;
                  }

                  .el-tag {
                    background: rgba(96, 165, 250, 0.2);
                    border-color: rgba(96, 165, 250, 0.3);
                    color: #93c5fd;

                    .el-tag__close {
                      color: #93c5fd;

                      &:hover {
                        background: rgba(96, 165, 250, 0.3);
                        color: #bfdbfe;
                      }
                    }
                  }
                }
              }
            }

            // 分隔线暗色模式
            .filter-divider {
              background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255, 255, 255, 0.1) 20%,
                rgba(255, 255, 255, 0.1) 80%,
                transparent 100%
              );
            }
          }

          // 下拉选项暗色模式
          .user-option {
            .el-icon {
              color: #9ca3af;
            }

            span {
              color: #e5e7eb;
            }
          }
        }
      }
    }
  }

  /* 导入对话框样式 */
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
</style>
