# 工作日志导航栏优化

## 📋 需求说明

### 用户需求

1. **三层导航结构**：

   - 第一级：使用工作组进行分组
   - 第二级：按年月分组
   - 第三级：具体的工作周

2. **点击展开**：点击分组节点可以直接展开/收起，无需点击箭头

3. **创建优化**：创建不同分组的工作周时，周序号应该基于当前选择的工作组的最新周序号

---

## ✅ 实现方案

### 1. 三层树结构

#### 1.1 工作组提取

新增 `extractGroupName` 函数，从工作周标题中提取工作组名称：

```typescript
// 从标题中提取工作组名称
const extractGroupName = (title: string): string => {
  // 匹配格式：2025W50标注组工作计划 -> 标注组
  const match = title.match(/\d{4}W\d{2}(.+?)工作计划/)
  return match ? match[1] : '其他'
}
```

**示例**：

- `2025W50标注组工作计划` → `标注组`
- `2025W51算法组工作计划` → `算法组`
- `其他工作周` → `其他`

#### 1.2 树结构构建

修改 `buildTree` 函数，构建三层结构：

```typescript
// 构建树形数据结构（三层：工作组 > 年月 > 工作周）
const buildTree = () => {
  // 第一层：按工作组分组
  const workGroups: Record<string, any[]> = {}

  sortedWeeks.forEach((week) => {
    const groupName = extractGroupName(week.title)
    if (!workGroups[groupName]) {
      workGroups[groupName] = []
    }
    workGroups[groupName].push(week)
  })

  // 构建三层树结构
  treeData.value = groupNames.map((groupName) => {
    const groupWeeks = workGroups[groupName]

    // 第二层：按年月分组
    const monthGroups: Record<string, any[]> = {}
    // ...按月份组织工作周...

    return {
      key: `group-${groupName}`,
      label: `${groupName}工作计划`,
      isWorkGroup: true, // 标记为工作组节点
      children: monthNodes
    }
  })
}
```

**树结构示例**：

```
标注组工作计划 (isWorkGroup: true)
  ├─ 2025年01月 (isGroup: true)
  │   ├─ 2025W01标注组工作计划 (isLeaf: true)
  │   └─ 2025W02标注组工作计划 (isLeaf: true)
  └─ 2024年12月 (isGroup: true)
      └─ 2024W52标注组工作计划 (isLeaf: true)
算法组工作计划 (isWorkGroup: true)
  └─ 2025年01月 (isGroup: true)
      └─ 2025W01算法组工作计划 (isLeaf: true)
```

---

### 2. 点击展开功能

#### 2.1 优化 onNodeClick

参考项目列表页面的实现，修改点击逻辑：

```typescript
// 树节点点击（支持点击展开）
const onNodeClick = (node: any) => {
  // 如果是叶子节点（工作周），直接选中
  if (node.isLeaf) {
    if (node.key !== currentWeekId.value) {
      currentWeekId.value = node.key
      currentWorkWeek.value = node.week
    }
    return
  }

  // 如果是分组节点（工作组或月份），切换展开/收起
  if (node.isWorkGroup || node.isGroup) {
    const treeInstance = treeRef.value
    const treeNode = treeInstance.getNode(node.key)

    if (treeNode.expanded) {
      // 已展开，收起
      treeInstance.store.nodesMap[node.key].expanded = false
      expandedKeys.value.splice(expandedKeys.value.indexOf(node.key), 1)
    } else {
      // 未展开，展开
      treeInstance.store.nodesMap[node.key].expanded = true
      expandedKeys.value.push(node.key)

      // 如果是工作组节点，自动展开第一个月份
      if (node.isWorkGroup && node.children && node.children.length > 0) {
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

**关键点**：

- ✅ 点击工作组节点：展开/收起，并自动展开第一个月份
- ✅ 点击月份节点：展开/收起
- ✅ 点击工作周节点：选中并显示详情
- ✅ 无需点击箭头图标

---

### 3. 创建工作周优化

#### 3.1 智能初始化

修改 `initializeCreateForm` 函数，基于当前选择的工作组初始化：

```typescript
// 初始化表单（基于当前选择的工作组或最新工作周）
const initializeCreateForm = () => {
  let targetGroupName = '标注组' // 默认工作组
  let targetWeek: WorkWeek | null = null

  if (workWeeks.value.length > 0) {
    // 尝试从当前选择的工作周获取工作组
    if (currentWorkWeek.value) {
      targetGroupName = extractGroupName(currentWorkWeek.value.title)

      // 在同一工作组中找到最新的工作周
      const sameGroupWeeks = workWeeks.value
        .filter((w) => extractGroupName(w.title) === targetGroupName)
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

      targetWeek = sameGroupWeeks[0]
    } else {
      // 没有选中，使用整体最新的
      targetWeek = workWeeks.value[0]
      targetGroupName = extractGroupName(targetWeek.title)
    }

    if (targetWeek) {
      // 解析标题并设置为下一周
      const match = latestTitle.match(/(\d{4})W(\d{2})(.+?)工作计划/)
      if (match) {
        const year = parseInt(match[1])
        const weekNum = parseInt(match[2])
        const groupName = match[3]

        // 设置为下一周
        createForm.value.year = weekNum >= 52 ? year + 1 : year
        createForm.value.weekNumber = weekNum >= 52 ? 1 : weekNum + 1
        createForm.value.groupName = groupName
      }
    }
  }

  // 生成标题和日期
  generateTitle()
  const dateRange = getWeekDateRange(createForm.value.year, createForm.value.weekNumber)
  createForm.value.startDate = new Date(dateRange.start)
}
```

**优化效果**：

| 场景                 | 优化前               | 优化后                        |
| -------------------- | -------------------- | ----------------------------- |
| **选中标注组W50**    | 创建时使用整体最新周 | 基于标注组最新周（W50+1=W51） |
| **选中算法组W03**    | 创建时使用整体最新周 | 基于算法组最新周（W03+1=W04） |
| **未选中任何工作周** | 使用整体最新周       | 使用整体最新周                |
| **首次创建**         | 使用当前日期         | 使用当前日期                  |

**示例场景**：

```
系统中已有：
- 标注组: 2025W50, 2025W51, 2025W52
- 算法组: 2025W01, 2025W02, 2025W03

用户操作：
1. 选中"2025W51标注组工作计划"
2. 点击"创建工作周"
3. 系统自动填充：
   - 工作组：标注组
   - 周序号：53 (52的下一周)
   - 标题：2025W53标注组工作计划

用户操作：
1. 选中"2025W02算法组工作计划"
2. 点击"创建工作周"
3. 系统自动填充：
   - 工作组：算法组
   - 周序号：04 (03的下一周)
   - 标题：2025W04算法组工作计划
```

---

### 4. UI优化

#### 4.1 树节点模板

更新树节点模板，支持三种节点类型的不同显示：

```vue
<template #default="{ data }">
  <!-- 工作周叶子节点 -->
  <template v-if="data.isLeaf">
    <el-tooltip placement="right" :content="`${data.dateRange} · ${data.statusText}`">
      <span class="tree-leaf" :class="{ active: data.key === currentWeekId }">
        {{ data.label }}
      </span>
    </el-tooltip>
  </template>

  <!-- 工作组节点（第一级） -->
  <template v-else-if="data.isWorkGroup">
    <span class="tree-work-group">
      <i class="iconfont" style="margin-right: 6px;">&#xe761;</i>
      {{ data.label }}
    </span>
  </template>

  <!-- 月份分组节点（第二级） -->
  <template v-else-if="data.isGroup">
    <span class="tree-month-group">
      <i class="iconfont" style="margin-right: 6px;">&#xe623;</i>
      {{ data.label }}
    </span>
  </template>
</template>
```

#### 4.2 样式优化

为三种节点类型定义不同的样式：

```scss
// 工作组节点样式（第一级）
.tree-work-group {
  font-weight: 700;
  color: #1f2937;
  font-size: 15px;
  user-select: none;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;

  .iconfont {
    color: #667eea; // 紫色图标
    font-size: 16px;
  }
}

// 月份分组节点样式（第二级）
.tree-month-group {
  font-weight: 500;
  color: #4b5563;
  font-size: 14px;
  user-select: none;
  letter-spacing: 0.3px;
  display: flex;
  align-items: center;

  .iconfont {
    color: #9ca3af; // 灰色图标
    font-size: 14px;
  }
}

// 工作周叶子节点（第三级）
.tree-leaf {
  font-size: 14px;
  color: #1f2937;
  padding: 8px 12px;
  margin-left: 4px;
  border-radius: 8px;
  display: block;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f0f7ff;
    color: #409eff;
    transform: translateX(2px);
  }

  &.active {
    background: linear-gradient(90deg, #e6f4ff 0%, #f0f7ff 100%);
    color: #1890ff;
    font-weight: 500;
  }
}
```

---

## 📊 修改对比

### 修改前的结构

```
2025-01 (第一级)
  ├─ 2025W01标注组工作计划
  ├─ 2025W02标注组工作计划
  └─ 2025W01算法组工作计划
2024-12 (第一级)
  └─ 2024W52标注组工作计划
```

### 修改后的结构

```
标注组工作计划 (第一级)
  ├─ 2025年01月 (第二级)
  │   ├─ 2025W01标注组工作计划 (第三级)
  │   └─ 2025W02标注组工作计划 (第三级)
  └─ 2024年12月 (第二级)
      └─ 2024W52标注组工作计划 (第三级)
算法组工作计划 (第一级)
  └─ 2025年01月 (第二级)
      └─ 2025W01算法组工作计划 (第三级)
```

---

## 🎯 优化效果

| 功能           | 优化前         | 优化后               |
| -------------- | -------------- | -------------------- |
| **分组方式**   | 按年月分组     | 按工作组 > 年月分组  |
| **点击展开**   | 必须点击箭头   | 点击节点即可展开     |
| **创建工作周** | 基于整体最新周 | 基于当前工作组最新周 |
| **视觉层次**   | 两层结构       | 三层结构，更清晰     |
| **工作组识别** | 无             | 自动提取和分组       |

---

## 🔄 修改文件列表

### 修改的文件（1个）

- `src/views/work-log/index.vue`
  - 新增 `extractGroupName` 函数
  - 重构 `buildTree` 函数（三层结构）
  - 优化 `onNodeClick` 函数（点击展开）
  - 优化 `initializeCreateForm` 函数（智能初始化）
  - 更新树节点模板（支持三种节点类型）
  - 新增节点样式（三种节点的差异化样式）
  - 修复lint错误（`getUsersBasic` 参数）

---

## 🚀 使用说明

### 1. 查看工作周

1. **展开工作组**：

   - 点击"标注组工作计划"节点
   - 自动展开并显示第一个月份

2. **展开月份**：

   - 点击"2025年01月"节点
   - 展开并显示该月的所有工作周

3. **选中工作周**：
   - 点击"2025W01标注组工作计划"
   - 右侧显示该工作周的详情

### 2. 创建工作周

1. **选中某个工作周**（如：2025W02标注组工作计划）
2. 点击"创建工作周"按钮
3. 系统自动填充：
   - 工作组：标注组（继承自选中工作周）
   - 周序号：03（标注组最新周+1）
   - 标题：2025W03标注组工作计划
4. 可以手动修改工作组名称以创建不同工作组的工作周

### 3. 批量创建

批量创建时，周序号会依次递增：

- 2025W03标注组工作计划
- 2025W04标注组工作计划
- 2025W05标注组工作计划
- ...

---

## 📝 注意事项

### 1. 工作周标题格式

**必须遵守的格式**：`{年份}W{周序号}{工作组名}工作计划`

**示例**：

- ✅ `2025W01标注组工作计划`
- ✅ `2025W52算法组工作计划`
- ✅ `2025W01研发组工作计划`
- ❌ `标注组2025W01工作计划`（格式不正确）
- ❌ `工作计划2025W01`（格式不正确）

**提取逻辑**：

```typescript
const match = title.match(/\d{4}W\d{2}(.+?)工作计划/)
// 匹配：年份(4位数字) + W + 周序号(2位数字) + 工作组名 + "工作计划"
```

### 2. 工作组名称

- 工作组名称会从标题中自动提取
- 无法提取时默认为"其他"
- 建议使用有意义的工作组名称：标注组、算法组、研发组等

### 3. 周序号

- 周序号范围：1-53
- 超过53周时自动跨年
- 创建时会自动计算下一周的周序号

---

## 🐛 已知问题

无

---

## 📚 相关文档

- [工作日志系统文档](./WORK_LOG_SYSTEM.md)
- [项目管理导航栏实现](./PROJECT_NAV_IMPLEMENTATION.md)

---

**版本**: v1.0  
**更新时间**: 2025-10-17  
**优化人员**: AI Assistant
