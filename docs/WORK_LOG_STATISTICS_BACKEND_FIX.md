# 工作日志统计报表后端修复

## 🐛 问题描述

工作类型堆叠图显示为空白，原因是后端统计API没有提供 `work_type_hours` 字段。

**问题截图**：

- 第一个图表"员工工作类型工时统计"是空白的
- 只显示了横轴和纵轴标签，但没有柱状图数据

---

## ✅ 解决方案

### 1. 后端API修改

**文件**：`backend/app/api/work_logs.py`

**接口**：`GET /api/work-weeks/{week_id}/statistics`

#### 修改点1：统计时按工作类型分组

**位置**：第688-713行

```python
# 按用户统计
user_stats = {}
for entry in entries:
    user_id = entry.user_id
    if user_id not in user_stats:
        user_stats[user_id] = {
            'user_id': user_id,
            'user_name': getattr(entry.user, 'real_name', None) or getattr(entry.user, 'username', ''),
            'entries': [],
            'total_planned_hours': 0,
            'total_actual_hours': 0,
            'completion_rates': [],
            'status_count': {'pending': 0, 'submitted': 0, 'approved': 0, 'rejected': 0},
            'work_type_hours': {}  # ✅ 新增：按工作类型统计工时
        }

    user_stats[user_id]['entries'].append(entry)
    user_stats[user_id]['total_planned_hours'] += entry.planned_hours
    if entry.actual_hours:
        user_stats[user_id]['total_actual_hours'] += entry.actual_hours
        # ✅ 新增：按工作类型统计实际工时
        work_type = entry.work_type or '其他'
        if work_type not in user_stats[user_id]['work_type_hours']:
            user_stats[user_id]['work_type_hours'][work_type] = 0
        user_stats[user_id]['work_type_hours'][work_type] += entry.actual_hours
    user_stats[user_id]['completion_rates'].append(entry.completion_rate)
    user_stats[user_id]['status_count'][entry.status] += 1
```

**关键逻辑**：

- 获取每个日志条目的 `work_type` 字段
- 如果 `work_type` 为空，默认为"其他"
- 按工作类型累加实际工时（`actual_hours`）

---

#### 修改点2：返回数据中包含工作类型工时

**位置**：第715-734行

```python
# 生成用户汇总
user_summaries = []
for user_id, stats in user_stats.items():
    avg_completion = sum(stats['completion_rates']) / len(stats['completion_rates']) if stats['completion_rates'] else 0
    submitted_days = stats['status_count']['submitted'] + stats['status_count']['approved']

    summary_dict = {
        'work_week_id': week_id,
        'user_id': user_id,
        'user_name': stats['user_name'],
        'total_planned_hours': stats['total_planned_hours'],
        'total_actual_hours': stats['total_actual_hours'],
        'average_completion_rate': avg_completion,
        'submitted_days': submitted_days,
        'total_days': len(stats['entries']),
        'status_summary': stats['status_count'],
        'total_entries': len(stats['entries']),  # ✅ 新增
        'work_type_hours': stats['work_type_hours']  # ✅ 新增
    }
    user_summaries.append(WorkWeekSummary(**summary_dict))
```

---

### 2. Schema模型修改

**文件**：`backend/app/schemas/work_log.py`

**位置**：第156-167行

```python
class WorkWeekSummary(BaseModel):
    work_week_id: str
    user_id: str
    user_name: str
    total_planned_hours: int
    total_actual_hours: int
    average_completion_rate: float
    submitted_days: int
    total_days: int
    status_summary: Dict[str, int]  # 各状态的天数统计
    total_entries: int = 0  # ✅ 新增：日志条目总数
    work_type_hours: Dict[str, int] = {}  # ✅ 新增：按工作类型统计的工时
```

**字段说明**：

- `total_entries`：该用户本周的日志条目总数
- `work_type_hours`：字典类型，键为工作类型，值为该类型的总工时

---

## 📊 返回数据示例

### API响应格式

```json
{
  "work_week": {
    "id": "week-001",
    "title": "2025W51标注组工作计划",
    ...
  },
  "overall_stats": {
    "total_users": 2,
    "total_entries": 10,
    "submitted_entries": 8,
    "completion_rate": 80.0,
    "total_planned_hours": 80,
    "total_actual_hours": 78
  },
  "user_summaries": [
    {
      "work_week_id": "week-001",
      "user_id": "user-001",
      "user_name": "高培璐国政",
      "total_planned_hours": 40,
      "total_actual_hours": 40,
      "average_completion_rate": 100.0,
      "submitted_days": 5,
      "total_days": 5,
      "status_summary": {
        "pending": 0,
        "submitted": 5,
        "approved": 0,
        "rejected": 0
      },
      "total_entries": 5,
      "work_type_hours": {
        "标注": 32,
        "会议": 5,
        "文档": 3
      }
    },
    {
      "work_week_id": "week-001",
      "user_id": "user-002",
      "user_name": "张泳娜",
      "total_planned_hours": 40,
      "total_actual_hours": 38,
      "average_completion_rate": 95.0,
      "submitted_days": 5,
      "total_days": 5,
      "status_summary": {
        "pending": 0,
        "submitted": 5,
        "approved": 0,
        "rejected": 0
      },
      "total_entries": 5,
      "work_type_hours": {
        "标注": 30,
        "审核": 6,
        "会议": 2
      }
    }
  ]
}
```

---

## 🔍 数据来源说明

### WorkLogEntry 模型字段

**文件**：`backend/app/models/work_log.py`

**相关字段**：

```python
class WorkLogEntry(Base):
    """工作日志条目表"""
    __tablename__ = "work_log_entries"

    # ...
    work_type = Column(String(50), comment="工作类型（开发、测试、会议、学习等）")
    actual_hours = Column(Integer, comment="实际工作小时数")
    # ...
```

**数据统计**：

1. 获取工作周的所有日志条目
2. 按用户分组
3. 对每个用户的日志条目：
   - 提取 `work_type` 字段（如果为空，默认为"其他"）
   - 累加该类型的 `actual_hours`
4. 生成 `work_type_hours` 字典

---

## 🎨 前端图表效果

### 修复前

```
工时 (小时)
┌─────────────────────────────┐
│                             │
│                             │
│        （空白图表）          │
│                             │
│                             │
└─────────────────────────────┘
  高培璐国政    张泳娜
```

### 修复后

```
工时 (小时)
 40h ┤
     │   ████ 文档
 30h ┤   ████ 会议
     │   ████ 审核
 20h ┤   ████ 标注
     │   ████
 10h ┤   ████
     │   ████
  0h └───────┴───────
     高培璐国政  张泳娜

图例：
■ 标注: #17a2b8
■ 审核: #ff9800
■ 会议: #f56c6c
■ 文档: #909399
```

---

## 🚀 部署步骤

### 1. 重启后端服务

```bash
# 方式1：直接重启
cd backend
python -m uvicorn app.main:app --reload

# 方式2：Docker重启
docker-compose restart backend
```

### 2. 验证API响应

**打开浏览器控制台**，查看统计API的响应：

```javascript
// 在浏览器控制台执行
fetch('/api/work-logs/weeks/{week_id}/statistics', {
  headers: {
    Authorization: 'Bearer YOUR_TOKEN'
  }
})
  .then((r) => r.json())
  .then((data) => {
    console.log(
      '用户工作类型统计:',
      data.user_summaries.map((u) => ({
        name: u.user_name,
        work_types: u.work_type_hours
      }))
    )
  })
```

**预期输出**：

```javascript
;[
  {
    name: '高培璐国政',
    work_types: { 标注: 32, 会议: 5, 文档: 3 }
  },
  {
    name: '张泳娜',
    work_types: { 标注: 30, 审核: 6, 会议: 2 }
  }
]
```

### 3. 刷新前端页面

1. **清除缓存**（Ctrl + F5 或 Cmd + Shift + R）
2. **打开统计报表**
3. **验证图表**：
   - ✅ 堆叠柱状图显示数据
   - ✅ 不同工作类型有不同颜色
   - ✅ 鼠标悬停显示详细信息

---

## 📝 数据填写说明

### 工作日志填写时指定工作类型

**位置**：工作周详情页 > 添加/编辑日志条目

**工作类型选项**（示例）：

- 开发
- 测试
- 标注
- 审核
- 培训
- 会议
- 文档
- 设计
- 请假
- 病假
- 年假
- 其他

**重要**：

- 每个日志条目都应该指定工作类型
- 如果不指定，默认归类为"其他"
- 只有有实际工时（`actual_hours` > 0）的条目才会计入统计

---

## 🔧 故障排查

### 问题1：图表仍然是空白

**可能原因**：

1. 后端服务没有重启
2. 浏览器缓存没有清除
3. 所有日志条目的 `actual_hours` 都为 0 或 null

**解决方法**：

```bash
# 1. 检查后端日志
tail -f backend/logs/app.log

# 2. 检查数据库
psql -U your_user -d your_db
SELECT
  wle.user_id,
  u.real_name,
  wle.work_type,
  wle.actual_hours
FROM work_log_entries wle
JOIN users u ON wle.user_id = u.id
WHERE wle.work_week_id = 'your_week_id';

# 3. 强制清除浏览器缓存
# Chrome: Ctrl + Shift + Delete > 清除缓存
# Firefox: Ctrl + Shift + Delete > 清除缓存
```

---

### 问题2：某些工作类型没有显示

**可能原因**：

- 该工作类型的工时为 0
- `work_type` 字段为空（归类到"其他"）

**解决方法**：

1. 检查日志条目是否填写了工作类型
2. 检查是否填写了实际工时
3. 查看图例中的"其他"类型

---

### 问题3：工时数据不准确

**可能原因**：

- 日志条目的 `actual_hours` 填写错误
- 多个日志条目的工时重复计算

**解决方法**：

```python
# 在后端添加调试日志
for entry in entries:
    print(f"用户: {entry.user.real_name}, 工作类型: {entry.work_type}, 实际工时: {entry.actual_hours}")
```

---

## 📚 相关文档

- [工作日志统计报表重构](./WORK_LOG_STATISTICS_REFACTOR.md)
- [工作日志周表格优化](./WORK_LOG_WEEK_DAYS_UPDATE.md)
- [工作日志条目控件优化](./WORK_LOG_ENTRY_CELL_OPTIMIZATION.md)

---

## 📊 测试数据示例

### 创建测试数据

```sql
-- 插入测试工作日志条目
INSERT INTO work_log_entries (
  id, work_week_id, user_id, work_date, day_of_week,
  work_content, work_type, actual_hours, status
) VALUES
  -- 高培璐国政
  ('entry-001', 'week-001', 'user-001', '2025-01-06', 1, '数据标注', '标注', 8, 'submitted'),
  ('entry-002', 'week-001', 'user-001', '2025-01-07', 2, '数据标注', '标注', 8, 'submitted'),
  ('entry-003', 'week-001', 'user-001', '2025-01-08', 3, '数据标注+会议', '标注', 6, 'submitted'),
  ('entry-004', 'week-001', 'user-001', '2025-01-08', 3, '团队会议', '会议', 2, 'submitted'),
  ('entry-005', 'week-001', 'user-001', '2025-01-09', 4, '数据标注', '标注', 8, 'submitted'),
  ('entry-006', 'week-001', 'user-001', '2025-01-10', 5, '数据标注+文档', '标注', 5, 'submitted'),
  ('entry-007', 'week-001', 'user-001', '2025-01-10', 5, '编写文档', '文档', 3, 'submitted'),

  -- 张泳娜
  ('entry-008', 'week-001', 'user-002', '2025-01-06', 1, '数据标注', '标注', 8, 'submitted'),
  ('entry-009', 'week-001', 'user-002', '2025-01-07', 2, '数据标注', '标注', 7, 'submitted'),
  ('entry-010', 'week-001', 'user-002', '2025-01-08', 3, '数据审核', '审核', 6, 'submitted'),
  ('entry-011', 'week-001', 'user-002', '2025-01-09', 4, '数据标注', '标注', 8, 'submitted'),
  ('entry-012', 'week-001', 'user-002', '2025-01-10', 5, '数据标注+审核', '标注', 5, 'submitted'),
  ('entry-013', 'week-001', 'user-002', '2025-01-10', 5, '数据审核', '审核', 2, 'submitted');
```

### 预期统计结果

**高培璐国政**：

- 标注: 32h (8 + 8 + 6 + 8 + 5)
- 会议: 5h (2 + 3)
- 文档: 3h

**张泳娜**：

- 标注: 28h (8 + 7 + 8 + 5)
- 审核: 8h (6 + 2)
- 会议: 2h

---

**版本**: v1.0  
**更新时间**: 2025-10-17  
**修复人员**: AI Assistant

**状态**: ✅ 已修复，待测试
