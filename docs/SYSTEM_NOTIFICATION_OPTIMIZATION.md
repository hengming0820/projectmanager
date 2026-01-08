# 系统级通知优化

## 📋 优化概述

本次优化改进了系统级通知（Windows/macOS 通知中心）的显示效果，使其更加友好和专业。

## 🎯 优化内容

### 1. 应用名称优化

**问题**: 通知显示来源为 "localhost:3006"，不够专业

**解决方案**:

- 创建 `public/manifest.json` 文件，配置应用名称
- 在 `index.html` 中添加 `<meta name="application-name">` 和 `<link rel="manifest">`

**效果**: 通知来源现在显示为 "星像精准研发部管理系统"

### 2. 通知标题优化

**问题**: 通知标题缺乏个性化，语气生硬（如 "需修订"、"审核通过"）

**解决方案**:

- 在通知标题中加入用户真实姓名 (`real_name`)
- 采用更亲切的表达方式

**示例**:

| 通知类型     | 优化前         | 优化后                   |
| ------------ | -------------- | ------------------------ |
| 任务驳回     | 需修订         | 曹翠红，您的任务需要修订 |
| 任务通过     | 审核通过       | 曹翠红，恭喜任务通过！   |
| 新任务待审核 | 新任务待审核   | 李明，有新任务待审核     |
| 跳过申请通过 | 跳过申请已同意 | 张三，跳过申请已通过     |
| 下班提醒     | 🏃 下班提醒    | 王五，该下班了~          |

## 📁 修改文件

### 前端

1. **`public/manifest.json`** (新建)

   - 配置应用名称、图标、主题色
   - 让浏览器正确识别应用信息

2. **`index.html`**

   - 添加 `<meta name="application-name" content="星像精准研发部管理系统" />`
   - 添加 `<link rel="manifest" href="/manifest.json" />`

3. **`src/views/auth/login/index.vue`**

   - 优化离线通知标题，加入用户真实姓名
   - 为不同通知类型定制友好标题

4. **`src/store/modules/user.ts`**
   - 优化实时 WebSocket 通知标题，加入用户真实姓名
   - 统一各类通知的语气和风格

## 🎨 通知类型完整列表

| 通知类型 (`type`)   | 标题模板                   | 语气     |
| ------------------- | -------------------------- | -------- |
| `task_rejected`     | `{姓名}，您的任务需要修订` | 委婉提醒 |
| `task_approved`     | `{姓名}，恭喜任务通过！`   | 积极鼓励 |
| `task_submitted`    | `{姓名}，有新任务待审核`   | 中性通知 |
| `skip_requested`    | `{姓名}，有新的跳过申请`   | 中性通知 |
| `skip_approved`     | `{姓名}，跳过申请已通过`   | 积极确认 |
| `skip_rejected`     | `{姓名}，跳过申请被拒绝`   | 委婉告知 |
| `work_end_reminder` | `{姓名}，该下班了~`        | 轻松友好 |
| 其他类型            | `{姓名}，{原标题}`         | 根据内容 |

## 🔧 技术细节

### PWA Manifest 配置

```json
{
  "name": "星像精准研发部管理系统",
  "short_name": "星像研发系统",
  "display": "standalone",
  "theme_color": "#1890ff",
  "icons": [
    {
      "src": "/xingxiang_logo.ico",
      "sizes": "any",
      "type": "image/x-icon"
    }
  ]
}
```

### 用户姓名获取逻辑

```typescript
// 离线通知（登录时）
const userRealName = userStore.userInfo?.real_name || username

// 实时通知（WebSocket）
const userRealName = userInfo.value?.real_name || userInfo.value?.username || '您'
```

### 系统通知 API

```typescript
new Notification(friendlyTitle, {
  body: notification.content,
  icon: '/xingxiang_logo.ico',
  tag: `offline-notif-${notification.id}`,
  requireInteraction: notification.priority === 'urgent'
})
```

## ✅ 效果对比

### 优化前

```
┌─────────────────────────────────┐
│  Google Chrome                  │
├─────────────────────────────────┤
│  需修订                          │
│  您的任务《CaoCuihong》需修订，  │
│  请修改                          │
│  localhost:3006                 │
└─────────────────────────────────┘
```

### 优化后

```
┌─────────────────────────────────┐
│  Google Chrome                  │
├─────────────────────────────────┤
│  曹翠红，您的任务需要修订         │
│  您的任务《CaoCuihong》需修订，  │
│  请修改                          │
│  星像精准研发部管理系统           │
└─────────────────────────────────┘
```

## 🌟 优势

1. **专业性**: 应用名称替代技术细节（localhost:3006）
2. **个性化**: 使用用户真实姓名，增强归属感
3. **友好性**: 语气亲切，符合中文表达习惯
4. **一致性**: 统一所有通知类型的风格
5. **可扩展**: 易于添加新的通知类型

## 📌 注意事项

1. **浏览器缓存**: 修改 `manifest.json` 后，需要清除浏览器缓存或强制刷新
2. **通知权限**: 确保用户已授予系统通知权限
3. **测试环境**: 在不同浏览器（Chrome、Edge、Firefox）和操作系统（Windows、macOS）上测试效果
4. **姓名回退**: 如果 `real_name` 为空，会自动回退到 `username`

## 🧪 测试步骤

1. **清除浏览器缓存** 或使用无痕模式
2. **重新登录系统**
3. **关闭浏览器**（离线）
4. **触发通知**（例如管理员驳回任务）
5. **重新打开浏览器**（自动登录）
6. **检查系统通知**:
   - 标题是否包含用户姓名
   - 来源是否显示 "星像精准研发部管理系统"
   - 点击通知是否能正确跳转

## 📚 相关文档

- [登录持久化与通知增强](./LOGIN_PERSISTENCE_AND_NOTIFICATION_ENHANCEMENT.md)
- [WebSocket 与 Redis 通知升级](./WEBSOCKET_REDIS_NOTIFICATION_UPGRADE.md)
- [Redis 离线通知系统](./REDIS_OFFLINE_NOTIFICATION.md)

---

**版本**: v1.0.0  
**更新日期**: 2025-11-03  
**作者**: AI Assistant
