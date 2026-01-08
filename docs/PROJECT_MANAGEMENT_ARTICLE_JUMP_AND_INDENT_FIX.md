# 项目管理页面文章跳转和缩进修复

## 修复时间

2025-11-05

## 问题描述

### 症状

用户报告了两个问题：

1. **文章链接无法定位** ❌

   - 在周列表中关联了项目下的文章（如 20250902 项目下的需求文档）
   - 点击链接后跳转到项目管理页面
   - 但没有自动定位到具体的文章，需要手动查找

2. **导航栏缩进不对** ❌
   - 项目列表下的"项目详情"和各分类项（如需求文档、技术文档等）在同一缩进级别
   - 视觉层次不清晰，"项目详情"应该更靠近项目名称

### 根本原因

#### 1. 缺少 articleId 定位功能

**文件**: `src/views/project/management/index-new.vue`

- 页面只监听 `projectId` 和 `refreshProject` 参数
- 没有监听 `articleId` 参数
- 没有 `selectArticleById` 函数来定位具体文章

#### 2. 缩进样式不合理

**文件**: `src/views/project/management/index-new.vue`

原始缩进：

```scss
// 一级节点（项目）
padding-left: 8px;

// 二级节点（项目详情 + 分类）- 统一缩进
padding-left: 32px;

// 三级节点（文章）
padding-left: 56px;
```

问题：

- "项目详情"和"分类"节点使用相同的缩进 (32px)
- 无法区分它们的层级关系
- "项目详情"应该更靠近项目（如 16px），分类保持 32px

## 解决方案

### 1. 添加 articleId 定位功能

#### 步骤 1: 新增 `selectArticleById` 函数

```typescript
const selectArticleById = async (projectId: string, articleId: string) => {
  console.log('🔍 [ProjectManagement] 开始定位文章:', { projectId, articleId })

  // 1. 确保项目数据已加载
  if (projects.value.length === 0) {
    await loadProjects()
  }

  // 2. 查找目标项目
  const targetProject = projects.value.find((p) => p.id === projectId)
  if (!targetProject) {
    ElMessage.warning('未找到指定的项目')
    router.replace({ path: route.path, query: {} })
    return
  }

  // 3. 确保项目的文章数据已加载
  if (!projectArticles.value[projectId]) {
    await loadArticlesForProject(projectId)
  }

  // 4. 查找目标文章（在所有分类中查找）
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

  // 5. 获取分类信息
  const categories = projectCategories.value[projectId] || []
  const category = categories.find((c: ProjectCategory) => c.type === targetCategoryType)
  const categoryName = category?.name || targetCategoryType

  // 6. 构建树节点路径
  const projectKey = `project-${projectId}`
  const categoryKey = `${projectKey}-${targetCategoryType}`
  const articleKey = `${categoryKey}-${articleId}`

  // 7. 展开树节点
  const treeInstance = treeRef.value
  if (!treeInstance) return

  // 展开项目
  if (!expandedKeys.value.includes(projectKey)) {
    expandedKeys.value.push(projectKey)
  }
  treeInstance.store.nodesMap[projectKey].expanded = true

  await nextTick()

  // 展开分类
  if (!expandedKeys.value.includes(categoryKey)) {
    expandedKeys.value.push(categoryKey)
  }
  if (treeInstance.store.nodesMap[categoryKey]) {
    treeInstance.store.nodesMap[categoryKey].expanded = true
  }

  await nextTick()

  // 8. 设置当前选中的文章
  currentSelection.value = {
    type: 'article-detail',
    key: articleKey,
    articleId: targetArticle.id,
    projectId: projectId,
    projectName: targetProject.name,
    articleType: targetCategoryType,
    categoryName: categoryName
  }

  ElMessage.success(`已定位到文章：${targetArticle.title}`)

  // 9. 清除 URL 参数
  router.replace({ path: route.path, query: {} })
}
```

**关键逻辑**：

1. ✅ 加载项目列表（如果未加载）
2. ✅ 加载项目的文章列表（如果未加载）
3. ✅ 在所有分类中查找目标文章
4. ✅ 展开树节点到文章所在的分类
5. ✅ 设置当前选中的文章
6. ✅ 显示成功提示
7. ✅ 清除 URL 参数

#### 步骤 2: 修改路由监听逻辑

```typescript
watch(
  () => route.query,
  async (newQuery) => {
    const refreshProjectId = newQuery.refreshProject as string
    const selectProjectId = newQuery.projectId as string
    const selectArticleId = newQuery.articleId as string // 新增

    if (refreshProjectId) {
      // 刷新项目文章
      await loadArticlesForProject(refreshProjectId)
      router.replace({ path: route.path, query: {} })
    } else if (selectProjectId && selectArticleId) {
      // 选中项目并定位文章 ✨ 新增
      console.log('🔍 [ProjectManagement] 检测到 projectId 和 articleId，准备定位文章...')
      await selectArticleById(selectProjectId, selectArticleId)
    } else if (selectProjectId) {
      // 只选中项目
      await selectProjectById(selectProjectId)
    }
  },
  { immediate: false }
)
```

#### 步骤 3: 修改初始化逻辑

```typescript
onMounted(async () => {
  await loadProjects()

  const initialProjectId = route.query.projectId as string
  const initialArticleId = route.query.articleId as string // 新增

  if (initialProjectId && initialArticleId) {
    // 定位到具体文章 ✨ 新增
    console.log('🚀 [ProjectManagement] 检测到初始 projectId 和 articleId:', {
      initialProjectId,
      initialArticleId
    })
    await nextTick()
    await selectArticleById(initialProjectId, initialArticleId)
  } else if (initialProjectId) {
    // 只选中项目
    await selectProjectById(initialProjectId)
  }
})
```

### 2. 修复导航栏缩进

#### 步骤 1: 添加节点类型识别

在模板中为 `project-detail` 类型节点添加特定 class：

```vue
<template #default="{ node, data }">
  <div
    :class="[
      'tree-node',
      {
        'tree-project': data.type === 'project',
        'tree-project-detail': data.type === 'project-detail', // ✨ 新增
        'tree-category': data.type === 'category',
        'tree-article': data.type === 'article',
        active: isNodeActive(data)
      }
    ]"
  ></div>
</template>
```

#### 步骤 2: 应用差异化缩进

```scss
// 二级节点（项目详情、分类）
> .el-tree-node__children {
  > .el-tree-node {
    > .el-tree-node__content {
      padding-left: 32px !important; // 分类默认 32px
    }

    // 项目详情节点使用更小的缩进 ✨ 新增
    &:has(.tree-project-detail) > .el-tree-node__content {
      padding-left: 16px !important; // 项目详情 16px
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
```

**关键技术**：

- 使用 `:has(.tree-project-detail)` 选择器
- 为包含特定 class 的节点应用不同的缩进
- 保持 CSS 选择器的优先级

#### 步骤 3: 添加样式区分

```scss
&.tree-project-detail {
  color: var(--art-text-gray-600); // 更浅的颜色
  font-weight: 500; // 中等字重

  .node-label {
    font-size: 14px; // 稍小的字体
  }
}
```

## 最终效果

### 缩进层级

```
📁 20250902 项目                    (8px)
  ├─ 📋 项目详情                     (16px) ✨ 更靠近项目
  ├─ 📄 需求文档 (3)                 (32px)
  │   ├─ 📃 系统需求规格说明书       (56px)
  │   ├─ 📃 用户需求文档              (56px)
  │   └─ 📃 技术需求文档              (56px)
  └─ 📄 设计文档 (2)                 (32px)
      ├─ 📃 架构设计文档              (56px)
      └─ 📃 数据库设计文档            (56px)
```

### 跳转流程

```
用户在周列表添加工作项
  ↓
选择关联文章：20250902 项目 -> 需求文档 -> 系统需求规格说明书
  ↓
生成链接: /project/management?projectId=20250902&articleId=xxx
  ↓
用户点击链接 🖱️
  ↓
项目管理页面加载
  ↓
watch 检测到 projectId 和 articleId 👀
  ↓
调用 selectArticleById('20250902', 'xxx')
  ↓
1. 查找项目: 20250902 ✅
  ↓
2. 加载项目文章列表
  ↓
3. 在所有分类中查找文章 🔍
  ↓
4. 找到文章: 系统需求规格说明书（需求文档分类）✅
  ↓
5. 展开树节点: 20250902 -> 需求文档
  ↓
6. 显示文章详情 📄
  ↓
7. 提示: "已定位到文章：系统需求规格说明书" ✅
  ↓
8. 清除 URL 参数，保持干净
```

## 技术细节

### URL 参数格式

```
/project/management?projectId=<项目ID>&articleId=<文章ID>
```

### 树节点 key 结构

```
project-<项目ID>                           // 项目节点
project-<项目ID>-detail                   // 项目详情节点
project-<项目ID>-<分类类型>               // 分类节点
project-<项目ID>-<分类类型>-<文章ID>      // 文章节点
```

示例：

```
project-20250902                           // 20250902 项目
project-20250902-detail                    // 项目详情
project-20250902-requirement               // 需求文档分类
project-20250902-requirement-abc123        // 具体文章
```

### CSS `:has()` 选择器

```scss
&:has(.tree-project-detail) > .el-tree-node__content {
  padding-left: 16px !important;
}
```

**说明**：

- `:has()` 是 CSS 的父选择器
- 选择包含 `.tree-project-detail` 的节点
- 为其子节点 `.el-tree-node__content` 应用样式

**浏览器兼容性**：

- Chrome 105+
- Firefox 121+
- Safari 15.4+
- Edge 105+

## 测试要点

### 文章定位

- [ ] 从周列表点击项目文章链接
- [ ] 自动跳转到项目管理页面
- [ ] 自动展开项目和分类节点
- [ ] 右侧显示文章详情
- [ ] 提示："已定位到文章：xxx"
- [ ] URL 自动清理，无参数残留
- [ ] 控制台日志显示定位过程

### 缩进效果

- [ ] "项目详情"缩进小于分类节点
- [ ] 视觉层次清晰
- [ ] "项目详情"更靠近项目名称
- [ ] 分类节点对齐（如需求文档、设计文档）
- [ ] 文章节点对齐

### 边缘情况

- [ ] 文章不存在时显示警告
- [ ] 项目不存在时显示警告
- [ ] 文章列表未加载时自动加载
- [ ] 快速连续点击多个链接，每个都能正确定位

## 相关文件

- `src/views/project/management/index-new.vue` - 项目管理页面（带导航栏）
- `src/views/work-log/components/WorkLogEntryCell.vue` - 链接生成逻辑（已在上一次修复）
- `docs/ARTICLE_LINK_JUMP_FIX.md` - 上一次修复文档

## 已知限制

### 旧版项目管理页面

`src/views/project/management/index.vue` 是表格形式的项目管理页面，没有导航栏。如果路由配置指向这个页面，则无法定位文章。

**建议**：

- 确保路由指向 `index-new.vue`
- 或者在 `index.vue` 中添加类似的定位逻辑

## 进一步优化建议

### 1. 统一项目管理入口

将 `index-new.vue` 重命名为 `index.vue`，统一为唯一的项目管理页面。

### 2. 面包屑导航

在文章详情页面顶部显示面包屑：

```
项目管理 > 20250902 项目 > 需求文档 > 系统需求规格说明书
```

### 3. 历史记录

记录用户访问过的文章，快速返回。

### 4. 键盘导航

支持方向键在树节点间导航，回车键选中。

## 总结

这次修复通过两个核心改进：

1. **实现 articleId 定位功能**：从外部链接可以直接定位到项目下的具体文章
2. **优化导航栏缩进**："项目详情"和"分类"节点区分更清晰

现在用户从周列表点击项目文章链接后，能够：

- ✅ 自动跳转到项目管理页面
- ✅ 自动展开到正确的节点
- ✅ 显示文章详细内容
- ✅ 获得清晰的视觉层次

显著提升了跨页面导航和信息架构的用户体验！
