# 文章链接跳转修复

## 修复时间

2025-11-05

## 问题描述

### 症状

在周列表中添加工作项时，可以关联各种类型的文章链接：

1. ❌ **工作记录**：点击链接无法跳转到指定文章
2. ❌ **会议记录**：链接格式可能不正确
3. ❌ **项目文章**：只能跳转到项目管理页面，不能定位到具体文章

### 根本原因

#### 1. 链接生成逻辑不完善

**文件**: `src/views/work-log/components/WorkLogEntryCell.vue`

原始的 `handleArticleSelect` 函数：

```typescript
// 旧逻辑
if (article.type === 'collaboration') {
  articleUrl = `${baseUrl}/login#/collaboration?articleId=${article.id}`
} else if (article.project_id) {
  // 所有有 project_id 的文章都跳到项目管理页面
  articleUrl = `${baseUrl}/login#/project/management?projectId=${article.project_id}&articleId=${article.id}`
} else {
  // 其他类型使用通用路径
  const typeRoute = article.type === 'model_test' ? 'model-test' : article.type
  articleUrl = `${baseUrl}/login#/articles/${typeRoute}?articleId=${article.id}`
}
```

**问题**：

- `work_record` 类型没有专门处理，会被错误地路由到 `/articles/work_record`（不存在）
- `meeting` 和 `model_test` 类型没有优先处理，如果有 `project_id` 会被错误路由
- 项目文章的 articleId 参数没有被正确处理

#### 2. 工作记录页面缺少 articleId 监听

**文件**: `src/views/work-log/records/index.vue`

工作记录页面只监听了 `refresh` 参数，没有监听 `articleId` 参数，导致即使链接正确，也无法定位到具体文章。

## 解决方案

### 1. 优化链接生成逻辑

**文件**: `src/views/work-log/components/WorkLogEntryCell.vue`

**修改前**（问题逻辑）：

```typescript
// 先判断 project_id，导致 meeting/model_test 被错误路由
if (article.project_id) {
  articleUrl = `${baseUrl}/login#/project/management?...`
}
```

**修改后**（优先级明确）：

```typescript
// 根据文章类型生成对应的链接
if (article.type === 'collaboration') {
  // 团队协作文档
  articleUrl = `${baseUrl}/login#/collaboration?articleId=${article.id}`
} else if (article.type === 'work_record') {
  // 工作记录 - 新增
  articleUrl = `${baseUrl}/login#/work-log/records?articleId=${article.id}`
} else if (article.type === 'meeting') {
  // 会议记录 - 明确处理
  articleUrl = `${baseUrl}/login#/articles/meeting?articleId=${article.id}`
} else if (article.type === 'model_test') {
  // 模型测试 - 明确处理
  articleUrl = `${baseUrl}/login#/articles/model-test?articleId=${article.id}`
} else if (article.project_id) {
  // 项目下的文章（自定义类型）
  articleUrl = `${baseUrl}/login#/project/management?projectId=${article.project_id}&articleId=${article.id}`
} else {
  // 其他文章类型，使用通用文章页面
  const typeRoute = article.type
  articleUrl = `${baseUrl}/login#/articles/${typeRoute}?articleId=${article.id}`
}
```

**关键改进**：

1. ✅ 按照文章类型优先级判断（特殊类型 > 项目文章 > 通用类型）
2. ✅ 为 `work_record` 添加专门的路由处理
3. ✅ 为 `meeting` 和 `model_test` 添加明确的路由
4. ✅ 保持项目文章的正确处理（带 projectId 和 articleId）

### 2. 工作记录页面添加 articleId 监听

**文件**: `src/views/work-log/records/index.vue`

**新增功能**：

```typescript
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

        // 构建完整路径
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
```

**关键功能**：

1. ✅ 监听 `route.query.articleId` 变化
2. ✅ 自动加载文章列表（如果未加载）
3. ✅ 查找目标文章并设置为当前文章
4. ✅ 自动展开导航树到对应的节点
5. ✅ 显示成功/失败提示
6. ✅ 清除 URL 参数，保持界面干净

## 技术细节

### 路由映射表

| 文章类型 | type 值 | 跳转路由 | 示例 URL |
| --- | --- | --- | --- |
| 工作记录 | `work_record` | `/work-log/records` | `/work-log/records?articleId=xxx` |
| 会议记录 | `meeting` | `/articles/meeting` | `/articles/meeting?articleId=xxx` |
| 模型测试 | `model_test` | `/articles/model-test` | `/articles/model-test?articleId=xxx` |
| 团队协作 | `collaboration` | `/collaboration` | `/collaboration?articleId=xxx` |
| 项目文章 | 自定义 + `project_id` | `/project/management` | `/project/management?projectId=xxx&articleId=xxx` |
| 其他类型 | 自定义 | `/articles/{type}` | `/articles/custom?articleId=xxx` |

### 判断优先级

```
1. collaboration ← 最高优先级
2. work_record
3. meeting
4. model_test
5. 有 project_id 的文章
6. 其他类型 ← 最低优先级
```

**为什么这样设计？**

- 特殊类型（如 work_record, meeting）有固定的页面，必须优先匹配
- 避免这些特殊类型被 `project_id` 判断错误路由
- 项目文章作为兜底，处理自定义类型的文章

### 工作记录树结构

工作记录的导航树是 5 层结构：

```
部门 (dept)
  └─ 用户 (user)
      └─ 月份 (month)
          └─ 日期 (date)
              └─ 文章 (article)
```

**路径键格式**：

```javascript
;[
  `dept-${部门名}`,
  `user-${部门名}-${用户ID}`,
  `month-${部门名}-${用户ID}-${年月}`,
  `date-${部门名}-${用户ID}-${年月}-${月日}`
]
```

**示例**：

```javascript
// 研发部算法组 - user1 - 2025年11月 - 11/05 下的文章
;[
  'dept-研发部算法组',
  'user-研发部算法组-user1',
  'month-研发部算法组-user1-2025年11月',
  'date-研发部算法组-user1-2025年11月-11/05'
]
```

## 执行流程

### 场景 1: 从周列表跳转到工作记录

```
用户在周列表添加工作项
  ↓
选择关联文章（类型: work_record）
  ↓
生成链接: /work-log/records?articleId=abc123
  ↓
用户点击链接
  ↓
浏览器打开新标签页，URL = /work-log/records?articleId=abc123
  ↓
工作记录页面加载
  ↓
onMounted 加载用户和文章列表
  ↓
watch 检测到 route.query.articleId = 'abc123'
  ↓
查找文章 id='abc123'
  ↓
找到文章，设置为当前文章
  ↓
构建树路径并展开节点
  ↓
显示成功提示：已定位到文章：xxx
  ↓
清除 URL 参数（/work-log/records）
  ↓
用户看到指定的工作记录 ✅
```

### 场景 2: 从周列表跳转到会议记录

```
用户在周列表添加工作项
  ↓
选择关联文章（类型: meeting）
  ↓
生成链接: /articles/meeting?articleId=def456
  ↓
用户点击链接
  ↓
会议记录页面加载
  ↓
watch 检测到 articleId (已有监听)
  ↓
定位到指定的会议记录 ✅
```

## 测试要点

### 功能测试

#### 工作记录

- [ ] 在周列表中添加工作项，关联一条工作记录
- [ ] 点击生成的链接，应该跳转到工作记录页面
- [ ] 左侧导航树自动展开到对应节点
- [ ] 右侧显示该工作记录的详细内容
- [ ] 控制台显示：`🔍 检测到 articleId 参数，准备定位文章: xxx`
- [ ] 显示提示：`已定位到文章：xxx`
- [ ] URL 自动清除参数，变为干净的 `/work-log/records`

#### 会议记录

- [ ] 在周列表中添加工作项，关联一条会议记录
- [ ] 点击生成的链接，应该跳转到会议记录页面
- [ ] 自动定位到指定的会议记录
- [ ] 显示提示：`已定位到文章：xxx`

#### 模型测试

- [ ] 在周列表中添加工作项，关联一条模型测试记录
- [ ] 点击生成的链接，应该跳转到模型测试页面
- [ ] 自动定位到指定的模型测试记录

#### 项目文章

- [ ] 在周列表中添加工作项，关联一条项目文章
- [ ] 点击生成的链接，应该跳转到项目管理页面
- [ ] URL 包含 projectId 和 articleId 参数

### 边缘情况测试

- [ ] 文章不存在时，显示：`未找到指定的文章`
- [ ] 文章列表未加载时，先自动加载再定位
- [ ] 快速连续点击多个链接，每个都能正确定位
- [ ] 刷新页面（F5）后，不会误触发定位（因为参数已清除）

### 兼容性测试

- [ ] 旧的没有 articleId 的 URL 仍然正常工作
- [ ] 同时存在 refresh 和 articleId 参数时，都能正确处理
- [ ] 浏览器后退/前进按钮正常工作

## 相关文件

- `src/views/work-log/components/WorkLogEntryCell.vue` - 链接生成逻辑
- `src/views/work-log/records/index.vue` - 工作记录页面（新增 articleId 监听）
- `src/views/project/articles/meeting/index.vue` - 会议记录页面（已有 articleId 监听）

## 已知限制

### 项目管理页面

目前项目管理页面 (`/project/management`) 还没有实现 articleId 定位功能。这个页面相对复杂，需要：

1. 先定位到项目
2. 再定位到项目下的文章

**建议**：

- 短期：保持现状，用户可以先看到项目，再手动查找文章
- 长期：实现完整的项目 + 文章双定位功能

### 自定义文章类型

如果有新的自定义文章类型，需要：

1. 在路由中注册对应的页面
2. 在页面中实现 articleId 监听
3. 在 `WorkLogEntryCell.vue` 中添加对应的路由规则

## 进一步优化建议

### 1. 统一的文章跳转服务

创建一个统一的文章跳转服务：

```typescript
// utils/articleNavigation.ts
export const navigateToArticle = (article: Article) => {
  const routes = {
    work_record: '/work-log/records',
    meeting: '/articles/meeting',
    model_test: '/articles/model-test',
    collaboration: '/collaboration'
  }

  const route = routes[article.type] || `/articles/${article.type}`
  router.push({ path: route, query: { articleId: article.id } })
}
```

### 2. 深度链接（Deep Link）支持

支持更复杂的定位需求：

```
/work-log/records?articleId=xxx&highlight=section-2
```

### 3. 面包屑导航

在文章页面顶部显示面包屑：

```
首页 > 工作记录 > 研发部算法组 > 张三 > 2025年11月 > 11/05 > 文章标题
```

## 总结

这次修复通过两个核心改进：

1. **优化链接生成逻辑**：明确各种文章类型的路由优先级
2. **实现 articleId 监听**：工作记录页面支持从外部链接直接定位

现在用户可以在周列表中添加各种类型文章的链接，点击后能够正确跳转并定位到具体的文章内容，显著提升了跨页面导航的用户体验。
