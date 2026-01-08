# 项目仪表板 API 数据解析修复

**修复日期**: 2025-11-14  
**问题**: 首次登录进入项目管理页面时出现 el-message 错误提示"请求的资源不存在"

## 问题分析

### 错误现象
控制台报错：
```
❌ [ProjectStore] 获取项目进度失败，尝试从其他API计算: 
TypeError: tasks is not iterable
    at Object.getProjectProgress (projectApi.ts:1047:21)
```

### 根本原因
在 `src/api/projectApi.ts` 中，有两处代码错误地假设 `backendApi.get('/tasks/')` 直接返回任务数组：

```typescript
// ❌ 错误写法
const tasks: any[] = await backendApi.get<any[]>('/tasks/', {
  params: { skip: 0, limit: 1000 }
})
for (const t of tasks) { // tasks 实际是对象 {list: [], total: 460}，不是数组
  // ...
}
```

实际上后端返回的是：
```json
{
  "list": [...],  // 任务数组
  "total": 460    // 总数
}
```

因此 `for...of` 遍历时报错 "tasks is not iterable"。

## 修复内容

### 1. 修复 `getProjectProgress` 函数（第 1043-1047 行）

**文件**: `src/api/projectApi.ts`

```typescript
// ✅ 修复后
const response: any = await backendApi.get<any>('/tasks/', {
  params: { skip: 0, limit: 1000 }
})
// 后端返回 {list: Array, total: number}，需要提取 list
const tasks: any[] = response?.list || response?.data?.list || []
const map = new Map<string, any>()
for (const t of tasks) {
  // ...
}
```

### 2. 修复 `getDashboardOverview` 回退策略（第 975-982 行）

**文件**: `src/api/projectApi.ts`

```typescript
// ✅ 修复后
const response: any = await backendApi.get<any>('/tasks/', {
  params: { skip: 0, limit: 1000 }
})
// 后端返回 {list: Array, total: number}，需要提取 list
const tasks: any[] = response?.list || response?.data?.list || []

// 统计任务
const totalTasks = tasks.length
```

## 测试验证

修复后，登录进入项目管理页面应该：
1. ✅ 不再出现 "tasks is not iterable" 错误
2. ✅ 不再显示 el-message 错误提示
3. ✅ 项目进度数据正常显示
4. ✅ 仪表板数据正常加载

## 注意事项

该问题只在首次登录或某些特定场景下触发，因为：
- 主要 API `/performance/dashboard` 正常时不会走回退逻辑
- 只有当主 API 失败时才会调用回退方法，此时才会触发 bug

## 相关文件

- `src/api/projectApi.ts` - 修复了 2 处数据解析错误
- `src/store/modules/project.ts` - 调用 dashboard API 的地方
- `src/views/project/dashboard/index.vue` - 仪表板页面

## 总结

这是一个经典的数据结构不匹配问题：
- **预期**: API 直接返回数组
- **实际**: API 返回 `{list: [], total: number}` 对象
- **解决**: 正确提取 `response.list` 字段

修复后系统运行更稳定，用户体验更好。

