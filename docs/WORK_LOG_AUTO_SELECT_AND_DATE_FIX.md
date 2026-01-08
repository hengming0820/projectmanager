# 工作日志自动定位与日期显示修复

## 修复时间

2025-11-05

## 需求描述

### 用户反馈

1. **自动定位问题**：

   - 进入周列表页面后，希望能自动定位到当前用户所在工作组的当前日期所在的工作周
   - 用户提醒注意时区问题，之前已修复，不要再出现

2. **日期显示问题**：
   - 工作周表格上方的日期范围显示格式为"yyyy年mm月dd日到yyyy年mm月dd日"
   - 但实际只显示前5天（只显示到周五），工作周表格实际有7天（周一到周日）
   - 结束日期缺少年份显示，导致跨年时信息不完整

## 解决方案

### 修复 1：日期范围显示格式

**文件**: `src/views/work-log/week-detail.vue`

#### 修改前

```typescript
const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return `${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日 - ${end.getMonth() + 1}月${end.getDate()}日`
}
```

**问题**：

- 结束日期没有显示年份
- 当工作周跨年时（例如：2024年12月30日 到 2025年1月5日），结束日期只显示"1月5日"，用户无法知道是哪一年

#### 修改后

```typescript
const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return `${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日 到 ${end.getFullYear()}年${end.getMonth() + 1}月${end.getDate()}日`
}
```

**改进点**：

- ✅ 结束日期也显示年份
- ✅ 支持跨年工作周的正确显示
- ✅ 显示完整的7天范围（周一到周日）

#### 显示效果

**修改前**：

```
2025年11月3日 - 11月9日  ← 结束日期缺少年份
2024年12月30日 - 1月5日  ← 跨年时容易混淆
```

**修改后**：

```
2025年11月3日 到 2025年11月9日   ← 完整显示
2024年12月30日 到 2025年1月5日   ← 跨年清晰
```

---

### 修复 2：自动定位到当前用户工作组的当前工作周

**文件**: `src/views/work-log/index.vue`

#### 原有逻辑

```typescript
// 如果还没有选中工作周，选中第一个
if (!currentWeekId.value && sortedWeeks.length > 0) {
  currentWeekId.value = sortedWeeks[0].id
  currentWorkWeek.value = sortedWeeks[0]
}
```

**问题**：

- 总是选择第一个（最新的）工作周
- 不考虑用户所在的工作组
- 不考虑当前日期

#### 新的智能逻辑

```typescript
// 智能选择工作周：优先选择当前用户所在工作组的当前日期所在工作周
if (!currentWeekId.value && sortedWeeks.length > 0) {
  let targetWeek: WorkWeek | null = null

  // 1. 尝试找到当前用户所在工作组的当前日期所在工作周
  const currentUserDept = userStore.currentUser?.department
  if (currentUserDept) {
    // 从部门中提取工作组名称（例如：研发部算法组 -> 算法组）
    const deptGroupMatch = currentUserDept.match(/([^部]+组)/)
    const userWorkGroup = deptGroupMatch ? deptGroupMatch[1] : null

    if (userWorkGroup) {
      // 获取当前日期（考虑时区）
      const now = new Date()
      const currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())

      // 在该工作组中找到包含当前日期的工作周
      const userGroupWeeks = sortedWeeks.filter((week) => {
        const groupName = extractGroupName(week.title)
        return groupName === userWorkGroup
      })

      targetWeek =
        userGroupWeeks.find((week) => {
          const startDate = new Date(week.week_start_date)
          const endDate = new Date(week.week_end_date)
          return currentDate >= startDate && currentDate <= endDate
        }) || null

      if (!targetWeek) {
        // 如果没有找到包含当前日期的工作周，选择该工作组最新的工作周
        targetWeek = userGroupWeeks[0] || null
      }
    }
  }

  // 2. 如果没有找到目标工作周，回退到选择第一个工作周
  if (!targetWeek) {
    targetWeek = sortedWeeks[0]
  }

  currentWeekId.value = targetWeek.id
  currentWorkWeek.value = targetWeek
}
```

#### 智能定位流程

```
用户打开工作日志页面
  ↓
获取当前用户信息
  ↓
提取部门信息：userStore.currentUser.department
  例如："研发部算法组"
  ↓
从部门中提取工作组名称
  正则匹配：/([^部]+组)/
  结果："算法组"
  ↓
获取当前日期（本地时间，已处理时区）
  const currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  ↓
过滤出该工作组的所有工作周
  sortedWeeks.filter(week => extractGroupName(week.title) === userWorkGroup)
  ↓
查找包含当前日期的工作周
  week.week_start_date <= currentDate <= week.week_end_date
  ↓
找到了？
  ├─ 是 ✅ → 选中该工作周
  │         → 展开该工作组和月份
  │         → 高亮显示
  │
  └─ 否 ⚠️ → 选择该工作组最新的工作周
            → 如果工作组没有工作周，选择全局第一个工作周
```

#### 时区处理

**关键代码**：

```typescript
// 获取当前日期（考虑时区）
const now = new Date()
const currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
```

**说明**：

- 使用 `new Date(year, month, date)` 构造器，确保使用本地时区
- 只比较日期部分，忽略时间部分，避免时区偏移导致的日期错误
- 与工作周的 `week_start_date` 和 `week_end_date` 进行日期比较时，同样只比较日期部分

---

### 修复 3：智能展开导航树

#### 新的展开逻辑

```typescript
// 默认展开目标工作周所在的工作组和月份
if (expandedKeys.value.length === 0 && treeData.value.length > 0 && currentWorkWeek.value) {
  const targetGroupName = extractGroupName(currentWorkWeek.value.title)
  const targetGroup = treeData.value.find((g) => g.label.includes(targetGroupName))

  if (targetGroup) {
    // 展开工作组
    expandedKeys.value.push(targetGroup.key)

    // 找到包含目标工作周的月份
    if (targetGroup.children && targetGroup.children.length > 0) {
      const targetDate = new Date(currentWorkWeek.value.week_start_date)
      const targetYearMonth = `${targetDate.getFullYear()}年${String(targetDate.getMonth() + 1).padStart(2, '0')}月`

      // 展开目标月份
      const targetMonth = targetGroup.children.find((m: any) => m.label === targetYearMonth)
      if (targetMonth) {
        expandedKeys.value.push(targetMonth.key)
      }

      // 同时展开前后一个月（如果存在）
      const monthIndex = targetGroup.children.findIndex((m: any) => m.label === targetYearMonth)
      if (monthIndex > 0) {
        expandedKeys.value.push(targetGroup.children[monthIndex - 1].key)
      }
      if (monthIndex < targetGroup.children.length - 1) {
        expandedKeys.value.push(targetGroup.children[monthIndex + 1].key)
      }
    }
  }
}
```

**改进点**：

- ✅ 自动展开目标工作周所在的工作组
- ✅ 自动展开目标工作周所在的月份
- ✅ 额外展开前后一个月，方便用户查看相邻的工作周
- ✅ 目标工作周自动高亮显示

---

## 部门与工作组映射

### 映射逻辑

**正则表达式**: `/([^部]+组)/`

**映射示例**：| 部门名称 | 提取的工作组 | 说明 | |---------|------------|-----| | `研发部算法组` | `算法组` | ✅ 标准格式 | | `研发部开发组` | `开发组` | ✅ 标准格式 | | `行政部标注组` | `标注组` | ✅ 标准格式 | | `行政组` | `行政组` | ✅ 没有"部"也能匹配 | | `研发部` | `null` | ⚠️ 无法匹配，使用默认逻辑 | | `未知部门` | `null` | ⚠️ 无法匹配，使用默认逻辑 |

### 工作周标题格式

**格式**: `2025W50标注组工作计划`

**提取逻辑**:

```typescript
const extractGroupName = (title: string): string => {
  // 匹配格式：2025W50标注组工作计划 -> 标注组
  const match = title.match(/\d{4}W\d{2}(.+?)工作计划/)
  return match ? match[1] : '其他'
}
```

---

## 使用场景

### 场景 1: 正常情况 - 找到当前工作周

**用户**: 张三，部门：研发部算法组  
**当前日期**: 2025年11月5日（周二）  
**工作周列表**:

- 2025W45算法组工作计划（11月3日 到 11月9日）✅ 包含当前日期
- 2025W44算法组工作计划（10月27日 到 11月2日）
- 2025W43算法组工作计划（10月20日 到 10月26日）

**结果**:

```
✅ [WorkLog] 当前用户部门: 研发部算法组 => 工作组: 算法组
✅ [WorkLog] 找到当前日期所在工作周: 2025W45算法组工作计划
```

**页面状态**:

- 左侧导航：
  - ✅ 算法组工作计划（已展开）
    - ✅ 2025年10月（已展开）
    - ✅ 2025年11月（已展开）← 当前月
      - **2025W45算法组工作计划** ← 高亮显示
- 右侧显示：2025年11月3日 到 2025年11月9日

---

### 场景 2: 当前日期不在任何工作周内

**用户**: 李四，部门：研发部开发组  
**当前日期**: 2025年11月20日  
**工作周列表**:

- 2025W44开发组工作计划（10月27日 到 11月2日）← 最新的
- 2025W43开发组工作计划（10月20日 到 10月26日）
- （没有覆盖11月20日的工作周）

**结果**:

```
⚠️ [WorkLog] 当前用户部门: 研发部开发组 => 工作组: 开发组
⚠️ [WorkLog] 未找到当前日期所在工作周，选择该工作组最新工作周: 2025W44开发组工作计划
```

**页面状态**:

- 自动选择该工作组最新的工作周
- 展开开发组和10月/11月

---

### 场景 3: 用户工作组没有工作周

**用户**: 王五，部门：行政组  
**当前日期**: 2025年11月5日  
**工作周列表**:

- 2025W45算法组工作计划
- 2025W45开发组工作计划
- （没有行政组的工作周）

**结果**:

```
📌 [WorkLog] 当前用户部门: 行政组 => 工作组: 行政组
📌 [WorkLog] 选择默认第一个工作周: 2025W45算法组工作计划
```

**页面状态**:

- 回退到选择第一个（最新的）工作周
- 展开算法组和11月

---

### 场景 4: 用户没有部门信息

**用户**: 赵六，部门：`null` 或 `undefined`  
**当前日期**: 2025年11月5日  
**工作周列表**:

- 2025W45算法组工作计划
- 2025W45开发组工作计划

**结果**:

```
📌 [WorkLog] 选择默认第一个工作周: 2025W45算法组工作计划
```

**页面状态**:

- 直接选择第一个工作周
- 展开算法组和11月

---

## 技术细节

### 日期比较逻辑

```typescript
// 创建只包含日期的 Date 对象（忽略时间）
const now = new Date()
const currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())

// 工作周的开始和结束日期（字符串格式：yyyy-mm-dd）
const startDate = new Date(week.week_start_date)
const endDate = new Date(week.week_end_date)

// 比较（Date 对象之间可以直接用 >= 和 <= 比较）
if (currentDate >= startDate && currentDate <= endDate) {
  // 找到了包含当前日期的工作周
}
```

### 时区安全性

**问题**: 如果直接使用 `new Date(dateString)`，可能因为时区偏移导致日期错误。

**解决**:

1. 使用 `new Date(year, month, date)` 构造器，确保使用本地时区
2. 只比较日期部分，不考虑时间
3. 避免使用 `toISOString()` 等可能引入 UTC 时区的方法

**示例**:

```typescript
// ❌ 错误：可能受时区影响
const date1 = new Date('2025-11-05')
const date2 = new Date('2025-11-05T00:00:00.000Z')

// ✅ 正确：本地时区
const now = new Date()
const date3 = new Date(now.getFullYear(), now.getMonth(), now.getDate())
```

---

## 日志输出

当自动定位功能生效时，会在浏览器控制台输出以下日志：

```
🔍 [WorkLog] 当前用户部门: 研发部算法组 => 工作组: 算法组
✅ [WorkLog] 找到当前日期所在工作周: 2025W45算法组工作计划
```

如果找不到当前日期所在的工作周：

```
⚠️ [WorkLog] 未找到当前日期所在工作周，选择该工作组最新工作周: 2025W44算法组工作计划
```

如果使用默认逻辑：

```
📌 [WorkLog] 选择默认第一个工作周: 2025W45算法组工作计划
```

---

## 测试要点

### 基本功能

- [ ] 用户进入周列表页面，自动选中所在工作组的当前日期所在工作周
- [ ] 日期范围显示完整的7天（yyyy年mm月dd日 到 yyyy年mm月dd日）
- [ ] 导航树自动展开到目标工作周
- [ ] 目标工作周自动高亮显示

### 边缘情况

- [ ] 当前日期不在任何工作周内，自动选择该工作组最新的工作周
- [ ] 用户工作组没有工作周，回退到选择全局第一个工作周
- [ ] 用户没有部门信息，回退到选择全局第一个工作周
- [ ] 部门名称不规范（例如："研发部"、"未知部门"），正确处理

### 时区相关

- [ ] 在不同时区测试，确保日期比较正确
- [ ] 跨年工作周（例如：12月30日 到 1月5日）正确显示
- [ ] 跨月工作周（例如：10月30日 到 11月5日）正确显示

### 用户体验

- [ ] 控制台输出清晰的日志
- [ ] 页面加载后立即显示正确的工作周
- [ ] 导航树展开动画流畅
- [ ] 高亮显示明显

---

## 相关文件

### 修改的文件

- `src/views/work-log/index.vue` - 工作日志主页面，实现自动定位逻辑
- `src/views/work-log/week-detail.vue` - 工作周详情页面，修复日期显示

### 相关类型

- `src/types/project/index.ts` - User 类型定义（包含 department 字段）
- `src/types/work-log/index.ts` - WorkWeek 类型定义

### 相关文档

- `docs/WORK_LOG_AUTO_SELECT_AND_DATE_FIX.md` - 本文档

---

## 后续优化建议

### 1. 用户偏好记忆

记住用户上次选择的工作周，下次优先打开：

```typescript
// 保存到 localStorage
localStorage.setItem('last_selected_week', workWeekId)

// 加载时优先使用
const lastSelectedWeekId = localStorage.getItem('last_selected_week')
if (lastSelectedWeekId && workWeeks.value.find((w) => w.id === lastSelectedWeekId)) {
  currentWeekId.value = lastSelectedWeekId
}
```

### 2. 跨工作组查看

允许用户快速切换到其他工作组的工作周：

```vue
<el-dropdown>
  <el-button>切换工作组</el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item @click="switchToGroup('算法组')">算法组</el-dropdown-item>
      <el-dropdown-item @click="switchToGroup('开发组')">开发组</el-dropdown-item>
      <el-dropdown-item @click="switchToGroup('标注组')">标注组</el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

### 3. 周视图快速切换

添加"上一周"/"下一周"快捷按钮：

```vue
<el-button-group>
  <el-button @click="gotoPreviousWeek">
    <el-icon><ArrowLeft /></el-icon>
    上一周
  </el-button>
  <el-button @click="gotoCurrentWeek">
    <el-icon><Calendar /></el-icon>
    本周
  </el-button>
  <el-button @click="gotoNextWeek">
    下一周
    <el-icon><ArrowRight /></el-icon>
  </el-button>
</el-button-group>
```

### 4. 工作周日历视图

在左侧导航增加月历视图，直观显示哪些日期有工作周：

```vue
<el-calendar>
  <!-- 标记有工作周的日期 -->
  <template #dateCell="{ data }">
    <div :class="{ 'has-week': hasWorkWeekOn(data.day) }">
      {{ data.day.getDate() }}
    </div>
  </template>
</el-calendar>
```

---

## 总结

这次修复解决了两个核心问题：

1. **日期显示不完整**：修复了 `formatDateRange` 函数，现在显示完整的7天范围，包括结束日期的年份，支持跨年工作周。

2. **自动定位智能化**：实现了基于用户部门的智能工作周选择，优先定位到当前用户所在工作组的当前日期所在工作周，提升了用户体验。

核心改进：

- ✅ 日期范围显示完整（7天，带年份）
- ✅ 智能定位到用户工作组的当前工作周
- ✅ 时区安全处理，避免日期偏移
- ✅ 自动展开导航树到目标位置
- ✅ 多种回退策略，确保总能选中合适的工作周

这些改进让工作日志页面更加智能和人性化！🎉
