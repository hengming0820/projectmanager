# 工作日志统计报表重构

## 📋 功能说明

重构工作日志统计报表弹窗，移除完成率相关统计，改为按工作类型统计工时，更直观地展示员工工作情况。

---

## ✅ 重构内容

### 1. 统计概览卡片调整

**修改前**：

- 参与人数
- 总条目数
- 总工时
- 整体完成率

**修改后**：

- 参与人数
- 计划工时（h）
- 实际工时（h）
- 工时完成率

**改进点**：

- ✅ 去除"总条目数"，改为"计划工时"
- ✅ 去除"整体完成率"，改为"工时完成率"
- ✅ 计划工时 = 参与人数 × 40小时（周一到周五，每天8小时）
- ✅ 工时完成率 = 实际工时 / 计划工时 × 100%

---

### 2. 图表调整

#### 2.1 员工工作类型工时统计（堆叠柱状图）

**替代**：完成率分布、工时统计、用户完成情况

**特性**：

- 📊 **图表类型**：堆叠柱状图
- 📐 **横轴**：员工姓名
- 📏 **纵轴**：工作时间（小时）
- 🎨 **堆叠**：按工作类型分类

**工作类型颜色**：| 工作类型 | 颜色 | 说明 | |---------|------|------| | 开发 | #409eff | 蓝色 | | 测试 | #67c23a | 绿色 | | 标注 | #17a2b8 | 青色 | | 审核 | #ff9800 | 橙色 | | 培训 | #9c27b0 | 紫色 | | 会议 | #f56c6c | 红色 | | 文档 | #909399 | 灰色 | | 设计 | #e6a23c | 黄色 | | 请假 | #f59e0b | 琥珀色 | | 病假 | #ef4444 | 深红色 | | 年假 | #10b981 | 翠绿色 |

**Tooltip 内容**：

```
姓名
开发: 20h
测试: 10h
会议: 5h
文档: 3h
总计: 38h
```

---

#### 2.2 计划工时 vs 实际工时对比（分组柱状图）

**新增图表**

**特性**：

- 📊 **图表类型**：分组柱状图
- 📐 **横轴**：员工姓名
- 📏 **纵轴**：工作时间（小时）
- 🎨 **分组**：计划工时（蓝色）、实际工时（绿色）

**说明**：

- 计划工时：固定 40小时（周一到周五，每天8小时）
- 实际工时：包括周一到周日所有工作日志的实际工时总和

**Tooltip 内容**：

```
姓名
计划工时: 40h
实际工时: 38h
完成率: 95.0%
```

---

### 3. 表格调整

**修改前列**：

- 姓名
- 计划工时
- 实际工时
- 工时效率
- 平均完成率
- 提交天数
- 状态分布
- 综合评分

**修改后列**：

- 姓名
- 计划工时（固定40h）
- 实际工时
- 工时完成率
- 工作类型分布
- 日志条目数

**改进点**：

- ✅ 移除"平均完成率"（任务完成率）
- ✅ 移除"提交天数"和"状态分布"
- ✅ 移除"综合评分"
- ✅ 添加"工作类型分布"（彩色标签展示）
- ✅ 计划工时固定为40h（不再从后端获取）
- ✅ 工时完成率基于40h计算

**工作类型分布示例**：

```
[开发: 20h] [测试: 10h] [会议: 5h] [文档: 3h]
```

---

## 🔄 计划工时说明

### 计算规则

**固定计划工时**：40小时

**计算方式**：

- 周一到周五：5天 × 8小时/天 = 40小时
- 周六、周日：不计入计划工时

**实际工时**：

- 包括周一到周日所有天的实际工作时长
- 即使周六、周日有工作，也计入实际工时

### 示例场景

#### 场景1：正常工作周

```
周一：8h
周二：8h
周三：8h
周四：8h
周五：8h
周六：休息
周日：休息

计划工时：40h
实际工时：40h
完成率：100%
```

#### 场景2：有加班

```
周一：8h
周二：8h
周三：8h
周四：8h
周五：8h
周六：4h（加班）
周日：2h（加班）

计划工时：40h
实际工时：46h
完成率：115%
```

#### 场景3：有请假

```
周一：8h
周二：8h
周三：0h（请假）
周四：8h
周五：8h
周六：休息
周日：休息

计划工时：40h
实际工时：32h（请假时长会单独统计）
完成率：80%
```

---

## 🎨 实现细节

### 1. 组件结构

**文件**：`src/views/work-log/components/WorkLogStatistics.vue`

**依赖**：

- ECharts：图表库
- Element Plus：UI组件库

**图表实例**：

```typescript
let workTypeChart: echarts.ECharts | null = null
let hoursCompareChart: echarts.ECharts | null = null
```

---

### 2. 堆叠柱状图实现

**数据结构**：

```typescript
// 工作类型数据映射
const workTypeData: Record<string, number[]> = {
  '开发': [20, 15, 18, 22, ...],  // 每个数字对应一个员工
  '测试': [10, 12, 8, 10, ...],
  '会议': [5, 3, 4, 2, ...],
  ...
}
```

**ECharts 配置**：

```typescript
const series = Object.entries(workTypeData).map(([workType, data]) => ({
  name: workType,
  type: 'bar' as const,
  stack: 'total', // 堆叠标识
  data: data,
  itemStyle: {
    color: getWorkTypeColor(workType)
  },
  emphasis: {
    focus: 'series' as const
  }
}))
```

**关键配置**：

- `stack: 'total'`：同一stack的series会堆叠显示
- `emphasis.focus: 'series'`：鼠标悬停时高亮整个系列

---

### 3. 分组柱状图实现

**数据结构**：

```typescript
const userNames = ['张三', '李四', '王五', ...]
const plannedHours = [40, 40, 40, ...]  // 每人固定40小时
const actualHours = [38, 42, 35, ...]   // 实际工时
```

**ECharts 配置**：

```typescript
const series = [
  {
    name: '计划工时',
    type: 'bar' as const,
    data: plannedHours,
    itemStyle: { color: '#409eff' },
    label: {
      show: true,
      position: 'inside',
      formatter: '{c}h'
    }
  },
  {
    name: '实际工时',
    type: 'bar' as const,
    data: actualHours,
    itemStyle: { color: '#67c23a' },
    label: {
      show: true,
      position: 'inside',
      formatter: (params: any) => (params.value > 0 ? `${params.value}h` : '')
    }
  }
]
```

**关键配置**：

- 不设置 `stack`：series会并排显示
- `label.show: true`：在柱子内部显示数值

---

### 4. 辅助函数

#### 计算总计划工时

```typescript
const calculateTotalPlannedHours = () => {
  if (!statistics.value) return 0
  const users = (statistics.value as any).user_summaries || []
  return users.length * 40 // 每人40小时
}
```

#### 计算工时效率

```typescript
const calculateWorkEfficiency = () => {
  if (!statistics.value) return '0.0'
  const totalPlanned = calculateTotalPlannedHours()
  const totalActual = statistics.value.overall_stats?.total_actual_hours || 0
  if (totalPlanned === 0) return '0.0'
  return ((totalActual / totalPlanned) * 100).toFixed(1)
}
```

#### 获取工作类型工时

```typescript
const getWorkTypeHours = (user: any): Record<string, number> => {
  // 假设后端返回 work_type_hours 字段
  if (user.work_type_hours) {
    return user.work_type_hours
  }
  return {}
}
```

---

### 5. 图表自适应

**窗口大小变化**：

```typescript
const handleResize = () => {
  if (workTypeChart) {
    workTypeChart.resize()
  }
  if (hoursCompareChart) {
    hoursCompareChart.resize()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  destroyCharts()
})
```

---

## ⚠️ 后端需求

### 需要添加的字段

**`WorkWeekSummary` 需要包含**：

```typescript
interface WorkWeekSummary {
  user_name: string
  total_actual_hours: number
  total_entries: number // 日志条目数

  // 【新增】按工作类型统计的工时
  work_type_hours: Record<string, number>
  // 示例：
  // {
  //   "开发": 20,
  //   "测试": 10,
  //   "会议": 5,
  //   "文档": 3,
  //   "请假": 2
  // }
}
```

### API 修改建议

**接口**：`GET /api/work-weeks/{work_week_id}/statistics`

**返回数据示例**：

```json
{
  "overall_stats": {
    "total_users": 5,
    "total_entries": 35,
    "total_actual_hours": 190
  },
  "user_summaries": [
    {
      "user_id": "user1",
      "user_name": "张三",
      "total_actual_hours": 38,
      "total_entries": 7,
      "work_type_hours": {
        "开发": 20,
        "测试": 10,
        "会议": 5,
        "文档": 3
      }
    },
    {
      "user_id": "user2",
      "user_name": "李四",
      "total_actual_hours": 42,
      "total_entries": 8,
      "work_type_hours": {
        "开发": 25,
        "测试": 12,
        "会议": 3,
        "文档": 2
      }
    }
  ]
}
```

### 后端实现建议

**Python/FastAPI 示例**：

```python
# 统计每个用户的工作类型工时
for user_summary in user_summaries:
    # 获取该用户本周的所有工作日志
    entries = db.query(WorkLogEntry).filter(
        WorkLogEntry.work_week_id == work_week_id,
        WorkLogEntry.user_id == user_summary.user_id
    ).all()

    # 按工作类型分组统计
    work_type_hours = {}
    for entry in entries:
        work_type = entry.work_type or '其他'
        hours = entry.actual_hours or 0
        work_type_hours[work_type] = work_type_hours.get(work_type, 0) + hours

    user_summary.work_type_hours = work_type_hours
```

---

## 📊 效果展示

### 1. 统计概览

```
┌─────────────────────────────────────────────────────────┐
│  参与人数        计划工时       实际工时      工时完成率  │
│     5           200h           190h          95.0%      │
└─────────────────────────────────────────────────────────┘
```

### 2. 工作类型堆叠图

```
 50h ┤
     │   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
 40h ┤   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
     │   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
 30h ┤   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
     │   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
 20h ┤   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
     │   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
 10h ┤   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
     │   ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓      ▓▓▓▓
  0h └───────┴─────────┴─────────┴─────────┴─────────
       张三      李四      王五      赵六      钱七

图例：▓ 开发  ▒ 测试  ░ 会议  ▪ 文档
```

### 3. 计划 vs 实际工时对比

```
 50h ┤
     │  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
 40h ┤  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
     │  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
 30h ┤  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
     │  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
 20h ┤  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
     │  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
 10h ┤  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
     │  ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░   ▓▓ ░░
  0h └───────┴───────┴───────┴───────┴───────
      张三     李四     王五     赵六     钱七

图例：▓ 计划工时  ░ 实际工时
```

---

## 🚀 验证步骤

### 1. 打开统计报表

1. **进入工作日志周详情页**
2. **点击"统计报表"按钮**
3. **验证统计概览**：
   - ✅ 显示参与人数
   - ✅ 显示计划工时（人数 × 40）
   - ✅ 显示实际工时
   - ✅ 显示工时完成率

---

### 2. 验证工作类型堆叠图

1. **查看图表**：

   - ✅ 横轴显示员工姓名
   - ✅ 纵轴显示工时（小时）
   - ✅ 柱子按工作类型堆叠
   - ✅ 不同工作类型有不同颜色

2. **鼠标悬停**：

   - ✅ 显示员工姓名
   - ✅ 显示每个工作类型的工时
   - ✅ 显示总工时

3. **点击图例**：
   - ✅ 可以隐藏/显示某个工作类型

---

### 3. 验证计划 vs 实际工时对比图

1. **查看图表**：

   - ✅ 横轴显示员工姓名
   - ✅ 纵轴显示工时（小时）
   - ✅ 每个员工有两个柱子（计划和实际）
   - ✅ 计划工时（蓝色）固定40h
   - ✅ 实际工时（绿色）根据实际情况

2. **鼠标悬停**：
   - ✅ 显示计划工时
   - ✅ 显示实际工时
   - ✅ 显示完成率

---

### 4. 验证表格

1. **查看表格列**：

   - ✅ 姓名
   - ✅ 计划工时（固定40h）
   - ✅ 实际工时
   - ✅ 工时完成率（带颜色）
   - ✅ 工作类型分布（彩色标签）
   - ✅ 日志条目数

2. **验证工时完成率颜色**：

   - ✅ 90%-110%：绿色（良好）
   - ✅ >110%：黄色（超额）
   - ✅ <90%：红色（不足）

3. **验证工作类型分布**：
   - ✅ 显示彩色标签
   - ✅ 每个标签显示"类型: 工时h"
   - ✅ 工时为0的类型不显示

---

## 💡 使用建议

### 1. 管理者视角

**查看整体情况**：

- 查看统计概览，了解团队总体工时完成率
- 查看堆叠图，了解团队工作类型分布
- 查看对比图，找出工时不足或超额的员工

**发现问题**：

- 某员工工时不足：是否工作量分配不均？
- 某员工工时超额：是否工作效率低或任务太重？
- 某工作类型占比过高：是否需要调整工作分配？

---

### 2. 员工视角

**了解自己的工作情况**：

- 查看表格中自己的行，了解工时完成情况
- 查看工作类型分布，了解时间分配
- 对比其他员工，了解自己的工作量

---

### 3. 数据分析

**工作类型分析**：

- 哪些类型工时最多？
- 是否符合项目特性？
- 是否需要调整人员配置？

**工时完成率分析**：

- 平均完成率是多少？
- 是否合理？
- 是否需要调整计划工时？

---

## 📚 相关文档

- [工作日志周表格优化](./WORK_LOG_WEEK_DAYS_UPDATE.md)
- [工作日志条目控件优化](./WORK_LOG_ENTRY_CELL_OPTIMIZATION.md)
- [工作日志条目布局优化](./WORK_LOG_ENTRY_LAYOUT_V2.md)

---

**版本**: v2.0  
**更新时间**: 2025-10-17  
**优化人员**: AI Assistant

**后端支持**: 需要后端提供 `work_type_hours` 字段
