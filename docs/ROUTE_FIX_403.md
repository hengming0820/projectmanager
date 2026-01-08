# 修复创建文章按钮路由 403 错误

## 问题描述

点击导航树分类节点的"+"按钮后，跳转到了 403 错误页面，而不是文章创建页面。

## 问题原因

### 错误的路由调用

```typescript
// ❌ 错误 - 使用了不存在的路径
router.push({
  path: '/project/articles/create',
  query: {
    project_id: projectId,
    type: articleType
  }
})
```

### 实际的路由定义

```typescript
// 路由定义在 src/router/routes/projectRoutes.ts
{
  path: 'article/create/:type',  // ← type 是路径参数，不是查询参数
  name: 'ArticleCreate',
  component: '/project/articles/create/index',
  meta: {
    title: '发布文章',
    keepAlive: false,
    isHide: true
  }
}
```

**关键点**：

- 路径不是 `/project/articles/create`，而是相对路径 `article/create/:type`
- `:type` 是路径参数，必须使用 `params` 传递，不能用 `query`

## 解决方案

### 正确的路由调用

```typescript
// ✅ 正确 - 使用命名路由和正确的参数类型及参数名
router.push({
  name: 'ArticleCreate', // 使用路由名称
  params: {
    type: articleType // type 作为路径参数
  },
  query: {
    projectId: projectId, // 使用驼峰命名（重要！）
    projectName: projectName // 传递项目名称用于显示
  }
})
```

**生成的 URL**：

```
/project/article/create/meeting?projectId=proj123&projectName=20250902
                        ^^^^^^^ 路径参数
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 查询参数
```

**重要提示**：

- 必须使用 `projectId`（驼峰命名），不能用 `project_id`（下划线）
- 文章创建页面期望的是 `route.query.projectId`
- 传递 `projectName` 可以在页面上显示友好的项目名称

## 修改的代码

### 文件

`src/views/project/management/index-new.vue`

### 修改前

```typescript
const createArticleForCategory = (categoryData: any) => {
  const projectId = categoryData.projectId
  const articleType = categoryData.articleType

  router.push({
    path: '/project/articles/create',
    query: {
      project_id: projectId,
      type: articleType
    }
  })
}
```

### 修改后

```typescript
const createArticleForCategory = (categoryData: any) => {
  console.log('📝 为分类创建文章:', categoryData)

  // 从categoryData中获取项目ID、项目名称和文章类型
  const projectId = categoryData.projectId
  const projectName = categoryData.projectName
  const articleType = categoryData.articleType

  if (!projectId || !articleType) {
    ElMessage.error('无法获取项目或文章类型信息')
    return
  }

  // 跳转到创建文章页面（使用正确的路由路径和参数名）
  router.push({
    name: 'ArticleCreate',
    params: {
      type: articleType
    },
    query: {
      projectId: projectId, // 使用驼峰命名
      projectName: projectName // 传递项目名称用于显示
    }
  })
}
```

## 额外修复：文章创建页面项目绑定

### 问题

文章创建页面在初始化时从路由获取 `projectId`，但如果路由参数在组件挂载后才设置，表单的 `project_id` 不会自动更新。

### 解决方案

在 `src/views/project/articles/create/index.vue` 中添加 watch 监听：

```typescript
// 监听路由中的 projectId 变化，同步到表单
watch(
  () => route.query.projectId,
  (newProjectId) => {
    if (newProjectId && typeof newProjectId === 'string') {
      form.value.project_id = newProjectId
      console.log('✅ 项目ID已绑定:', newProjectId)
    }
  },
  { immediate: true }
)
```

**关键点**：

- `immediate: true` 确保组件挂载时立即执行
- 监听 `route.query.projectId` 的变化
- 自动同步到 `form.value.project_id`

---

## 验证测试

### 测试步骤

1. 在项目列表页面，展开任意项目（如"20250902"）
2. 悬停在分类节点上（如"会议记录"、"模型测试"等）
3. 点击出现的"+"按钮
4. 验证是否正确跳转到文章创建页面
5. 检查页面是否显示：**正在为项目「20250902」创建文章**
6. 检查项目下拉框是否已选中并禁用
7. 检查 URL 是否为 `/project/article/create/<type>?projectId=<id>&projectName=<name>`

### 预期结果

- ✅ 正确跳转到文章创建页面
- ✅ 显示项目提示信息："正在为项目「XXX」创建文章"
- ✅ 项目ID已自动选中并禁用编辑
- ✅ 文章类型已自动设置
- ✅ 无 403 错误
- ✅ 控制台输出："✅ 项目ID已绑定: xxx"

## Vue Router 最佳实践

### 使用命名路由的好处

1. **避免路径错误**

   ```typescript
   // ❌ 容易拼错路径
   router.push({ path: '/projcet/articls/create' })

   // ✅ 使用名称，TypeScript 可以检查
   router.push({ name: 'ArticleCreate' })
   ```

2. **路径参数更清晰**

   ```typescript
   // ❌ 不清楚哪些是路径参数
   router.push({ path: `/project/article/create/${type}` })

   // ✅ 明确区分路径参数和查询参数
   router.push({
     name: 'ArticleCreate',
     params: { type },
     query: { project_id }
   })
   ```

3. **更易维护**
   - 路由路径改变时，只需修改路由定义
   - 使用名称的代码无需改动

### 参数类型选择指南

| 场景                 | 使用类型 | 示例                      |
| -------------------- | -------- | ------------------------- |
| **必需的资源标识**   | `params` | `/user/:id`               |
| **可选的筛选条件**   | `query`  | `/users?role=admin`       |
| **路由层级的一部分** | `params` | `/blog/:category/:postId` |
| **附加元数据**       | `query`  | `/search?q=vue&page=2`    |

### 常见错误

```typescript
// ❌ 错误 1: params 用于非路径参数
router.push({
  path: '/create',
  params: { type: 'meeting' } // 不会生效！
})

// ✅ 正确 1: 使用 query
router.push({
  path: '/create',
  query: { type: 'meeting' }
})

// ❌ 错误 2: query 用于路径参数
router.push({
  name: 'ArticleCreate',
  query: { type: 'meeting' } // 路由会失败！
})

// ✅ 正确 2: 使用 params
router.push({
  name: 'ArticleCreate',
  params: { type: 'meeting' }
})
```

## 总结

### 问题根源

1. **路由错误**

   - 使用了错误的路径 `/project/articles/create`
   - 将路径参数 `:type` 错误地作为查询参数传递

2. **参数命名错误**

   - 使用了 `project_id`（下划线），而文章创建页面期望 `projectId`（驼峰）
   - 未传递 `projectName` 导致无法显示友好的项目名称

3. **数据绑定问题**
   - 表单初始化时获取 `projectId`，但未监听路由变化
   - 如果路由参数延迟设置，表单不会更新

### 解决方案

1. **修正路由调用**

   - 使用命名路由 `name: 'ArticleCreate'`
   - 正确区分 `params`（路径参数）和 `query`（查询参数）
   - 使用正确的参数名：`projectId` 和 `projectName`

2. **添加数据监听**
   - 添加 watch 监听 `route.query.projectId` 的变化
   - 使用 `immediate: true` 确保立即执行
   - 自动同步到表单的 `project_id`

### 修改的文件

| 文件                                          | 修改内容                                       |
| --------------------------------------------- | ---------------------------------------------- |
| `src/views/project/management/index-new.vue`  | 修正 `createArticleForCategory` 函数的路由调用 |
| `src/views/project/articles/create/index.vue` | 添加 watch 监听 projectId 变化                 |

### 经验教训

1. ✅ 优先使用命名路由
2. ✅ 理解 `params` 和 `query` 的区别
3. ✅ 查看路由定义确认参数类型
4. ✅ 注意参数命名约定（驼峰 vs 下划线）
5. ✅ 使用 watch 监听路由参数变化
6. ✅ 添加参数验证和错误处理
7. ✅ 添加日志帮助调试

🎉 **问题已解决！创建文章功能现在可以正常工作，并且会自动绑定项目！**
