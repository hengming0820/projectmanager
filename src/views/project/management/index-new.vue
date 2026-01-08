<template>
  <div class="project-management-new">
    <el-container class="page-container">
      <!-- 顶部标题栏 -->
      <ArtPageHeader
        title="项目管理"
        description="管理医学影像标注项目及相关文档"
        icon="📁"
        badge="Projects"
        theme="purple"
      >
        <template #actions>
          <el-button @click="loadProjects">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button v-if="isAdmin" type="primary" @click="showCreateProjectDialog = true">
            <el-icon><FolderAdd /></el-icon>
            新建项目
          </el-button>
        </template>
      </ArtPageHeader>

      <!-- 左右布局 -->
      <el-container class="page-body">
        <!-- 左侧导航 -->
        <el-aside width="360px" class="sidebar">
          <div class="nav-panel">
            <div class="filter-section">
              <el-input
                v-model="filterSearch"
                placeholder="搜索项目..."
                :prefix-icon="Search"
                clearable
                @input="handleFilterChange"
              />
            </div>

            <el-tree
              ref="treeRef"
              :data="treeData"
              :props="{ label: 'label', children: 'children' }"
              :filter-node-method="filterNode"
              :expand-on-click-node="false"
              :default-expanded-keys="expandedKeys"
              :indent="0"
              node-key="key"
              @node-click="onNodeClick"
              @node-expand="onNodeExpand"
              @node-collapse="onNodeCollapse"
            >
              <template #default="{ node, data }">
                <div
                  :class="[
                    'tree-node',
                    {
                      'tree-project': data.type === 'project',
                      'tree-project-detail': data.type === 'project-detail',
                      'tree-category': data.type === 'category',
                      'tree-article': data.type === 'article',
                      active: isNodeActive(data)
                    }
                  ]"
                >
                  <span class="node-icon">{{ getNodeIcon(data) }}</span>
                  <el-tooltip
                    :content="data.label"
                    placement="right"
                    :disabled="data.label.length <= 20"
                    :show-after="300"
                  >
                    <span class="node-label">{{ data.label }}</span>
                  </el-tooltip>
                  <el-tag
                    v-if="data.type === 'project' && data.status"
                    size="small"
                    :type="getProjectStatusType(data.status)"
                    effect="plain"
                    class="node-status-tag"
                  >
                    {{ getProjectStatusText(data.status) }}
                  </el-tag>
                  <span
                    v-if="data.type === 'category' && data.count !== undefined"
                    class="node-count"
                  >
                    ({{ data.count }})
                  </span>

                  <!-- 分类节点的新建文章按钮 -->
                  <div
                    v-if="data.type === 'category'"
                    class="node-action-btn-wrapper"
                    @click.stop.prevent
                    @mousedown.stop
                    @mouseup.stop
                  >
                    <el-tooltip content="发布文章" placement="right" :show-after="500">
                      <el-button
                        @click.stop="createArticleForCategory(data)"
                        type="primary"
                        text
                        size="small"
                        class="node-action-btn"
                      >
                        <el-icon><Plus /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>

                  <!-- 项目节点的管理分类按钮（仅管理员可见） -->
                  <div
                    v-if="data.type === 'project' && isAdmin"
                    class="node-manage-btn-wrapper"
                    @click.stop.prevent
                    @mousedown.stop
                    @mouseup.stop
                  >
                    <el-button
                      @click.stop="openCategoryManage(data.project)"
                      type="primary"
                      text
                      size="small"
                      class="node-manage-btn"
                    >
                      <el-icon><Setting /></el-icon>
                    </el-button>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </el-aside>

        <!-- 右侧主内容 -->
        <el-main class="main-col">
          <!-- 欢迎页面（未选择任何项目） -->
          <div v-if="!currentSelection" class="welcome-page">
            <el-empty description="请从左侧选择项目查看详情">
              <el-button type="primary" @click="showCreateProjectDialog = true">
                <el-icon><Plus /></el-icon>
                创建第一个项目
              </el-button>
            </el-empty>
          </div>

          <!-- 项目详情页面 -->
          <div v-else-if="currentSelection.type === 'project-detail'" class="project-detail-page">
            <ProjectDetailView
              :project="currentSelection.project"
              @refresh="loadProjects"
              @deleted="handleProjectDeleted"
            />
          </div>

          <!-- 文章详情页面 -->
          <ArticleDetailView
            v-else-if="
              currentSelection.type === 'article-detail' &&
              currentSelection.articleId &&
              currentSelection.projectId &&
              currentSelection.articleType &&
              currentSelection.projectName
            "
            :article-id="currentSelection.articleId"
            :project-id="currentSelection.projectId"
            :project-name="currentSelection.projectName"
            :article-type="currentSelection.articleType"
            :category-name="currentSelection.categoryName"
            @refresh="loadArticlesForProject"
          />

          <!-- 文章空状态页面 -->
          <div
            v-else-if="
              currentSelection.type === 'article-empty' &&
              currentSelection.projectId &&
              currentSelection.articleType &&
              currentSelection.projectName
            "
            class="article-empty-page"
          >
            <ArticleEmptyView
              :project-id="currentSelection.projectId"
              :project-name="currentSelection.projectName"
              :article-type="currentSelection.articleType"
              :category-name="currentSelection.categoryName"
              @refresh="loadArticlesForProject"
            />
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 新建项目对话框 -->
    <ProjectFormDialog v-model="showCreateProjectDialog" @success="handleProjectCreated" />

    <!-- 分类管理对话框 -->
    <CategoryManageDialog
      v-if="managingProject"
      v-model="showCategoryManageDialog"
      :project-id="managingProject.id"
      :project-name="managingProject.name"
      @refresh="handleCategoryRefresh"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, watch, nextTick } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { Search, Refresh, FolderAdd, Plus, Setting } from '@element-plus/icons-vue'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import { articlesApi } from '@/api/articlesApi'
  import { projectCategoryApi, type ProjectCategory } from '@/api/projectCategoryApi'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import ProjectDetailView from './components/ProjectDetailView.vue'
  import ArticleListView from './components/ArticleListView.vue'
  import ArticleDetailView from './components/ArticleDetailView.vue'
  import ProjectFormDialog from './components/ProjectFormDialog.vue'
  import CategoryManageDialog from './components/CategoryManageDialog.vue'
  // @ts-ignore - TypeScript cache issue
  import ArticleEmptyView from './components/ArticleEmptyView.vue'
  import type { Project } from '@/types/project'

  defineOptions({ name: 'ProjectManagementNew' })

  const router = useRouter()
  const route = useRoute()
  const projectStore = useProjectStore()
  const userStore = useUserStore()

  // 权限判断：是否为管理员
  const isAdmin = computed(() => {
    return userStore.currentUser?.role === 'admin'
  })

  // State
  const loading = ref(false)
  const projects = ref<Project[]>([])
  const treeRef = ref()
  const filterSearch = ref('')
  const expandedKeys = ref<string[]>([])
  const showCreateProjectDialog = ref(false)
  const showCategoryManageDialog = ref(false)
  const managingProject = ref<Project | null>(null)

  // 项目分类缓存
  const projectCategories = ref<Record<string, ProjectCategory[]>>({})
  // 文章数据缓存（动态结构，key为分类type）
  const articleCounts = ref<Record<string, Record<string, number>>>({})
  // 文章数据（用于树形结构，动态结构）
  const projectArticles = ref<Record<string, Record<string, any[]>>>({})

  // 当前选中的内容
  interface Selection {
    type: 'project-detail' | 'category' | 'article-detail' | 'article-empty'
    key: string
    project?: Project
    projectId?: string
    projectName?: string
    articleType?: string
    categoryName?: string
    articleId?: string
    articleTitle?: string
  }

  const currentSelection = ref<Selection | null>(null)

  // 树形数据（三级结构：项目 -> 分类 -> 文章）
  const treeData = computed(() => {
    return projects.value.map((project) => {
      const projectKey = `project-${project.id}`
      const counts = articleCounts.value[project.id] || {}
      const articles = projectArticles.value[project.id] || {}
      const categories = projectCategories.value[project.id] || []

      // 构建子节点
      const children: any[] = [
        {
          key: `${projectKey}-detail`,
          label: '项目详情',
          type: 'project-detail',
          projectId: project.id,
          project: project
        }
      ]

      // 根据分类动态构建分类节点（包含文章子节点）
      categories.forEach((category: ProjectCategory) => {
        const categoryArticles = articles[category.type] || []
        const count = counts[category.type] || 0

        // 构建该分类下的文章子节点
        const articleChildren = categoryArticles.map((article: any) => ({
          key: `article-${article.id}`,
          label: article.title,
          type: 'article',
          isLeaf: true,
          articleId: article.id,
          articleTitle: article.title,
          articleType: category.type,
          projectId: project.id,
          projectName: project.name,
          categoryName: category.name,
          article: article
        }))

        children.push({
          key: `${projectKey}-${category.type}`,
          label: `${category.name} (${count})`,
          icon: category.icon || '📄',
          type: 'category',
          articleType: category.type,
          categoryId: category.id,
          categoryName: category.name,
          projectId: project.id,
          projectName: project.name,
          count: count,
          children: articleChildren
        })
      })

      return {
        key: projectKey,
        label: project.name,
        type: 'project',
        status: project.status,
        project: project,
        children: children
      }
    })
  })

  // 节点图标
  const getNodeIcon = (data: any) => {
    if (data.type === 'project') return '📁'
    if (data.type === 'project-detail') return '📊'
    if (data.type === 'category') return data.icon || '📄'
    if (data.type === 'article' || data.isLeaf) return '📄'
    return '📄'
  }

  // 判断节点是否激活
  const isNodeActive = (data: any) => {
    if (!currentSelection.value) return false
    return currentSelection.value.key === data.key
  }

  // 项目状态类型
  const getProjectStatusType = (status: string) => {
    const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
      active: 'success',
      completed: 'info',
      paused: 'warning',
      cancelled: 'danger'
    }
    return map[status] || 'info'
  }

  // 项目状态文本
  const getProjectStatusText = (status: string) => {
    const map: Record<string, string> = {
      active: '进行中',
      completed: '已完成',
      paused: '已暂停',
      cancelled: '已取消'
    }
    return map[status] || status
  }

  // 过滤节点
  const filterNode = (value: string, data: any) => {
    if (!value) return true
    return data.label.toLowerCase().includes(value.toLowerCase())
  }

  // 处理过滤变化
  const handleFilterChange = () => {
    treeRef.value?.filter(filterSearch.value)
  }

  // 节点点击
  const onNodeClick = (data: any) => {
    if (data.type === 'project') {
      // 点击项目节点，展开/收起
      const treeInstance = treeRef.value
      if (!treeInstance) return

      const node = treeInstance.getNode(data.key)
      if (!node) return

      if (node.expanded) {
        // 已展开，收起
        treeInstance.store.nodesMap[data.key].expanded = false
        const idx = expandedKeys.value.indexOf(data.key)
        if (idx >= 0) {
          expandedKeys.value.splice(idx, 1)
        }
      } else {
        // 未展开，展开
        treeInstance.store.nodesMap[data.key].expanded = true
        if (!expandedKeys.value.includes(data.key)) {
          expandedKeys.value.push(data.key)
        }
        // 默认展开后选中项目详情
        const detailKey = `${data.key}-detail`
        nextTick(() => {
          const detailNode = findNodeByKey(detailKey)
          if (detailNode) {
            onNodeClick(detailNode)
          }
        })
      }
    } else if (data.type === 'project-detail') {
      // 显示项目详情
      currentSelection.value = {
        type: 'project-detail',
        key: data.key,
        project: data.project
      }
    } else if (data.type === 'category') {
      // 点击分类节点，展开/收起
      const treeInstance = treeRef.value
      if (!treeInstance) return

      const node = treeInstance.getNode(data.key)
      if (!node) return

      if (node.expanded) {
        // 已展开，收起
        treeInstance.store.nodesMap[data.key].expanded = false
        const idx = expandedKeys.value.indexOf(data.key)
        if (idx >= 0) {
          expandedKeys.value.splice(idx, 1)
        }
      } else {
        // 未展开，展开并显示内容
        treeInstance.store.nodesMap[data.key].expanded = true
        if (!expandedKeys.value.includes(data.key)) {
          expandedKeys.value.push(data.key)
        }

        // 选中第一篇文章，如果有的话
        const articles = projectArticles.value[data.projectId]
        const articleType = data.articleType || ''
        const categoryArticles = articles?.[articleType] || []

        if (categoryArticles.length > 0) {
          // 有文章，选中第一篇
          const firstArticle = categoryArticles[0]
          currentSelection.value = {
            type: 'article-detail',
            key: `article-${firstArticle.id}`,
            projectId: data.projectId,
            projectName: data.projectName,
            articleType: data.articleType,
            categoryName: data.categoryName,
            articleId: firstArticle.id,
            articleTitle: firstArticle.title
          }
        } else {
          // 没有文章，显示空状态
          currentSelection.value = {
            type: 'article-empty',
            key: data.key,
            projectId: data.projectId,
            projectName: data.projectName,
            articleType: data.articleType,
            categoryName: data.categoryName
          }
        }
      }
    } else if (data.type === 'article' || data.isLeaf) {
      // 显示文章详情
      currentSelection.value = {
        type: 'article-detail',
        key: data.key,
        projectId: data.projectId,
        projectName: data.projectName,
        articleType: data.articleType,
        categoryName: data.categoryName,
        articleId: data.articleId,
        articleTitle: data.articleTitle
      }
    }
  }

  // 通过 key 查找节点
  const findNodeByKey = (key: string): any => {
    for (const project of treeData.value) {
      if (project.key === key) return project
      if (project.children) {
        for (const child of project.children) {
          if (child.key === key) return child
        }
      }
    }
    return null
  }

  // 节点展开事件（点击箭头展开时）
  const onNodeExpand = (data: any) => {
    const idx = expandedKeys.value.indexOf(data.key)
    if (idx < 0) {
      expandedKeys.value.push(data.key)
    }
  }

  // 节点收起事件（点击箭头收起时）
  const onNodeCollapse = (data: any) => {
    const idx = expandedKeys.value.indexOf(data.key)
    if (idx >= 0) {
      expandedKeys.value.splice(idx, 1)
    }
  }

  // 加载项目列表
  const loadProjects = async () => {
    loading.value = true
    try {
      await projectStore.fetchProjects({})
      projects.value = projectStore.projects

      // 加载每个项目的文章数量
      for (const project of projects.value) {
        await loadArticleCounts(project.id)
      }

      ElMessage.success('项目列表已刷新')
    } catch (error) {
      console.error('加载项目失败:', error)
      ElMessage.error('加载项目失败')
    } finally {
      loading.value = false
    }
  }

  // 加载项目分类
  const loadProjectCategories = async (projectId: string) => {
    try {
      const result = await projectCategoryApi.getProjectCategories(projectId)
      projectCategories.value[projectId] = result?.items || []
    } catch (error) {
      console.error(`加载项目 ${projectId} 的分类失败:`, error)
      projectCategories.value[projectId] = []
    }
  }

  // 加载项目文章统计和数据
  const loadArticleCounts = async (projectId: string) => {
    try {
      // 先加载分类
      await loadProjectCategories(projectId)

      const categories = projectCategories.value[projectId] || []
      if (categories.length === 0) {
        articleCounts.value[projectId] = {}
        projectArticles.value[projectId] = {}
        return
      }

      // 并行加载所有分类的文章
      const articlePromises = categories.map((category) =>
        articlesApi.getArticles({
          project_id: projectId,
          type: category.type,
          page: 1,
          page_size: 100
        })
      )

      const results = await Promise.all(articlePromises)

      // 存储结果
      const counts: Record<string, number> = {}
      const articles: Record<string, any[]> = {}

      categories.forEach((category, index) => {
        const result = results[index]
        counts[category.type] = result?.total || 0
        articles[category.type] = result?.items || []
      })

      articleCounts.value[projectId] = counts
      projectArticles.value[projectId] = articles
    } catch (error) {
      console.error(`加载项目 ${projectId} 的文章数量失败:`, error)
      // 失败时设置为空
      articleCounts.value[projectId] = {}
      projectArticles.value[projectId] = {}
    }
  }

  // 加载指定项目的文章
  const loadArticlesForProject = async (projectId: string) => {
    await loadArticleCounts(projectId)

    // 如果当前正在查看这个项目的文章空状态，刷新后检查是否有新文章
    if (
      currentSelection.value?.type === 'article-empty' &&
      currentSelection.value.projectId === projectId
    ) {
      const articles = projectArticles.value[projectId]
      const articleType = currentSelection.value.articleType || ''
      const categoryArticles = articles?.[articleType] || []

      // 如果现在有文章了，自动切换到第一篇文章
      if (categoryArticles.length > 0) {
        const firstArticle = categoryArticles[0]
        currentSelection.value = {
          type: 'article-detail',
          key: `article-${firstArticle.id}`,
          projectId: currentSelection.value.projectId,
          projectName: currentSelection.value.projectName,
          articleType: currentSelection.value.articleType,
          categoryName: currentSelection.value.categoryName,
          articleId: firstArticle.id,
          articleTitle: firstArticle.title
        }
      }
    }

    // 如果当前正在查看某篇文章，刷新文章列表
    if (
      currentSelection.value?.type === 'article-detail' &&
      currentSelection.value.projectId === projectId
    ) {
      // 文章列表已更新，无需额外操作
    }
  }

  // 项目创建成功
  const handleProjectCreated = () => {
    loadProjects()
  }

  // 项目删除成功
  const handleProjectDeleted = () => {
    // 清空当前选中
    currentSelection.value = null
    // 重新加载项目列表
    loadProjects()
  }

  // 为分类创建文章
  const createArticleForCategory = (categoryData: any) => {
    console.log('📝 为分类创建文章:', categoryData)

    // 从categoryData中获取项目ID、项目名称和文章类型
    const projectId = categoryData.projectId
    const projectName = categoryData.projectName
    const articleType = categoryData.articleType

    if (!projectId || !articleType) {
      ElMessage.error('无法获取项目或文章类型信息')
      return
    }

    // 跳转到创建文章页面（使用正确的路由路径和参数名）
    router.push({
      name: 'ArticleCreate',
      params: {
        type: articleType
      },
      query: {
        projectId: projectId, // 使用驼峰命名
        projectName: projectName // 传递项目名称用于显示
      }
    })
  }

  // 打开分类管理
  const openCategoryManage = (project: Project) => {
    console.log('🔧 打开分类管理:', project)
    managingProject.value = project
    // 使用 nextTick 确保组件创建后再打开对话框
    nextTick(() => {
      showCategoryManageDialog.value = true
      console.log('✅ 对话框状态已更新:', showCategoryManageDialog.value)
    })
  }

  // 分类管理刷新（重新加载项目分类和文章数据）
  const handleCategoryRefresh = async () => {
    if (managingProject.value) {
      // 重新加载该项目的分类和文章数据
      await loadArticleCounts(managingProject.value.id)

      // 如果当前正在查看该项目下的内容，保持选中状态
      if (currentSelection.value?.projectId === managingProject.value.id) {
        // 无需额外操作，treeData 的响应式会自动更新视图
      }
    }
  }

  // 选中指定项目（用于从其他页面跳转过来）
  const selectProjectById = async (projectId: string) => {
    console.log('🎯 [ProjectManagement] 尝试选中项目:', projectId)

    // 等待项目加载完成
    if (projects.value.length === 0) {
      console.log('⏳ [ProjectManagement] 项目列表未加载，等待加载...')
      await nextTick()
    }

    // 查找项目
    const targetProject = projects.value.find((p) => p.id === projectId)
    if (!targetProject) {
      console.warn('⚠️ [ProjectManagement] 未找到项目:', projectId)
      return
    }

    console.log('✅ [ProjectManagement] 找到目标项目:', targetProject.name)

    // 展开项目节点
    const projectKey = `project-${projectId}`
    const treeInstance = treeRef.value
    if (!treeInstance) {
      console.warn('⚠️ [ProjectManagement] 树组件未加载')
      return
    }

    await nextTick()

    // 展开项目
    if (!expandedKeys.value.includes(projectKey)) {
      expandedKeys.value.push(projectKey)
    }
    treeInstance.store.nodesMap[projectKey].expanded = true

    // 选中项目详情
    await nextTick()
    const detailKey = `${projectKey}-detail`
    const detailNode = findNodeByKey(detailKey)
    if (detailNode) {
      console.log('✅ [ProjectManagement] 选中项目详情')
      currentSelection.value = {
        type: 'project-detail',
        key: detailKey,
        project: targetProject
      }

      // 清除 URL 中的 projectId 参数
      router.replace({
        path: route.path,
        query: {}
      })
    }
  }

  // 根据 projectId 和 articleId 选中文章
  const selectArticleById = async (projectId: string, articleId: string) => {
    console.log('🔍 [ProjectManagement] 开始定位文章:', { projectId, articleId })

    // 先确保项目数据已加载
    if (projects.value.length === 0) {
      await loadProjects()
    }

    // 查找目标项目
    const targetProject = projects.value.find((p) => p.id === projectId)
    if (!targetProject) {
      ElMessage.warning('未找到指定的项目')
      router.replace({ path: route.path, query: {} })
      return
    }

    // 刷新项目的文章数据（确保包含新创建的文章）
    console.log('🔄 [ProjectManagement] 刷新项目文章列表，projectId:', projectId)
    await loadArticlesForProject(projectId)

    // 查找目标文章（在所有分类中查找）
    let targetArticle: any = null
    let targetCategoryType: string = ''
    const articles = projectArticles.value[projectId] || {}

    for (const [categoryType, categoryArticles] of Object.entries(articles)) {
      const found = categoryArticles.find((a: any) => a.id === articleId)
      if (found) {
        targetArticle = found
        targetCategoryType = categoryType
        break
      }
    }

    if (!targetArticle) {
      ElMessage.warning('未找到指定的文章')
      router.replace({ path: route.path, query: {} })
      return
    }

    console.log(
      '✅ [ProjectManagement] 找到目标文章:',
      targetArticle.title,
      '分类:',
      targetCategoryType
    )

    // 获取分类信息
    const categories = projectCategories.value[projectId] || []
    const category = categories.find((c: ProjectCategory) => c.type === targetCategoryType)
    const categoryName = category?.name || targetCategoryType

    // 构建树节点的 key
    const projectKey = `project-${projectId}`
    const categoryKey = `${projectKey}-${targetCategoryType}`
    const articleKey = `${categoryKey}-${articleId}`

    // 确保树组件已渲染
    const treeInstance = treeRef.value
    if (!treeInstance) {
      console.error('❌ [ProjectManagement] 树组件未渲染')
      return
    }

    // 展开路径：项目 -> 分类
    await nextTick()

    if (!expandedKeys.value.includes(projectKey)) {
      expandedKeys.value.push(projectKey)
    }
    treeInstance.store.nodesMap[projectKey].expanded = true

    await nextTick()

    if (!expandedKeys.value.includes(categoryKey)) {
      expandedKeys.value.push(categoryKey)
    }
    if (treeInstance.store.nodesMap[categoryKey]) {
      treeInstance.store.nodesMap[categoryKey].expanded = true
    }

    await nextTick()

    // 设置当前选中的文章
    currentSelection.value = {
      type: 'article-detail',
      key: articleKey,
      articleId: targetArticle.id,
      projectId: projectId,
      projectName: targetProject.name,
      articleType: targetCategoryType,
      categoryName: categoryName
    }

    console.log('✅ [ProjectManagement] 文章定位完成')
    ElMessage.success(`已定位到文章：${targetArticle.title}`)

    // 清除 URL 参数
    router.replace({
      path: route.path,
      query: {}
    })
  }

  // 监听路由变化，处理文章创建后的刷新、项目选中和文章定位
  watch(
    () => route.query,
    async (newQuery) => {
      // 只在当前路由是项目管理页面时处理 query 参数
      // 避免影响其他页面（如文章创建页面）的 query 参数
      if (route.name !== 'ProjectManagement') {
        console.log('ℹ️ [ProjectManagement] 当前不在项目管理页面，跳过 query 处理')
        return
      }

      const refreshProjectId = newQuery.refreshProject as string
      const selectProjectId = newQuery.projectId as string
      const selectArticleId = newQuery.articleId as string

      if (refreshProjectId) {
        // 刷新指定项目的文章数据
        await loadArticlesForProject(refreshProjectId)

        // 清除 URL 中的刷新参数，避免重复刷新
        router.replace({
          path: route.path,
          query: {}
        })
      } else if (selectProjectId && selectArticleId) {
        // 选中指定项目并定位到指定文章
        console.log('🔍 [ProjectManagement] 检测到 projectId 和 articleId，准备定位文章...')
        await selectArticleById(selectProjectId, selectArticleId)
      } else if (selectProjectId) {
        // 只选中指定项目
        await selectProjectById(selectProjectId)
      }
    },
    { immediate: false }
  )

  // 初始化
  onMounted(async () => {
    await loadProjects()

    // 检查初始 URL 中是否有 projectId 和 articleId 参数
    const initialProjectId = route.query.projectId as string
    const initialArticleId = route.query.articleId as string

    if (initialProjectId && initialArticleId) {
      console.log('🚀 [ProjectManagement] 检测到初始 projectId 和 articleId:', {
        initialProjectId,
        initialArticleId
      })
      await nextTick()
      await selectArticleById(initialProjectId, initialArticleId)
    } else if (initialProjectId) {
      console.log('🚀 [ProjectManagement] 检测到初始 projectId:', initialProjectId)
      await nextTick()
      await selectProjectById(initialProjectId)
    }
  })
</script>

<style lang="scss" scoped>
  .project-management-new {
    width: 100%;
    height: 100vh;
    background: var(--art-bg-color);
    overflow: hidden;
  }

  .page-container {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    padding: 10px;
    box-sizing: border-box;
  }

  // 主体布局 - 使用相对定位作为 Sidebar 的容器
  .page-body {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: row;
    padding-left: 310px; // 300px (Sidebar) + 10px (Gap)
    position: relative; // 关键：作为 absolute 定位的基准
  }

  // 左侧导航栏 - 绝对定位，自动位于 Header 下方
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 300px; // 更紧凑的宽度
    display: flex;
    flex-direction: column;
    z-index: 50;
  }

  .nav-panel {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    background: var(--art-main-bg-color);
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    overflow: hidden;
  }

  .filter-section {
    padding: 16px;
    border-bottom: 1px solid var(--art-card-border);
  }

  .el-tree {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    background: transparent;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background: var(--art-gray-400);
      border-radius: 3px;

      &:hover {
        background: var(--art-gray-500);
      }
    }

    // 禁用 Element Plus 默认缩进
    :deep(.el-tree-node) {
      .el-tree-node__content {
        padding-left: 0 !important;
      }
    }

    // 一级节点（项目）- 基础缩进
    :deep(> .el-tree-node) {
      > .el-tree-node__content {
        padding-left: 8px !important;
      }

      // 二级节点（项目详情、分类）- 统一缩进
      > .el-tree-node__children {
        > .el-tree-node {
          > .el-tree-node__content {
            padding-left: 32px !important;
          }

          // 三级节点（文章）
          > .el-tree-node__children {
            > .el-tree-node {
              > .el-tree-node__content {
                padding-left: 56px !important;
              }
            }
          }
        }
      }
    }
  }

  // 树节点样式
  .tree-node {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 6px;
    width: 100%;
    min-width: 0;
    transition: all 0.2s ease;

    .node-icon {
      font-size: 16px;
      flex-shrink: 0;
      width: 20px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .node-label {
      flex: 1;
      font-size: 14px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .node-status-tag {
      flex-shrink: 0;
      margin-left: auto;
    }

    .node-count {
      color: var(--art-text-gray-500);
      font-size: 12px;
      flex-shrink: 0;
    }

    .node-action-btn-wrapper,
    .node-manage-btn-wrapper {
      flex-shrink: 0;
      margin-left: 4px;
      z-index: 10; /* 降低 z-index，确保不会覆盖抽屉遮罩层 */
      position: relative;
      display: flex;
      align-items: center;
    }

    .node-action-btn,
    .node-manage-btn {
      opacity: 0;
      transition: all 0.2s ease;
      padding: 4px 8px !important;

      &:hover {
        opacity: 1 !important;
        transform: scale(1.1);
        background: rgba(102, 126, 234, 0.15) !important;
      }
    }

    &.tree-project {
      font-weight: 600;
      color: var(--art-text-gray-900);
      position: relative;

      .node-label {
        font-size: 15px;
      }

      &:hover .node-manage-btn-wrapper .node-manage-btn {
        opacity: 0.8;
      }
    }

    &.tree-project-detail {
      color: var(--art-text-gray-700);
      font-weight: 500;
      font-size: 14px;
    }

    &.tree-category {
      color: var(--art-text-gray-700);
      font-weight: 500;
      font-size: 14px;

      &:hover .node-action-btn-wrapper .node-action-btn {
        opacity: 0.7;
      }
    }

    &.tree-article {
      color: var(--art-text-gray-600);
      font-size: 13px;
    }

    &.active {
      background: linear-gradient(
        90deg,
        rgba(102, 126, 234, 0.15) 0%,
        rgba(118, 75, 162, 0.08) 100%
      );
      color: var(--art-primary-color);
      font-weight: 600;
      border-left: 3px solid #667eea;
      padding-left: 5px !important;
      box-shadow: 0 1px 3px rgba(102, 126, 234, 0.1);

      .node-icon {
        color: #667eea;
        transform: scale(1.1);
      }

      .node-label {
        color: #667eea;
      }
    }

    &:hover:not(.active) {
      background: var(--art-bg-color);
    }
  }

  // 主内容区 - 完全参照会议记录页面
  .main-col {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0;
    flex: 1;
    min-height: 0;
  }

  .welcome-page {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    background: var(--art-main-bg-color);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }

  .project-detail-page,
  .article-list-page,
  .article-empty-page {
    flex: 1;
    min-height: 0;
    padding: 24px;
    overflow-y: auto;
    overflow-x: hidden;
    background: var(--art-main-bg-color);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }

  // Element Plus 树组件覆盖
  :deep(.el-tree) {
    --el-tree-node-hover-bg-color: transparent;

    .el-tree-node__content {
      height: auto;
      min-height: 38px;
      padding: 4px 8px;
      border-radius: 6px;

      &:hover {
        background-color: transparent;
      }
    }

    .el-tree-node__expand-icon {
      color: var(--art-text-gray-500);
      font-size: 14px;
    }
  }
</style>
