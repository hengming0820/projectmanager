# 工作记录创建页面简化文档

## 📝 修改内容

### 1. 删除老的文章详情页面

#### 删除的文件

- ✅ `src/views/project/articles/detail/index.vue` - 已删除

#### 删除的路由

- ✅ `src/router/routes/projectRoutes.ts` - 删除 `ArticleDetail` 路由
- ✅ `src/router/routes/asyncRoutes.ts` - 删除 `ArticleDetailStandalone` 路由

### 2. 简化工作记录创建页面

#### 隐藏的字段（工作记录不显示）

```vue
<!-- 只有非工作记录才显示这些字段 -->
<template v-if="!isWorkRecord">
  <!-- 封面上传 -->
  <el-upload>...</el-upload>

  <!-- 可见性开关 -->
  <el-switch v-model="form.is_public" />

  <!-- 可编辑角色 -->
  <el-select v-model="form.editable_roles">...</el-select>

  <!-- 可编辑成员 -->
  <el-select v-model="form.editable_user_ids">...</el-select>

  <!-- 所属部门 -->
  <el-select v-model="form.departments">...</el-select>
</template>
```

#### 工作记录显示简化说明

```vue
<template v-else>
  <el-alert type="info" :closable="false" show-icon>
    <template #title>工作记录说明</template>
    <div>
      <p>• 工作记录为个人记录，自动归属到您所在的部门</p>
      <p>• 只有您本人和管理员可以编辑/删除</p>
      <p>• 所有人可以查看工作记录</p>
    </div>
  </el-alert>
</template>
```

#### 标题栏简化

```vue
<div class="title-row">
  <el-input v-model="form.title" placeholder="请输入文章标题" />
  <!-- 工作记录不显示分类选择 -->
  <el-select v-if="!isWorkRecord" v-model="form.category">...</el-select>
</div>

<!-- 工作记录不显示摘要输入 -->
<el-input v-if="!isWorkRecord" v-model="form.summary" type="textarea" />
```

### 3. 工作记录提交逻辑

#### 自动处理的字段

```typescript
if (isWorkRecord.value) {
  const userDepartment = userStore.currentUser?.department || '未分类'
  const data = {
    title: form.value.title,
    content: form.value.content,
    type: 'work_record',
    status: 'published' as const, // ✅ 直接发布，无需选择状态
    category: '日常记录', // ✅ 默认分类
    departments: [userDepartment], // ✅ 自动使用用户所在部门
    is_public: true, // ✅ 公开可见
    editable_roles: [], // ✅ 只有作者和管理员可编辑
    editable_user_ids: [], // ✅ 只有作者和管理员可编辑
    tags: [],
    summary: '', // ✅ 无摘要
    cover_url: '', // ✅ 无封面
    project_id: form.value.project_id || null
  }
  await articlesApi.create(data)
}
```

## 🎯 工作记录特点

### 个人化

- ✅ **自动归属部门**: 使用当前用户所在的部门
- ✅ **作者唯一性**: 只有作者本人创建

### 简化创建

- ✅ **无需选择状态**: 直接发布，无草稿
- ✅ **无需摘要**: 简化输入
- ✅ **无需封面**: 不需要图片
- ✅ **无需选择部门**: 自动使用用户部门
- ✅ **无需选择权限**: 自动配置权限

### 权限控制

- ✅ **只有作者可编辑**: `editable_roles: []`, `editable_user_ids: []`
- ✅ **管理员可编辑**: 后端自动处理管理员权限
- ✅ **所有人可查看**: `is_public: true`

## 📊 对比表格

| 字段           | 会议记录/模型测试 | 工作记录            |
| -------------- | ----------------- | ------------------- |
| **标题**       | ✅ 必填           | ✅ 必填             |
| **分类**       | ✅ 选择           | ❌ 自动（日常记录） |
| **摘要**       | ✅ 可选           | ❌ 无               |
| **内容**       | ✅ 必填           | ✅ 必填             |
| **封面**       | ✅ 可选           | ❌ 无               |
| **状态**       | ✅ 草稿/发布      | ❌ 自动发布         |
| **可见性**     | ✅ 公开/私有      | ❌ 自动公开         |
| **可编辑角色** | ✅ 可选           | ❌ 自动（无）       |
| **可编辑成员** | ✅ 可选           | ❌ 自动（无）       |
| **所属部门**   | ✅ 可选           | ❌ 自动（用户部门） |
| **归属项目**   | ✅ 可选           | ✅ 可选             |

## 🔒 权限逻辑

### 创建

- 所有登录用户可以创建工作记录

### 查看

```typescript
// 工作记录设置为公开
is_public: true
// 所有人都可以查看
```

### 编辑

```typescript
// 工作记录不设置可编辑角色和成员
editable_roles: []
editable_user_ids: []

// 后端在 canEdit 判断中会自动处理：
// 1. 管理员可以编辑所有文章
// 2. 作者可以编辑自己的文章
```

### 删除

```typescript
// 后端在 canDelete 判断中会自动处理：
// 1. 管理员可以删除所有文章
// 2. 作者可以删除自己的文章
```

## 🎨 UI变化

### 创建页面（工作记录）

**简化前**:

```
┌────────────────────────────────────┐
│ 标题: [_____________] [分类选择▼]  │
│ 摘要: [___________________________]│
│ 编辑器...                          │
├────────────────────────────────────┤
│ [封面上传]                         │
│ 可见: [ON/OFF]                     │
│ 可编辑角色: [选择▼]                │
│ 可编辑成员: [选择▼]                │
│ 所属部门: [选择▼]                  │
│ 归属项目: [选择▼]                  │
└────────────────────────────────────┘
```

**简化后**:

```
┌────────────────────────────────────┐
│ 标题: [________________________]   │
│ 编辑器...                          │
├────────────────────────────────────┤
│ ℹ️ 工作记录说明                    │
│ • 自动归属到您所在的部门           │
│ • 只有您本人和管理员可编辑/删除    │
│ • 所有人可以查看                   │
│                                    │
│ 归属项目(可选): [选择▼]            │
└────────────────────────────────────┘
```

## ✅ 测试步骤

### 1. 测试工作记录创建

1. 进入"工作日志 → 工作记录"
2. 点击"新建记录"
3. ✅ 确认页面只显示：标题、编辑器、说明框、项目选择
4. ✅ 确认没有：分类、摘要、封面、角色/成员/部门选择

### 2. 测试提交

1. 输入标题和内容
2. 点击"发布"
3. ✅ 成功创建并返回工作记录页面
4. ✅ 工作记录归属到你的部门
5. ✅ 只显示"编辑内容"和"删除"按钮

### 3. 测试权限

1. 创建一条工作记录
2. ✅ 作为作者，可以编辑和删除
3. 切换到其他普通用户
4. ✅ 可以查看，但无编辑/删除按钮
5. 切换到管理员
6. ✅ 可以编辑和删除

### 4. 测试其他文章类型

1. 创建会议记录或模型测试
2. ✅ 应该显示完整的字段（分类、摘要、封面等）
3. ✅ 确认工作记录的简化不影响其他类型

## 📝 代码关键点

### 判断是否为工作记录

```typescript
const isWorkRecord = computed(() => articleType.value === 'work_record')
```

### 条件渲染

```vue
<el-select v-if="!isWorkRecord" v-model="form.category"></el-select>
```

### 提交分支

```typescript
if (isWorkRecord.value) {
  // 工作记录简化逻辑
} else {
  // 其他文章正常逻辑
}
```

## 🎉 优化效果

### 用户体验

- ✅ **简化创建流程**: 从12个字段减少到2个必填字段
- ✅ **清晰的说明**: 用户明确知道权限规则
- ✅ **快速发布**: 无需关心复杂的权限配置

### 开发维护

- ✅ **代码复用**: 复用现有创建页面，仅添加条件判断
- ✅ **逻辑清晰**: 工作记录特殊处理与其他类型分离
- ✅ **易于扩展**: 未来添加其他简化类型很容易

---

**修改时间**: 2025-11-05  
**状态**: ✅ 已完成  
**版本**: v1.0.3
