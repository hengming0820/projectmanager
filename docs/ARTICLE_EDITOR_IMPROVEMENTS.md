# 📝 文章发布页面优化

> 🗓️ **更新日期**: 2025-10-27  
> 🎯 **优化内容**: 移除角色硬编码 & 角色联动成员选择

---

## 🎉 更新内容

### 1️⃣ 移除角色列表硬编码

#### 问题描述

之前在文章发布页面，当角色列表加载失败时，会使用硬编码的默认角色列表：

```typescript
// ❌ 之前：硬编码默认角色
roleOptions.value = [
  { label: '管理员', value: 'admin' },
  { label: '标注员', value: 'annotator' },
  { label: '审核员', value: 'reviewer' },
  { label: '执行人员', value: 'executive' }
]
```

这种方式存在以下问题：

- 🚫 不够灵活，新增角色需要修改代码
- 🚫 与后端角色配置不同步
- 🚫 无法适应动态的角色管理需求

#### 解决方案

✅ **完全依赖后端角色数据**

- 移除硬编码的默认角色
- 加载失败时显示空列表，并给出友好提示
- 增加详细的日志输出，便于调试

```typescript
// ✅ 现在：完全依赖后端数据
try {
  // 从后端 API 加载角色列表
  const response = await roleApi.getRoles({ size: 100 })
  // ... 解析并设置角色列表
  console.log('✅ 角色列表加载成功:', roleOptions.value, '共', roleOptions.value.length, '个角色')
} catch (error) {
  // 加载失败时显示空列表
  roleOptions.value = []
  ElMessage.error('加载角色列表失败，请联系管理员')
}
```

---

### 2️⃣ 角色联动成员选择功能

#### 功能描述

在选择"可编辑角色"后，"可编辑成员"下拉框会自动过滤，只显示属于所选角色的用户。

#### 实现细节

**数据结构扩展**

```typescript
// 扩展用户选项，增加角色信息
const userOptions = ref<
  Array<{
    label: string // 用户名称
    value: string // 用户ID
    role: string // 用户角色 ✨ 新增
  }>
>([])
```

**计算属性 - 过滤用户**

```typescript
const filteredUserOptions = computed(() => {
  if (form.value.editable_roles.length === 0) {
    // 如果没有选择角色，显示所有用户
    return userOptions.value
  }
  // 过滤出属于所选角色的用户
  return userOptions.value.filter((user) => form.value.editable_roles.includes(user.role))
})
```

**监听器 - 自动清理不符合角色的已选用户**

```typescript
watch(
  () => form.value.editable_roles,
  (newRoles) => {
    if (newRoles.length === 0) return

    // 过滤出符合新角色的已选用户
    form.value.editable_user_ids = form.value.editable_user_ids.filter((userId) => {
      const user = userOptions.value.find((u) => u.value === userId)
      return user && newRoles.includes(user.role)
    })

    console.log('🔄 角色变化，已选用户已更新:', form.value.editable_user_ids.length, '人')
  },
  { deep: true }
)
```

---

## 🎨 UI 改进

### 用户选择器增强

**显示用户角色信息**

```vue
<el-option v-for="u in filteredUserOptions" :key="u.value" :label="u.label" :value="u.value">
  <span>{{ u.label }}</span>
  <span style="color: #8492a6; font-size: 12px; margin-left: 8px;">
    ({{ roleOptions.find(r => r.value === u.role)?.label || u.role }})
  </span>
</el-option>
```

**智能禁用状态**

```vue
<el-select
  v-model="form.editable_user_ids"
  multiple
  filterable
  placeholder="选择人员"
  :disabled="form.editable_roles.length === 0"  <!-- 未选角色时禁用 -->
>
```

**友好的提示信息**

```vue
<!-- 未选择角色时的提示 -->
<div v-if="form.editable_roles.length === 0" style="color: #e6a23c;">
  请先选择可编辑角色
</div>

<!-- 已选择角色时的统计信息 -->
<div v-else style="color: #909399;">
  已选择 {{ form.editable_user_ids.length }} 人，共 {{ filteredUserOptions.length }} 人可选
</div>
```

---

## 📊 用户体验对比

### 修复前 vs 修复后

| 功能点           | 修复前              | 修复后                      |
| ---------------- | ------------------- | --------------------------- |
| **角色列表来源** | ❌ 硬编码 + 后端    | ✅ 完全来自后端             |
| **角色动态性**   | ❌ 新增角色需改代码 | ✅ 自动同步后端配置         |
| **成员过滤**     | ❌ 显示所有用户     | ✅ 按角色智能过滤           |
| **角色信息显示** | ❌ 不显示           | ✅ 显示用户所属角色         |
| **已选用户管理** | ❌ 手动清理         | ✅ 自动清理不符合角色的用户 |
| **操作提示**     | ❌ 无提示           | ✅ 智能提示 + 统计信息      |

---

## 🔍 使用场景

### 场景 1：创建会议记录文章

1. **选择可编辑角色**
   - 用户选择"审核员"和"管理员"角色
2. **系统自动过滤成员**
   - "可编辑成员"下拉框自动只显示"审核员"和"管理员"角色的用户
   - 每个用户后面显示其角色标签（如"张三 (审核员)"）
3. **选择具体成员**

   - 用户从过滤后的列表中选择具体的可编辑成员
   - 底部显示统计信息："已选择 3 人，共 8 人可选"

4. **修改角色选择**
   - 用户取消选择"审核员"，只保留"管理员"
   - 系统自动清除之前选择的"审核员"用户
   - 只保留"管理员"角色的已选用户

---

## 🛠️ 技术实现

### 修改的文件

- ✅ `src/views/project/articles/create/index.vue`

### 核心修改点

#### 1. 数据结构扩展

```typescript
// 用户选项增加角色字段
userOptions: Array<{
  label: string
  value: string
  role: string // ✨ 新增
}>
```

#### 2. 新增计算属性

```typescript
const filteredUserOptions = computed(() => {
  // 根据选中的角色过滤用户
})
```

#### 3. 新增监听器

```typescript
watch(
  () => form.value.editable_roles,
  (newRoles) => {
    // 自动清理不符合新角色的已选用户
  }
)
```

#### 4. 更新用户加载函数

```typescript
async function loadUsersAndDepts() {
  // 保存用户的角色信息
  userOptions.value = list.map((u) => ({
    label: u.real_name || u.username,
    value: u.id,
    role: u.role || '' // ✨ 新增
  }))
}
```

#### 5. 移除硬编码

```typescript
// ❌ 删除
roleOptions.value = [
  { label: '管理员', value: 'admin' }
  // ...
]

// ✅ 替换为
roleOptions.value = [] // 加载失败时为空
```

---

## 🎯 优化效果

### 功能增强

- ✅ **动态角色管理**：支持后端动态配置角色，无需修改前端代码
- ✅ **智能过滤**：根据选中的角色自动过滤可选成员
- ✅ **自动清理**：角色变更时自动清理不符合条件的已选用户
- ✅ **信息可视化**：显示用户角色标签和统计信息

### 用户体验

- ✅ **操作流程优化**：先选角色再选人，逻辑清晰
- ✅ **减少错误**：防止选择不符合角色要求的用户
- ✅ **提示友好**：未选角色时禁用并提示，已选时显示统计
- ✅ **信息透明**：每个用户显示其角色标签

### 系统维护

- ✅ **代码简洁**：移除硬编码，减少维护成本
- ✅ **扩展性强**：新增角色无需修改前端代码
- ✅ **数据一致**：与后端角色配置完全同步
- ✅ **调试方便**：增加详细的日志输出

---

## 📋 测试建议

### 基本功能测试

1. ✅ 页面加载时，角色列表正确显示（来自后端）
2. ✅ 用户列表正确显示，并包含角色信息
3. ✅ 未选择角色时，成员选择器被禁用并显示提示
4. ✅ 选择角色后，成员列表自动过滤

### 交互测试

1. ✅ 选择单个角色，成员列表只显示该角色的用户
2. ✅ 选择多个角色，成员列表显示所有选中角色的用户
3. ✅ 取消角色选择，已选的该角色用户自动清除
4. ✅ 成员选项显示用户名和角色标签

### 边界情况测试

1. ✅ 角色列表加载失败，显示友好错误提示
2. ✅ 用户列表加载失败，不影响其他功能
3. ✅ 选择的角色没有对应用户，显示"0 人可选"
4. ✅ 清空所有角色选择，成员选择器恢复禁用状态

### 权限测试

1. ✅ 403 错误时不显示警告消息（预期行为）
2. ✅ 其他错误时显示错误提示
3. ✅ 非管理员用户正常使用功能

---

## 🔮 未来扩展

### 可能的增强功能

1. **角色分组**：在角色选择器中按部门或类型分组显示角色
2. **快速选择**：添加"选择所有管理员"等快捷按钮
3. **角色权限说明**：显示每个角色的权限范围
4. **批量操作**：支持按部门批量添加用户

---

## 📚 相关文档

- 📄 **`README.md`** - 系统完整文档
- 📄 **`WORK_WEEK_IMPROVEMENTS.md`** - 工作周优化文档（相似的角色选择功能）
- 📄 **`src/views/project/articles/create/index.vue`** - 文章发布页面源代码

---

## 💡 开发建议

如果您需要在其他页面实现类似的角色联动成员选择功能，可以参考本次实现：

**核心步骤：**

1. 扩展用户数据结构，包含角色信息
2. 创建计算属性过滤用户列表
3. 添加监听器自动清理不符合角色的用户
4. 更新 UI 显示角色标签和统计信息

**代码模板：**

```typescript
// 1. 数据结构
const userOptions = ref<Array<{ label: string; value: string; role: string }>>([])

// 2. 计算属性
const filteredUserOptions = computed(() => {
  if (form.value.roles.length === 0) return userOptions.value
  return userOptions.value.filter((u) => form.value.roles.includes(u.role))
})

// 3. 监听器
watch(
  () => form.value.roles,
  (newRoles) => {
    form.value.userIds = form.value.userIds.filter((uid) => {
      const user = userOptions.value.find((u) => u.value === uid)
      return user && newRoles.includes(user.role)
    })
  }
)
```

---

**🎉 文章发布功能优化完成！**
