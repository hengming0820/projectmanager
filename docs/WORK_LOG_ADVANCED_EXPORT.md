# 📊 工作日志高级导出功能

> 🗓️ **实施日期**: 2025-10-27  
> 🎯 **功能**: 支持单周/月度/季度/年度的工作日志统计报告导出  
> ✨ **版本**: v2.0

---

## 🎨 功能概述

在原有单个工作周导出基础上，增加了月度、季度、年度统计报告导出功能，用户可以灵活选择导出范围和统计维度。

### ✅ 支持的报告类型

| 报告类型          | 说明                     | 统计范围         | 数据来源       |
| ----------------- | ------------------------ | ---------------- | -------------- |
| 🗓️ **单个工作周** | 导出指定的单个工作周     | 5个工作日        | 当前工作周     |
| 📅 **月度报告**   | 汇总一个月的所有工作周   | 该月所有工作周   | 多个工作周聚合 |
| 📆 **季度报告**   | 汇总一个季度的所有工作周 | 该季度所有工作周 | 多个工作周聚合 |
| 📖 **年度报告**   | 汇总一整年的所有工作周   | 该年所有工作周   | 多个工作周聚合 |

---

## 🎯 使用方法

### 1. 打开导出对话框

在工作周详情页面，点击 **"导出数据"** 按钮（黄色按钮，带下载图标）

### 2. 选择报告类型

对话框中提供4种报告类型选项：

#### 🗓️ 单个工作周

- **选择此项**：导出当前查看的工作周
- **无需其他选择**：系统自动使用当前工作周
- **适用场景**：查看单周详细数据

#### 📅 月度报告

- **选择年份**：使用年份选择器
- **选择月份**：1月~12月下拉选择
- **示例**：2025年10月
- **适用场景**：月度工作汇总、月度考核

#### 📆 季度报告

- **选择年份**：使用年份选择器
- **选择季度**：
  - 第一季度（1-3月）
  - 第二季度（4-6月）
  - 第三季度（7-9月）
  - 第四季度（10-12月）
- **示例**：2025年第4季度
- **适用场景**：季度总结、季度考核

#### 📖 年度报告

- **选择年份**：使用年份选择器
- **示例**：2025年度
- **适用场景**：年度总结、年度考核

### 3. 确认导出

点击 **"导出报告"** 按钮，系统开始生成PDF报告

### 4. 下载报告

PDF生成完成后会自动下载到本地

---

## 📋 报告内容

### 单个工作周报告

与之前一致，包含：

- 工作周信息
- 整体工时统计
- 工作类型分布饼图
- 计划 vs 实际工时对比图
- 用户详细统计表格

### 月度/季度/年度报告

聚合报告，包含以下内容：

#### 1. 报告标题

- 格式：`{年份}年{月份}月工作日志统计报告`
- 例如：`2025年10月工作日志统计报告`

#### 2. 时间周期信息

- 统计周期：开始日期 ~ 结束日期
- 年度/周数：聚合的工作周数量
- 状态：聚合报告（X个工作周）

#### 3. 整体工时统计

- **参与人数**：该期间内填写工作日志的员工总数
- **计划工时**：`参与人数 × 工作周数 × 40小时`
- **实际工时**：所有员工实际工作时间总和
- **工时完成率**：`(实际工时 / 计划工时) × 100%`

#### 4. 工作类型分布饼图

- 展示各工作类型的工时占比
- 支持多种工作类型
- 自动计算百分比

#### 5. 计划工时 vs 实际工时对比图

- 柱状图对比每个员工的计划与实际工时
- 横轴：员工姓名
- 纵轴：工时（小时）
- 蓝色柱：计划工时
- 绿色柱：实际工时

#### 6. 用户详细统计表格

- 姓名
- 计划工时（每人每周40小时 × 工作周数）
- 实际工时
- 完成率
- 工作类型分布
- 日志条目数

---

## 🔧 技术实现

### 前端实现 (`src/views/work-log/week-detail.vue`)

#### 1. 导出对话框

```vue
<el-dialog v-model="showExportDialog" title="导出工作日志报告" width="500px">
  <el-form :model="exportForm" label-width="100px">
    <el-form-item label="报告类型">
      <el-radio-group v-model="exportForm.reportType">
        <el-radio label="single">单个工作周</el-radio>
        <el-radio label="monthly">月度报告</el-radio>
        <el-radio label="quarterly">季度报告</el-radio>
        <el-radio label="yearly">年度报告</el-radio>
      </el-radio-group>
    </el-form-item>
    <!-- 根据类型显示不同的选择器 -->
  </el-form>
</el-dialog>
```

#### 2. 数据结构

```typescript
const exportForm = reactive({
  reportType: 'single', // single, monthly, quarterly, yearly
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  quarter: Math.floor(new Date().getMonth() / 3) + 1
})
```

#### 3. API调用

```typescript
const confirmExport = async () => {
  const params = new URLSearchParams()

  if (exportForm.reportType === 'single') {
    params.append('week_id', workWeekId.value)
    params.append('report_type', 'single')
  } else if (exportForm.reportType === 'monthly') {
    params.append('report_type', 'monthly')
    params.append('year', exportForm.year.toString())
    params.append('month', exportForm.month.toString())
  } else if (exportForm.reportType === 'quarterly') {
    params.append('report_type', 'quarterly')
    params.append('year', exportForm.year.toString())
    params.append('quarter', exportForm.quarter.toString())
  } else if (exportForm.reportType === 'yearly') {
    params.append('report_type', 'yearly')
    params.append('year', exportForm.year.toString())
  }

  const apiUrl = `/api/work-logs/export?${params.toString()}`
  // ... 调用API并下载文件
}
```

### 后端实现 (`backend/app/api/work_logs.py`)

#### 1. 统一导出端点

```python
@router.get("/export")
async def export_work_log_report(
    report_type: str,
    week_id: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """统一的工作日志导出端点"""
```

#### 2. 日期范围计算

**月度报告：**

```python
start_date = date(year, month, 1)
if month == 12:
    end_date = date(year + 1, 1, 1)
else:
    end_date = date(year, month + 1, 1)
```

**季度报告：**

```python
start_month = (quarter - 1) * 3 + 1
end_month = start_month + 3
start_date = date(year, start_month, 1)
```

**年度报告：**

```python
start_date = date(year, 1, 1)
end_date = date(year + 1, 1, 1)
```

#### 3. 工作周查询

```python
work_weeks = db.query(WorkWeek).filter(
    and_(
        WorkWeek.week_start_date >= start_date,
        WorkWeek.week_start_date < end_date
    )
).order_by(WorkWeek.week_start_date).all()
```

#### 4. 数据聚合

```python
# 查询所有相关的工作日志条目
week_ids = [ww.id for ww in work_weeks]
entries = db.query(WorkLogEntry).filter(
    WorkLogEntry.work_week_id.in_(week_ids)
).options(
    joinedload(WorkLogEntry.user),
    joinedload(WorkLogEntry.work_type)
).all()

# 统计用户工时
for entry in entries:
    if entry.user_id:
        user_ids.add(entry.user_id)
    if entry.actual_hours:
        total_actual_hours += entry.actual_hours
        # ... 统计逻辑
```

#### 5. 计划工时计算

```python
# 计划工时 = 用户数 × 工作周数 × 40小时/周
total_planned_hours = total_users * len(work_weeks) * 40
```

### PDF生成服务

使用现有的 `WorkLogWeekPDFService`，无需修改。服务自动根据传入的数据生成PDF：

- 如果是单周，显示单周信息
- 如果是聚合，显示聚合信息（工作周数量、总时间段）

---

## 📊 数据统计说明

### 计划工时计算

**单个工作周：**

```
计划工时 = 参与人数 × 40小时
```

**月度/季度/年度报告：**

```
计划工时 = 参与人数 × 工作周数 × 40小时
```

**示例：**

- 10个员工
- 4个工作周（一个月）
- 计划工时 = 10 × 4 × 40 = 1600小时

### 工时完成率

```
工时完成率 = (实际工时 / 计划工时) × 100%
```

### 工作类型统计

汇总所有工作日志条目的工作类型和工时，按工作类型分组统计。

### 用户统计

按用户汇总所有工作日志条目的：

- 总工时
- 工作类型分布
- 日志条目数

---

## 🎯 使用场景

### 📅 月度报告适用场景

1. **月度工作总结**：查看本月整体工作情况
2. **月度考核**：评估员工月度工作完成情况
3. **月度汇报**：向上级汇报部门月度工作
4. **工时统计**：财务或人事进行工时统计

### 📆 季度报告适用场景

1. **季度总结**：季度工作回顾和分析
2. **季度考核**：员工季度绩效评估
3. **季度规划**：基于季度数据进行下季度规划
4. **趋势分析**：观察季度工作趋势

### 📖 年度报告适用场景

1. **年度总结**：全年工作回顾
2. **年度考核**：员工年度绩效评估
3. **年度汇报**：向管理层汇报年度工作
4. **数据分析**：年度数据分析和洞察

---

## 🔍 报告示例

### 文件名格式

| 报告类型   | 文件名示例                           |
| ---------- | ------------------------------------ |
| 单个工作周 | `2025W44标注组工作计划_统计报告.pdf` |
| 月度报告   | `2025年10月_工作日志统计报告.pdf`    |
| 季度报告   | `2025年第4季度_工作日志统计报告.pdf` |
| 年度报告   | `2025年度_工作日志统计报告.pdf`      |

### 报告标题

| 报告类型   | 标题示例                        |
| ---------- | ------------------------------- |
| 单个工作周 | `2025W44标注组工作计划`         |
| 月度报告   | `2025年10月工作日志统计报告`    |
| 季度报告   | `2025年第4季度工作日志统计报告` |
| 年度报告   | `2025年度工作日志统计报告`      |

### 聚合信息显示

在PDF的"工作周信息"部分，聚合报告会显示：

- **年度/周数**：`10个工作周`（而不是具体周数）
- **状态**：`聚合报告（10个工作周）`

---

## ⚠️ 注意事项

### 1. 数据要求

- 选择的时间范围内必须有至少一个工作周
- 如果没有工作周，会返回404错误：`{period}没有工作周数据`

### 2. 性能考虑

- 年度报告可能包含50+个工作周，生成时间较长（5-15秒）
- 建议在数据量大时添加耐心等待的提示

### 3. 计划工时说明

- 聚合报告的计划工时是累加的
- 如果某个员工只参与了部分工作周，计划工时仍然按全部工作周计算
- 这样可以真实反映实际参与情况

### 4. 工作周统计

- 只统计 `week_start_date` 在指定时间范围内的工作周
- 跨月/跨年的工作周归属于开始日期所在的期间

---

## 🐛 错误处理

### 常见错误及解决方法

| 错误信息                 | 原因                       | 解决方法           |
| ------------------------ | -------------------------- | ------------------ |
| `缺少 week_id 参数`      | 选择单周但未提供工作周ID   | 检查前端参数传递   |
| `{period}没有工作周数据` | 选择的时间范围内没有工作周 | 选择有数据的时间段 |
| `不支持的报告类型`       | report_type参数错误        | 检查参数值         |
| `导出失败: 权限不足`     | 用户未登录                 | 重新登录           |

### 日志级别

```python
logger.info(f"📊 [WorkLogExport] 开始生成{report_type}报告")
logger.info(f"📅 [WorkLogExport] 日期范围: {start_date} ~ {end_date}")
logger.info(f"📋 [WorkLogExport] 找到 {len(work_weeks)} 个工作周")
logger.info(f"📊 [WorkLogExport] 统计完成: {len(work_weeks)}个工作周, {total_users}个用户")
logger.info(f"✅ [WorkLogExport] 报告生成成功: {filename}")
logger.error(f"❌ [WorkLogExport] 生成报告失败: {error}")
```

---

## 📊 API接口文档

### 统一导出接口

**端点：** `GET /api/work-logs/export`

**参数：**

| 参数名      | 类型    | 必填 | 说明     | 示例                                       |
| ----------- | ------- | ---- | -------- | ------------------------------------------ |
| report_type | string  | ✅   | 报告类型 | `single`, `monthly`, `quarterly`, `yearly` |
| week_id     | string  | ⚠️   | 工作周ID | `uuid`                                     |
| year        | integer | ⚠️   | 年份     | `2025`                                     |
| month       | integer | ⚠️   | 月份     | `10`                                       |
| quarter     | integer | ⚠️   | 季度     | `4`                                        |

**必填规则：**

- `report_type=single`：必须提供 `week_id`
- `report_type=monthly`：必须提供 `year` 和 `month`
- `report_type=quarterly`：必须提供 `year` 和 `quarter`
- `report_type=yearly`：必须提供 `year`

**请求示例：**

```bash
# 单个工作周
GET /api/work-logs/export?report_type=single&week_id=xxx-xxx-xxx

# 月度报告
GET /api/work-logs/export?report_type=monthly&year=2025&month=10

# 季度报告
GET /api/work-logs/export?report_type=quarterly&year=2025&quarter=4

# 年度报告
GET /api/work-logs/export?report_type=yearly&year=2025
```

**响应：**

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename*=UTF-8''{filename}`
- Body: PDF文件流

---

## 🎨 UI/UX改进

### 对话框设计

1. **直观的单选按钮**：4个报告类型并排显示
2. **动态表单**：根据选择显示对应的选择器
3. **友好提示**：单周模式下显示当前工作周名称
4. **加载状态**：导出时按钮显示"生成中..."
5. **禁用重复点击**：使用 loading 状态防止重复提交

### 用户体验优化

1. **智能默认值**：

   - 年份：默认当前工作周的年份
   - 月份：默认当前月份
   - 季度：默认当前季度

2. **清晰的提示信息**：

   - 开始生成："正在生成PDF报告，请稍候..."
   - 成功："PDF报告导出成功"
   - 失败：显示具体错误原因

3. **便捷的操作**：
   - 一键打开对话框
   - 一键确认导出
   - 自动下载文件

---

## 🔮 未来增强方向

### 功能增强

1. ⭐ **自定义时间范围**：用户自选开始和结束日期
2. ⭐ **部门筛选**：只导出特定部门的数据
3. ⭐ **用户筛选**：只导出特定用户的数据
4. ⭐ **工作类型筛选**：只统计特定工作类型
5. ⭐ **多工作周选择**：手动勾选要导出的工作周

### 数据增强

1. 📊 **趋势图表**：添加工时趋势折线图
2. 📊 **对比分析**：同比/环比数据对比
3. 📊 **TOP排行**：工时排行榜、工作量排行榜
4. 📊 **异常分析**：标记异常数据（工时过低/过高）

### 导出格式

1. 📄 **Excel格式**：支持导出为Excel进行二次分析
2. 📄 **Word格式**：适合编辑和修改
3. 📄 **在线预览**：导出前预览报告内容

---

## 📚 相关文件

### 后端

- `backend/app/api/work_logs.py` - 工作日志API（新增统一导出端点）
- `backend/app/services/pdf_export_service.py` - PDF生成服务

### 前端

- `src/views/work-log/week-detail.vue` - 工作周详情页面（新增导出对话框）

### 文档

- `WORK_LOG_EXPORT_FEATURE.md` - 基础导出功能文档
- `WORK_LOG_ADVANCED_EXPORT.md` - 本文档（高级导出功能）

---

## ✨ 版本历史

### v2.0 (2025-10-27)

- ✅ 新增月度报告导出
- ✅ 新增季度报告导出
- ✅ 新增年度报告导出
- ✅ 重构导出对话框UI
- ✅ 优化数据聚合逻辑
- ✅ 完善错误处理

### v1.0 (2025-10-27)

- ✅ 单个工作周PDF导出
- ✅ 基础统计报表
- ✅ 图表可视化

---

## 🎉 总结

工作日志高级导出功能已完整实现，支持：

- ✅ 4种报告类型（单周/月度/季度/年度）
- ✅ 灵活的时间选择
- ✅ 自动数据聚合
- ✅ 美观的PDF报告
- ✅ 完善的错误处理
- ✅ 友好的用户体验

用户现在可以根据需要，灵活导出不同时间范围和统计维度的工作日志报告！

---

**🎉 功能实现完成！**
