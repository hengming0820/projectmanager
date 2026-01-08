# 工作记录API修复文档

## 🐛 问题描述

用户报告了两个关键问题：

1. **API函数不存在错误**：

   ```
   TypeError: userApi.getUserList is not a function
   TypeError: articlesApi.getArticleList is not a function
   ```

2. **创建工作记录后跳转错误**：
   - 创建工作记录后应该返回工作记录页面
   - 实际却跳转到了项目列表页面

## ✅ 修复内容

### 1. 修复API调用（src/views/work-log/records/index.vue）

#### 修复前 ❌

```typescript
// 错误的API调用
const loadUsers = async () => {
  const response = await userApi.getUserList()  // ❌ 不存在的方法
  users.value = response.data || response.users || []
}

const loadArticles = async () => {
  const response = await articlesApi.getArticleList({ ... })  // ❌ 不存在的方法
  articles.value = response.data || response.articles || []
}

const handleDeleteArticle = async (articleId: string) => {
  await articlesApi.deleteArticle(articleId)  // ❌ 不存在的方法
}
```

#### 修复后 ✅

```typescript
// 正确的API调用
const loadUsers = async () => {
  const response = await userApi.getUsersBasic({ status: 'active', size: 9999 }) // ✅
  users.value = response.data?.users || response.users || []
}

const loadArticles = async () => {
  const response = await articlesApi.list({
    page: 1,
    page_size: 200,
    type: 'work_record',
    status: 'published'
  }) // ✅
  articles.value = response.items || [] // ✅ 使用 items 字段
}

const handleDeleteArticle = async (articleId: string) => {
  await articlesApi.remove(articleId) // ✅
}
```

### 2. 修复路由跳转（src/views/project/articles/create/index.vue）

#### 修复前 ❌

```typescript
const submit = async () => {
  await articlesApi.create(data)
  ElMessage.success('发布成功')

  // 所有文章类型都返回到项目管理页面
  const finalProjectId = form.value.project_id || projectId.value
  if (finalProjectId) {
    router.push({ path: '/project/management' })
  } else {
    router.back()
  }
}
```

#### 修复后 ✅

```typescript
const submit = async () => {
  await articlesApi.create(data)
  ElMessage.success('发布成功')

  const finalProjectId = form.value.project_id || projectId.value
  if (finalProjectId) {
    router.push({ path: '/project/management' })
  } else {
    // 根据文章类型返回相应页面 ✅
    if (articleType.value === 'work_record') {
      router.replace({ name: 'WorkRecords' }) // ✅ 返回工作记录页面
    } else if (articleType.value === 'meeting') {
      router.replace({ name: 'MeetingNotes' })
    } else if (articleType.value === 'model_test') {
      router.replace({ name: 'ModelTests' })
    } else {
      router.replace({ path: '/project/management' })
    }
  }
}

const goBack = () => {
  // 根据文章类型返回到不同页面 ✅
  if (form.value.type === 'work_record') {
    router.push('/work-log/records') // ✅
  } else if (form.value.type === 'meeting') {
    router.push('/articles/meeting')
  } else if (projectId.value) {
    router.push('/project/management')
  } else {
    router.back()
  }
}
```

### 3. 修复编辑页面跳转（src/views/work-log/records/index.vue）

#### 修复前 ❌

```typescript
const goEditPage = (articleId: string) => {
  router.push(`/articles/detail/${articleId}`) // ❌ 路径形式
}
```

#### 修复后 ✅

```typescript
const goEditPage = (articleId: string) => {
  router.push({ name: 'ArticleDetail', params: { articleId } }) // ✅ 命名路由
}
```

## 📊 API对照表

| 功能 | 错误调用 ❌ | 正确调用 ✅ |
| --- | --- | --- |
| 获取用户列表 | `userApi.getUserList()` | `userApi.getUsersBasic({ status: 'active', size: 9999 })` |
| 获取文章列表 | `articlesApi.getArticleList({ ... })` | `articlesApi.list({ page: 1, page_size: 200, type: 'work_record' })` |
| 删除文章 | `articlesApi.deleteArticle(id)` | `articlesApi.remove(id)` |
| 响应数据字段 | `response.data` 或 `response.articles` | `response.items` (文章列表) |

## 🔧 完整的API签名

### userApi.getUsersBasic()

```typescript
// 获取用户基本信息列表（所有用户可访问）
getUsersBasic: (params?: {
  status?: string // 'active' | 'inactive'
  size?: number // 返回数量
}) =>
  Promise<{
    data: {
      users: User[]
    }
  }>
```

### articlesApi.list()

```typescript
// 获取文章列表
list: (params: {
  page?: number
  page_size?: number
  type?: string // 文章类型：'meeting', 'work_record', 'model_test' 等
  status?: string // 'published' | 'draft'
  search?: string
  year?: number
  month?: number
  author_name?: string
  project_id?: string
}) =>
  Promise<{
    items: Article[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }>
```

### articlesApi.remove()

```typescript
// 删除文章
remove: (id: string) => Promise<void>
```

## 🚀 测试步骤

### 1. 测试API调用

```bash
1. 刷新页面（Ctrl+Shift+R）
2. 进入"工作日志 → 工作记录"
3. 检查控制台是否还有 "is not a function" 错误
4. 确认左侧导航树正确显示
```

### 2. 测试创建工作记录

```bash
1. 点击"新建记录"
2. 填写标题和内容
3. 点击"发布"
4. ✅ 应该返回到"工作记录"页面（而不是项目列表）
5. ✅ 新创建的记录应该出现在导航树中
```

### 3. 测试编辑工作记录

```bash
1. 在工作记录页面，点击任意文章
2. 点击"编辑"按钮
3. 修改内容并保存
4. ✅ 应该返回到工作记录页面
```

### 4. 测试删除工作记录

```bash
1. 点击任意文章
2. 点击"删除"按钮
3. 确认删除
4. ✅ 文章应该从导航树中消失
5. ✅ 右侧显示空状态
```

## 📝 修改的文件

1. **src/views/work-log/records/index.vue**

   - 修复 `loadUsers()` 函数
   - 修复 `loadArticles()` 函数
   - 修复 `handleDeleteArticle()` 函数
   - 修复 `goEditPage()` 函数

2. **src/views/project/articles/create/index.vue**
   - 修复 `submit()` 函数，根据文章类型返回不同页面
   - 修复 `goBack()` 函数，根据文章类型返回不同页面

## 🎯 根本原因

### 问题1：API调用错误

- **原因**：使用了不存在的API方法名
- **解决**：查看 `src/api/userApi.ts` 和 `src/api/articlesApi.ts` 的真实API定义
- **教训**：创建新页面时，应该参考现有页面（如会议记录）的API调用方式

### 问题2：路由跳转错误

- **原因**：文章创建页面没有根据文章类型区分返回路径
- **解决**：在 `submit()` 和 `goBack()` 中添加类型判断逻辑
- **教训**：通用页面（如文章创建）需要考虑多种使用场景

## ✅ 验证结果

修复后，工作记录页面应该：

- ✅ 页面加载无错误
- ✅ 左侧导航树正确显示（部门→员工→月份→日期→文章）
- ✅ 创建工作记录后返回工作记录页面
- ✅ 编辑工作记录后返回工作记录页面
- ✅ 删除工作记录功能正常
- ✅ 刷新按钮功能正常

---

**修复时间**: 2025-11-05  
**状态**: ✅ 已完成  
**版本**: v1.0.1
