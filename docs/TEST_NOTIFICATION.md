# 定时通知功能测试指南

## 🎯 快速测试步骤

### 1️⃣ 启动后端（确认定时任务已加载）

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**预期日志：**

```
⏰ [Startup] 正在初始化定时任务...
⏰ [Scheduler] 定时任务调度器已启动
⏰ [Scheduler] 已添加下班提醒任务：每天 17:10
⏰ [Scheduler] 下次执行时间：2025-10-22 16:02:00+08:00
✅ [Startup] 定时任务初始化成功，已加载 1 个任务
  📅 下班提醒 (ID: work_end_reminder) - 下次执行: 2025-10-22 16:02:00+08:00
```

✅ **检查点：** 看到上述日志，说明后端定时任务已成功加载

---

### 2️⃣ 启动前端

```bash
npm run dev
```

访问 `http://localhost:3006`（或你的前端端口）

---

### 3️⃣ 登录并检查 WebSocket 连接

1. **登录系统**

2. **打开浏览器开发者工具** (F12)

3. **查看 Console 标签**，应该看到：

```
🔔 [UserStore] 用户登录成功，请求通知权限
✅ [UserStore] 通知权限已授予
🔔 [WS] 已连接: role=annotator user=张三
```

✅ **检查点：** 看到 WebSocket 连接成功日志

4. **查看 Network 标签 → WS (WebSocket)**
   - 应该看到 `ws://localhost:8000/ws/notifications`
   - Status: `101 Switching Protocols`

✅ **检查点：** WebSocket 连接状态为 101

---

### 4️⃣ 检查通知权限

**方法 1：查看浏览器地址栏**

- 地址栏左侧应该有 🔒 或 🔓 图标
- 点击 → 查看权限 → 通知应该是"允许"

**方法 2：控制台检查**

```javascript
// 在浏览器控制台执行
Notification.permission
```

**预期结果：** `"granted"`

❌ **如果是 `"denied"` 或 `"default"`，需要手动授权：**

**Chrome/Edge:**

1. 点击地址栏左侧 🔒
2. 网站设置
3. 通知 → 允许

**Firefox:**

1. 点击地址栏左侧 🔒
2. 权限 → 接收通知 → 允许

---

### 5️⃣ 手动触发通知（测试）

**方法 1：使用 Swagger UI（推荐）**

1. 访问 `http://localhost:8000/docs`
2. 点击右上角 **Authorize**，输入 Token
3. 找到 **定时任务** 分组
4. 展开 `POST /api/scheduler/trigger-work-reminder`
5. 点击 **Try it out** → **Execute**

**预期响应：**

```json
{
  "success": true,
  "message": "下班提醒已发送给所有在线用户"
}
```

**方法 2：使用 curl**

```bash
# 替换 YOUR_TOKEN 为实际 Token
curl -X POST "http://localhost:8000/api/scheduler/trigger-work-reminder" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 6️⃣ 验证前端收到通知

**手动触发后，你应该看到：**

#### ✅ 页面内通知（Element Plus Message）

- 页面右上角出现**黄色警告框**
- 内容：`请及时保存文件，填写好今天的工作日志，下班请关电脑！`
- 显示 10 秒后自动消失（可手动关闭）

#### ✅ 浏览器系统通知

- 桌面右下角（Windows）或右上角（Mac）弹出系统通知
- 标题：`🏃 下班提醒`
- 内容：`请及时保存文件，填写好今天的工作日志，下班请关电脑！`

#### ✅ 控制台日志

```
🔔 [WS] 收到消息: {type: "work_end_reminder", title: "🏃 下班提醒", content: "...", ...}
```

#### ✅ 后端日志

```
🧪 [Scheduler] 手动触发下班提醒（测试）
⏰ [Scheduler] 开始执行下班提醒任务
✅ [Scheduler] 下班提醒已发送给所有在线用户
🔔 [WS] 开始向所有在线用户广播，当前连接数: 1
🔔 [WS] 广播完成，成功: 1/1，失败: 0
```

---

## ❌ 故障排查清单

### 问题 1: 后端日志显示成功，但前端没有任何反应

**可能原因：**

- ❌ 前端代码未更新
- ❌ 前端页面未刷新
- ❌ WebSocket 连接断开

**解决方案：**

1. **确认前端代码已更新**

   ```bash
   # 查看 src/store/modules/user.ts 是否包含 work_end_reminder 处理
   grep -n "work_end_reminder" src/store/modules/user.ts
   ```

   应该看到第 230 行左右有相关代码

2. **刷新浏览器页面** (Ctrl+R 或 Cmd+R)

3. **检查 WebSocket 连接**

   - 开发者工具 → Network → WS
   - 确认 `ws://localhost:8000/ws/notifications` 连接状态

4. **重新登录**
   - 退出登录
   - 重新登录
   - 查看控制台是否有 WebSocket 连接日志

---

### 问题 2: 看到页面通知，但没有系统通知

**可能原因：**

- ❌ 浏览器未授予通知权限
- ❌ 操作系统禁用了浏览器通知

**解决方案：**

1. **检查浏览器权限**

   ```javascript
   // 控制台执行
   Notification.permission
   ```

   如果不是 `"granted"`，需要重新授权（参见步骤 4）

2. **检查操作系统通知设置**

   **Windows 10/11:**

   - 设置 → 系统 → 通知和操作
   - 确保通知已开启
   - 找到你的浏览器，确保允许通知

   **macOS:**

   - 系统偏好设置 → 通知
   - 找到你的浏览器
   - 允许通知，选择"提醒"样式

3. **测试浏览器通知**
   ```javascript
   // 在控制台手动测试
   new Notification('测试通知', {
     body: '如果你看到这个，说明通知权限正常',
     icon: '/xingxiang_logo.ico'
   })
   ```

---

### 问题 3: WebSocket 连接失败

**症状：**

- 控制台显示 WebSocket 连接错误
- Network 标签看不到 WS 连接

**解决方案：**

1. **检查后端是否运行**

   ```bash
   curl http://localhost:8000/health
   ```

   应该返回 `{"status": "healthy", "redis": "ok"}`

2. **检查防火墙**

   - 确保 8000 端口未被阻止

3. **检查 CORS 配置**

   - 后端 `backend/app/main.py` 中的 `ALLOWED_ORIGINS` 应包含前端地址

4. **尝试使用其他浏览器**
   - 排除浏览器兼容性问题

---

### 问题 4: 定时任务未触发

**症状：**

- 到了 17:10，但没有自动发送通知

**解决方案：**

1. **检查服务器时间和时区**

   ```bash
   # Linux/Mac
   date
   timedatectl

   # Windows (PowerShell)
   Get-Date
   ```

2. **检查定时任务列表**

   ```bash
   curl -X GET "http://localhost:8000/api/scheduler/jobs" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **查看后端日志**

   ```bash
   tail -f backend/app/logs/app.log | grep -E "Scheduler|下班"
   ```

4. **重启后端服务**
   - 重新加载定时任务

---

## 📊 测试报告模板

完成测试后，请记录结果：

```
✅ 后端定时任务加载成功
✅ 前端 WebSocket 连接成功
✅ 通知权限已授予
✅ 手动触发通知成功
✅ 前端收到页面通知
✅ 前端收到系统通知
✅ 后端日志正常
✅ 控制台日志正常

测试时间：2025-10-22 16:05
测试人员：张三
浏览器：Chrome 118
操作系统：Windows 11
```

---

## 🎉 测试成功！

如果以上所有检查点都通过，恭喜你！定时通知功能已成功部署。

**下一步：**

1. 修改提醒时间为实际需要的时间（默认 17:10）
2. 自定义提醒内容
3. 添加更多定时任务（如早安提醒、午餐提醒等）

详细配置请参考：`SCHEDULED_NOTIFICATION_GUIDE.md`
