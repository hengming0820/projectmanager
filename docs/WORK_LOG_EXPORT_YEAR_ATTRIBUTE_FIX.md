# 🔧 工作日志导出 WorkWeek Year 属性错误修复

> 🗓️ **修复日期**: 2025-10-27  
> 🐛 **错误**: 'WorkWeek' object has no attribute 'year'  
> ✅ **状态**: 已修复

---

## 🐛 错误信息

```
AttributeError: 'WorkWeek' object has no attribute 'year'
```

**完整堆栈跟踪：**

```python
File "backend/app/api/work_logs.py", line 945, in export_work_week_report
    'year': work_week.year,
AttributeError: 'WorkWeek' object has no attribute 'year'
```

---

## 🔍 问题原因

### WorkWeek 模型实际结构

查看 `backend/app/models/work_log.py` 中的 `WorkWeek` 模型定义：

```python
class WorkWeek(Base):
    """工作周模板表"""
    __tablename__ = "work_weeks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="工作周标题")
    week_start_date = Column(Date, nullable=False, comment="周开始日期（周一）")
    week_end_date = Column(Date, nullable=False, comment="周结束日期（周五）")
    description = Column(Text, comment="工作周描述")
    status = Column(String(20), default="active")
    config = Column(JSON, comment="周配置信息")
    # ... 其他字段
```

**关键发现：**

- ❌ `WorkWeek` 模型**没有** `year` 字段
- ❌ `WorkWeek` 模型**没有** `week_number` 字段
- ✅ 只有 `week_start_date` 和 `week_end_date` 字段

### 错误代码

```python
work_week_info = {
    'title': work_week.title,
    'week_start_date': work_week.week_start_date.strftime('%Y-%m-%d'),
    'week_end_date': work_week.week_end_date.strftime('%Y-%m-%d'),
    'year': work_week.year,           # ❌ 不存在的属性
    'week_number': work_week.week_number,  # ❌ 不存在的属性
    'status': work_week.status,
    'status_text': status_text_map.get(work_week.status, '未知')
}
```

---

## ✅ 解决方案

### 后端修复

从 `week_start_date` 中计算年份和周数：

```python
# 从日期中提取年份和周数
year = work_week.week_start_date.year
# 计算ISO周数
week_number = work_week.week_start_date.isocalendar()[1]

work_week_info = {
    'title': work_week.title,
    'week_start_date': work_week.week_start_date.strftime('%Y-%m-%d'),
    'week_end_date': work_week.week_end_date.strftime('%Y-%m-%d'),
    'year': year,                      # ✅ 从日期计算
    'week_number': week_number,        # ✅ 从日期计算
    'status': work_week.status,
    'status_text': status_text_map.get(work_week.status, '未知')
}
```

**关键方法：**

- `date.year` - 获取日期的年份
- `date.isocalendar()[1]` - 获取ISO周数（1-53）

### 前端修复

前端在初始化导出表单时，也错误地尝试访问 `workWeek.value?.year`：

**修复前：**

```typescript
exportForm.value.year = (workWeek.value?.year || new Date().getFullYear()).toString()
```

**修复后：**

```typescript
// 从 week_start_date 中提取年份
let defaultYear = new Date().getFullYear()
if (workWeek.value?.week_start_date) {
  defaultYear = new Date(workWeek.value.week_start_date).getFullYear()
}

exportForm.value.year = defaultYear.toString()
```

---

## 📊 ISO 周数说明

### isocalendar() 方法

Python 的 `date.isocalendar()` 返回一个元组 `(year, week, weekday)`：

```python
from datetime import date

d = date(2025, 10, 27)  # 2025年10月27日（周一）
iso = d.isocalendar()
# 返回: (2025, 44, 1)
# 其中:
#   2025 - ISO年份
#   44 - ISO周数（第44周）
#   1 - 星期几（1=周一, 7=周日）
```

**取周数：**

```python
week_number = d.isocalendar()[1]  # 44
```

### ISO周数特点

1. **周一作为一周的开始**
2. **第一周的定义**：包含1月4日的那一周
3. **周数范围**：1-52 或 1-53（闰周）

---

## 🔧 修改内容

### 后端文件

- `backend/app/api/work_logs.py`

**修改位置：**

- 第 941-954 行：单个工作周导出（`export_work_week_report` 函数）

### 前端文件

- `src/views/work-log/week-detail.vue`

**修改位置：**

- 第 912-928 行：打开导出对话框（`exportWorkLog` 函数）

---

## 📝 代码对比

### 后端修改

#### 修改前 ❌

```python
work_week_info = {
    'title': work_week.title,
    'week_start_date': work_week.week_start_date.strftime('%Y-%m-%d'),
    'week_end_date': work_week.week_end_date.strftime('%Y-%m-%d'),
    'year': work_week.year,           # AttributeError!
    'week_number': work_week.week_number,  # AttributeError!
    'status': work_week.status,
    'status_text': status_text_map.get(work_week.status, '未知')
}
```

#### 修改后 ✅

```python
# 从日期中提取年份和周数
year = work_week.week_start_date.year
week_number = work_week.week_start_date.isocalendar()[1]

work_week_info = {
    'title': work_week.title,
    'week_start_date': work_week.week_start_date.strftime('%Y-%m-%d'),
    'week_end_date': work_week.week_end_date.strftime('%Y-%m-%d'),
    'year': year,                      # ✅
    'week_number': week_number,        # ✅
    'status': work_week.status,
    'status_text': status_text_map.get(work_week.status, '未知')
}
```

### 前端修改

#### 修改前 ❌

```typescript
const exportWorkLog = () => {
  exportForm.value.reportType = 'single'
  exportForm.value.year = (workWeek.value?.year || new Date().getFullYear()).toString()
  // ... 其他代码
  showExportDialog.value = true
}
```

#### 修改后 ✅

```typescript
const exportWorkLog = () => {
  exportForm.value.reportType = 'single'

  // 从 week_start_date 中提取年份
  let defaultYear = new Date().getFullYear()
  if (workWeek.value?.week_start_date) {
    defaultYear = new Date(workWeek.value.week_start_date).getFullYear()
  }

  exportForm.value.year = defaultYear.toString()
  // ... 其他代码
  showExportDialog.value = true
}
```

---

## ✅ 验证方法

### 1. 测试单个工作周导出

**操作步骤：**

1. 进入工作周详情页面
2. 点击"导出数据"按钮
3. 选择"单个工作周"
4. 点击"导出报告"

**预期结果：**

- ✅ 不抛出 `AttributeError`
- ✅ 成功生成 PDF
- ✅ PDF 中年份和周数显示正确

### 2. 检查导出的 PDF

打开生成的 PDF，检查"工作周信息"部分：

- **年度/周数**：应显示如 `2025年 第44周`
- **工作周期**：应显示如 `2025-10-27 至 2025-10-31`

### 3. 检查日志

```
INFO:app.api.work_logs:📊 [WorkLogExport] 开始生成工作周报告
INFO:app.api.work_logs:📋 [WorkLogExport] 查询到工作日志条目数: 25
INFO:app.api.work_logs:📊 [WorkLogExport] 统计完成: 用户数=5, 总工时=180.5h
INFO:app.api.work_logs:✅ [WorkLogExport] 报告生成成功: 2025W44标注组工作计划_统计报告.pdf
```

---

## 🎯 相关知识

### Python 日期处理

```python
from datetime import date

d = date(2025, 10, 27)

# 获取年份
year = d.year  # 2025

# 获取月份
month = d.month  # 10

# 获取日
day = d.day  # 27

# 获取ISO周数
week = d.isocalendar()[1]  # 44

# 格式化日期
formatted = d.strftime('%Y-%m-%d')  # "2025-10-27"
```

### JavaScript 日期处理

```javascript
const d = new Date('2025-10-27')

// 获取年份
const year = d.getFullYear() // 2025

// 获取月份（0-11）
const month = d.getMonth() + 1 // 10

// 获取日
const day = d.getDate() // 27

// 格式化日期
const formatted = d.toISOString().split('T')[0] // "2025-10-27"
```

---

## 💡 最佳实践

### 1. 避免假设对象属性

**不好的做法：**

```python
year = work_week.year  # 假设有 year 属性
```

**好的做法：**

```python
# 方式1: 检查属性是否存在
if hasattr(work_week, 'year'):
    year = work_week.year
else:
    year = work_week.week_start_date.year

# 方式2: 直接从可靠的字段计算
year = work_week.week_start_date.year  # ✅ 推荐
```

### 2. 使用日期计算而非存储冗余数据

**数据库设计优势：**

- ✅ 只存储 `week_start_date` 和 `week_end_date`
- ✅ 年份和周数在需要时计算
- ✅ 避免数据不一致
- ✅ 节省存储空间

**何时存储计算字段：**

- 频繁查询且计算复杂
- 需要按该字段排序或筛选
- 性能优化需求

### 3. 前后端数据结构一致性

确保前后端对数据结构有相同的理解：

```typescript
// 定义 TypeScript 接口
interface WorkWeek {
  id: string
  title: string
  week_start_date: string // ISO date string
  week_end_date: string // ISO date string
  status: string
  // 注意：没有 year 和 week_number
}
```

---

## 🔮 建议改进

### 如果需要频繁使用年份和周数

可以考虑在模型中添加计算属性：

```python
class WorkWeek(Base):
    # ... 现有字段 ...

    @property
    def year(self):
        """返回工作周的年份"""
        return self.week_start_date.year

    @property
    def week_number(self):
        """返回ISO周数"""
        return self.week_start_date.isocalendar()[1]

    @property
    def iso_week(self):
        """返回ISO周标识，如 '2025W44'"""
        return f"{self.year}W{self.week_number:02d}"
```

**优点：**

- ✅ 提供便捷的访问方式
- ✅ 不存储冗余数据
- ✅ 保持数据一致性
- ✅ 代码更简洁

**使用方式：**

```python
work_week = db.query(WorkWeek).first()
print(work_week.year)         # 2025
print(work_week.week_number)  # 44
print(work_week.iso_week)     # "2025W44"
```

---

## 📝 总结

### 问题根源

- ❌ 错误假设 `WorkWeek` 模型有 `year` 和 `week_number` 属性
- ❌ 直接访问不存在的属性导致 `AttributeError`

### 解决方案

- ✅ 后端：从 `week_start_date` 计算年份和周数
- ✅ 前端：从 `week_start_date` 提取年份
- ✅ 使用 Python 的 `isocalendar()` 方法获取ISO周数

### 影响范围

- 修改了 1 个后端函数
- 修改了 1 个前端函数
- 不影响其他功能

---

**🎉 错误已修复，单个工作周导出功能恢复正常！**
