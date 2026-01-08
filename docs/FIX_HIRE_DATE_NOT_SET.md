# 修复个人中心入职时间显示"未设置"的问题

## 问题原因

个人中心显示"未设置"是因为数据库中该用户的 `hire_date` 字段为 `NULL`（空值）。

## 解决方案

有三种方式可以设置用户的入职时间：

---

## 方式一：使用 Python 脚本（推荐）

### 1. 查看所有用户的入职时间状态

```bash
cd backend
python scripts/set_hire_date.py --list
```

输出示例：

```
================================================================================
用户入职时间状态
================================================================================
用户名            姓名            入职时间         状态       创建时间
--------------------------------------------------------------------------------
admin           管理员           2025-08-29      ✅ 已设置   2025-08-15 10:30:00
whh             王欢欢           未设置          ❌ 未设置   2025-08-29 09:00:00
================================================================================

📊 统计: 总计 2 个用户, 已设置 1 个, 未设置 1 个
```

### 2. 为特定用户设置入职时间

```bash
# 设置用户 whh 的入职时间为 2025-08-29
python scripts/set_hire_date.py --username whh --date 2025-08-29
```

输出示例：

```
✅ 成功: 已将用户 'whh' (王欢欢) 的入职时间设置为 2025-08-29
```

### 3. 批量设置所有用户（使用创建日期）

如果有多个用户都没有设置入职时间，可以批量将他们的入职时间设置为账号创建日期：

```bash
python scripts/set_hire_date.py --set-all-from-created
```

系统会提示确认：

```
⚠️  确定要为所有未设置入职时间的用户设置为其创建日期吗? (y/N): y

找到 5 个未设置入职时间的用户
将为这些用户设置入职时间为其创建日期...

✅ whh            (王欢欢          ) 入职时间设置为 2025-08-29
✅ user1          (用户1           ) 入职时间设置为 2025-09-01
...

📊 完成: 成功设置 5/5 个用户的入职时间
```

---

## 方式二：使用 SQL 脚本

### 1. 连接到数据库

使用你的数据库管理工具（如 pgAdmin, DBeaver 等）连接到 PostgreSQL 数据库。

### 2. 查看未设置入职时间的用户

```sql
SELECT
    id,
    username,
    real_name,
    hire_date,
    created_at,
    CASE
        WHEN hire_date IS NULL THEN '未设置'
        ELSE '已设置'
    END AS hire_date_status
FROM users
ORDER BY created_at DESC;
```

### 3. 为特定用户设置入职时间

```sql
-- 为用户名为 whh 的用户设置入职时间
UPDATE users
SET hire_date = '2025-08-29'
WHERE username = 'whh';
```

或者使用邮箱：

```sql
-- 为邮箱为 whh@xxjz.com 的用户设置入职时间
UPDATE users
SET hire_date = '2025-08-29'
WHERE email = 'whh@xxjz.com';
```

### 4. 批量设置（使用创建日期）

```sql
-- 将所有未设置入职时间的用户的入职日期设置为其创建日期
UPDATE users
SET hire_date = DATE(created_at)
WHERE hire_date IS NULL;
```

### 5. 验证结果

```sql
-- 查看特定用户的入职时间
SELECT username, real_name, hire_date
FROM users
WHERE username = 'whh';
```

---

## 方式三：通过用户管理界面（前端）

### 步骤：

1. **以管理员身份登录系统**

2. **进入用户管理页面**

   - 导航到：系统管理 → 用户管理

3. **编辑用户信息**

   - 找到需要设置入职时间的用户
   - 点击"编辑"按钮
   - 在弹出的编辑对话框中找到"入职日期"字段
   - 选择或输入入职日期
   - 点击"保存"

4. **刷新个人中心**
   - 用户退出登录并重新登录
   - 或直接刷新个人中心页面（F5）
   - 入职时间应该正常显示了

---

## 验证修复

### 1. 刷新页面

设置入职时间后，用户需要：

- 刷新个人中心页面（按 F5）
- 或退出登录后重新登录

### 2. 检查显示

访问个人中心页面，应该看到：

```
📧 whh@xxjz.com
👤 annotator
📍 四川省成都市
🏢 星像精准－研发部标注组－王欢欢
📅 入职时间：2025年08月29日         ← 应该正常显示
```

而不是：

```
📅 入职时间：未设置
```

---

## 技术细节

### 数据流程

```
1. 数据库 users 表
   ↓ (hire_date 字段)
2. 后端 API: /api/users/me/profile
   ↓ (返回 hire_date)
3. 前端 userStore
   ↓ (同步到 currentUser.hireDate)
4. 个人中心页面
   ↓ (formatHireDate 格式化)
5. 显示：2025年08月29日
```

### 检查后端日志

如果设置后还是显示"未设置"，可以检查后端日志：

```bash
# 在后端目录查看日志
cd backend
tail -f app/logs/app.log | grep -i "hire_date"
```

应该看到类似的日志：

```
[UsersAPI] /me/profile - user.hire_date: 2025-08-29
[UsersAPI] /me/profile - UserProfileResponse: {..., 'hire_date': '2025-08-29', ...}
```

### 检查前端控制台

打开浏览器开发者工具（F12），在控制台应该看到：

```
📋 [UserCenter] 用户信息: {...}
📅 [UserCenter] 入职时间: 2025-08-29
```

---

## 常见问题

### Q1: 设置后还是显示"未设置"？

**解决方法**：

1. 确认数据库中确实已更新（执行查询SQL验证）
2. 清除浏览器缓存
3. 退出登录后重新登录
4. 检查后端和前端日志

### Q2: 日期格式不正确？

**确保日期格式为**：`YYYY-MM-DD`（如：`2025-08-29`）

不要使用：

- ❌ `2025/08/29`
- ❌ `29-08-2025`
- ❌ `08-29-2025`

### Q3: 批量设置会覆盖已有的入职时间吗？

**不会**。批量设置脚本和SQL只会更新 `hire_date IS NULL` 的用户，已经设置过的用户不会被修改。

### Q4: 可以为未来的日期设置入职时间吗？

**可以**。系统允许设置未来的日期（例如：提前创建即将入职员工的账号）。

### Q5: 入职时间影响其他功能吗？

目前入职时间主要用于：

- 个人中心展示
- 绩效报告中的个人信息
- 未来可能用于工龄计算、权限判断等

---

## 完整示例

### 示例场景：为用户 whh 设置入职时间为 2025年8月29日

**方法 1 - Python 脚本（最简单）**：

```bash
cd backend
python scripts/set_hire_date.py --username whh --date 2025-08-29
```

**方法 2 - SQL**：

```sql
UPDATE users
SET hire_date = '2025-08-29'
WHERE username = 'whh';

-- 验证
SELECT username, real_name, hire_date FROM users WHERE username = 'whh';
```

**方法 3 - 用户管理界面**：

1. 登录管理员账号
2. 系统管理 → 用户管理
3. 找到 whh 用户，点击编辑
4. 设置入职日期为 2025-08-29
5. 保存

**验证结果**：

1. 刷新个人中心页面
2. 应该看到：`入职时间：2025年08月29日`

---

## 相关文件

- **Python 脚本**：`backend/scripts/set_hire_date.py`
- **SQL 脚本**：`backend/scripts/check_and_set_hire_date.sql`
- **前端页面**：`src/views/system/user-center/index.vue`
- **用户 Schema**：`backend/app/schemas/user.py`
- **用户模型**：`backend/app/models/user.py`

---

## 更新日期

- 2025-10-21: 创建文档，提供三种设置入职时间的方法

## 维护者

- AI Assistant
