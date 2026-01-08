# 工作周创建权限管理指南

## 📋 当前权限配置

### 🎯 权限控制点总览

工作周创建权限由**两个层面**控制：

1. **前端层面** - 控制按钮是否显示
2. **后端层面** - 控制 API 是否可以调用（最终权限控制）

---

## 🔍 当前配置详情

### 1️⃣ 前端权限控制

**文件位置：** `src/views/work-log/index.vue`

**代码位置：** 第 468 行

```typescript
const canManageWorkLog = computed(() =>
  ['admin', 'reviewer'].includes(userStore.currentUser?.role || '')
)
```

**当前允许的角色：**

- ✅ `admin` - 管理员
- ✅ `reviewer` - 审核员
- ❌ `annotator` - 标注员（不允许）

**影响的 UI 元素：**

- 创建工作周按钮（第 20-26 行）
- 批量管理按钮（第 13-18 行）

```vue
<el-button v-if="canManageWorkLog" type="primary" @click="showCreateDialog = true">
  <el-icon><Plus /></el-icon>
  创建工作周
</el-button>
```

---

### 2️⃣ 后端权限控制（最终权限）

**文件位置：** `backend/app/api/work_logs.py`

**代码位置：** 第 26-32 行

```python
@router.post("/weeks")
async def create_work_week(
    work_week: WorkWeekCreate,
    auto_init: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):
    """创建工作周（管理员权限）"""
```

**权限标识：** `WorkLogManagement`

**当前拥有此权限的角色：**

- ✅ `admin` - 管理员（拥有所有工作日志权限）
- ❌ `reviewer` - 审核员（默认**没有** `WorkLogManagement` 权限）
- ❌ `annotator` - 标注员（默认**没有** `WorkLogManagement` 权限）

**权限配置脚本：** `backend/scripts/add_work_log_permissions.py`

```python
# 第 53-58 行
if role.role.lower() in ['admin', 'administrator', 'super']:
    # 管理员拥有所有工作日志权限
    for perm in work_log_permissions:  # 包括 WorkLogManagement
        if perm not in new_permissions:
            new_permissions.append(perm)

# 第 68-74 行
elif role.role.lower() in ['reviewer']:
    # 审核员可以查看和审核工作日志
    reviewer_permissions = ["WorkLogView", "WorkLogReview"]  # 不包括 WorkLogManagement
```

---

## ⚠️ 当前存在的问题

### 问题：前后端权限不一致

**前端：**

```typescript
['admin', 'reviewer'].includes(...)  // reviewer 可以看到创建按钮
```

**后端：**

```python
require_permission("WorkLogManagement")  // reviewer 默认没有此权限
```

**结果：**

- `reviewer` 角色可以看到"创建工作周"按钮
- 但点击后，后端 API 会返回 **403 Forbidden**（权限不足）

---

## 🔧 修改权限的方法

### 方案 A：允许 Reviewer 创建工作周（推荐）

如果你希望 **审核员也能创建工作周**，需要修改后端权限配置。

#### 步骤 1: 修改权限配置脚本

**文件：** `backend/scripts/add_work_log_permissions.py`

**修改位置：** 第 68-74 行

```python
# 修改前：
elif role.role.lower() in ['reviewer']:
    # 审核员可以查看和审核工作日志
    reviewer_permissions = ["WorkLogView", "WorkLogReview"]
    for perm in reviewer_permissions:
        if perm not in new_permissions:
            new_permissions.append(perm)

# 修改后：✅
elif role.role.lower() in ['reviewer']:
    # 审核员可以查看、审核和管理工作日志
    reviewer_permissions = ["WorkLogView", "WorkLogReview", "WorkLogManagement"]
    for perm in reviewer_permissions:
        if perm not in new_permissions:
            new_permissions.append(perm)
```

#### 步骤 2: 运行权限更新脚本

```bash
# 进入 backend 目录
cd backend

# 运行权限更新脚本
python scripts/add_work_log_permissions.py
```

#### 步骤 3: 或手动更新数据库

如果脚本有问题，可以直接修改数据库：

```sql
-- 查看当前 reviewer 角色的权限
SELECT id, role, permissions FROM roles WHERE role = 'reviewer';

-- 更新 reviewer 角色的权限（添加 WorkLogManagement）
UPDATE roles
SET permissions = '["WorkLogView", "WorkLogReview", "WorkLogManagement"]'
WHERE role = 'reviewer';

-- 验证修改
SELECT role, permissions FROM roles WHERE role = 'reviewer';
```

#### 步骤 4: 重启后端服务

```bash
# 如果使用 Docker
docker-compose restart backend

# 或停止后重新启动
docker-compose down
docker-compose up -d
```

---

### 方案 B：仅允许 Admin 创建工作周

如果你希望 **只有管理员能创建工作周**，需要修改前端代码。

#### 步骤 1: 修改前端权限检查

**文件：** `src/views/work-log/index.vue`

**修改位置：** 第 468 行

```typescript
// 修改前：
const canManageWorkLog = computed(() =>
  ['admin', 'reviewer'].includes(userStore.currentUser?.role || '')
)

// 修改后：✅
const canManageWorkLog = computed(() => ['admin'].includes(userStore.currentUser?.role || ''))
```

#### 步骤 2: 重新构建前端

```bash
# 开发环境（自动热更新，无需手动构建）
npm run dev

# 生产环境
npm run build

# 如果使用 Docker，需要重新构建前端镜像
docker-compose restart frontend
```

---

### 方案 C：自定义角色权限（灵活配置）

如果你希望灵活控制不同角色的权限，可以使用更细粒度的权限管理。

#### 步骤 1: 创建新的权限标识

**文件：** `backend/scripts/add_work_log_permissions.py`

```python
# 第 25-30 行
work_log_permissions = [
    "WorkLogManagement",   # 管理工作周（创建、删除、归档）
    "WorkLogEdit",         # 编辑工作日志
    "WorkLogView",         # 查看工作日志
    "WorkLogReview",       # 审核工作日志
    "WorkLogCreate",       # 创建工作周（新增）✅
]
```

#### 步骤 2: 分配权限给不同角色

```python
if role.role.lower() in ['admin', 'administrator', 'super']:
    # 管理员拥有所有权限
    for perm in work_log_permissions:
        if perm not in new_permissions:
            new_permissions.append(perm)

elif role.role.lower() in ['reviewer']:
    # 审核员可以创建、查看和审核工作日志
    reviewer_permissions = ["WorkLogView", "WorkLogReview", "WorkLogCreate"]
    for perm in reviewer_permissions:
        if perm not in new_permissions:
            new_permissions.append(perm)

elif role.role.lower() in ['annotator', 'user']:
    # 标注员只能查看和编辑自己的工作日志
    basic_permissions = ["WorkLogView", "WorkLogEdit"]
    for perm in basic_permissions:
        if perm not in new_permissions:
            new_permissions.append(perm)
```

#### 步骤 3: 修改后端 API 权限要求

**文件：** `backend/app/api/work_logs.py`

```python
# 修改前：
@router.post("/weeks")
async def create_work_week(
    work_week: WorkWeekCreate,
    auto_init: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):

# 修改后：✅
@router.post("/weeks")
async def create_work_week(
    work_week: WorkWeekCreate,
    auto_init: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(["WorkLogManagement", "WorkLogCreate"]))
    # 支持多个权限，任意一个满足即可
):
```

---

## 📊 权限体系总览

### 工作日志相关权限

| 权限标识            | 含义                           | Admin | Reviewer | Annotator |
| ------------------- | ------------------------------ | ----- | -------- | --------- |
| `WorkLogManagement` | 管理工作周（创建、删除、归档） | ✅    | ❌       | ❌        |
| `WorkLogView`       | 查看工作日志                   | ✅    | ✅       | ✅        |
| `WorkLogEdit`       | 编辑工作日志                   | ✅    | ❌       | ✅        |
| `WorkLogReview`     | 审核工作日志                   | ✅    | ✅       | ❌        |

### 推荐的权限分配（修改后）

| 权限标识            | 含义                           | Admin | Reviewer | Annotator |
| ------------------- | ------------------------------ | ----- | -------- | --------- |
| `WorkLogManagement` | 管理工作周（创建、删除、归档） | ✅    | ✅       | ❌        |
| `WorkLogView`       | 查看工作日志                   | ✅    | ✅       | ✅        |
| `WorkLogEdit`       | 编辑工作日志                   | ✅    | ❌       | ✅        |
| `WorkLogReview`     | 审核工作日志                   | ✅    | ✅       | ❌        |

---

## 🧪 验证权限修改

### 1. 查看数据库中的权限配置

```sql
-- 连接到数据库
psql -U admin -d medical_annotation

-- 或使用 Docker
docker exec -it pm-postgres psql -U admin -d medical_annotation

-- 查询所有角色的权限
SELECT role, permissions FROM roles;

-- 查询特定角色的权限
SELECT role, permissions FROM roles WHERE role = 'reviewer';
```

### 2. 测试 API 权限

```bash
# 获取 token（使用 reviewer 账号登录）
TOKEN="your-reviewer-token"

# 测试创建工作周 API
curl -X POST http://localhost:8000/api/work-logs/weeks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试工作周",
    "week_start_date": "2025-10-27",
    "week_end_date": "2025-10-31",
    "year": 2025,
    "week_number": 44
  }'

# 如果返回 403 Forbidden，说明权限不足
# 如果返回 200/201，说明权限配置成功
```

### 3. 前端测试

1. 以 `reviewer` 角色登录
2. 进入"工作日志管理"页面
3. 检查是否显示"创建工作周"按钮
4. 点击按钮，尝试创建工作周
5. 观察是否成功（无 403 错误）

---

## 📝 快速修改指南

### 最简单的修改（允许 Reviewer 创建工作周）

**1. 后端数据库修改：**

```sql
-- 直接在生产数据库执行
UPDATE roles
SET permissions = '["WorkLogView", "WorkLogReview", "WorkLogManagement"]'
WHERE role = 'reviewer';
```

**2. 重启后端：**

```bash
docker-compose restart backend
```

**3. 测试：**

以 reviewer 身份登录，尝试创建工作周。

---

## ❓ 常见问题

### Q1: 修改后前端还是提示权限不足？

**A:**

1. 确认数据库已更新：`SELECT permissions FROM roles WHERE role = 'reviewer'`
2. 确认后端已重启：`docker-compose restart backend`
3. 清除浏览器缓存或使用无痕模式
4. 重新登录（获取新的 token）

### Q2: 修改数据库后没有生效？

**A:**

- 权限信息在用户登录时被写入 token
- 需要**重新登录**才能获取新的权限
- 或者清除 token 缓存：`localStorage.clear()`

### Q3: 如何给特定用户添加权限？

**A:** 权限是基于**角色**分配的，不是基于用户：

1. 修改用户的角色：`UPDATE users SET role = 'admin' WHERE username = 'xxx'`
2. 或者修改角色的权限（影响所有该角色的用户）

### Q4: 如何查看当前用户的权限？

**A:** 前端：

```javascript
console.log(userStore.currentUser)
```

后端 API：

```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔗 相关文件

- **前端权限控制：** `src/views/work-log/index.vue`（第 468 行）
- **后端 API 权限：** `backend/app/api/work_logs.py`（第 31 行）
- **权限检查逻辑：** `backend/app/utils/permissions.py`
- **权限配置脚本：** `backend/scripts/add_work_log_permissions.py`
- **角色数据表：** 数据库 `roles` 表

---

## ✅ 推荐操作

**建议使用方案 A**（允许 Reviewer 创建工作周），因为：

- ✅ 审核员通常需要管理工作日志的能力
- ✅ 保持前后端逻辑一致
- ✅ 符合业务需求（审核员 = 半管理员角色）

**执行步骤：**

1. 执行 SQL 更新 reviewer 权限
2. 重启后端服务
3. 测试验证

---

**权限修改完成！** 🎉

如有问题，请查看日志：

```bash
# 后端日志
docker-compose logs -f backend | grep -i "permission\|403"

# 前端控制台
# 打开浏览器开发者工具 → Console
```
