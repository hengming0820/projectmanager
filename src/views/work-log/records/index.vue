<template>
  <div class="work-records-page">
    <el-container class="page-container">
      <!-- 顶部标题栏 -->
      <el-header height="auto" class="page-header-wrapper">
        <ArtPageHeader
          title="工作记录"
          description="记录日常工作进展与总结"
          icon="📝"
          badge="Work Records"
          theme="purple"
        >
          <template #actions>
            <el-button v-if="canManageArticles" @click="showBatchManageDialog = true">
              <el-icon><Setting /></el-icon>
              批量管理
            </el-button>
            <el-button @click="goCreatePage" type="primary">
              <el-icon><Plus /></el-icon>
              发布工作记录
            </el-button>
            <el-button @click="loadArticles">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </template>
        </ArtPageHeader>
      </el-header>

      <!-- 左右布局 -->
      <el-container class="page-body">
        <!-- 左侧导航 -->
        <el-aside width="320px" class="sidebar">
          <div class="nav-panel">
            <div class="filter-section">
              <el-input
                v-model="filterSearch"
                placeholder="搜索工作记录..."
                :prefix-icon="Search"
                clearable
              />
            </div>

            <!-- 导航栏操作按钮 -->
            <div class="nav-actions">
              <el-button
                v-if="canManageArticles"
                @click="showBatchManageDialog = true"
                size="small"
                style="flex: 1"
              >
                <el-icon><Setting /></el-icon>
                批量管理
              </el-button>
              <el-button @click="goCreatePage" type="primary" size="small" style="flex: 1">
                <el-icon><Plus /></el-icon>
                新建
              </el-button>
            </div>

            <el-tree
              ref="treeRef"
              :data="treeData"
              :props="{ label: 'label', children: 'children' }"
              :indent="8"
              :filter-node-method="filterNode"
              :expand-on-click-node="true"
              :default-expanded-keys="expandedKeys"
              :current-node-key="currentArticleId"
              highlight-current
              node-key="key"
              @node-click="onNodeClick"
            >
              <template #default="{ node, data }">
                <div
                  :class="[
                    'tree-node',
                    data.isLeaf ? 'tree-leaf' : 'tree-group',
                    { active: data.key === currentArticleId, 'user-node': data.isUser }
                  ]"
                >
                  <!-- 用户颜色指示器 -->
                  <span
                    v-if="data.isUser"
                    class="user-color-dot"
                    :style="{ backgroundColor: data.color }"
                  ></span>

                  <!-- 文章图标 -->
                  <el-icon v-if="data.isLeaf" class="node-icon">
                    <Document />
                  </el-icon>

                  <el-tooltip
                    v-if="data.isLeaf"
                    :content="data.label"
                    placement="right"
                    :disabled="data.label.length <= 18"
                    :show-after="300"
                  >
                    <span class="node-label">{{ truncateLabel(data.label, 18) }}</span>
                  </el-tooltip>
                  <span v-else class="node-label">{{ data.label }}</span>
                </div>
              </template>
            </el-tree>
          </div>
        </el-aside>

        <!-- 右侧主内容 -->
        <el-main class="main-col">
          <!-- 文章详情 -->
          <div v-if="currentArticle" class="article-detail-wrapper">
            <el-card class="article-card" shadow="never">
              <template #header>
                <div class="article-header">
                  <div class="header-left">
                    <div class="header-info">
                      <h3>{{ currentArticle.title }}</h3>
                      <span class="meta-info">
                        <el-tag
                          v-if="currentArticle.category"
                          size="small"
                          :color="getCategoryColor(currentArticle.category)"
                          effect="light"
                        >
                          {{ currentArticle.category }}
                        </el-tag>
                        <span class="author-info">
                          <el-icon><User /></el-icon>
                          {{ currentArticle.author_name }}
                        </span>
                        <span class="date-info">
                          <el-icon><Clock /></el-icon>
                          {{ formatDate(currentArticle.updated_at) }}
                        </span>
                        <span class="view-info">
                          <el-icon><View /></el-icon>
                          {{ currentArticle.view_count || 0 }} 次浏览
                        </span>
                      </span>
                    </div>
                  </div>
                  <div class="header-right">
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
                      <el-button v-if="canEditArticle(currentArticle)" @click="startEdit">
                        <el-icon><Document /></el-icon>
                        编辑内容
                      </el-button>
                      <el-button
                        v-if="canDeleteArticle(currentArticle)"
                        @click="handleDeleteArticle(currentArticle.id)"
                        type="danger"
                      >
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </template>
                    <template v-else>
                      <el-button @click="openImportMarkdown">
                        <el-icon><Upload /></el-icon>
                        导入 Markdown
                      </el-button>
                      <el-button @click="cancelEdit">取消</el-button>
                      <el-button type="primary" @click="saveEdit" :loading="saving"
                        >保存内容</el-button
                      >
                    </template>
                  </div>
                </div>
              </template>

              <div class="article-content" :class="{ 'editor-active': isEditing }">
                <!-- 查看模式 -->
                <template v-if="!isEditing">
                  <ArtXnotePreview :content="currentArticle.content" height="100%" />
                </template>

                <!-- 编辑模式（使用编辑器默认工具栏，不再启用顶部静态工具栏） -->
                <template v-else>
                  <div class="content-editor" :class="{ 'editing-active': isEditing }">
                    <ArtTextbusEditor
                      v-model="editForm.content"
                      height="100%"
                    />
                  </div>
                </template>
              </div>
            </el-card>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <el-empty description="请从左侧选择一条工作记录">
              <el-button type="primary" @click="goCreatePage">
                <el-icon><Plus /></el-icon>
                发布第一条工作记录
              </el-button>
            </el-empty>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 导入 Markdown 对话框（保持与发布文章页面一致） -->
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

    <!-- 批量管理对话框 -->
    <el-dialog
      v-model="showBatchManageDialog"
      title="批量管理工作记录"
      width="850px"
      :close-on-click-modal="false"
    >
      <div class="batch-manage-container">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px">
          <template #title>
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon><InfoFilled /></el-icon>
              批量管理说明
            </span>
          </template>
          <div style="font-size: 13px; color: #606266">
            <p style="margin: 0 0 8px 0">• 可以按部门、分类、关键词筛选工作记录</p>
            <p style="margin: 0">• 只有管理员和审核员可以批量删除工作记录</p>
          </div>
        </el-alert>

        <!-- 筛选器 -->
        <div class="batch-filters">
          <el-input
            v-model="batchSearchText"
            placeholder="搜索标题..."
            clearable
            style="width: 200px"
          >
            <template #prefix
              ><el-icon><Search /></el-icon
            ></template>
          </el-input>

          <el-select
            v-model="batchDeptFilter"
            placeholder="选择部门"
            clearable
            style="width: 150px"
          >
            <el-option v-for="dept in allDepartments" :key="dept" :label="dept" :value="dept" />
          </el-select>

          <el-select
            v-model="batchCategoryFilter"
            placeholder="选择分类"
            clearable
            style="width: 150px"
          >
            <el-option label="日常记录" value="日常记录" />
            <el-option label="问题修复" value="问题修复" />
            <el-option label="功能开发" value="功能开发" />
            <el-option label="会议纪要" value="会议纪要" />
          </el-select>

          <el-button @click="clearBatchFilters">清空筛选</el-button>
        </div>

        <!-- 文章列表 -->
        <div class="batch-article-list">
          <div
            style="
              margin: 16px 0;
              display: flex;
              justify-content: space-between;
              align-items: center;
            "
          >
            <el-checkbox v-model="selectAllArticles" @change="handleSelectAllArticles">
              全选 ({{ filteredArticlesForBatch.length }} 条记录)
            </el-checkbox>
            <span style="color: #909399; font-size: 13px">
              已选中 {{ selectedArticleIds.length }} 条记录
            </span>
          </div>

          <div class="batch-article-list-container">
            <div
              v-for="article in filteredArticlesForBatch"
              :key="article.id"
              class="batch-article-item"
              :class="{ selected: selectedArticleIds.includes(article.id) }"
              @click="toggleArticleSelection(article.id)"
            >
              <el-checkbox
                :model-value="selectedArticleIds.includes(article.id)"
                @click.stop
                @change="toggleArticleSelection(article.id)"
                class="article-checkbox"
              />
              <div class="article-info">
                <div class="article-title-row">
                  <span class="article-title">{{ article.title }}</span>
                  <el-tag size="small" v-if="article.category" class="category-tag">{{
                    article.category
                  }}</el-tag>
                </div>
                <div class="article-meta">
                  <span class="meta-item">
                    <el-icon><User /></el-icon>
                    {{ article.author_name }}
                  </span>
                  <span class="meta-item">
                    <el-icon><OfficeBuilding /></el-icon>
                    {{ article.departments?.join(', ') || '-' }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ formatCompactDate(article.created_at) }}
                  </span>
                </div>
              </div>
            </div>

            <div v-if="filteredArticlesForBatch.length === 0" class="empty-state">
              <el-icon size="48"><Document /></el-icon>
              <p style="margin-top: 12px">暂无符合条件的工作记录</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div style="display: flex; justify-content: space-between">
          <el-button @click="showBatchManageDialog = false">取消</el-button>
          <div style="display: flex; gap: 12px">
            <el-button
              type="danger"
              :disabled="selectedArticleIds.length === 0"
              :loading="batchDeleting"
              @click="batchDeleteArticles"
            >
              删除选中 ({{ selectedArticleIds.length }})
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, watch, nextTick } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Plus,
    Refresh,
    Search,
    Edit,
    Delete,
    User,
    Clock,
    View,
    OfficeBuilding,
    Document,
    Upload,
    UploadFilled,
    Setting,
    InfoFilled,
    Download,
    ArrowDown,
    Printer
  } from '@element-plus/icons-vue'
  import { useUserStore } from '@/store/modules/user'
  import { articlesApi, type Article } from '@/api/articlesApi'
  import { userApi } from '@/api/userApi'
  import ArtTextbusEditor from '@/components/core/forms/art-textbus-editor/index.vue'
  import ArtXnotePreview from '@/components/core/forms/art-xnote-preview/index.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import { markdownToHtml, validateMarkdownFile, readMarkdownFile } from '@/utils/markdown'

  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()

  // 状态
  const loading = ref(false)
  const articles = ref<Article[]>([])
  const treeData = ref<any[]>([])
  const expandedKeys = ref<string[]>([])
  const filterSearch = ref('')
  const currentArticleId = ref('')
  const currentArticle = ref<Article | null>(null)
  const treeRef = ref()
  const users = ref<any[]>([])

  // 编辑模式相关
  const isEditing = ref(false)
  const saving = ref(false)
  const editForm = ref({
    content: ''
  })

  // Markdown 导入相关
  const showMdDialog = ref(false)
  const mdFileName = ref('')

  // 批量管理相关
  const showBatchManageDialog = ref(false)
  const selectedArticleIds = ref<string[]>([])
  const selectAllArticles = ref(false)
  const batchSearchText = ref('')
  const batchDeptFilter = ref('')
  const batchCategoryFilter = ref('')
  const batchDeleting = ref(false)

  // 加载用户列表
  const loadUsers = async () => {
    try {
      const response = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      users.value = response.data?.users || response.users || []
      console.log('✅ 用户列表加载成功:', users.value.length, '个用户')
    } catch (error) {
      console.error('加载用户列表失败:', error)
    }
  }

  // 加载文章列表
  const loadArticles = async () => {
    loading.value = true
    try {
      const response = await articlesApi.list({
        page: 1,
        page_size: 200,
        type: 'work_record',
        status: 'published'
      })
      articles.value = (response.items || []).sort(
        (a: Article, b: Article) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      buildTree()
    } catch (error) {
      console.error('加载工作记录失败:', error)
      ElMessage.error('加载工作记录失败')
    } finally {
      loading.value = false
    }
  }

  // 为不同用户生成不同颜色
  const userColors = [
    '#667eea', // 紫色
    '#f093fb', // 粉色
    '#4facfe', // 蓝色
    '#43e97b', // 绿色
    '#fa709a', // 玫红
    '#feca57', // 黄色
    '#48dbfb', // 青色
    '#ff6348', // 橙红
    '#1dd1a1', // 青绿
    '#5f27cd', // 深紫
    '#00d2d3', // 青蓝
    '#ff9ff3' // 淡粉
  ]

  const getUserColor = (authorId: string) => {
    // 使用authorId的哈希值来确定颜色
    const hash = authorId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    return userColors[hash % userColors.length]
  }

  // 构建树形结构：部门 → 员工 → 月份 → 日期 → 文章
  const buildTree = () => {
    const tree: any[] = []

    // 按部门分组
    const articlesByDept: Record<string, Article[]> = {}
    articles.value.forEach((article) => {
      const dept = article.departments?.[0] || '未分类'
      if (!articlesByDept[dept]) {
        articlesByDept[dept] = []
      }
      articlesByDept[dept].push(article)
    })

    // 获取所有部门
    const departments = Object.keys(articlesByDept).sort()

    departments.forEach((dept) => {
      const deptArticles = articlesByDept[dept]

      // 按作者分组
      const articlesByAuthor: Record<string, Article[]> = {}
      deptArticles.forEach((article) => {
        const authorId = article.author_id
        if (!articlesByAuthor[authorId]) {
          articlesByAuthor[authorId] = []
        }
        articlesByAuthor[authorId].push(article)
      })

      // 构建员工节点
      const userNodes = Object.entries(articlesByAuthor).map(([authorId, userArticles]) => {
        const user = users.value.find((u) => u.id === authorId)
        const userName =
          user?.real_name || user?.username || userArticles[0]?.author_name || '未知用户'
        console.log('👤 用户映射:', { authorId, user, userName, allUsers: users.value.length })

        // 按月份分组
        const articlesByMonth: Record<string, Article[]> = {}
        userArticles.forEach((article) => {
          const date = new Date(article.created_at)
          const monthKey = `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月`
          if (!articlesByMonth[monthKey]) {
            articlesByMonth[monthKey] = []
          }
          articlesByMonth[monthKey].push(article)
        })

        // 构建月份节点
        const monthNodes = Object.entries(articlesByMonth)
          .sort(([a], [b]) => b.localeCompare(a))
          .map(([month, monthArticles]) => {
            // 按日期分组
            const articlesByDate: Record<string, Article[]> = {}
            monthArticles.forEach((article) => {
              const date = new Date(article.created_at)
              const dateKey = `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`
              if (!articlesByDate[dateKey]) {
                articlesByDate[dateKey] = []
              }
              articlesByDate[dateKey].push(article)
            })

            // 构建日期节点
            const dateNodes = Object.entries(articlesByDate)
              .sort(([a], [b]) => b.localeCompare(a)) // yyyy/mm/dd格式直接字符串比较
              .map(([dateStr, dateArticles]) => ({
                key: `date-${dept}-${authorId}-${month}-${dateStr}`,
                label: dateStr,
                isLeaf: false,
                children: dateArticles
                  .sort(
                    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                  )
                  .map((article) => ({
                    key: article.id,
                    label: article.title,
                    category: article.category,
                    isLeaf: true,
                    article: article
                  }))
              }))

            return {
              key: `month-${dept}-${authorId}-${month}`,
              label: month,
              isLeaf: false,
              children: dateNodes
            }
          })

        return {
          key: `user-${dept}-${authorId}`,
          label: userName,
          isLeaf: false,
          isUser: true, // 标记为用户节点
          color: getUserColor(authorId), // 分配颜色
          children: monthNodes
        }
      })

      tree.push({
        key: `dept-${dept}`,
        label: dept,
        isLeaf: false,
        children: userNodes
      })
    })

    treeData.value = tree

    // 如果还没有选中文章，自动定位到当前用户的最新日志
    if (!currentArticle.value && tree.length > 0) {
      autoSelectLatestUserArticle()
    } else {
      // 默认展开第一级
      if (tree.length > 0 && expandedKeys.value.length === 0) {
        expandedKeys.value = tree.slice(0, 2).map((node) => node.key)
      }
    }
  }

  // 自动选择当前用户的最新日志
  const autoSelectLatestUserArticle = () => {
    const currentUserId = userStore.info?.id
    if (!currentUserId) return

    // 找到当前用户的所有文章
    const userArticles = articles.value.filter((article) => article.author_id === currentUserId)
    if (userArticles.length === 0) return

    // 获取最新的文章（已按时间排序）
    const latestArticle = userArticles[0]

    // 构建树节点路径
    const dept = latestArticle.departments?.[0] || '未分类'
    const date = new Date(latestArticle.created_at)
    const monthKey = `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月`
    const dateKey = `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`

    // 构建所有父节点的key
    const keysToExpand = [
      `dept-${dept}`,
      `user-${dept}-${currentUserId}`,
      `month-${dept}-${currentUserId}-${monthKey}`,
      `date-${dept}-${currentUserId}-${monthKey}-${dateKey}`
    ]

    // 设置展开的节点
    expandedKeys.value = keysToExpand

    // 选中当前文章
    currentArticleId.value = latestArticle.id
    currentArticle.value = latestArticle

    // 使用nextTick确保树已渲染后再设置当前节点
    nextTick(() => {
      if (treeRef.value) {
        treeRef.value.setCurrentKey(latestArticle.id)
      }
    })

    console.log('🎯 自动定位到最新日志:', {
      title: latestArticle.title,
      date: latestArticle.created_at,
      expandedKeys: keysToExpand
    })
  }

  // 递归获取所有子节点的key
  const getAllChildKeys = (node: any): string[] => {
    const keys: string[] = []
    if (node.children && node.children.length > 0) {
      node.children.forEach((child: any) => {
        keys.push(child.key)
        keys.push(...getAllChildKeys(child))
      })
    }
    return keys
  }

  // 树节点点击
  const onNodeClick = (data: any) => {
    if (data.isLeaf) {
      // 点击文章节点，显示文章内容
      currentArticleId.value = data.key
      currentArticle.value = data.article
    } else if (data.isUser) {
      // 点击用户节点（第二级），展开该用户下的所有子节点
      const childKeys = getAllChildKeys(data)
      const currentExpanded = new Set(expandedKeys.value)

      // 如果用户节点已经展开，则收起；否则展开所有子节点
      if (currentExpanded.has(data.key)) {
        // 移除该用户节点及其所有子节点
        currentExpanded.delete(data.key)
        childKeys.forEach((key) => currentExpanded.delete(key))
      } else {
        // 添加该用户节点及其所有子节点
        currentExpanded.add(data.key)
        childKeys.forEach((key) => currentExpanded.add(key))
      }

      expandedKeys.value = Array.from(currentExpanded)
    }
  }

  // 树节点过滤
  const filterNode = (value: string, data: any) => {
    if (!value) return true
    return data.label.toLowerCase().includes(value.toLowerCase())
  }

  // 监听搜索
  watch(filterSearch, (val) => {
    nextTick(() => {
      treeRef.value?.filter(val)
    })
  })

  // 跳转到创建页面
  const goCreatePage = () => {
    router.push({ name: 'ArticleCreate', params: { type: 'work_record' } })
  }

  // 开始编辑内容
  const startEdit = async () => {
    if (!currentArticle.value) return

    // 先获取当前文章的最新状态（而不是重新加载整个列表）
    try {
      const refreshedArticle = await articlesApi.get(currentArticle.value.id)
      if (refreshedArticle) {
        currentArticle.value = refreshedArticle
      }
    } catch (error) {
      console.error('获取文章最新状态失败:', error)
      // 继续执行，使用缓存的文章数据
    }

    try {
      await articlesApi.lock(currentArticle.value.id)
      editForm.value = {
        content: currentArticle.value.content
      }
      isEditing.value = true
      
      // 获取文章最新状态以更新锁定状态显示
      try {
        const refreshedArticle = await articlesApi.get(currentArticle.value.id)
        if (refreshedArticle) {
          currentArticle.value = refreshedArticle
        }
      } catch (error) {
        console.error('获取文章最新状态失败:', error)
      }
    } catch (error: any) {
      console.error('锁定文章失败:', error)
      ElMessage.error('无法开始编辑，请稍后重试')
    }
  }

  // 取消编辑
  const cancelEdit = async () => {
    if (!currentArticle.value) return

    try {
      await articlesApi.unlock(currentArticle.value.id)
    } catch (error) {
      console.error('解锁文章失败:', error)
    }

    isEditing.value = false
    editForm.value = { content: '' }
    
    // 获取文章最新状态以更新锁定状态显示
    try {
      const refreshedArticle = await articlesApi.get(currentArticle.value.id)
      if (refreshedArticle) {
        currentArticle.value = refreshedArticle
      }
    } catch (error) {
      console.error('获取文章最新状态失败:', error)
    }
  }

  // 保存编辑内容
  const saveEdit = async () => {
    if (!currentArticle.value || !editForm.value.content.trim()) {
      ElMessage.warning('内容不能为空')
      return
    }

    try {
      saving.value = true
      await articlesApi.update(currentArticle.value.id, {
        content: editForm.value.content,
        title: currentArticle.value.title,
        summary: currentArticle.value.summary,
        category: currentArticle.value.category,
        tags: currentArticle.value.tags,
        type: 'work_record'
      })

      try {
        await articlesApi.unlock(currentArticle.value.id)
      } catch (error) {
        console.error('解锁文章失败:', error)
      }

      ElMessage.success('工作记录内容更新成功')
      isEditing.value = false
      
      // 获取文章最新状态
      try {
        const refreshedArticle = await articlesApi.get(currentArticle.value.id)
        if (refreshedArticle) {
          currentArticle.value = refreshedArticle
        }
      } catch (error) {
        console.error('获取文章最新状态失败:', error)
      }
    } catch (error) {
      console.error('保存工作记录失败:', error)
      ElMessage.error('保存工作记录失败')
    } finally {
      saving.value = false
    }
  }

  // 导入 Markdown
  const openImportMarkdown = () => {
    showMdDialog.value = true
    mdFileName.value = ''
  }

  
  const onMdSelected = async (file: any) => {
    if (!file || !file.raw) return

    const validation = validateMarkdownFile(file.raw)
    if (!validation.valid) {
      ElMessage.error(validation.error || '文件验证失败')
      return
    }

    mdFileName.value = file.name

    try {
      const content = await readMarkdownFile(file.raw)
      const html = markdownToHtml(content)
      editForm.value.content = html
      showMdDialog.value = false
      ElMessage.success('Markdown 导入成功')
    } catch (error) {
      console.error('Markdown 导入失败:', error)
      ElMessage.error('Markdown 导入失败')
    }
  }

  // 删除文章
  const handleDeleteArticle = async (articleId: string) => {
    try {
      await ElMessageBox.confirm('确定要删除这条工作记录吗？', '提示', {
        type: 'warning'
      })
      await articlesApi.remove(articleId)
      ElMessage.success('删除成功')
      await loadArticles()
      currentArticle.value = null
      currentArticleId.value = ''
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
        ElMessage.error('删除失败')
      }
    }
  }

  // 权限判断
  const canEditArticle = (article: Article) => {
    const userId = userStore.info?.id
    return userId === article.author_id || userStore.info?.role?.toLowerCase().includes('admin')
  }

  const canDeleteArticle = (article: Article) => {
    const userId = userStore.info?.id
    return userId === article.author_id || userStore.info?.role?.toLowerCase().includes('admin')
  }

  // 批量管理权限：管理员和审核员可以进行批量管理
  const canManageArticles = computed(() => {
    const role = userStore.info?.role?.toLowerCase() || ''
    return ['admin', 'reviewer'].includes(role)
  })

  // 格式化日期
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }

  // 获取分类颜色
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      技术: '#667eea',
      业务: '#48bb78',
      会议: '#ed8936',
      总结: '#4299e1',
      计划: '#f56565'
    }
    return colors[category] || '#9ca3af'
  }

  // 获取分类标签类型
  const getCategoryTagType = (category: string) => {
    const types: Record<string, any> = {
      技术: 'primary',
      业务: 'success',
      会议: 'warning',
      总结: 'info',
      计划: 'danger'
    }
    return types[category] || 'info' // 默认返回 'info' 而不是空字符串
  }

  // 截断标签
  const truncateLabel = (label: string, maxLength: number) => {
    if (label.length <= maxLength) return label
    return label.substring(0, maxLength) + '...'
  }

  // 获取用户真实姓名
  const getUserRealName = (userId: string) => {
    const user = users.value.find((u) => u.id === userId)
    return user?.real_name || user?.username || userId
  }

  // 批量管理相关计算属性
  const allDepartments = computed(() => {
    const depts = new Set<string>()
    articles.value.forEach((article) => {
      ;(article.departments || []).forEach((dept: string) => depts.add(dept))
    })
    return Array.from(depts).sort()
  })

  const filteredArticlesForBatch = computed(() => {
    let filtered = [...articles.value]

    // 按部门筛选
    if (batchDeptFilter.value) {
      filtered = filtered.filter((a) => a.departments?.includes(batchDeptFilter.value))
    }

    // 按分类筛选
    if (batchCategoryFilter.value) {
      filtered = filtered.filter((a) => a.category === batchCategoryFilter.value)
    }

    // 按标题搜索
    if (batchSearchText.value) {
      const searchText = batchSearchText.value.toLowerCase()
      filtered = filtered.filter(
        (a) =>
          a.title?.toLowerCase().includes(searchText) ||
          a.author_name?.toLowerCase().includes(searchText)
      )
    }

    return filtered.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  // 批量管理方法
  const handleSelectAllArticles = () => {
    if (selectAllArticles.value) {
      selectedArticleIds.value = filteredArticlesForBatch.value.map((a) => a.id)
    } else {
      selectedArticleIds.value = []
    }
  }

  const toggleArticleSelection = (articleId: string) => {
    const index = selectedArticleIds.value.indexOf(articleId)
    if (index > -1) {
      selectedArticleIds.value.splice(index, 1)
    } else {
      selectedArticleIds.value.push(articleId)
    }
  }

  const clearBatchFilters = () => {
    batchSearchText.value = ''
    batchDeptFilter.value = ''
    batchCategoryFilter.value = ''
  }

  const formatCompactDate = (date: string) => {
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const batchDeleteArticles = async () => {
    if (selectedArticleIds.value.length === 0) {
      ElMessage.warning('请先选择要删除的工作记录')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedArticleIds.value.length} 条工作记录吗？此操作不可恢复！`,
        '批量删除确认',
        {
          type: 'warning',
          confirmButtonText: '确定删除',
          cancelButtonText: '取消'
        }
      )

      batchDeleting.value = true

      // 并行删除所有选中的文章
      const deletePromises = selectedArticleIds.value.map((id) => articlesApi.remove(id))
      await Promise.all(deletePromises)

      ElMessage.success(`成功删除 ${selectedArticleIds.value.length} 条工作记录`)

      // 重新加载数据
      await loadArticles()

      // 关闭对话框并清空选中
      showBatchManageDialog.value = false
      selectedArticleIds.value = []
      selectAllArticles.value = false
    } catch (e: any) {
      if (e !== 'cancel') {
        console.error('批量删除失败:', e)
        ElMessage.error('批量删除失败')
      }
    } finally {
      batchDeleting.value = false
    }
  }

  // 监听批量管理对话框关闭
  watch(
    () => showBatchManageDialog.value,
    (val) => {
      if (!val) {
        selectedArticleIds.value = []
        selectAllArticles.value = false
        batchSearchText.value = ''
        batchDeptFilter.value = ''
        batchCategoryFilter.value = ''
      }
    }
  )

  // 监听路由查询参数变化，触发刷新
  watch(
    () => route.query.refresh,
    async (newVal, oldVal) => {
      if (newVal && newVal !== oldVal) {
        console.log('🔄 检测到刷新参数变化，重新加载数据...')
        await loadArticles()
        // 清除查询参数，避免下次进入页面时重复刷新
        router.replace({ name: 'WorkRecords', query: {} })
      }
    }
  )

  // 导出命令处理
  const handleExportCommand = (command: string) => {
    if (command === 'html') {
      exportHtml()
    } else if (command === 'pdf') {
      exportPdf()
    }
  }

  // HTML 转义函数
  function escapeHtml(s: string) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }

  // 导出为 HTML
  const exportHtml = () => {
    if (!currentArticle.value) return
    const title = (currentArticle.value.title || 'article').replace(/[/\\:*?"<>|]/g, '_')
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
  <h1>${escapeHtml(currentArticle.value.title || '')}</h1>
  ${currentArticle.value.summary ? `<p>${escapeHtml(currentArticle.value.summary)}</p>` : ''}
  <div>${currentArticle.value.content || ''}</div>
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

  // 导出为 PDF（通过浏览器打印）
  const exportPdf = () => {
    if (!currentArticle.value) return

    const title = currentArticle.value.title || 'article'

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
    <h1>${escapeHtml(currentArticle.value.title || '')}</h1>
    ${currentArticle.value.summary ? `<p><strong>摘要：</strong>${escapeHtml(currentArticle.value.summary)}</p>` : ''}
    <div>${currentArticle.value.content || ''}</div>
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

  // 监听路由 articleId 参数，支持从外部链接跳转到指定文章
  watch(
    () => route.query.articleId,
    async (newArticleId) => {
      if (newArticleId && typeof newArticleId === 'string') {
        console.log('🔍 检测到 articleId 参数，准备定位文章:', newArticleId)

        // 如果文章列表还没加载，先加载
        if (articles.value.length === 0) {
          await loadArticles()
        }

        const targetArticle = articles.value.find((a) => a.id === newArticleId)
        if (targetArticle) {
          // 找到文章，设置为当前文章
          currentArticleId.value = targetArticle.id
          currentArticle.value = targetArticle

          // 构建树路径并展开
          const userDept = targetArticle.departments?.[0] || '未分类'
          const date = new Date(targetArticle.created_at)
          const year = date.getFullYear()
          const month = date.getMonth() + 1
          const day = date.getDate()
          const monthKey = `${year}年${month}月`
          const dateKey = `${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}`

          const pathKeys = [
            `dept-${userDept}`,
            `user-${userDept}-${targetArticle.author_id}`,
            `month-${userDept}-${targetArticle.author_id}-${monthKey}`,
            `date-${userDept}-${targetArticle.author_id}-${monthKey}-${dateKey}`
          ]

          expandedKeys.value = pathKeys

          // 等待 DOM 更新后滚动到对应节点
          await nextTick()

          ElMessage.success(`已定位到文章：${targetArticle.title}`)

          // 清除 URL 参数
          router.replace({ name: 'WorkRecords', query: {} })
        } else {
          ElMessage.warning('未找到指定的文章')
          // 清除 URL 参数
          router.replace({ name: 'WorkRecords', query: {} })
        }
      }
    }
  )

  // 生命周期
  onMounted(async () => {
    await Promise.all([loadUsers(), loadArticles()])
  })
</script>

<style lang="scss" scoped>
  .work-records-page {
    background: var(--art-bg-color);
    height: 100vh;
    overflow: hidden;

    .page-container {
      display: flex !important;
      flex-direction: column !important;
      height: 100% !important;
      padding: 10px;
      box-sizing: border-box;
    }

    .page-header-wrapper {
      flex-shrink: 0;
      height: auto !important;
      padding: 0 !important;
      margin-bottom: 10px;
    }
  }

  .page-body {
    flex: 0.95 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    gap: 16px;
    height: auto !important;

    .sidebar {
      padding: 0;
      background: transparent;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }
  }

  .nav-panel {
    padding: 16px;
    background: var(--art-main-bg-color);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;

    // 美化滚动条
    &::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }

    &::-webkit-scrollbar-track {
      background: var(--art-bg-color);
      border-radius: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: var(--art-text-gray-400);
      border-radius: 4px;

      &:hover {
        background: var(--art-text-gray-500);
      }
    }
  }

  .filter-section {
    flex-shrink: 0;
    margin-bottom: 12px;
  }

  .nav-actions {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;

    .el-button {
      border-radius: 6px;
      font-size: 13px;
      height: 32px;

      .el-icon {
        font-size: 14px;
      }
    }
  }

  :deep(.el-tree) {
    background: transparent;

    .el-tree-node {
      margin-bottom: 4px;

      &__content {
        height: auto;
        min-height: 36px;
        padding: 4px 8px;
        border-radius: 8px;

        &:hover {
          background: var(--art-bg-color);
        }
      }

      &.is-current > .el-tree-node__content {
        background: linear-gradient(
          90deg,
          rgba(102, 126, 234, 0.15) 0%,
          rgba(118, 75, 162, 0.08) 100%
        );
        border-left: 3px solid #667eea;
        padding-left: 5px !important;
        box-shadow: 0 1px 3px rgba(102, 126, 234, 0.1);
        font-weight: 600;

        .tree-node {
          color: #667eea;

          .node-icon {
            color: #667eea;
            transform: scale(1.1);
          }

          .node-label {
            color: #667eea;
            font-weight: 600;
          }

          .node-count,
          .node-meta {
            background: #667eea !important;
            color: white !important;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
          }
        }
      }
    }

    // 调整五级结构的缩进：部门 → 用户 → 月份 → 日期 → 文章
    // 使用属性选择器精确控制每一级的绝对缩进
    :deep(.el-tree-node) {
      // 第一级：部门（根节点）
      & > .el-tree-node__content {
        padding-left: 0px !important;
      }

      // 第二级：用户
      .el-tree-node > .el-tree-node__content {
        padding-left: 0px !important;
      }

      // 第三级：月份
      .el-tree-node .el-tree-node > .el-tree-node__content {
        padding-left: 0px !important;
      }

      // 第四级：日期
      .el-tree-node .el-tree-node .el-tree-node > .el-tree-node__content {
        padding-left: 0px !important;
      }

      // 第五级：文章
      .el-tree-node .el-tree-node .el-tree-node .el-tree-node > .el-tree-node__content {
        padding-left: 0px !important;
      }
    }

    // 调整展开图标样式
    :deep(.el-tree-node__expand-icon) {
      font-size: 14px;
      color: var(--art-text-gray-600);
      margin-right: 4px;
    }

    .tree-node {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;

      .user-color-dot {
        flex-shrink: 0;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
      }

      .node-icon {
        flex-shrink: 0;
        font-size: 14px;
        color: var(--art-primary-color);
        margin-right: 4px;
      }

      .node-label {
        flex: 1;
        font-size: 14px;
        color: var(--art-text-gray-800);
      }

      .node-meta-tag {
        flex-shrink: 0;
      }
    }

    // 用户节点特殊样式
    .user-node {
      .node-label {
        font-weight: 600;
      }
    }

    .tree-leaf {
      cursor: pointer;

      &.active .node-label {
        color: var(--art-primary-color);
        font-weight: 600;
      }
    }

    .tree-group {
      font-weight: 600;
      color: var(--art-text-gray-800);
    }
  }

  .main-col {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0;
    flex: 1;
    min-height: 0;

    .article-detail-wrapper {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    .empty-state {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 0;
    }
  }

  .article-card {
    background: var(--art-main-bg-color);
    border: 1px solid var(--art-card-border);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;

    :deep(.el-card__header) {
      padding: 24px;
      border-bottom: 1px solid var(--art-card-border);
      background: linear-gradient(
        to bottom,
        var(--art-main-bg-color) 0%,
        rgba(102, 126, 234, 0.02) 100%
      );
      flex-shrink: 0;
    }

    :deep(.el-card__body) {
      padding: 0;
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      min-height: 0;
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
    }

    .header-info {
      h3 {
        margin: 0 0 12px 0;
        font-size: 26px;
        font-weight: 600;
        color: var(--art-text-gray-900);
      }

      .meta-info {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        color: var(--art-text-gray-600);
        font-size: 14px;
        margin-bottom: 16px;

        span {
          display: flex;
          align-items: center;
          gap: 6px;

          .el-icon {
            font-size: 16px;
            color: var(--art-text-gray-500);
          }
        }

        .el-tag {
          margin-right: 8px;
          font-weight: 500;
        }
      }
    }

    .article-collaborators {
      margin-top: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .collaborators-inline {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .collaborators-label {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          color: var(--art-text-gray-600);
          font-weight: 500;
          flex-shrink: 0;
        }

        .collaborator-tag-inline {
          font-size: 12px;
        }
      }
    }

    .header-right {
      display: flex;
      gap: 8px;
      flex-shrink: 0;

      .el-button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;

        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        &:active {
          transform: translateY(0);
        }
      }
    }
  }

  .article-content {
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
      background: var(--art-text-gray-400);
      border-radius: 4px;

      &:hover {
        background: var(--art-text-gray-500);
      }
    }

    // 编辑模式的编辑器样式
    .content-editor {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: var(--art-main-bg-color);
      min-height: 0;
      overflow: visible;
    }

    // 当存在编辑器时，禁用article-content的滚动并去除padding
    &.editor-active {
      padding: 10;
      overflow: hidden;
    }

    .content-html {
      color: var(--art-text-gray-800);
      line-height: 1.8;

      :deep(h1),
      :deep(h2),
      :deep(h3) {
        margin: 24px 0 16px;
        font-weight: 600;
        color: var(--art-text-gray-900);
      }

      :deep(h1) {
        font-size: 28px;
      }

      :deep(h2) {
        font-size: 24px;
      }

      :deep(h3) {
        font-size: 20px;
      }

      :deep(p) {
        margin: 14px 0;
      }

      :deep(img) {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      :deep(pre) {
        background: #282c34;
        color: #abb2bf;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
      }

      :deep(code) {
        background: rgba(102, 126, 234, 0.08);
        color: #667eea;
        padding: 3px 8px;
        border-radius: 4px;
      }

      :deep(blockquote) {
        border-left: 4px solid #667eea;
        background: rgba(102, 126, 234, 0.05);
        padding: 12px 16px;
        margin: 16px 0;
      }

      :deep(a) {
        color: #667eea;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  /* 导入对话框样式（与发布文章页面保持一致） */
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

  // 批量管理对话框样式
  .batch-manage-container {
    .batch-filters {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }

    .batch-article-list {
      margin-top: 16px;
    }

    .batch-article-list-container {
      max-height: 400px;
      overflow-y: auto;
      border: 1px solid var(--el-border-color);
      border-radius: 8px;
      background: var(--el-bg-color);

      // 自定义滚动条
      &::-webkit-scrollbar {
        width: 8px;
      }
      &::-webkit-scrollbar-track {
        background: var(--el-fill-color-lighter);
        border-radius: 4px;
      }
      &::-webkit-scrollbar-thumb {
        background: var(--el-fill-color-darker);
        border-radius: 4px;

        &:hover {
          background: var(--el-text-color-secondary);
        }
      }
    }

    .batch-article-item {
      padding: 14px 16px;
      border-bottom: 1px solid var(--el-border-color-lighter);
      display: flex;
      align-items: flex-start;
      gap: 12px;
      transition: all 0.2s;
      cursor: pointer;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background: var(--el-fill-color-light);
      }

      &.selected {
        background: rgba(102, 126, 234, 0.05);
        border-left: 3px solid var(--el-color-primary);
        padding-left: 13px;
      }

      .article-checkbox {
        flex-shrink: 0;
        margin-top: 2px;
      }

      .article-info {
        flex: 1;
        min-width: 0;

        .article-title-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;

          .article-title {
            font-weight: 500;
            color: var(--el-text-color-primary);
            font-size: 14px;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .category-tag {
            flex-shrink: 0;
          }
        }

        .article-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          font-size: 12px;
          color: var(--el-text-color-secondary);
          flex-wrap: wrap;

          .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;

            .el-icon {
              font-size: 13px;
            }
          }
        }
      }
    }

    .empty-state {
      padding: 60px 20px;
      text-align: center;
      color: var(--el-text-color-secondary);

      .el-icon {
        color: var(--el-text-color-placeholder);
      }

      p {
        margin-top: 16px;
        font-size: 14px;
      }
    }
  }
</style>
