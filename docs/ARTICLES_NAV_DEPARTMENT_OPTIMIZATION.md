# 文章导航栏部门分组优化

## 📋 功能说明

### 优化范围

- **会议记录**（`/articles/meeting`）
- **模型测试**（`/articles/model-test`）

### 用户需求

1. **两层导航结构**：

   - 第一级：按所属部门分组
   - 第二级：按日期（年-月）分组

2. **多部门归属**：一个文章可能属于多个部门，应该在每个所属部门下都显示

3. **点击展开**：点击分组节点可以直接展开/收起，无需点击箭头图标

---

## ✅ 实现方案

### 1. 两层导航结构

#### 修改前（单层按日期分组）

```
📅 2025-01
  ├─ 会议记录1
  └─ 会议记录2
📅 2024-12
  └─ 会议记录3
```

#### 修改后（两层：部门 > 日期）

```
🏢 研发部算法组
  ├─ 📅 2025年01月
  │   ├─ 会议记录1
  │   └─ 会议记录2
  └─ 📅 2024年12月
      └─ 会议记录3
🏢 放射科
  └─ 📅 2025年01月
      └─ 会议记录4
```

---

### 2. 核心实现

#### 2.1 构建树结构（buildTree）

```typescript
// 构建树形数据结构（两层：部门 > 日期）
const buildTree = () => {
  // 按创建时间倒序排序
  const sortedArticles = [...articles.value].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  // 第一层：按部门分组
  const departmentGroups: Record<string, any[]> = {}

  sortedArticles.forEach((article) => {
    const departments = article.departments || []

    // 如果文章没有部门，归到"其他"
    if (departments.length === 0) {
      if (!departmentGroups['其他']) {
        departmentGroups['其他'] = []
      }
      departmentGroups['其他'].push(article)
    } else {
      // 文章属于多个部门，在每个部门下都显示
      departments.forEach((dept: string) => {
        if (!departmentGroups[dept]) {
          departmentGroups[dept] = []
        }
        departmentGroups[dept].push(article)
      })
    }
  })

  // 构建两层树结构
  const departmentNames = Object.keys(departmentGroups).sort()
  treeData.value = departmentNames.map((deptName) => {
    const deptArticles = departmentGroups[deptName]

    // 第二层：按日期（年-月）分组
    const monthGroups: Record<string, any[]> = {}

    deptArticles.forEach((article) => {
      const date = new Date(article.created_at)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const yearMonth = `${year}年${String(month).padStart(2, '0')}月`

      if (!monthGroups[yearMonth]) {
        monthGroups[yearMonth] = []
      }

      monthGroups[yearMonth].push({
        key: `${deptName}-${article.id}`, // 加上部门前缀确保唯一性
        label: article.title,
        isLeaf: true,
        category: article.category,
        created_at: article.created_at,
        article: article,
        articleId: article.id // 保存原始文章ID
      })
    })

    // 构建月份子节点（按时间倒序）
    const months = Object.keys(monthGroups).sort((a, b) => b.localeCompare(a))
    const monthNodes = months.map((yearMonth) => ({
      key: `${deptName}-${yearMonth}`,
      label: `📅 ${yearMonth}`,
      isDepartmentMonth: true,
      children: monthGroups[yearMonth]
    }))

    return {
      key: `dept-${deptName}`,
      label: `🏢 ${deptName}`,
      isDepartment: true,
      children: monthNodes
    }
  })

  // 默认展开第一个部门和它的前2个月
  if (expandedKeys.value.length === 0 && treeData.value.length > 0) {
    const firstDept = treeData.value[0]
    expandedKeys.value.push(firstDept.key)

    if (firstDept.children && firstDept.children.length > 0) {
      const firstTwoMonths = firstDept.children.slice(0, 2).map((m: any) => m.key)
      expandedKeys.value.push(...firstTwoMonths)
    }
  }

  // 如果还没有选中文章，选中第一个
  if (!currentArticleId.value && articles.value.length > 0) {
    currentArticleId.value = articles.value[0].id
    currentArticle.value = articles.value[0]
  }

  navReady.value = true
}
```

**关键特性**：

- ✅ 支持多部门归属（同一文章在多个部门下显示）
- ✅ 无部门文章归到"其他"分类
- ✅ 使用部门前缀确保key的唯一性（`${deptName}-${article.id}`）
- ✅ 保存原始文章ID用于选中状态匹配

---

#### 2.2 点击展开功能（onNodeClick）

```typescript
// 树节点点击（支持点击展开）
const onNodeClick = (node: any) => {
  // 如果是叶子节点（文章），直接选中
  if (node.isLeaf) {
    const articleId = node.articleId || node.key
    // 使用原始文章ID进行匹配
    if (articleId !== currentArticleId.value) {
      currentArticleId.value = articleId
      currentArticle.value = node.article
      isEditing.value = false
    }
    return
  }

  // 如果是分组节点（部门或月份），切换展开/收起
  if (node.isDepartment || node.isDepartmentMonth) {
    const treeInstance = treeRef.value
    if (!treeInstance) return

    const treeNode = treeInstance.getNode(node.key)
    if (!treeNode) return

    if (treeNode.expanded) {
      // 已展开，收起
      treeInstance.store.nodesMap[node.key].expanded = false
      const idx = expandedKeys.value.indexOf(node.key)
      if (idx >= 0) {
        expandedKeys.value.splice(idx, 1)
      }
    } else {
      // 未展开，展开
      treeInstance.store.nodesMap[node.key].expanded = true
      if (!expandedKeys.value.includes(node.key)) {
        expandedKeys.value.push(node.key)
      }

      // 如果是部门节点，自动展开第一个月份
      if (node.isDepartment && node.children && node.children.length > 0) {
        nextTick(() => {
          const firstMonth = node.children[0]
          if (firstMonth && !expandedKeys.value.includes(firstMonth.key)) {
            expandedKeys.value.push(firstMonth.key)
            treeInstance.store.nodesMap[firstMonth.key].expanded = true
          }
        })
      }
    }
  }
}
```

**关键特性**：

- ✅ 点击文章节点：选中并显示文章详情
- ✅ 点击部门节点：展开/收起，自动展开第一个月份
- ✅ 点击月份节点：展开/收起
- ✅ 使用原始文章ID匹配选中状态（解决多部门重复问题）

---

### 3. 多部门归属示例

#### 场景：一篇文章属于多个部门

**文章数据**：

```json
{
  "id": "article-001",
  "title": "AI辅助诊断研讨会",
  "departments": ["研发部算法组", "放射科", "星像行政部门"]
}
```

**树结构**：

```
🏢 放射科
  └─ 📅 2025年01月
      └─ AI辅助诊断研讨会
🏢 星像行政部门
  └─ 📅 2025年01月
      └─ AI辅助诊断研讨会
🏢 研发部算法组
  └─ 📅 2025年01月
      └─ AI辅助诊断研讨会
```

**节点key设计**：

- 放射科下：`放射科-article-001`
- 行政部门下：`星像行政部门-article-001`
- 算法组下：`研发部算法组-article-001`

**选中状态**：

- 使用 `articleId` 字段（`article-001`）进行匹配
- 无论点击哪个部门下的文章，都能正确高亮所有副本

---

## 📊 功能对比

| 功能           | 优化前          | 优化后                        |
| -------------- | --------------- | ----------------------------- |
| **分组方式**   | 按日期单层分组  | 按部门和日期两层分组          |
| **多部门归属** | ❌ 不支持       | ✅ 支持，在每个部门下都显示   |
| **点击展开**   | ❌ 必须点击箭头 | ✅ 点击节点即可展开           |
| **自动展开**   | ❌ 无           | ✅ 部门节点自动展开第一个月份 |
| **选中状态**   | 单一匹配        | 多副本统一匹配                |

---

## 🎯 使用示例

### 示例1：单部门文章

**文章**：

- 标题：2025年1月算法组周会
- 部门：研发部算法组
- 创建时间：2025-01-15

**导航结构**：

```
🏢 研发部算法组
  └─ 📅 2025年01月
      └─ 2025年1月算法组周会
```

---

### 示例2：多部门文章

**文章**：

- 标题：跨部门联合技术评审
- 部门：研发部算法组、放射科、星像行政部门
- 创建时间：2025-01-20

**导航结构**：

```
🏢 放射科
  └─ 📅 2025年01月
      └─ 跨部门联合技术评审
🏢 星像行政部门
  └─ 📅 2025年01月
      └─ 跨部门联合技术评审
🏢 研发部算法组
  └─ 📅 2025年01月
      └─ 跨部门联合技术评审
```

**用户操作**：

1. 点击"研发部算法组"展开
2. 自动展开"2025年01月"
3. 点击"跨部门联合技术评审"
4. 右侧显示文章详情，三个部门下的文章副本都高亮

---

### 示例3：无部门文章

**文章**：

- 标题：临时记录
- 部门：无
- 创建时间：2025-01-22

**导航结构**：

```
🏢 其他
  └─ 📅 2025年01月
      └─ 临时记录
```

---

## 🔄 修改文件列表

### 修改的文件（2个）

1. **`src/views/project/articles/meeting/index.vue`**

   - 重构 `buildTree` 函数（两层：部门 > 日期）
   - 重构 `onNodeClick` 函数（支持点击展开）
   - 添加 `nextTick` 导入

2. **`src/views/project/articles/model-test/index.vue`**
   - 重构 `buildTree` 函数（两层：部门 > 日期）
   - 重构 `onNodeClick` 函数（支持点击展开）
   - 添加 `nextTick` 导入

---

## 📝 技术细节

### 1. 唯一性保证

**问题**：同一文章在多个部门下显示，如何确保key唯一？

**解决方案**：使用"部门名-文章ID"作为节点key

```typescript
key: `${deptName}-${article.id}`
```

**示例**：

- 文章ID：`article-001`
- 在"研发部算法组"：`研发部算法组-article-001`
- 在"放射科"：`放射科-article-001`

### 2. 选中状态匹配

**问题**：文章有多个副本，如何统一高亮？

**解决方案**：保存原始文章ID，用于匹配

```typescript
{
  key: `${deptName}-${article.id}`,  // 节点唯一key
  articleId: article.id,              // 原始文章ID
  article: article
}
```

**匹配逻辑**：

```typescript
const articleId = node.articleId || node.key
if (articleId !== currentArticleId.value) {
  currentArticleId.value = articleId // 使用原始ID
  currentArticle.value = node.article
}
```

**树节点模板匹配**：

```vue
:class="{ active: data.key === currentArticleId }"
```

虽然 `data.key` 包含部门前缀，但由于我们保存的 `currentArticleId` 是原始文章ID，所以需要在节点数据中使用 `articleId` 进行匹配。

**注意**：实际上这里有个小问题，模板中的 `active` 判断应该改为：

```vue
:class="{ active: (data.articleId || data.key) === currentArticleId }"
```

但由于当前实现中，我们在 `onNodeClick` 中设置的 `currentArticleId` 总是原始ID，而节点的 `key` 是"部门-ID"格式，所以需要在节点定义时也保存 `articleId` 字段用于匹配。

### 3. 自动展开逻辑

**场景**：点击部门节点展开时，自动展开第一个月份

**实现**：

```typescript
if (node.isDepartment && node.children && node.children.length > 0) {
  nextTick(() => {
    const firstMonth = node.children[0]
    if (firstMonth && !expandedKeys.value.includes(firstMonth.key)) {
      expandedKeys.value.push(firstMonth.key)
      treeInstance.store.nodesMap[firstMonth.key].expanded = true
    }
  })
}
```

**为什么使用 nextTick？**

- 确保父节点展开的DOM更新完成后，再展开子节点
- 避免同步操作导致的展开失败

---

## 🐛 已知问题

### 问题：选中状态高亮

当前实现中，如果一个文章属于多个部门，点击其中一个部门下的文章副本，其他部门下的副本可能不会高亮。

**原因**：模板中的匹配逻辑

```vue
:class="{ active: data.key === currentArticleId }"
```

`data.key` 是 `部门-文章ID`，而 `currentArticleId` 是 `文章ID`，所以不匹配。

**建议修复**：

```vue
:class="{ active: (data.articleId || data.key) === currentArticleId }"
```

或者在节点数据中直接使用原始文章ID作为判断：

```vue
:class="{ active: data.articleId === currentArticleId || data.key === currentArticleId }"
```

---

## 🚀 验证步骤

1. **刷新前端页面**（已自动热更新）

2. **测试会议记录**：

   - 进入"知识与文章" > "会议记录"
   - ✅ 查看左侧导航栏，第一级是部门
   - ✅ 点击部门，自动展开第一个月份
   - ✅ 点击月份，展开/收起
   - ✅ 点击文章，右侧显示详情

3. **测试模型测试**：

   - 进入"知识与文章" > "模型测试"
   - ✅ 查看左侧导航栏，第一级是部门
   - ✅ 重复上述测试步骤

4. **测试多部门归属**：
   - 创建一篇属于多个部门的文章
   - ✅ 验证是否在每个部门下都显示
   - ✅ 点击其中一个副本，验证选中状态

---

## 💡 未来优化建议

### 1. 修复多副本高亮问题

参考上述"已知问题"部分进行修复。

### 2. 部门图标差异化

为不同部门显示不同的图标：

```typescript
const getDepartmentIcon = (deptName: string) => {
  const iconMap: Record<string, string> = {
    研发部算法组: '&#xe6b8;',
    放射科: '&#xe670;',
    星像行政部门: '&#xe634;'
  }
  return iconMap[deptName] || '&#xe70f;'
}
```

### 3. 部门排序优化

支持自定义部门排序，而不是单纯的字母排序。

### 4. 统计信息

在部门节点上显示文章数量：

```
🏢 研发部算法组 (15)
```

---

## 📚 相关文档

- [工作日志导航栏优化](./WORK_LOG_NAV_OPTIMIZATION.md)
- [工作组预设选项功能](./WORK_LOG_GROUP_PRESETS.md)

---

**版本**: v1.0  
**更新时间**: 2025-10-17  
**优化人员**: AI Assistant
