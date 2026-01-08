# 数据库时间存储详解

## 📊 现在存入数据库的时间格式

### 快速回答

**存入数据库的时间：UTC 时间，格式如 `2025-10-22 10:00:00.123456`**

---

## 🔍 详细解释

### 1. Python 生成的时间

```python
from app.utils.datetime_utils import utc_now

# 现在调用
time = utc_now()
print(time)
# 输出：2025-10-22 10:00:00.123456+00:00

# 关键信息：
# - 日期：2025-10-22
# - 时间：10:00:00.123456
# - 时区：+00:00 (即 UTC)
```

### 2. SQLAlchemy 存储行为

```python
# 在 API 中
task.assigned_at = utc_now()
db.commit()

# SQLAlchemy 会：
# 1. 检测到这是 aware datetime（含时区信息）
# 2. 如果数据库字段是 TIMESTAMP（无时区类型）
#    → 存储时间值：2025-10-22 10:00:00.123456
#    → 丢弃时区信息（但时间值正确）
# 3. 如果数据库字段是 TIMESTAMP WITH TIME ZONE
#    → 存储时间值 + 时区信息
```

### 3. PostgreSQL 数据库中的实际存储

#### 当前字段定义（TIMESTAMP 类型）

```python
# backend/app/models/task.py
class Task(Base):
    assigned_at = Column(DateTime)  # 默认是 TIMESTAMP（无时区）
    submitted_at = Column(DateTime)
    reviewed_at = Column(DateTime)
```

**数据库中实际存储：**

```sql
-- 查看任务表中的时间
SELECT id, title, assigned_at, submitted_at, reviewed_at
FROM tasks
WHERE id = 'xxx';

-- 实际存储示例：
id           | task-001
assigned_at  | 2025-10-22 10:00:00.123456
submitted_at | 2025-10-22 11:30:00.654321
reviewed_at  | 2025-10-22 12:45:00.987654

-- 注意：
-- ✅ 存储的是 UTC 时间（10:00）
-- ✅ 格式正确（YYYY-MM-DD HH:MI:SS.ffffff）
-- ❌ 但没有显示时区标识（因为字段类型是 TIMESTAMP）
```

---

## 📋 存储格式对比

### 修复前（问题）

```
Python 生成：
datetime.now()
→ 2025-10-22 18:00:00（naive，本地时间或混乱）

存入数据库：
→ 2025-10-22 18:00:00（可能被误认为 UTC）

问题：
- 时区语义不明确
- 本地时间 vs UTC 时间混乱
- 序列化时缺少时区标识
```

### 修复后（正确）

```
Python 生成：
utc_now()
→ 2025-10-22 10:00:00+00:00（aware，明确 UTC）

存入数据库：
→ 2025-10-22 10:00:00.123456（存储 UTC 时间值）

优点：
- ✅ 明确是 UTC 时间
- ✅ 时间值正确
- ✅ 序列化时包含时区标识
- ✅ 前端能正确解析
```

---

## 🔄 完整流程示例

### 场景：北京时间 2025-10-22 18:00:00 领取任务

#### Step 1: 用户操作

```
用户在北京（UTC+8）
本地时间：2025-10-22 18:00:00
点击"领取任务"按钮
```

#### Step 2: 后端生成时间

```python
# backend/app/api/tasks.py
assigned_time = utc_now()

# 返回值：
# datetime(2025, 10, 22, 10, 0, 0, 123456, tzinfo=timezone.utc)
#         年   月   日  时 分 秒 微秒    时区(UTC)

# 字符串表示：
# 2025-10-22 10:00:00.123456+00:00
```

#### Step 3: 存入数据库

```python
task.assigned_at = assigned_time
db.commit()

# SQLAlchemy 执行 SQL：
INSERT INTO tasks (id, assigned_at, ...)
VALUES ('task-001', '2025-10-22 10:00:00.123456', ...);

# 或（UPDATE）
UPDATE tasks
SET assigned_at = '2025-10-22 10:00:00.123456'
WHERE id = 'task-001';
```

#### Step 4: 数据库存储

```
PostgreSQL 表 tasks：
+----------+----------------------------+
| id       | assigned_at                |
+----------+----------------------------+
| task-001 | 2025-10-22 10:00:00.123456 |
+----------+----------------------------+

存储的是：UTC 时间 10:00
对应北京时间：18:00（+8小时）
```

#### Step 5: 读取并返回前端

```python
# 查询任务
task = db.query(Task).filter(Task.id == 'task-001').first()

# task.assigned_at 读取出来：
# Python 对象：datetime(2025, 10, 22, 10, 0, 0, 123456)
# 注意：从数据库读出来时，默认是 naive datetime（无时区信息）

# 但是！当 Pydantic 序列化时：
# 如果原始对象是 aware datetime，会保留时区
# 我们在存入前是 aware 的，读取出来需要确保也是 aware
```

#### Step 6: Pydantic 序列化

```python
# FastAPI 返回 JSON
{
  "id": "task-001",
  "assigned_at": "2025-10-22T10:00:00.123456Z",  # ✅ 含 Z
  ...
}

# 或者
{
  "assigned_at": "2025-10-22T10:00:00.123456+00:00",  # ✅ 含时区
  ...
}
```

#### Step 7: 前端接收并显示

```javascript
// 前端收到
const assignedAt = '2025-10-22T10:00:00.123456Z'

// JavaScript 解析
const date = new Date(assignedAt)
// → Date object representing UTC 10:00

// 显示为本地时间
date.toLocaleString('zh-CN')
// → "2025/10/22 18:00:00"  ✅ 正确！
```

---

## 🔍 如何验证数据库中的时间

### 方法1：直接查询数据库

```bash
# 进入数据库容器
docker exec -it postgres psql -U your_user -d your_database

# 查看任务时间
SELECT id, title, assigned_at, submitted_at, reviewed_at, created_at
FROM tasks
ORDER BY created_at DESC
LIMIT 5;

# 输出示例：
            id            |     title      |      assigned_at        |      submitted_at
--------------------------+----------------+-------------------------+-------------------------
 task-12345               | 测试任务       | 2025-10-22 10:00:00.12  | 2025-10-22 11:30:00.45
 task-12346               | 另一个任务     | 2025-10-22 09:15:00.78  | 2025-10-22 10:20:00.99
```

### 方法2：通过 API 查看

```bash
# 调用 API
curl http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | python -m json.tool

# 输出：
{
  "id": "task-12345",
  "title": "测试任务",
  "assigned_at": "2025-10-22T10:00:00.123456Z",  # ✅ 含 Z
  "submitted_at": "2025-10-22T11:30:00.456789Z",
  ...
}
```

### 方法3：Python 脚本验证

```python
# backend/check_db_time.py
from app.database import SessionLocal
from app.models.task import Task
from app.utils.datetime_utils import utc_now

db = SessionLocal()

# 查询最近的任务
task = db.query(Task).order_by(Task.created_at.desc()).first()

if task:
    print(f"Task ID: {task.id}")
    print(f"Created At: {task.created_at}")
    print(f"Assigned At: {task.assigned_at}")
    print(f"Type: {type(task.assigned_at)}")
    print(f"Has timezone: {task.assigned_at.tzinfo if task.assigned_at else None}")

    # 比较当前时间
    now = utc_now()
    print(f"\nCurrent UTC time: {now}")
    print(f"ISO format: {now.isoformat()}")
```

---

## ⚠️ 重要说明

### 1. 数据库字段类型

**当前配置：**

```python
Column(DateTime)  # TIMESTAMP（不含时区信息）
```

**存储行为：**

- ✅ 存储时间值（如 `2025-10-22 10:00:00.123456`）
- ❌ 不存储时区信息（`+00:00` 被丢弃）
- ✅ 但时间值是正确的 UTC 时间

**读取行为：**

- ❌ 读出来是 naive datetime（无时区信息）
- ⚠️ 需要在应用层重新添加时区信息

### 2. 改进建议（可选）

**升级为 TIMESTAMP WITH TIME ZONE：**

```python
# 修改模型定义
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import TIMESTAMP

class Task(Base):
    # 修改前
    # assigned_at = Column(DateTime)

    # 修改后
    assigned_at = Column(TIMESTAMP(timezone=True))
    submitted_at = Column(TIMESTAMP(timezone=True))
    reviewed_at = Column(TIMESTAMP(timezone=True))
```

**优点：**

- ✅ 数据库明确存储时区信息
- ✅ 读取时自动还原为 aware datetime
- ✅ 更符合标准

**迁移 SQL：**

```sql
-- 修改字段类型
ALTER TABLE tasks
ALTER COLUMN assigned_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE tasks
ALTER COLUMN submitted_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE tasks
ALTER COLUMN reviewed_at TYPE TIMESTAMP WITH TIME ZONE;
```

### 3. 当前方案的兼容性

**无需修改数据库字段，当前方案也完全有效：**

1. ✅ Python 生成 aware datetime（含时区）
2. ✅ 存入数据库时存储正确的 UTC 时间值
3. ✅ 序列化时添加时区标识
4. ✅ 前端正确解析

**关键在于：**

- Python 层面明确使用 `utc_now()`
- 序列化时确保添加时区标识
- 前端正确解析时区

---

## 📊 数据示例对比

### 数据库视图

```sql
-- 查询最近任务
SELECT
    id,
    title,
    assigned_at,
    submitted_at,
    reviewed_at,
    to_char(assigned_at, 'YYYY-MM-DD HH24:MI:SS TZ') as assigned_at_with_tz
FROM tasks
WHERE assigned_at IS NOT NULL
ORDER BY assigned_at DESC
LIMIT 3;

-- 可能的输出：
id          | assigned_at              | assigned_at_with_tz
------------+--------------------------+---------------------------
task-001    | 2025-10-22 10:00:00.123  | 2025-10-22 10:00:00 UTC
task-002    | 2025-10-22 09:30:00.456  | 2025-10-22 09:30:00 UTC
task-003    | 2025-10-22 08:15:00.789  | 2025-10-22 08:15:00 UTC
```

### API 响应

```json
{
  "items": [
    {
      "id": "task-001",
      "title": "任务1",
      "assigned_at": "2025-10-22T10:00:00.123456Z",
      "created_at": "2025-10-22T09:00:00.000000Z"
    },
    {
      "id": "task-002",
      "title": "任务2",
      "assigned_at": "2025-10-22T09:30:00.456789Z",
      "created_at": "2025-10-22T08:30:00.000000Z"
    }
  ]
}
```

### 前端显示

```
任务1
领取时间：2025/10/22 18:00:00  (UTC 10:00 + 8 = 北京时间 18:00)

任务2
领取时间：2025/10/22 17:30:00  (UTC 09:30 + 8 = 北京时间 17:30)
```

---

## ✅ 总结

### 现在存入数据库的时间

**格式：** `YYYY-MM-DD HH:MM:SS.ffffff`

**时区：** UTC（协调世界时）

**示例：** `2025-10-22 10:00:00.123456`

**含义：**

- 这是 UTC 时间的 10:00
- 对应北京时间 18:00
- 对应纽约时间 05:00（UTC-5）
- 对应伦敦时间 10:00（UTC+0）

### 关键优势

1. ✅ **统一标准** - 所有时间都是 UTC
2. ✅ **明确语义** - Python 层面是 aware datetime
3. ✅ **正确序列化** - API 返回含时区标识
4. ✅ **前端正确** - 自动转换为本地时间
5. ✅ **易于维护** - 集中使用 `utc_now()`

---

**文档完成时间：** 2025-10-22  
**存储格式：** UTC TIMESTAMP  
**序列化格式：** ISO 8601 with timezone
