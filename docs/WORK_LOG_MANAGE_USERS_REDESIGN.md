# 工作日志 - 管理覆盖员工弹窗重构

## 🎨 功能重构

将"管理覆盖员工"弹窗从 el-transfer 组件重构为按部门分组的自定义选择器，提供更清晰的层级结构和更好的用户体验。

---

## ✅ 重构内容

### 修改前（el-transfer）

```
┌──────────────────────────────────────────────┐
│         可选员工     ⇄      已覆盖员工         │
├──────────────────────────────────────────────┤
│ ☐ 王欢欢 研发部标注组  │  ☐ 张铭恒 研发部算法组 │
│ ☐ 开发测试 研发部开发组 │  ☐ 系统管理员 星像...  │
│ ☐ 行政测试 星像行政部门 │                       │
│ ☐ 陈显慧 研发部标注组   │                       │
│ ...                    │                       │
└──────────────────────────────────────────────┘
```

**问题**：

- ❌ 员工和部门信息混在一起，不够清晰
- ❌ 最后一项对齐问题
- ❌ 无法快速定位某个部门的员工
- ❌ 部门信息重复显示

---

### 修改后（部门分组）

```
┌──────────────────────────────────────────────┐
│     可选员工 (11)                已覆盖员工 (2) │
├──────────────────────────────────────────────┤
│ [搜索员工]                     [搜索员工]      │
├──────────────────────────────────────────────┤
│ ▼ 研发部标注组 (5)            ☐ 张铭恒         │
│   ☐ 王欢欢                    研发部算法组      │
│   ☐ 陈显慧                    ☐ 系统管理员     │
│   ☐ 龚奕非                    星像行政部门      │
│   ☐ 王民昭                                     │
│   ☐ 邱诚                                       │
│                                               │
│ ▶ 研发部算法组 (2)                            │
│                                               │
│ ▶ 研发部开发组 (2)                            │
│                                               │
│ ▶ 星像行政部门 (1)                            │
│                                               │
│ ▶ 未分配部门 (1)                              │
└──────────────────────────────────────────────┘
```

**改进**：

- ✅ 按部门分组，层级清晰
- ✅ 分组标题显示部门名称和员工数量
- ✅ Accordion 模式，一次只展开一个部门
- ✅ 分组下只显示员工姓名，无冗余信息
- ✅ 支持搜索筛选
- ✅ 右侧保留部门信息，便于识别

---

## 🔧 技术实现

### 1. 模板结构

**文件**：`src/views/work-log/week-detail.vue`

#### 左侧面板（按部门分组）

```vue
<div class="left-panel">
  <!-- 标题栏 -->
  <div class="panel-header">
    <span class="panel-title">可选员工</span>
    <span class="panel-count">{{ availableUsersList.length }}</span>
  </div>

  <!-- 搜索框 -->
  <div class="panel-search">
    <el-input
      v-model="leftSearchText"
      placeholder="搜索员工"
      clearable
      size="small"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>
  </div>

  <!-- 部门分组列表 -->
  <div class="panel-body">
    <el-scrollbar height="380px">
      <el-collapse v-model="expandedDepts" accordion>
        <el-collapse-item
          v-for="dept in filteredDepartmentGroups"
          :key="dept.name"
          :name="dept.name"
        >
          <template #title>
            <div class="dept-title">
              <span class="dept-name">{{ dept.name }}</span>
              <span class="dept-count">({{ dept.users.length }})</span>
            </div>
          </template>

          <!-- 部门下的员工复选框 -->
          <div class="dept-users">
            <el-checkbox
              v-for="user in dept.users"
              :key="user.id"
              :label="user.id"
              :model-value="selectedCoveredUserIds.includes(user.id)"
              @change="(val) => toggleUser(user.id, val)"
              class="user-checkbox"
            >
              {{ user.label }}
            </el-checkbox>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-scrollbar>
  </div>
</div>
```

**关键点**：

- `el-collapse` with `accordion` 模式：一次只展开一个部门
- `model-value` 绑定：直接检查用户是否已选中
- `@change` 事件：实时更新选中状态
- 分组标题显示员工数量

---

#### 中间操作按钮

```vue
<div class="center-buttons">
  <el-button
    size="small"
    @click="addSelectedUsers"
    :disabled="tempSelectedUserIds.length === 0"
  >
    添加 <el-icon><ArrowRight /></el-icon>
  </el-button>
  <el-button
    size="small"
    @click="removeSelectedUsers"
    :disabled="tempRemovedUserIds.length === 0"
  >
    <el-icon><ArrowLeft /></el-icon> 移除
  </el-button>
</div>
```

**说明**：

- 目前左侧使用直接勾选，添加按钮可选（保留以备将来扩展）
- 移除按钮用于批量移除右侧选中的用户

---

#### 右侧面板（已选择员工）

```vue
<div class="right-panel">
  <div class="panel-header">
    <span class="panel-title">已覆盖员工</span>
    <span class="panel-count">{{ selectedCoveredUserIds.length }}</span>
  </div>

  <div class="panel-search">
    <el-input
      v-model="rightSearchText"
      placeholder="搜索员工"
      clearable
      size="small"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>
  </div>

  <div class="panel-body">
    <el-scrollbar height="380px">
      <el-checkbox-group v-model="tempRemovedUserIds" class="selected-users-list">
        <el-checkbox
          v-for="user in filteredSelectedUsers"
          :key="user.id"
          :label="user.id"
          class="user-checkbox"
        >
          <div class="selected-user-item">
            <span class="user-name">{{ user.label }}</span>
            <span class="user-dept">{{ user.department || '-' }}</span>
          </div>
        </el-checkbox>
      </el-checkbox-group>
    </el-scrollbar>
  </div>
</div>
```

**关键点**：

- 显示已选择的用户列表
- 支持搜索筛选
- 勾选后可批量移除
- 右侧保留部门信息，便于识别

---

### 2. 数据结构

#### 响应式变量

```typescript
// 管理覆盖员工 - 自定义选择器状态
const leftSearchText = ref('') // 左侧搜索文本
const rightSearchText = ref('') // 右侧搜索文本
const expandedDepts = ref<string>('') // 当前展开的部门（accordion 模式）
const tempSelectedUserIds = ref<string[]>([]) // 临时选中要添加的用户
const tempRemovedUserIds = ref<string[]>([]) // 临时选中要移除的用户
```

---

#### 计算属性

**1. 可选用户列表**

```typescript
const availableUsersList = computed(() => {
  return allActiveUsers.value.map((user) => ({
    id: user.id,
    label: user.real_name || user.username,
    department: user.department || '未分配部门'
  }))
})
```

---

**2. 按部门分组**

```typescript
const departmentGroups = computed(() => {
  const groups: Record<string, typeof availableUsersList.value> = {}

  // 按部门分组
  availableUsersList.value.forEach((user) => {
    const dept = user.department || '未分配部门'
    if (!groups[dept]) {
      groups[dept] = []
    }
    groups[dept].push(user)
  })

  // 转换为数组格式，并排序
  return Object.entries(groups)
    .map(([name, users]) => ({
      name,
      users: users.sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
    }))
    .sort((a, b) => {
      // "未分配部门"排在最后
      if (a.name === '未分配部门') return 1
      if (b.name === '未分配部门') return -1
      return a.name.localeCompare(b.name, 'zh-CN')
    })
})
```

**排序规则**：

1. 部门内员工按中文名排序
2. 部门按中文名排序
3. "未分配部门"始终排在最后

---

**3. 筛选后的部门分组**

```typescript
const filteredDepartmentGroups = computed(() => {
  if (!leftSearchText.value.trim()) {
    return departmentGroups.value
  }

  const searchLower = leftSearchText.value.toLowerCase()
  return departmentGroups.value
    .map((dept) => ({
      ...dept,
      users: dept.users.filter(
        (user) =>
          user.label.toLowerCase().includes(searchLower) ||
          user.department.toLowerCase().includes(searchLower)
      )
    }))
    .filter((dept) => dept.users.length > 0)
})
```

**筛选逻辑**：

- 根据员工名称或部门名称搜索
- 只显示有匹配员工的部门
- 空搜索时显示全部

---

**4. 已选择的用户列表**

```typescript
const selectedUsers = computed(() => {
  return availableUsersList.value.filter((user) => selectedCoveredUserIds.value.includes(user.id))
})

const filteredSelectedUsers = computed(() => {
  if (!rightSearchText.value.trim()) {
    return selectedUsers.value
  }

  const searchLower = rightSearchText.value.toLowerCase()
  return selectedUsers.value.filter(
    (user) =>
      user.label.toLowerCase().includes(searchLower) ||
      user.department.toLowerCase().includes(searchLower)
  )
})
```

---

### 3. 操作方法

#### 切换用户选择状态

```typescript
const toggleUser = (userId: string, checked: boolean | string | number) => {
  const isChecked = !!checked
  if (isChecked) {
    if (!selectedCoveredUserIds.value.includes(userId)) {
      selectedCoveredUserIds.value.push(userId)
    }
  } else {
    const index = selectedCoveredUserIds.value.indexOf(userId)
    if (index > -1) {
      selectedCoveredUserIds.value.splice(index, 1)
    }
  }
}
```

**说明**：

- 接受 `CheckboxValueType` 类型（boolean | string | number）
- 转换为布尔值进行判断
- 直接修改 `selectedCoveredUserIds`

---

#### 批量移除用户

```typescript
const removeSelectedUsers = () => {
  tempRemovedUserIds.value.forEach((userId) => {
    const index = selectedCoveredUserIds.value.indexOf(userId)
    if (index > -1) {
      selectedCoveredUserIds.value.splice(index, 1)
    }
  })
  tempRemovedUserIds.value = []
}
```

---

### 4. 样式设计

#### 整体布局

```scss
.user-selector-custom {
  display: flex;
  gap: 16px;
  align-items: stretch;

  .left-panel,
  .right-panel {
    flex: 1; // 左右各占一半
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    background: #fff;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .center-buttons {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12px;
    padding: 0 8px;
  }
}
```

---

#### 面板样式

```scss
.panel-header {
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .panel-title {
    font-weight: 600;
    color: #303133;
    font-size: 14px;
  }

  .panel-count {
    color: #909399;
    font-size: 12px;
    background: #e4e7ed;
    padding: 2px 8px;
    border-radius: 10px;
  }
}

.panel-search {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.panel-body {
  flex: 1;
  overflow: hidden;
}
```

---

#### 部门分组样式

```scss
.dept-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;

  .dept-name {
    font-weight: 500;
    color: #303133;
  }

  .dept-count {
    color: #909399;
    font-size: 12px;
  }
}

.dept-users {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;

  .user-checkbox {
    margin-left: 0 !important;
    padding: 6px 15px;
    width: 100%;

    &:hover {
      background: #f5f7fa;
    }
  }
}
```

---

#### 已选择用户样式

```scss
.selected-users-list {
  display: flex;
  flex-direction: column;
  padding: 8px;

  .user-checkbox {
    margin-left: 0 !important;
    padding: 8px 10px;
    width: 100%;
    border-radius: 4px;

    &:hover {
      background: #f5f7fa;
    }

    .selected-user-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;

      .user-name {
        flex: 1;
        font-size: 14px;
        color: #303133;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
      }

      .user-dept {
        font-size: 12px;
        color: #909399;
        margin-left: 8px;
        flex-shrink: 0;
      }
    }
  }
}
```

---

## 🎯 使用流程

### 1. 打开管理覆盖员工弹窗

1. 进入工作周详情页
2. 点击"管理覆盖员工"按钮

---

### 2. 添加员工

**方式1：直接勾选**

1. 在左侧展开某个部门
2. 直接勾选要添加的员工
3. 员工自动出现在右侧列表

**方式2：搜索后勾选**

1. 在左侧搜索框输入员工名称
2. 在筛选结果中勾选员工
3. 员工自动出现在右侧列表

---

### 3. 移除员工

1. 在右侧勾选要移除的员工
2. 点击中间的"移除"按钮
3. 员工从右侧列表消失

---

### 4. 保存更改

1. 完成添加/移除操作后
2. 点击"保存"按钮
3. 系统更新工作周配置

---

## 📊 数据流程

```
allActiveUsers (原始用户数据)
        ↓
availableUsersList (格式化用户列表)
        ↓
departmentGroups (按部门分组)
        ↓
filteredDepartmentGroups (搜索筛选)
        ↓
[用户勾选/取消]
        ↓
selectedCoveredUserIds (已选择的用户ID数组)
        ↓
selectedUsers (已选择的用户对象)
        ↓
filteredSelectedUsers (右侧搜索筛选)
        ↓
[点击保存]
        ↓
handleUpdateCoveredUsers (更新工作周配置)
```

---

## 💡 最佳实践

### 1. 部门分组命名

```typescript
// ✅ 推荐：统一部门命名
'研发部标注组'
'研发部算法组'
'研发部开发组'
'星像行政部门'

// ❌ 避免：不一致的命名
'标注组' // 缺少上级部门
'开发' // 太简短
'Research Team' // 混用中英文
```

---

### 2. 搜索优化

```typescript
// ✅ 推荐：同时搜索姓名和部门
user.label.toLowerCase().includes(searchLower) ||
  user.department.toLowerCase().includes(searchLower)

// ❌ 避免：只搜索姓名
user.label.toLowerCase().includes(searchLower)
```

---

### 3. 中文排序

```typescript
// ✅ 推荐：使用 localeCompare 进行中文排序
users.sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))

// ❌ 避免：直接字符串比较
users.sort((a, b) => (a.label > b.label ? 1 : -1))
```

---

## 🚀 验证步骤

### 1. 部门分组显示

- ✅ 左侧按部门分组显示
- ✅ 每个部门显示员工数量
- ✅ Accordion 模式，一次只展开一个部门
- ✅ 部门按中文排序
- ✅ "未分配部门"在最后

---

### 2. 搜索功能

- ✅ 左侧搜索可以找到员工
- ✅ 左侧搜索可以按部门名筛选
- ✅ 右侧搜索可以筛选已选择的员工
- ✅ 清除搜索后恢复显示全部

---

### 3. 选择操作

- ✅ 勾选员工后立即出现在右侧
- ✅ 取消勾选后立即从右侧消失
- ✅ 右侧勾选员工后可批量移除
- ✅ 员工数量统计实时更新

---

### 4. 数据保存

- ✅ 点击保存后更新工作周配置
- ✅ 刷新页面后选择状态保持
- ✅ 新增员工自动创建空白日志条目

---

## 📚 相关文档

- [工作日志管理覆盖员工对齐修复](./WORK_LOG_MANAGE_USERS_DIALOG_FIX.md)
- [工作日志导航优化](./WORK_LOG_NAV_OPTIMIZATION.md)
- [工作日志周表格优化](./WORK_LOG_WEEK_DAYS_UPDATE.md)

---

**版本**: v2.0  
**更新时间**: 2025-10-17  
**重构人员**: AI Assistant

**状态**: ✅ 已完成，待测试
