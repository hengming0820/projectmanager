# 工作组预设选项功能

## 📋 功能说明

### 用户需求

在创建工作周时：

1. 提供预设的工作组选项（算法组、标注组、开发组、行政组）
2. 每个工作组的周序号独立维护
3. 切换工作组时，自动更新周序号为该工作组的最新周序号+1
4. 支持自定义输入新的工作组名称

---

## ✅ 实现方案

### 1. 预设工作组配置

定义预设工作组列表，包含图标和颜色：

```typescript
// 预设工作组列表
const PRESET_WORK_GROUPS = [
  { value: '标注组', label: '标注组', icon: '&#xe70f;', color: '#667eea' },
  { value: '算法组', label: '算法组', icon: '&#xe6b8;', color: '#f59e0b' },
  { value: '开发组', label: '开发组', icon: '&#xe666;', color: '#10b981' },
  { value: '行政组', label: '行政组', icon: '&#xe634;', color: '#ec4899' }
]
```

**工作组配置说明**：

| 工作组     | 图标 | 颜色           | 用途             |
| ---------- | ---- | -------------- | ---------------- |
| **标注组** | 📋   | 紫色 (#667eea) | 医学影像标注工作 |
| **算法组** | 🧮   | 橙色 (#f59e0b) | 算法开发和优化   |
| **开发组** | 💻   | 绿色 (#10b981) | 系统开发和维护   |
| **行政组** | 📁   | 粉色 (#ec4899) | 行政管理工作     |

---

### 2. 独立周序号管理

新增函数 `getGroupLatestWeekNumber`，为每个工作组独立管理周序号：

```typescript
// 获取指定工作组的最新周序号
const getGroupLatestWeekNumber = (groupName: string): { year: number; weekNumber: number } => {
  // 过滤出该工作组的所有工作周
  const groupWeeks = workWeeks.value
    .filter((w) => extractGroupName(w.title) === groupName)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  if (groupWeeks.length > 0) {
    const latestWeek = groupWeeks[0]
    const match = latestWeek.title.match(/(\d{4})W(\d{2})(.+?)工作计划/)
    if (match) {
      const year = parseInt(match[1])
      const weekNum = parseInt(match[2])

      // 返回下一周
      return {
        year: weekNum >= 52 ? year + 1 : year,
        weekNumber: weekNum >= 52 ? 1 : weekNum + 1
      }
    }
  }

  // 如果该工作组没有历史记录，返回当前日期的周信息
  const now = new Date()
  return {
    year: now.getFullYear(),
    weekNumber: getWeekNumber(now)
  }
}
```

**功能说明**：

- ✅ 查找指定工作组的所有工作周
- ✅ 获取该工作组的最新周序号
- ✅ 自动计算下一周序号（处理跨年情况）
- ✅ 新工作组默认使用当前日期的周序号

---

### 3. UI组件优化

#### 3.1 工作组选择器

将原来的输入框改为 `el-select` 组件，支持选择和输入：

```vue
<el-form-item label="工作组">
  <el-select 
    v-model="createForm.groupName" 
    placeholder="选择或输入工作组名称"
    filterable          <!-- 支持搜索 -->
    allow-create        <!-- 支持创建新选项 -->
    default-first-option <!-- 默认选中第一项 -->
    style="width: 100%;"
    @change="handleGroupNameChange"
  >
    <el-option
      v-for="group in PRESET_WORK_GROUPS"
      :key="group.value"
      :label="group.label"
      :value="group.value"
    >
      <div style="display: flex; align-items: center; gap: 8px;">
        <i 
          class="iconfont" 
          :style="{ color: group.color, fontSize: '16px' }"
          v-html="group.icon"
        ></i>
        <span>{{ group.label }}</span>
      </div>
    </el-option>
  </el-select>
  <div style="margin-top: 6px; color: #909399; font-size: 12px;">
    可选择预设工作组或输入自定义名称
  </div>
</el-form-item>
```

**特点**：

- ✅ 下拉选择预设工作组
- ✅ 显示图标和颜色
- ✅ 支持搜索过滤
- ✅ 支持手动输入自定义名称

#### 3.2 自动更新周序号

修改 `handleGroupNameChange` 函数，切换工作组时自动更新：

```typescript
// 处理工作组名称变化
const handleGroupNameChange = (value: string) => {
  // 更新工作组名称
  createForm.value.groupName = value

  // 获取该工作组的最新周序号并更新
  const { year, weekNumber } = getGroupLatestWeekNumber(value)
  createForm.value.year = year
  createForm.value.weekNumber = weekNumber

  // 更新起始日期
  const dateRange = getWeekDateRange(year, weekNumber)
  createForm.value.startDate = new Date(dateRange.start)

  // 重新生成标题
  generateTitle()
}
```

**自动更新内容**：

- ✅ 年份
- ✅ 周序号
- ✅ 起始日期
- ✅ 标题预览

---

## 📊 功能演示

### 场景1：首次创建不同工作组的工作周

**系统中无任何工作周**

| 选择工作组 | 自动填充                              |
| ---------- | ------------------------------------- |
| 标注组     | 2025W03标注组工作计划（当前日期的周） |
| 算法组     | 2025W03算法组工作计划（当前日期的周） |
| 开发组     | 2025W03开发组工作计划（当前日期的周） |
| 行政组     | 2025W03行政组工作计划（当前日期的周） |

---

### 场景2：已有工作周的情况

**系统中已有工作周**：

- 标注组: 2025W01, 2025W02, 2025W03
- 算法组: 2025W01, 2025W02
- 开发组: 2025W01

**用户操作**：

#### 步骤1：选择"标注组"

```
自动填充：
- 年份：2025
- 周序号：04（标注组最新周W03 + 1）
- 标题：2025W04标注组工作计划
- 起始日期：2025-01-22（自动计算）
```

#### 步骤2：切换到"算法组"

```
自动更新：
- 年份：2025
- 周序号：03（算法组最新周W02 + 1）
- 标题：2025W03算法组工作计划
- 起始日期：2025-01-15（自动计算）
```

#### 步骤3：切换到"开发组"

```
自动更新：
- 年份：2025
- 周序号：02（开发组最新周W01 + 1）
- 标题：2025W02开发组工作计划
- 起始日期：2025-01-06（自动计算）
```

#### 步骤4：切换到"行政组"

```
自动更新：
- 年份：2025
- 周序号：03（行政组无历史，使用当前周）
- 标题：2025W03行政组工作计划
- 起始日期：2025-01-15（自动计算）
```

---

### 场景3：自定义工作组

**步骤1**：在工作组下拉框中输入"测试组"（回车确认）

```
自动填充：
- 年份：2025
- 周序号：03（测试组无历史，使用当前周）
- 标题：2025W03测试组工作计划
- 起始日期：2025-01-15（自动计算）
```

**步骤2**：创建成功后，再次选择"测试组"

```
自动填充：
- 年份：2025
- 周序号：04（测试组最新周W03 + 1）
- 标题：2025W04测试组工作计划
- 起始日期：2025-01-22（自动计算）
```

---

### 场景4：跨年处理

**系统中已有**：标注组 2024W52

**用户操作**：选择"标注组"

```
自动填充：
- 年份：2025（自动跨年）
- 周序号：01（52 + 1 = 53 > 52，重置为01）
- 标题：2025W01标注组工作计划
- 起始日期：2025-01-01（自动计算）
```

---

## 🎯 优化效果

### 优化前

| 项目       | 状态                     |
| ---------- | ------------------------ |
| 工作组输入 | 手动输入，容易出错       |
| 周序号管理 | 统一管理，无法区分工作组 |
| 用户体验   | 需要记住各组的最新周序号 |
| 灵活性     | 低                       |

### 优化后

| 项目       | 状态                          |
| ---------- | ----------------------------- |
| 工作组输入 | 下拉选择 + 图标显示，清晰直观 |
| 周序号管理 | 每个工作组独立管理            |
| 用户体验   | 自动计算，无需手动输入        |
| 灵活性     | 支持预设工作组 + 自定义工作组 |

---

## 🔄 修改文件列表

### 修改的文件（1个）

- `src/views/work-log/index.vue`
  - 新增 `PRESET_WORK_GROUPS` 常量（预设工作组列表）
  - 新增 `getGroupLatestWeekNumber` 函数（获取工作组最新周序号）
  - 修改 `handleGroupNameChange` 函数（支持自动更新）
  - 修改工作组表单项（输入框 → 选择器）

---

## 📝 使用说明

### 1. 创建工作周

#### 方式1：选择预设工作组

1. 点击"创建工作周"按钮
2. 在"工作组"下拉框中选择一个预设工作组
3. 系统自动填充该工作组的下一周序号
4. 检查并确认其他信息
5. 点击"创建"

#### 方式2：输入自定义工作组

1. 点击"创建工作周"按钮
2. 在"工作组"下拉框中输入自定义名称（如："研发组"）
3. 按 Enter 确认
4. 系统自动使用当前日期的周序号
5. 检查并确认其他信息
6. 点击"创建"

### 2. 批量创建

选择工作组后，启用"批量创建"模式：

1. 选择工作组（如：标注组，当前最新W03）
2. 勾选"批量创建"
3. 设置批量数量（如：4）
4. 系统自动生成：
   - 2025W04标注组工作计划
   - 2025W05标注组工作计划
   - 2025W06标注组工作计划
   - 2025W07标注组工作计划

---

## 🔍 技术细节

### 周序号独立管理原理

```typescript
// 系统中的工作周数据
workWeeks = [
  { title: '2025W03标注组工作计划', ... },  // 标注组最新
  { title: '2025W02标注组工作计划', ... },
  { title: '2025W02算法组工作计划', ... },  // 算法组最新
  { title: '2025W01算法组工作计划', ... },
  { title: '2025W01开发组工作计划', ... }   // 开发组最新
]

// 选择"标注组"时
getGroupLatestWeekNumber('标注组')
  → 过滤: [2025W03标注组, 2025W02标注组]
  → 最新: 2025W03标注组
  → 下一周: 2025W04

// 选择"算法组"时
getGroupLatestWeekNumber('算法组')
  → 过滤: [2025W02算法组, 2025W01算法组]
  → 最新: 2025W02算法组
  → 下一周: 2025W03

// 选择"行政组"时（无历史记录）
getGroupLatestWeekNumber('行政组')
  → 过滤: []
  → 无历史记录
  → 使用当前日期: 2025W03
```

### 跨年处理

```typescript
// 假设当前是 2024W52
if (weekNum >= 52) {
  year = year + 1 // 2024 → 2025
  weekNumber = 1 // 52 + 1 = 53 → 01
} else {
  year = year // 保持不变
  weekNumber = weekNum + 1
}
```

---

## 🐛 已知问题

无

---

## 💡 未来优化建议

### 1. 动态工作组配置

将预设工作组配置移到后端数据库，支持管理员动态添加/编辑工作组。

### 2. 工作组权限

为不同工作组设置权限，只有特定角色才能创建特定工作组的工作周。

### 3. 工作组统计

在导航栏显示每个工作组的工作周数量和状态统计。

### 4. 工作组图标上传

支持管理员为工作组上传自定义图标。

---

## 📚 相关文档

- [工作日志导航栏优化](./WORK_LOG_NAV_OPTIMIZATION.md)
- [工作日志系统文档](./WORK_LOG_SYSTEM.md)

---

**版本**: v1.0  
**更新时间**: 2025-10-17  
**功能开发**: AI Assistant
