# 🚀 任务池性能优化 - 执行指南

## 📊 当前状态

- **任务数量**: 450+
- **加载速度**: ~3秒 (慢)
- **优化目标**: <0.5秒

## ✅ 已完成的优化

### 1. 数据库索引优化 (预期提升 60-80%)

已为以下字段添加索引：

- `tasks.status` - 状态筛选
- `tasks.assigned_to` - 分配人筛选
- `tasks.created_at` - 时间排序
- `tasks.project_id` - 项目关联
- `projects.status` - 过滤完结项目

复合索引：

- `idx_task_project_status` - 项目+状态组合查询
- `idx_task_status_assigned` - 状态+分配人组合查询

## 🎯 执行步骤

### 步骤1: 应用数据库迁移

```bash
cd backend

# 1. 查看当前迁移状态
alembic current

# 2. 查看待执行的迁移
alembic history

# 3. 应用性能优化迁移
alembic upgrade head

# 4. 验证索引创建成功
# 如果使用MySQL:
mysql -u your_user -p your_database -e "SHOW INDEX FROM tasks;"
mysql -u your_user -p your_database -e "SHOW INDEX FROM projects;"

# 如果使用PostgreSQL:
psql -d your_database -c "\d tasks"
psql -d your_database -c "\d projects"
```

**预期输出**:

```
✅ 性能索引创建成功！预期查询速度提升 60-80%
```

### 步骤2: 验证查询性能

#### 2.1 查看执行计划（MySQL）

```sql
-- 优化前后对比
EXPLAIN SELECT * FROM tasks
JOIN projects ON tasks.project_id = projects.id
WHERE projects.status != 'completed'
AND tasks.status = 'pending'
ORDER BY tasks.created_at DESC
LIMIT 20;
```

**优化前**:

- type: ALL (全表扫描)
- rows: 450+
- Extra: Using filesort

**优化后**:

- type: ref 或 index
- rows: <50
- Extra: Using index

#### 2.2 测试查询速度

```bash
# 在项目根目录执行
cd backend
python -c "
import time
from app.database import SessionLocal
from app.models.task import Task
from app.models.project import Project

db = SessionLocal()

# 测试查询速度
start = time.time()
query = db.query(Task).join(Project).filter(Project.status != 'completed').limit(20)
tasks = query.all()
end = time.time()

print(f'✅ 查询耗时: {(end - start)*1000:.2f}ms')
print(f'✅ 返回任务数: {len(tasks)}')
db.close()
"
```

**预期结果**:

- 优化前: ~500-1000ms
- 优化后: ~50-150ms
- **提升**: 70-85%

### 步骤3: 重启后端服务

```bash
# 如果使用uvicorn
pkill -f uvicorn
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者如果有systemd服务
sudo systemctl restart your-backend-service
```

### 步骤4: 测试前端加载速度

1. 打开浏览器开发者工具 (F12)
2. 切换到 Network 标签
3. 访问任务池页面: `http://localhost:3006/project/task-pool`
4. 查看 `/api/tasks/` 请求的响应时间

**预期结果**:

- 优化前: ~1000-2000ms
- 优化后: ~200-400ms
- **提升**: 60-80%

---

## 📈 性能监控

### 实时监控查询性能

#### MySQL 慢查询日志

```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.5;  -- 超过0.5秒的查询会被记录

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log_file';
```

#### 查看索引使用情况

```sql
-- 查看索引统计
SELECT
    TABLE_NAME,
    INDEX_NAME,
    SEQ_IN_INDEX,
    COLUMN_NAME
FROM
    information_schema.STATISTICS
WHERE
    TABLE_SCHEMA = 'your_database'
    AND TABLE_NAME IN ('tasks', 'projects')
ORDER BY
    TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
```

---

## 🔧 常见问题

### Q1: 迁移失败 - "索引已存在"

```bash
# 解决方案：删除已有索引
mysql -u user -p database -e "DROP INDEX idx_tasks_status ON tasks;"

# 然后重新执行迁移
alembic upgrade head
```

### Q2: 查询仍然很慢

```sql
-- 检查索引是否被使用
EXPLAIN SELECT * FROM tasks WHERE status = 'pending';

-- 如果type仍然是ALL，尝试分析表
ANALYZE TABLE tasks;
OPTIMIZE TABLE tasks;
```

### Q3: 索引占用空间过大

```sql
-- 查看索引大小
SELECT
    TABLE_NAME,
    INDEX_NAME,
    ROUND(SUM(stat_value * @@innodb_page_size) / 1024 / 1024, 2) AS size_mb
FROM
    mysql.innodb_index_stats
WHERE
    database_name = 'your_database'
    AND TABLE_NAME IN ('tasks', 'projects')
GROUP BY
    TABLE_NAME, INDEX_NAME;
```

一般情况下，索引占用 5-10% 的表空间是正常的。

---

## 🚀 下一步优化（可选）

### Redis缓存 (推荐)

如果性能仍不满意，可以添加Redis缓存，预期再提升 **80-90%**

```bash
# 1. 安装Redis
sudo apt install redis-server  # Ubuntu/Debian
brew install redis              # macOS

# 2. 启动Redis
redis-server

# 3. 安装Python Redis客户端
cd backend
pip install redis

# 4. 应用缓存代码（见 TASK_POOL_PERFORMANCE_OPTIMIZATION.md）
```

### 虚拟滚动 (1000+任务时推荐)

如果任务数量超过1000个，可以考虑前端虚拟滚动

```bash
cd frontend
npm install vue-virtual-scroller
```

---

## 📊 预期效果对比

| 场景     | 优化前 | 优化后 | 提升    |
| -------- | ------ | ------ | ------- |
| 首次加载 | ~3秒   | ~0.8秒 | **73%** |
| 筛选查询 | ~2秒   | ~0.5秒 | **75%** |
| 分页切换 | ~1.5秒 | ~0.4秒 | **73%** |

---

## ✅ 验证清单

完成以下检查确保优化生效：

- [ ] 数据库迁移成功执行
- [ ] 索引已创建 (使用 `SHOW INDEX` 验证)
- [ ] 后端服务已重启
- [ ] 任务池页面加载时间 < 1秒
- [ ] Network请求 `/api/tasks/` 响应时间 < 500ms
- [ ] 浏览器控制台无错误

---

## 📞 需要帮助？

如果遇到问题，请检查：

1. 数据库连接是否正常
2. Alembic版本是否最新
3. 数据库用户是否有CREATE INDEX权限
4. 日志文件中是否有错误信息

查看详细优化方案：`TASK_POOL_PERFORMANCE_OPTIMIZATION.md`
