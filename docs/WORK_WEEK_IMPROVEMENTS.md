# 工作周创建功能优化

## ✅ 已完成的改进

### 1. 修复时区问题 - 工作周日期计算错误

**问题描述：**

- 用户报告：今天是 10月27日（周一），但创建的工作周显示 10月26日（周日）为周一
- 日期偏差 1 天

**根本原因：**

- 使用 `Date.toISOString()` 会将本地时间转换为 UTC 时间
- 中国时区（UTC+8）在凌晨 0-8 点之间会产生跨天问题
- `toISOString().split('T')[0]` 返回的是 UTC 日期，不是本地日期

**修复位置：**

#### 📁 `src/api/workLogApi.ts`

修复了 5 个日期相关的工具函数：

1. **`getCurrentWeekMonday()`** - 获取当前周的周一
2. **`getWeekMonday(date)`** - 获取指定日期所在周的周一
3. **`getWorkWeekDates(startDate)`** - 计算工作周的日期范围
4. **`formatWorkDate(date)`** - 格式化工作日期
5. **`validateWorkWeekDates(startDate, endDate)`** - 验证工作周日期范围

**修复方法：**

```typescript
// ❌ 之前：使用 UTC 时间
const date = new Date()
return date.toISOString().split('T')[0]

// ✅ 现在：使用本地时区
const year = date.getFullYear()
const month = String(date.getMonth() + 1).padStart(2, '0')
const day = String(date.getDate()).padStart(2, '0')
return `${year}-${month}-${day}`
```

#### 📁 `src/views/work-log/index.vue`

修复了 `getWeekDateRange()` 函数：

```typescript
// 根据ISO周计算日期范围（使用本地时区）
const getWeekDateRange = (year: number, week: number): { start: string; end: string } => {
  // ... 计算逻辑 ...

  // ✅ 使用本地时区格式化为 YYYY-MM-DD
  const formatLocalDate = (date: Date) => {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }

  return {
    start: formatLocalDate(weekStart),
    end: formatLocalDate(weekEnd)
  }
}
```

---

### 2. 添加按部门选择员工功能

**功能描述：**

- 在创建工作周和编辑工作周时，可以通过选择部门快速添加该部门的所有员工
- 支持多选部门
- 显示每个部门的人数
- 员工列表按部门分组显示

**实现位置：**

#### 📁 `src/views/work-log/index.vue`

##### 新增数据结构

```typescript
// 部门选择相关
const selectedDepartments = ref<string[]>([]) // 创建对话框的部门选择
const editSelectedDepartments = ref<string[]>([]) // 编辑对话框的部门选择

// 用户选项扩展为包含部门信息
const userOptions = ref<
  Array<{
    label: string
    value: string
    realName: string
    department: string
  }>
>([])
```

##### 新增计算属性

1. **`usersByDepartment`** - 按部门分组的用户列表（创建对话框）

   ```typescript
   const usersByDepartment = computed(() => {
     const grouped: Record<string, any[]> = {}
     userOptions.value.forEach((user) => {
       if (!grouped[user.department]) {
         grouped[user.department] = []
       }
       grouped[user.department].push(user)
     })
     return Object.entries(grouped).map(([department, users]) => ({
       department,
       users
     }))
   })
   ```

2. **`departmentOptions`** - 部门选项列表（创建对话框）

   ```typescript
   const departmentOptions = computed(() => {
     const depts = new Set<string>()
     userOptions.value.forEach((user) => {
       if (user.department) {
         depts.add(user.department)
       }
     })
     return Array.from(depts).sort()
   })
   ```

3. **`editUsersByDepartment`** - 按部门分组的用户列表（编辑对话框）
4. **`editDepartmentOptions`** - 部门选项列表（编辑对话框）

##### 新增方法

1. **`getDepartmentUserCount(dept)`** - 获取部门人数

   ```typescript
   const getDepartmentUserCount = (dept: string): number => {
     return userOptions.value.filter((u) => u.department === dept).length
   }
   ```

2. **`handleDepartmentSelect(departments)`** - 处理部门选择（创建对话框）

   ```typescript
   const handleDepartmentSelect = (departments: string[]) => {
     const userIds = new Set(createForm.value.coveredUserIds)

     departments.forEach((dept) => {
       const deptUsers = userOptions.value.filter((u) => u.department === dept)
       deptUsers.forEach((u) => userIds.add(u.value))
     })

     createForm.value.coveredUserIds = Array.from(userIds)
   }
   ```

3. **`handleEditDepartmentSelect(departments)`** - 处理部门选择（编辑对话框）
4. **`getEditDepartmentUserCount(dept)`** - 获取部门人数（编辑对话框）

##### UI 改进

**创建工作周对话框：**

```vue
<!-- 按部门选择 -->
<el-form-item label="按部门选择">
  <el-select
    v-model="selectedDepartments"
    multiple
    filterable
    collapse-tags
    placeholder="选择部门快速添加人员"
    style="width: 100%; margin-bottom: 12px;"
    @change="handleDepartmentSelect"
  >
    <el-option
      v-for="dept in departmentOptions"
      :key="dept"
      :label="dept"
      :value="dept"
    >
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>{{ dept }}</span>
        <el-tag size="small" type="info">{{ getDepartmentUserCount(dept) }}人</el-tag>
      </div>
    </el-option>
  </el-select>
</el-form-item>

<!-- 覆盖人员（按部门分组） -->
<el-form-item label="覆盖人员">
  <el-select
    v-model="createForm.coveredUserIds"
    multiple
    filterable
    collapse-tags
    collapse-tags-tooltip
    placeholder="选择人员"
    style="width: 100%;"
  >
    <el-option-group
      v-for="dept in usersByDepartment"
      :key="dept.department"
      :label="dept.department"
    >
      <el-option
        v-for="user in dept.users"
        :key="user.value"
        :label="user.label"
        :value="user.value"
      >
        <span>{{ user.realName }}</span>
        <span style="color: #8492a6; font-size: 13px; margin-left: 8px;">
          {{ user.department }}
        </span>
      </el-option>
    </el-option-group>
  </el-select>
  <div style="margin-top: 8px; font-size: 12px; color: #909399;">
    已选择 {{ createForm.coveredUserIds.length }} 人
    <el-button 
      v-if="createForm.coveredUserIds.length > 0"
      text 
      type="primary" 
      size="small"
      @click="createForm.coveredUserIds = []"
      style="margin-left: 8px;"
    >
      清空
    </el-button>
  </div>
</el-form-item>
```

**编辑工作周对话框：**

同样的 UI 结构，使用 `editForm`、`editSelectedDepartments`、`editUsersByDepartment` 等对应的数据和方法。

##### 对话框状态管理

```typescript
// 监听对话框打开，清空部门选择
watch(showCreateDialog, (show) => {
  if (show) {
    selectedDepartments.value = [] // 清空部门选择
    initializeCreateForm()
  }
})

watch(showEditDialog, (show) => {
  if (show) {
    editSelectedDepartments.value = [] // 清空部门选择
  }
})
```

---

## 🎯 功能亮点

### 时区修复

- ✅ 完全解决了时区问题，无论在什么时间创建工作周都能正确显示日期
- ✅ 统一了所有日期工具函数，使用本地时区格式化
- ✅ 避免了 UTC 时间转换导致的跨天问题

### 部门选择功能

- ✅ **快速选择**：一键选择整个部门的所有员工
- ✅ **多选部门**：可以同时选择多个部门
- ✅ **可视化反馈**：显示每个部门的人数
- ✅ **分组显示**：员工列表按部门分组，清晰直观
- ✅ **清空功能**：一键清空所有已选人员
- ✅ **智能合并**：选择部门会追加到已选人员，不会覆盖

---

## 📊 使用场景

### 场景 1：创建新工作周

1. 打开"创建工作周"对话框
2. 在"按部门选择"下拉框中选择一个或多个部门（如"星像行政部门"、"开发部"）
3. 系统自动将这些部门的所有员工添加到"覆盖人员"列表
4. 可以继续手动添加或删除个别人员
5. 显示"已选择 X 人"，方便确认

### 场景 2：编辑工作周

1. 打开"编辑工作周"对话框
2. 查看当前已覆盖的人员
3. 在"按部门选择"下拉框中选择新的部门快速添加人员
4. 或者手动添加/删除个别人员
5. 保存修改

---

## 🧪 测试建议

### 时区修复测试

1. **不同时间点测试**

   - ✅ 凌晨 0-8 点（原问题最严重时段）
   - ✅ 上午 8-12 点
   - ✅ 下午 12-18 点
   - ✅ 晚上 18-24 点

2. **边界情况测试**
   - ✅ 周日创建当前周（应该创建下周）
   - ✅ 周一创建当前周（应该创建本周）
   - ✅ 跨月工作周（如 10月28日-11月1日）
   - ✅ 跨年工作周（如 12月30日-1月3日）

### 部门选择功能测试

1. **基本功能**

   - ✅ 选择单个部门，验证所有该部门员工被添加
   - ✅ 选择多个部门，验证所有部门员工被添加且不重复
   - ✅ 清空部门选择后，已添加的员工保留

2. **组合场景**

   - ✅ 先选择部门，再手动添加个别员工
   - ✅ 先手动选择员工，再选择部门（不应覆盖已选）
   - ✅ 部门选择 + 手动移除某些员工
   - ✅ 清空按钮能正确清空所有员工

3. **UI 交互**
   - ✅ 部门列表显示正确的人数标签
   - ✅ 员工列表按部门分组
   - ✅ 已选人员数量显示正确
   - ✅ 过滤搜索功能正常

---

## 📝 技术细节

### 日期格式化原则

- **本地时区优先**：所有日期字符串都基于本地时区生成
- **避免 toISOString()**：不使用 UTC 时间转换
- **手动格式化**：使用 `getFullYear()`、`getMonth()`、`getDate()` 手动拼接

### 部门选择实现原则

- **非覆盖式追加**：选择部门不覆盖已选人员，而是追加
- **去重处理**：使用 `Set` 确保人员不重复
- **响应式更新**：computed 属性自动根据用户列表更新
- **状态隔离**：创建和编辑对话框的部门选择状态独立

---

## 🔄 相关文件

### 修改的文件

- ✅ `src/api/workLogApi.ts` - 修复日期工具函数
- ✅ `src/views/work-log/index.vue` - 修复工作周创建日期计算 + 添加部门选择功能

### 影响的功能模块

- ✅ 工作日志 - 工作周创建
- ✅ 工作日志 - 工作周编辑
- ✅ 工作日志 - 工作周列表显示
- ✅ 工作日志 - 日期验证

---

## ✅ 用户体验改进

**修复前：**

- ❌ 周一创建工作周，显示周日开始
- ❌ 需要逐个选择员工，效率低
- ❌ 部门员工多时选择繁琐

**修复后：**

- ✅ 周一创建工作周，正确显示周一开始
- ✅ 可以快速选择整个部门的员工
- ✅ 支持多部门批量选择
- ✅ 显示部门人数和已选人数，便于确认
- ✅ 员工列表按部门分组，查找方便

---

## 🎉 总结

本次优化解决了两个关键问题：

1. **时区问题**：彻底修复了工作周日期计算的时区问题，确保在任何时间点创建工作周都能得到正确的日期。

2. **用户体验**：新增按部门选择员工功能，大大提高了创建和编辑工作周时选择覆盖人员的效率。

这两个改进使工作周管理功能更加稳定、易用！ 🎊
