# 记住密码功能实现文档

## 📋 概述

已为登录页面实现完整的"记住密码"功能，用户可以选择保存登录凭证，下次访问时自动填充用户名和密码。

## ✨ 功能特性

### 1. 自动填充登录信息

- 页面加载时自动检查本地存储
- 如果用户之前勾选了"记住密码"，自动填充用户名和密码
- 复选框状态也会被恢复

### 2. 安全性考虑

- 密码使用 **Base64 编码**存储（不是明文）
- 使用 `localStorage` 持久化存储
- 用户可以随时取消勾选以清除保存的信息

### 3. 灵活控制

- 用户勾选"记住密码" → 登录成功后自动保存
- 用户取消勾选"记住密码" → 登录成功后自动清除已保存的信息

## 🔧 技术实现

### 存储位置

**浏览器 localStorage**：

- `saved_username`: 保存的用户名（明文）
- `saved_password`: 保存的密码（Base64编码）
- `remember_password`: 是否记住密码的标志（'true' 或不存在）

### 核心代码

**位置**: `src/views/auth/login/index.vue`

#### 1. 页面加载时恢复登录信息

```typescript
onMounted(() => {
  try {
    const savedUsername = localStorage.getItem('saved_username')
    const savedPassword = localStorage.getItem('saved_password')
    const rememberPassword = localStorage.getItem('remember_password')

    if (rememberPassword === 'true' && savedUsername) {
      formData.username = savedUsername
      formData.rememberPassword = true

      // 如果保存了密码，解码并填充（Base64编码）
      if (savedPassword) {
        try {
          formData.password = atob(savedPassword) // Base64解码
        } catch (e) {
          console.warn('密码解码失败，清除保存的密码')
          localStorage.removeItem('saved_password')
        }
      }

      console.log('🔑 [Login] 已恢复保存的登录信息')
    }
  } catch (error) {
    console.error('恢复登录信息失败:', error)
  }
})
```

#### 2. 登录成功后保存或清除信息

```typescript
// 在 handleSubmit 函数中，登录成功后
if (formData.rememberPassword) {
  // 保存用户名和密码（密码使用Base64编码）
  localStorage.setItem('saved_username', username)
  localStorage.setItem('saved_password', btoa(password)) // Base64编码
  localStorage.setItem('remember_password', 'true')
  console.log('💾 [Login] 已保存登录信息（记住密码）')
} else {
  // 清除保存的登录信息
  localStorage.removeItem('saved_username')
  localStorage.removeItem('saved_password')
  localStorage.removeItem('remember_password')
  console.log('🗑️ [Login] 已清除保存的登录信息')
}
```

## 🔒 安全性说明

### ⚠️ 重要提醒

1. **Base64 不是加密**

   - Base64 只是一种编码方式，不是加密算法
   - 可以轻易被解码，因此不应认为密码是"安全"的
   - 适用于内网环境，不推荐用于公网应用

2. **适用场景**

   - ✅ 内网办公系统（如本项目）
   - ✅ 个人设备上的应用
   - ❌ 公共设备
   - ❌ 高安全要求的系统

3. **用户责任**
   - 用户应自行判断是否在当前设备上使用"记住密码"功能
   - 在公共设备或不信任的环境中，不应勾选"记住密码"

### 🛡️ 更安全的替代方案（可选）

如果需要更高的安全性，可以考虑：

#### 方案1: 只记住用户名

```typescript
// 只保存用户名，密码不保存
if (formData.rememberPassword) {
  localStorage.setItem('saved_username', username)
  localStorage.setItem('remember_password', 'true')
  // 不保存密码
} else {
  localStorage.removeItem('saved_username')
  localStorage.removeItem('remember_password')
}
```

#### 方案2: 使用 Refresh Token

```typescript
// 依赖后端的长期有效的 Refresh Token
// 用户勾选"记住我"时，使用 Refresh Token 自动续期
// 不需要保存密码，更安全
if (formData.rememberPassword) {
  localStorage.setItem('refresh_token', loginResult.refreshToken)
  localStorage.setItem('remember_me', 'true')
}
```

**注意**: 当前项目已经实现了 Token 自动续期（滑动窗口），配合 `localStorage` 存储 Token，已经能够实现"保持登录"的效果。

#### 方案3: 使用 Web Crypto API 加密

```typescript
// 使用浏览器原生的加密API
async function encryptPassword(password: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(password)
  const key = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
    'encrypt',
    'decrypt'
  ])
  // ... 加密逻辑
}
```

## 📊 工作流程

```
用户访问登录页面
    ↓
检查 localStorage 中的 remember_password
    ↓
┌─────────────────┐
│ 存在且为 'true'? │
└────────┬────────┘
         ↓ 是
    恢复用户名
    恢复密码（Base64解码）
    勾选"记住密码"复选框
         ↓
    用户点击登录
         ↓
    登录成功
         ↓
┌─────────────────────┐
│ 复选框是否勾选？     │
└──────┬──────────┬───┘
   是  ↓          ↓ 否
保存用户名      清除所有
保存密码        保存的信息
(Base64编码)
```

## 🎯 用户体验

### 首次登录

1. 用户输入用户名和密码
2. 勾选"记住密码"复选框（默认勾选）
3. 点击登录
4. 登录成功后，系统自动保存登录信息

### 再次访问

1. 打开登录页面
2. 用户名和密码已自动填充 ✨
3. 可以直接点击登录，无需重新输入

### 取消记住

1. 取消勾选"记住密码"复选框
2. 点击登录
3. 登录成功后，系统自动清除保存的信息
4. 下次访问需要重新输入

## 🧪 测试步骤

### 测试1: 记住密码

1. 打开登录页面
2. 输入用户名 `testuser` 和密码 `password123`
3. 确保"记住密码"复选框已勾选 ✓
4. 点击登录
5. 登录成功后，打开浏览器开发者工具
6. 查看 `localStorage`，应该看到：
   ```javascript
   saved_username: 'testuser'
   saved_password: 'cGFzc3dvcmQxMjM=' // Base64编码
   remember_password: 'true'
   ```
7. 关闭浏览器或标签页
8. 重新打开登录页面
9. ✅ 验证：用户名和密码已自动填充

### 测试2: 取消记住密码

1. 登录页面已自动填充用户名和密码
2. 取消勾选"记住密码"复选框
3. 点击登录
4. 登录成功后，打开开发者工具
5. 查看 `localStorage`，应该**没有**以下项：
   ```javascript
   saved_username
   saved_password
   remember_password
   ```
6. 关闭浏览器或标签页
7. 重新打开登录页面
8. ✅ 验证：用户名和密码为空，需要重新输入

### 测试3: 切换用户

1. 用户A登录并勾选"记住密码"
2. 用户A登出
3. 登录页面显示用户A的用户名和密码
4. 用户B想要登录，清空表单，输入自己的凭证
5. 用户B取消勾选"记住密码"
6. 用户B登录成功
7. ✅ 验证：localStorage 中不再有用户A的信息

### 测试4: 密码解码错误处理

1. 手动修改 `localStorage` 中的 `saved_password` 为非法Base64字符串
2. 刷新登录页面
3. ✅ 验证：系统自动清除错误的密码，不会导致页面崩溃

## 📝 相关文件

- 登录页面: `src/views/auth/login/index.vue`
- 用户Store: `src/store/modules/user.ts`

## 🔄 与 Token 机制的关系

### 两种"记住"机制

本项目现在有两种"记住登录"机制：

#### 1. Token 自动续期（已有）

- **机制**: Token 存储在 `localStorage`，后端自动续期
- **有效期**: 10小时（滑动窗口，持续使用则永不过期）
- **适用**: 用户关闭标签页后再次打开，无需登录
- **文件**: `docs/TOKEN_EXPIRATION_MECHANISM.md`

#### 2. 记住密码（新增）

- **机制**: 用户名和密码存储在 `localStorage`
- **有效期**: 永久（直到用户取消勾选或清除浏览器数据）
- **适用**: Token 过期后，自动填充登录表单，用户只需点击登录按钮
- **文件**: 本文档

### 协同工作

```
用户首次登录
    ↓
勾选"记住密码"
    ↓
登录成功
    ↓
├─ Token 存储到 localStorage (有效期10小时)
└─ 用户名密码存储到 localStorage (永久)
    ↓
用户关闭浏览器
    ↓
用户再次打开网站
    ↓
┌─────────────────┐
│ Token 是否有效？│
└────┬────────┬───┘
  有效↓      ↓无效
自动登录   显示登录页面
(无感知)   ├─ 用户名已填充
           ├─ 密码已填充
           └─ 用户只需点击"登录"
```

## 🆕 更新日志

### v1.0 (2025-11-05)

- ✅ 实现"记住密码"功能
- ✅ 页面加载时自动恢复登录信息
- ✅ 登录成功后根据复选框状态保存或清除信息
- ✅ 密码使用 Base64 编码存储
- ✅ 错误处理：密码解码失败时自动清除

---

**更新日期**: 2025-11-05  
**版本**: v1.0  
**相关问题**: 登录页面的"记住密码"功能没有起作用
