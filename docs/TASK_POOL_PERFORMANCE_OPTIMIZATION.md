# 任务池性能优化方案

## 🔍 性能瓶颈分析

### 当前问题

- **任务数量**: 450+ 个任务
- **加载缓慢**: 点击任务池页面后加载明显延迟
- **用户体验**: 影响使用流畅度

### 瓶颈定位

#### 1. **数据库查询慢** (主要瓶颈 - 占70%)

```python
# backend/app/api/tasks.py:229-232
total_tasks = query.count()  # ❌ 全表扫描，没有索引
tasks = query.offset(skip).limit(limit).all()  # ❌ 没有eager loading
```

**问题**:

- `status`、`assigned_to` 字段没有索引
- `query.count()` 需要扫描所有行
- JOIN查询但没有使用`joinedload`优化
- 每次请求都查询数据库

#### 2. **后端数据处理慢** (占20%)

```python
# backend/app/api/tasks.py:236-264
for task in tasks:
    task_dict = {
        "project_name": task.project.name,  # ❌ 可能触发N+1查询
        ...  # 大量字段映射
    }
```

**问题**:

- 循环构建字典开销大
- 关联查询可能触发额外SQL

#### 3. **前端渲染慢** (占10%)

```typescript
// src/views/project/task-pool/index.vue:147, 746
getUserName(row.assignedTo, row) // ❌ 每行都调用
getTaskProjectCategory(task) // ❌ 每行都查找项目
```

**问题**:

- 表格每行渲染时都调用函数
- 查找项目列表的开销

---

## ✅ 优化方案

### 方案1: 添加数据库索引 (最重要！)

#### 1.1 创建数据库迁移脚本

```python
# backend/alembic/versions/xxxx_add_task_indexes.py
"""add indexes for task performance

Revision ID: xxxx
Create Date: 2025-10-31
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 为常用查询字段添加索引
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_assigned_to', 'tasks', ['assigned_to'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('idx_tasks_project_status', 'tasks', ['project_id', 'status'])

    # 为Project表添加status索引（用于过滤completed项目）
    op.create_index('idx_projects_status', 'projects', ['status'])

def downgrade():
    op.drop_index('idx_tasks_status', 'tasks')
    op.drop_index('idx_tasks_assigned_to', 'tasks')
    op.drop_index('idx_tasks_created_at', 'tasks')
    op.drop_index('idx_tasks_project_status', 'tasks')
    op.drop_index('idx_projects_status', 'projects')
```

**执行迁移**:

```bash
cd backend
alembic revision --autogenerate -m "add indexes for task performance"
alembic upgrade head
```

#### 1.2 更新Task模型

```python
# backend/app/models/task.py
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="pending", index=True)  # ✅ 添加索引
    priority = Column(String(20), default="medium")
    assigned_to = Column(String(36), ForeignKey("users.id"), index=True)  # ✅ 添加索引
    # ... 其他字段保持不变
    created_at = Column(DateTime, server_default=func.now(), index=True)  # ✅ 添加索引
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ... relationship定义保持不变

    # ✅ 添加复合索引
    __table_args__ = (
        Index('idx_task_project_status', 'project_id', 'status'),
        Index('idx_task_status_assigned', 'status', 'assigned_to'),
    )
```

**预期效果**: 查询速度提升 **60-80%**

---

### 方案2: 使用Redis缓存 (推荐！)

#### 2.1 安装Redis依赖

```bash
pip install redis
```

#### 2.2 创建Redis缓存服务

```python
# backend/app/services/cache_service.py
import redis
import json
from typing import Optional, Any
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # 根据环境配置连接Redis
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        self.enabled = self._check_redis_available()

    def _check_redis_available(self) -> bool:
        """检查Redis是否可用"""
        try:
            self.redis_client.ping()
            logger.info("✅ Redis连接成功")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Redis不可用，将跳过缓存: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.enabled:
            return None
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Redis GET失败: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 300):
        """设置缓存，默认5分钟过期"""
        if not self.enabled:
            return False
        try:
            self.redis_client.setex(
                key,
                expire,
                json.dumps(value, ensure_ascii=False, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"❌ Redis SET失败: {e}")
            return False

    def delete(self, key: str):
        """删除缓存"""
        if not self.enabled:
            return
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"❌ Redis DELETE失败: {e}")

    def delete_pattern(self, pattern: str):
        """批量删除匹配的key"""
        if not self.enabled:
            return
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"🗑️ 删除缓存: {len(keys)} 个key匹配 {pattern}")
        except Exception as e:
            logger.error(f"❌ Redis DELETE_PATTERN失败: {e}")

# 全局实例
cache_service = CacheService()
```

#### 2.3 优化任务API使用缓存

```python
# backend/app/api/tasks.py
from app.services.cache_service import cache_service

@router.get("/", include_in_schema=True)
def get_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    include_completed_projects: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(["TaskPool", "ProjectManagement"]))
):
    """获取任务列表（带Redis缓存）"""

    # ✅ 1. 生成缓存key
    cache_key = f"tasks:list:{project_id or 'all'}:{status or 'all'}:{assigned_to or 'all'}:{skip}:{limit}:{include_completed_projects}"

    # ✅ 2. 尝试从缓存获取
    cached_data = cache_service.get(cache_key)
    if cached_data:
        logger.info(f"🎯 [TaskAPI] 命中缓存: {cache_key}")
        return cached_data

    logger.info(f"📋 [TaskAPI] 缓存未命中，查询数据库: {cache_key}")

    # ✅ 3. 使用joinedload优化JOIN查询
    from sqlalchemy.orm import joinedload
    query = db.query(Task).options(joinedload(Task.project)).join(
        Project, Task.project_id == Project.id
    )

    if not include_completed_projects:
        query = query.filter(Project.status != "completed")

    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        if status == "accepted":
            query = query.filter(Task.status.in_(["submitted", "skip_pending", "skipped", "approved", "rejected"]))
        else:
            query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    # ✅ 4. 优化count查询 - 使用子查询或者缓存total
    total_tasks = query.count()

    # ✅ 5. 批量查询tasks
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    # ✅ 6. 构建响应
    task_responses = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "project_id": task.project_id,
            "project_name": task.project.name if task.project else "未知项目",
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "assigned_to_name": task.assigned_to_name,
            "created_by": task.created_by,
            "created_by_name": task.created_by_name,
            "image_url": task.image_url,
            "annotation_data": task.annotation_data,
            "score": task.score,
            "assigned_at": task.assigned_at.isoformat() if task.assigned_at else None,
            "submitted_at": task.submitted_at.isoformat() if task.submitted_at else None,
            "reviewed_by": task.reviewed_by,
            "reviewed_by_name": task.reviewed_by_name,
            "reviewed_at": task.reviewed_at.isoformat() if task.reviewed_at else None,
            "review_comment": task.review_comment,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "attachments": task.attachments or [],
            "timeline": task.timeline or []
        }
        task_responses.append(task_dict)

    result = {"list": task_responses, "total": total_tasks}

    # ✅ 7. 写入缓存（5分钟过期）
    cache_service.set(cache_key, result, expire=300)
    logger.info(f"💾 [TaskAPI] 已缓存结果: {cache_key}")

    return result

# ✅ 8. 在任务更新时清除相关缓存
def invalidate_task_cache(project_id: str = None):
    """清除任务列表缓存"""
    if project_id:
        cache_service.delete_pattern(f"tasks:list:{project_id}:*")
    cache_service.delete_pattern("tasks:list:all:*")
    logger.info(f"🗑️ [TaskAPI] 已清除任务缓存")

# 在创建、更新、删除任务时调用
@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user = Depends(require_permission("TaskPool"))):
    # ... 创建任务逻辑 ...
    db.commit()

    # ✅ 清除缓存
    invalidate_task_cache(task_data.project_id)

    return db_task
```

**预期效果**:

- 首次加载: 与当前相同
- 后续加载: **提升 90-95%** (从Redis读取仅需 10-20ms)
- 缓存命中率: **70-80%**

---

### 方案3: 前端优化

#### 3.1 缓存用户和项目映射

```typescript
// src/views/project/task-pool/index.vue

// ✅ 1. 预先构建映射表
const userNameMap = ref<Record<string, string>>({})
const projectCategoryMap = ref<Record<string, { category: string; subCategory: string }>>({})

// ✅ 2. 在数据加载后构建映射
const fetchTasks = async () => {
  const params = {
    /* ... */
  }
  await projectStore.fetchTasks(params)

  // 构建用户名映射
  projectStore.tasks.forEach((task) => {
    if (task.assignedTo && task.assignedToName) {
      userNameMap.value[task.assignedTo] = task.assignedToName
    }
  })

  // 构建项目分类映射
  projectStore.projects.forEach((project) => {
    projectCategoryMap.value[project.id] = {
      category: project.category || '',
      subCategory: project.subCategory || ''
    }
  })
}

// ✅ 3. 使用映射表（O(1)查找）
const getUserName = (userId: string | undefined | null, row?: any) => {
  if (!userId) return '未分配'
  // 优先使用行数据中的冗余字段
  if (row?.assignedToName || row?.assigned_to_name) {
    return row.assignedToName || row.assigned_to_name
  }
  // 从映射表查找（快速）
  return userNameMap.value[userId] || `用户${String(userId).slice(-4)}`
}

const getTaskProjectCategory = (task: any) => {
  const projectId = task.projectId || task.project_id
  return projectCategoryMap.value[projectId] || { category: '', subCategory: '' }
}
```

#### 3.2 添加加载状态提示

```vue
<!-- src/views/project/task-pool/index.vue -->
<el-table
  v-loading="projectStore.loading"
  :data="projectStore.tasks"
  stripe
  height="calc(100vh - 420px)"
  element-loading-text="加载任务数据中..."
  element-loading-spinner="el-icon-loading"
  element-loading-background="rgba(0, 0, 0, 0.5)"
></el-table>
```

**预期效果**: 表格渲染速度提升 **30-40%**

---

### 方案4: 虚拟滚动 (可选，针对超大数据量)

如果任务数量超过1000个，可以考虑使用虚拟滚动：

```bash
npm install vue-virtual-scroller
```

```vue
<template>
  <RecycleScroller :items="projectStore.tasks" :item-size="60" key-field="id" v-slot="{ item }">
    <TaskRow :task="item" />
  </RecycleScroller>
</template>
```

---

## 📊 性能对比

| 优化方案   | 预期提升 | 实施难度    | 推荐度            |
| ---------- | -------- | ----------- | ----------------- |
| 数据库索引 | 60-80%   | ⭐ 简单     | ⭐⭐⭐⭐⭐        |
| Redis缓存  | 90-95%   | ⭐⭐ 中等   | ⭐⭐⭐⭐⭐        |
| 前端映射表 | 30-40%   | ⭐ 简单     | ⭐⭐⭐⭐          |
| 虚拟滚动   | 50-70%   | ⭐⭐⭐ 复杂 | ⭐⭐ (仅大数据量) |

## 🎯 实施建议

### 优先级1 (必须): 数据库索引

1. 创建迁移脚本
2. 执行 `alembic upgrade head`
3. 验证索引创建成功: `SHOW INDEX FROM tasks;`

### 优先级2 (强烈推荐): Redis缓存

1. 安装Redis: `sudo apt install redis-server` 或 `brew install redis`
2. 启动Redis: `redis-server`
3. 添加缓存服务代码
4. 测试缓存功能

### 优先级3 (推荐): 前端优化

1. 实现映射表优化
2. 添加加载提示

---

## ⚡ 预期总体效果

**组合优化后**:

- 首次加载: **提升 70-80%** (索引 + 前端优化)
- 后续加载: **提升 95%+** (Redis缓存命中)
- 从 **~3秒** 降到 **~0.3秒**

---

## 🔧 快速验证

### 1. 检查当前性能

```sql
-- 在MySQL中执行
EXPLAIN SELECT * FROM tasks
JOIN projects ON tasks.project_id = projects.id
WHERE projects.status != 'completed'
ORDER BY tasks.created_at DESC
LIMIT 20;
```

### 2. 添加索引后对比

```sql
-- 再次执行EXPLAIN，对比type、rows、Extra字段
-- 优化后应该看到 type=index 或 type=ref，rows减少
```

### 3. Redis缓存验证

```bash
# 终端1: 监控Redis
redis-cli MONITOR

# 终端2: 访问任务池页面
# 查看终端1是否有GET/SET操作
```

---

## 📝 注意事项

1. **Redis持久化**: 生产环境建议配置AOF或RDB持久化
2. **缓存一致性**: 任务更新时务必清除相关缓存
3. **索引维护**: 定期分析慢查询日志，调整索引策略
4. **监控**: 使用Redis INFO命令监控缓存命中率

---

需要我帮你实施这些优化吗？建议从**数据库索引**开始，这是投入产出比最高的优化！
