# 文章创建页面自动选中可编辑用户功能

## 修复时间

2025-11-05

## 需求描述

### 用户反馈

在文章创建页面中，选择可编辑角色后，默认没有任何用户被选中为可编辑成员。用户需要一个个手动添加，当角色下有很多用户时非常繁琐。

### 期望行为

当用户选择一个可编辑角色后，**自动选中该角色下的所有用户**，然后用户可以根据需要去掉不需要编辑权限的个别用户。这样操作更高效。

## 解决方案

### 修改逻辑

**文件**: `src/views/project/articles/create/index.vue`

#### 修改前

原来的 `watch` 只是过滤掉不符合新角色的用户：

```typescript
watch(
  () => form.value.editable_roles,
  (newRoles) => {
    if (newRoles.length === 0) {
      return
    }

    // 只是过滤，不会自动添加
    form.value.editable_user_ids = form.value.editable_user_ids.filter((userId) => {
      const user = userOptions.value.find((u) => u.value === userId)
      return user && newRoles.includes(user.role)
    })
  },
  { deep: true }
)
```

**问题**：

- 新增角色时，不会自动选中该角色下的用户
- 用户需要手动一个个添加

#### 修改后

新的 `watch` 会检测新增和移除的角色，并自动处理用户选择：

```typescript
watch(
  () => form.value.editable_roles,
  (newRoles, oldRoles) => {
    if (newRoles.length === 0) {
      // 清空已选用户
      form.value.editable_user_ids = []
      return
    }

    // 1. 找出新增和移除的角色
    const oldRolesSet = new Set(oldRoles || [])
    const newRolesSet = new Set(newRoles)
    const addedRoles = newRoles.filter((role) => !oldRolesSet.has(role))
    const removedRoles = (oldRoles || []).filter((role) => !newRolesSet.has(role))

    // 2. 使用 Set 管理已选用户，便于去重
    const selectedUserIds = new Set(form.value.editable_user_ids)

    // 3. 移除不再属于所选角色的用户
    if (removedRoles.length > 0) {
      form.value.editable_user_ids = form.value.editable_user_ids.filter((userId) => {
        const user = userOptions.value.find((u) => u.value === userId)
        return user && newRoles.includes(user.role)
      })
      // 更新 Set
      selectedUserIds.clear()
      form.value.editable_user_ids.forEach((id) => selectedUserIds.add(id))
    }

    // 4. 自动添加新增角色下的所有用户
    if (addedRoles.length > 0) {
      const usersToAdd = userOptions.value.filter(
        (user) => addedRoles.includes(user.role) && !selectedUserIds.has(user.value)
      )

      usersToAdd.forEach((user) => {
        selectedUserIds.add(user.value)
      })

      form.value.editable_user_ids = Array.from(selectedUserIds)

      console.log('✅ 自动选中新增角色的用户:', usersToAdd.length, '人')
    }
  },
  { deep: true }
)
```

**改进点**：

- ✅ 使用 `oldRoles` 参数对比新旧值
- ✅ 检测新增的角色（`addedRoles`）
- ✅ 检测移除的角色（`removedRoles`）
- ✅ 自动选中新增角色下的所有用户
- ✅ 自动移除已删除角色下的用户
- ✅ 使用 `Set` 去重，避免重复添加

## 技术细节

### 角色变化检测

```typescript
const oldRolesSet = new Set(oldRoles || [])
const newRolesSet = new Set(newRoles)

// 新增的角色 = 在 newRoles 中但不在 oldRoles 中
const addedRoles = newRoles.filter((role) => !oldRolesSet.has(role))

// 移除的角色 = 在 oldRoles 中但不在 newRoles 中
const removedRoles = (oldRoles || []).filter((role) => !newRolesSet.has(role))
```

### 自动选中逻辑

```typescript
// 找出新增角色下的所有用户（排除已选中的）
const usersToAdd = userOptions.value.filter(
  (user) => addedRoles.includes(user.role) && !selectedUserIds.has(user.value)
)

// 添加到已选用户集合
usersToAdd.forEach((user) => {
  selectedUserIds.add(user.value)
})

// 转换为数组并更新
form.value.editable_user_ids = Array.from(selectedUserIds)
```

### 使用 Set 的优势

1. **去重**: 自动确保用户ID唯一
2. **性能**: O(1) 查找时间，适合频繁检查是否存在
3. **清晰**: 代码逻辑更清晰易懂

## 用户体验改进

### 场景 1: 选择单个角色

**操作**：用户选择"研发"角色

**之前** ❌：

```
可编辑角色: [研发]
可编辑成员: []  ← 空的，需要手动添加
```

**现在** ✅：

```
可编辑角色: [研发]
可编辑成员: [张三, 李四, 王五, ...]  ← 自动选中所有研发人员
```

用户只需去掉不需要的个别人员即可。

### 场景 2: 添加第二个角色

**操作**：已选"研发"，再选择"测试"

**之前** ❌：

```
可编辑角色: [研发, 测试]
可编辑成员: [张三, 李四, 王五]  ← 只有手动添加的研发人员
```

**现在** ✅：

```
可编辑角色: [研发, 测试]
可编辑成员: [张三, 李四, 王五, 赵六, 孙七, ...]  ← 自动追加所有测试人员
```

### 场景 3: 移除某个角色

**操作**：已选"研发, 测试"，移除"测试"

**之前** ❌：

```
可编辑角色: [研发]
可编辑成员: [张三, 李四, 王五, 赵六, 孙七]  ← 测试人员仍在列表中
```

**现在** ✅：

```
可编辑角色: [研发]
可编辑成员: [张三, 李四, 王五]  ← 自动移除测试人员
```

### 场景 4: 清空所有角色

**操作**：清空可编辑角色

**现在** ✅：

```
可编辑角色: []
可编辑成员: []  ← 自动清空
```

## 执行流程

```
用户打开文章创建页面
  ↓
选择可编辑角色：[研发]
  ↓
watch 检测到角色变化
  ↓
检测到新增角色：[研发]
  ↓
查找研发角色下的所有用户
  ↓
自动添加到 editable_user_ids
  ↓
UI 显示已选中的用户列表 ✅
  ↓
用户可以手动取消不需要的个别用户
  ↓
继续添加角色：[研发, 测试]
  ↓
watch 检测到新增角色：[测试]
  ↓
查找测试角色下的所有用户
  ↓
追加到已选用户列表（去重）
  ↓
UI 更新显示所有已选用户 ✅
  ↓
用户移除角色：[研发]（只保留测试）
  ↓
watch 检测到移除角色：[研发]
  ↓
自动移除研发角色的用户
  ↓
UI 只显示测试角色的用户 ✅
```

## 适用范围

### ✅ 适用的文章类型

这个功能适用于所有非工作记录类型的文章：

- 会议记录
- 模型测试
- 项目文档
- 其他自定义类型文章

### ❌ 不适用的文章类型

**工作记录**：使用简化的权限模型，不显示可编辑角色和成员选择器，所以不受影响。

## 测试要点

### 基本功能

- [ ] 选择单个角色，所有该角色的用户自动被选中
- [ ] 选择多个角色，所有角色的用户都被选中（无重复）
- [ ] 移除某个角色，该角色的用户自动被取消选中
- [ ] 清空所有角色，所有用户自动被取消选中

### 边缘情况

- [ ] 角色下没有用户时，不会报错
- [ ] 快速连续选择/取消角色，不会出现重复用户
- [ ] 手动取消某个用户后，再次选择同一角色，该用户会被重新选中
- [ ] 在已有手动选择的用户基础上，添加新角色不会丢失手动选择

### 用户体验

- [ ] 控制台显示日志：`✅ 自动选中新增角色的用户: N 人`
- [ ] 控制台显示日志：`🔄 角色变化，已选用户已更新: N 人`
- [ ] 下方提示显示：`已选择 N 人，共 M 人可选`
- [ ] 用户列表立即更新，无延迟

## 相关文件

- `src/views/project/articles/create/index.vue` - 文章创建页面
- `docs/ARTICLE_CREATE_AUTO_SELECT_USERS.md` - 本文档

## 后续优化建议

### 1. 批量取消选择

添加一个"全选/取消全选"按钮，方便用户快速操作：

```vue
<div style="display: flex; align-items: center; gap: 8px;">
  <el-button size="small" @click="selectAllUsers">全选</el-button>
  <el-button size="small" @click="clearAllUsers">清空</el-button>
</div>
```

### 2. 角色展开视图

在用户列表中按角色分组显示，更清晰：

```
研发 (5人)
  ✓ 张三
  ✓ 李四
  ✓ 王五
  □ 赵六  ← 用户手动取消的
  ✓ 孙七

测试 (3人)
  ✓ 周八
  ✓ 吴九
  ✓ 郑十
```

### 3. 记住上次选择

记住用户的习惯性选择，下次创建同类型文章时自动应用：

```typescript
// 保存到 localStorage
const savedPreferences = {
  meeting: {
    roles: ['admin', 'reviewer'],
    excludedUsers: ['user3', 'user5']
  }
}
```

### 4. 智能推荐

根据文章类型智能推荐可编辑角色：

```typescript
const recommendedRoles = {
  meeting: ['admin', 'reviewer'], // 会议记录推荐管理员和审核员
  model_test: ['admin', 'developer'], // 模型测试推荐管理员和开发者
  requirement: ['admin', 'product'] // 需求文档推荐管理员和产品经理
}
```

## 总结

这个改进通过**自动选中新增角色下的所有用户**，大幅提升了文章创建时设置编辑权限的效率。用户现在采用"排除法"而非"包含法"来管理可编辑成员，减少了大量重复点击。

核心改进：

1. ✅ 检测角色变化（新增/移除）
2. ✅ 自动选中新增角色的所有用户
3. ✅ 自动移除已删除角色的用户
4. ✅ 使用 Set 去重确保数据一致性
5. ✅ 保留用户手动操作的灵活性

这是一个小改进，但带来了显著的用户体验提升！🎉
