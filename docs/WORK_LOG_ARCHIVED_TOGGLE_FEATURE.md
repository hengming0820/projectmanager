# 🔄 工作周归档过滤功能

> 🗓️ **开发日期**: 2025-10-27  
> ✨ **功能**: 添加切换开关控制是否显示已归档的工作周  
> ✅ **状态**: 已完成

---

## 🎯 功能概述

在工作日志管理页面的左侧导航栏中添加一个切换开关，用户可以选择是否显示已归档（archived）的工作周。默认情况下，已归档的工作周会被隐藏，保持界面整洁，只显示活跃的工作周。

---

## ✨ 核心特性

### 1️⃣ 开关控制

- **位置**：左侧导航栏的筛选区域，搜索框下方
- **类型**：`el-switch` 开关组件
- **文本**：
  - 开启时：「显示已归档」
  - 关闭时：「隐藏已归档」
- **默认状态**：关闭（隐藏已归档）

### 2️⃣ 智能过滤

- **关闭开关**：只显示 `status !== 'archived'` 的工作周
- **开启开关**：显示所有工作周（包括已归档）
- **实时更新**：切换后立即重新构建树形结构

### 3️⃣ 智能选择处理

当关闭「显示已归档」时，如果当前选中的工作周是已归档状态：

1. 自动清空当前选择
2. 尝试选中第一个活跃工作周
3. 如果没有活跃工作周，则显示空状态

---

## 🖼️ UI 设计

### 位置布局

```
┌────────────────────────────┐
│  工作日志管理              │
│  [批量管理] [创建] [刷新]  │
└────────────────────────────┘

┌─ 左侧导航 ────────────────┐
│                            │
│  [搜索工作周...]           │  ← 搜索框
│                            │
│  ┌──────────────────────┐ │
│  │ [○] 隐藏已归档       │ │  ← 切换开关（关闭状态）
│  └──────────────────────┘ │
│                            │
│  📋 标注组工作计划         │  ← 工作组
│    └─ 2025年10月           │  ← 月份
│        ├─ 2025W43标注组... │  ← 工作周
│        └─ 2025W44标注组... │
│                            │
└────────────────────────────┘
```

### 开关状态

**关闭状态（默认）**：

```
┌──────────────────────┐
│ [○] 隐藏已归档       │  ← 灰色，只显示活跃工作周
└──────────────────────┘
```

**开启状态**：

```
┌──────────────────────┐
│ [●] 显示已归档       │  ← 蓝色，显示所有工作周
└──────────────────────┘
```

---

## 🔧 技术实现

### 1. 数据结构

```typescript
// 是否显示已归档的工作周（默认关闭）
const showArchivedWeeks = ref(false)
```

### 2. 模板部分

```vue
<div class="filter-section">
  <!-- 搜索框 -->
  <el-input
    v-model="filterSearch"
    placeholder="搜索工作周..."
    clearable
    size="small"
    :prefix-icon="Search"
  />

  <!-- 显示已归档工作周的开关 -->
  <div class="archived-toggle">
    <el-switch
      v-model="showArchivedWeeks"
      size="small"
      active-text="显示已归档"
      inactive-text="隐藏已归档"
      @change="onArchivedToggleChange"
    />
  </div>
</div>
```

### 3. 核心逻辑

#### 构建树时过滤

```typescript
const buildTree = () => {
  // 按创建时间倒序排序
  let sortedWeeks = [...workWeeks.value].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  // ⭐ 如果不显示已归档的工作周，则过滤掉它们
  if (!showArchivedWeeks.value) {
    sortedWeeks = sortedWeeks.filter((week) => week.status !== 'archived')
  }

  // ... 后续构建树的逻辑
}
```

#### 切换处理函数

```typescript
const onArchivedToggleChange = (value: string | number | boolean) => {
  // 类型守卫：确保是布尔值
  if (typeof value !== 'boolean') {
    console.warn('⚠️ [WorkLog] 无效的切换值类型:', value)
    return
  }

  console.log('🔄 [WorkLog] 切换显示已归档工作周:', value)

  // 重新构建树（会根据 showArchivedWeeks 的值进行过滤）
  buildTree()

  // 如果关闭显示已归档，且当前选中的工作周是已归档状态
  if (!value && currentWorkWeek.value?.status === 'archived') {
    console.log('⚠️ [WorkLog] 当前选中的工作周是已归档状态，清空选择')

    // 清空当前选择
    currentWeekId.value = ''
    currentWorkWeek.value = null

    // 尝试选中第一个非归档的工作周
    const activeWeeks = workWeeks.value.filter((w) => w.status !== 'archived')
    if (activeWeeks.length > 0) {
      const firstActiveWeek = activeWeeks[0]
      currentWeekId.value = firstActiveWeek.id
      currentWorkWeek.value = firstActiveWeek
      console.log('✅ [WorkLog] 已自动选中第一个活跃工作周:', firstActiveWeek.title)
    }
  }
}
```

### 4. 样式设计

```scss
.filter-section {
  margin-bottom: 16px;

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .archived-toggle {
    margin-top: 12px;
    padding: 8px 12px;
    background: #f5f7fa; // 浅灰色背景
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;

    :deep(.el-switch) {
      .el-switch__label {
        font-size: 12px;
        color: #606266;
      }

      .el-switch__label.is-active {
        color: #409eff; // 激活时蓝色
      }
    }
  }
}
```

---

## 💡 使用场景

### 场景 1：日常使用（隐藏已归档）

**默认状态**：

- 开关关闭，只显示活跃的工作周
- 界面简洁，减少干扰
- 快速找到当前需要处理的工作周

**适用情况**：

- 日常查看和编辑工作日志
- 只关注当前进行中的工作
- 保持界面清爽整洁

### 场景 2：查找历史记录（显示已归档）

**开启开关**：

- 显示所有工作周，包括已归档
- 可以查看历史工作周的详情
- 回顾过往的工作记录

**适用情况**：

- 查找历史工作日志
- 复制往期工作内容作为参考
- 进行工作回顾和总结
- 导出历史数据

### 场景 3：归档操作

**操作流程**：

1. 开启「显示已归档」
2. 找到需要查看的已归档工作周
3. 查看详情或导出数据
4. 完成后关闭开关，恢复简洁视图

---

## 🎯 工作周状态说明

### 状态类型

| 状态   | 英文       | 说明                 | 显示规则     |
| ------ | ---------- | -------------------- | ------------ |
| 活跃   | `active`   | 正在进行中的工作周   | **总是显示** |
| 已归档 | `archived` | 已完成并归档的工作周 | 根据开关决定 |
| 草稿   | `draft`    | 未发布的工作周       | **总是显示** |

### 状态转换

```
draft (草稿)
    ↓
active (活跃)  ← 正常工作状态
    ↓
archived (已归档)  ← 归档后默认隐藏
```

---

## 🔍 边界情况处理

### 1. 当前选中工作周被隐藏

**场景**：

- 用户正在查看一个已归档的工作周
- 关闭「显示已归档」开关

**处理**：

1. 自动清空当前选择
2. 尝试选中第一个活跃工作周
3. 如果没有活跃工作周，显示空状态页

**用户体验**：

- 避免显示不存在的工作周详情
- 平滑过渡到合理的界面状态
- 提供清晰的日志输出便于调试

### 2. 所有工作周都已归档

**场景**：

- 所有工作周的状态都是 `archived`
- 开关处于关闭状态

**处理**：

- 左侧树形结构为空
- 右侧显示空状态提示
- 提示用户创建新的工作周

**UI 显示**：

```
┌─ 左侧导航 ────────────────┐
│                            │
│  (空)                      │
│                            │
└────────────────────────────┘

┌─ 右侧主内容 ──────────────┐
│                            │
│  🗂️ 暂无活跃工作周         │
│                            │
│  [创建第一个工作周]        │
│                            │
└────────────────────────────┘
```

### 3. 切换开关时树结构为空

**场景**：

- 关闭开关后没有活跃工作周
- 或开启开关后仍然没有任何工作周

**处理**：

- 正常重新构建树结构
- 显示空状态
- 不会报错或卡顿

---

## 📊 性能优化

### 1. 过滤逻辑

```typescript
// ✅ 好的做法：在构建树之前过滤
if (!showArchivedWeeks.value) {
  sortedWeeks = sortedWeeks.filter((week) => week.status !== 'archived')
}

// ❌ 不好的做法：在渲染时过滤
// 这会导致每次渲染都重新计算
```

**优点**：

- 一次性过滤，避免重复计算
- 减少树节点数量，提升渲染性能
- 降低内存占用

### 2. 批量操作

当有大量工作周时：

- 排序：O(n log n)
- 过滤：O(n)
- 构建树：O(n)

**总体时间复杂度**：O(n log n)，性能良好

---

## 🧪 测试要点

### 功能测试

- [x] 开关默认关闭，只显示活跃工作周
- [x] 开启开关后显示所有工作周（包括已归档）
- [x] 关闭开关后已归档工作周从列表中消失
- [x] 切换开关时树结构正确更新
- [x] 当前选中的已归档工作周在关闭开关后自动切换

### 边界测试

- [x] 所有工作周都已归档时的表现
- [x] 没有任何工作周时的表现
- [x] 切换开关时没有活跃工作周的表现
- [x] 快速多次切换开关不会出错

### UI 测试

- [x] 开关样式正确显示
- [x] 开关文本正确切换
- [x] 开关背景色正确变化
- [x] 切换动画流畅

### 性能测试

- [x] 大量工作周（100+）时切换开关的响应速度
- [x] 多次快速切换不会卡顿
- [x] 内存占用正常

---

## 📝 用户反馈

### 优点

- ✅ **界面简洁**：默认隐藏已归档，保持界面整洁
- ✅ **操作便捷**：一键切换，快速查看历史记录
- ✅ **体验流畅**：智能处理选中状态，无需手动调整
- ✅ **功能实用**：满足日常使用和历史查询两种需求

### 改进建议

- 💡 可以考虑记住用户的开关状态（localStorage）
- 💡 可以添加已归档工作周的数量统计
- 💡 可以支持更多状态的过滤（如只显示草稿）

---

## 🔮 未来优化

### 1. 记住用户偏好

```typescript
// 保存开关状态到 localStorage
watch(showArchivedWeeks, (newValue) => {
  localStorage.setItem('showArchivedWeeks', JSON.stringify(newValue))
})

// 初始化时读取
onMounted(() => {
  const saved = localStorage.getItem('showArchivedWeeks')
  if (saved !== null) {
    showArchivedWeeks.value = JSON.parse(saved)
  }
})
```

### 2. 统计信息

在开关旁边显示统计：

```
[○] 隐藏已归档 (3个已隐藏)
```

### 3. 多状态过滤

扩展为下拉框，支持更多过滤选项：

- 只显示活跃
- 显示所有
- 只显示草稿
- 只显示已归档

---

## 📄 修改文件

| 文件                                 | 修改内容         | 行数变化 |
| ------------------------------------ | ---------------- | -------- |
| `src/views/work-log/index.vue`       | 模板、逻辑、样式 | +50 行   |
| `src/views/work-log/week-detail.vue` | 归档后刷新逻辑   | +4 行    |

### 具体修改点

#### index.vue

1. **模板部分（50-58 行）**

   - 在筛选区域添加切换开关
   - 使用 `el-switch` 组件
   - 绑定 `showArchivedWeeks` 变量

2. **逻辑部分**

   - 添加 `showArchivedWeeks` ref（583 行）
   - 修改 `buildTree` 函数，添加过滤逻辑（697-700 行）
   - 添加 `onArchivedToggleChange` 函数（838-864 行）

3. **样式部分（1714-1733 行）**
   - 添加 `.archived-toggle` 样式
   - 优化开关组件的文本样式
   - 激活状态的颜色处理

#### week-detail.vue

1. **归档操作（1018-1051 行）**

   - `handleArchiveWeek` 函数添加 `emit('refresh')` 通知父组件
   - 归档成功后立即刷新父组件的工作周列表

2. **恢复归档操作（1054-1087 行）**
   - `handleUnarchiveWeek` 函数添加 `emit('refresh')` 通知父组件
   - 恢复成功后立即刷新父组件的工作周列表

---

## 🔄 归档后自动刷新

### 问题描述

归档工作周后，左侧导航栏不会立即刷新，已归档的工作周仍然显示在列表中（如果开关处于关闭状态）。

### 解决方案

在 `week-detail.vue` 组件中，归档/恢复操作成功后，通知父组件刷新工作周列表：

```typescript
// 归档工作周
const handleArchiveWeek = async () => {
  // ... 归档逻辑

  await workWeekApi.updateWorkWeek(workWeek.value.id, {
    status: 'archived'
  })

  ElMessage.success('归档成功')
  await refreshData() // 刷新当前工作周数据

  // ⭐ 通知父组件刷新工作周列表
  emit('refresh')
  console.log('✅ [WorkLogDetail] 已通知父组件刷新工作周列表')
}

// 恢复归档
const handleUnarchiveWeek = async () => {
  // ... 恢复逻辑

  await workWeekApi.updateWorkWeek(workWeek.value.id, {
    status: 'active'
  })

  ElMessage.success('恢复成功')
  await refreshData() // 刷新当前工作周数据

  // ⭐ 通知父组件刷新工作周列表
  emit('refresh')
  console.log('✅ [WorkLogDetail] 已通知父组件刷新工作周列表')
}
```

### 刷新流程

```
用户点击「归档工作周」
    ↓
handleArchiveWeek() 更新状态为 archived
    ↓
emit('refresh') 触发父组件刷新
    ↓
index.vue 接收到 refresh 事件
    ↓
loadWorkWeeks() 重新加载工作周数据
    ↓
buildTree() 重新构建树结构
    ↓
根据 showArchivedWeeks 过滤已归档工作周
    ↓
导航栏立即更新显示
```

### 父子组件通信

**父组件 (index.vue)**：

```vue
<WorkLogWeekDetail
  :key="currentWeekId"
  :week-id="currentWeekId"
  @refresh="loadWorkWeeks"
  ←
  监听
  refresh
  事件
/>
```

**子组件 (week-detail.vue)**：

```typescript
// 定义事件
const emit = defineEmits<{
  refresh: []
}>()

// 触发事件
emit('refresh')
```

---

## 🎓 技术要点

### 1. TypeScript 类型安全

```typescript
// el-switch 的 @change 事件参数类型
const onArchivedToggleChange = (value: string | number | boolean) => {
  // 类型守卫
  if (typeof value !== 'boolean') {
    return
  }
  // ... 后续处理
}
```

### 2. 响应式更新

```typescript
// 修改 showArchivedWeeks 会触发 buildTree
// buildTree 会重新过滤和构建树结构
// Vue 会自动更新视图
```

### 3. 边界处理

```typescript
// 智能处理当前选中的工作周
if (!value && currentWorkWeek.value?.status === 'archived') {
  // 清空选择并尝试选中活跃工作周
}
```

---

## 📚 相关文档

- `WORK_WEEK_IMPROVEMENTS.md` - 工作周管理优化
- `WORK_LOG_SUBJECT_TAG_FEATURE.md` - 工作标题快速选择功能
- `README.md` - 项目总体说明

---

**🎉 功能已完成，工作周列表支持归档过滤，界面更整洁，历史查询更方便！**
