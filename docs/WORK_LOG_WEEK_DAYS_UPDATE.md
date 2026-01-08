# 工作日志周表格优化 - 增加周六周日

## 📋 功能说明

为了适应调休等灵活工作安排，将工作日志周列表页面（week-detail.vue）的表格结构从5个工作日（周一到周五）扩展为7天（周一到周日），并去掉"本周汇总"列。

---

## ✅ 优化内容

### 1. 工作日扩展

**修改前**：

- 工作日：周一、周二、周三、周四、周五（5天）
- 汇总列：本周汇总（固定右侧）

**修改后**：

- 工作日：周一、周二、周三、周四、周五、周六、周日（7天）
- 汇总列：无（已移除）

**改进原因**：

- ✅ 支持周六、周日调休上班
- ✅ 记录完整的一周工作情况
- ✅ 更灵活的工作时间安排
- ✅ 简化表格，去掉冗余的汇总列

---

### 2. 表格列变化

**修改前（6列）**：

```
| 姓名 | 周一 | 周二 | 周三 | 周四 | 周五 | 本周汇总 |
```

**修改后（8列）**：

```
| 姓名 | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 |
```

**列宽设置**：

- 姓名列：120px（固定左侧）
- 工作日列：240px（每列）

---

### 3. 计划时间调整

**修改前**：

- 默认计划时间：5天 × 8小时 = 40小时
- 按实际工作天数：`totalDaysWithEntries * 8`

**修改后**：

- 默认计划时间：7天 × 8小时 = 56小时
- 按实际工作天数：`totalDaysWithEntries * 8`

**计算逻辑**：

```typescript
// 如果没有任何日志条目，默认7天56小时；否则按实际有日志的天数计算
const totalPlannedHours = totalDaysWithEntries === 0 ? 56 : totalDaysWithEntries * 8
```

---

## 🔄 实现方案

### 1. 工作日定义修改

**修改前**：

```typescript
const workDays = computed(() => {
  if (!workWeek.value) return []

  const days = []
  const startDate = new Date(workWeek.value.week_start_date)
  const dayNames = ['周一', '周二', '周三', '周四', '周五']

  for (let i = 0; i < 5; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    days.push({
      date: date.toISOString().split('T')[0],
      label: `${dayNames[i]} (${date.getMonth() + 1}/${date.getDate()})`
    })
  }

  return days
})
```

**修改后**：

```typescript
const workDays = computed(() => {
  if (!workWeek.value) return []

  const days = []
  const startDate = new Date(workWeek.value.week_start_date)
  const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

  for (let i = 0; i < 7; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    days.push({
      date: date.toISOString().split('T')[0],
      label: `${dayNames[i]} (${date.getMonth() + 1}/${date.getDate()})`
    })
  }

  return days
})
```

**改进点**：

1. ✅ `dayNames` 数组增加"周六"和"周日"
2. ✅ 循环次数从5改为7
3. ✅ 保持原有的日期格式和显示逻辑

---

### 2. 移除汇总列

**删除代码**：

```vue
<!-- 汇总列 -->
<el-table-column label="本周汇总" width="160" fixed="right">
  <template #default="{ row }">
    <div class="week-summary">
      <div class="summary-item">
        <span class="label">计划:</span>
        <span class="value">{{ row.weekSummary?.totalPlannedHours || 0 }}h</span>
      </div>
      <div class="summary-item">
        <span class="label">实际:</span>
        <span class="value">{{ row.weekSummary?.totalActualHours || 0 }}h</span>
      </div>
      <div class="summary-item">
        <span class="label">完成率:</span>
        <span class="value">{{ (row.weekSummary?.averageCompletionRate || 0).toFixed(1) }}%</span>
      </div>
      <div class="summary-item">
        <span class="label">提交:</span>
        <span class="value">{{ row.weekSummary?.submittedDays || 0 }}/5</span>
      </div>
    </div>
  </template>
</el-table-column>
```

**原因**：

- ✅ 汇总数据可以在统计报表中查看
- ✅ 简化表格，聚焦每日工作内容
- ✅ 表格宽度更合理，避免横向滚动

---

### 3. 汇总数据收集修改

**修改前**：

```typescript
const daysEntries = [
  getEntriesForDay(row, 0), // 周一
  getEntriesForDay(row, 1), // 周二
  getEntriesForDay(row, 2), // 周三
  getEntriesForDay(row, 3), // 周四
  getEntriesForDay(row, 4) // 周五
]
```

**修改后**：

```typescript
const daysEntries = [
  getEntriesForDay(row, 0), // 周一
  getEntriesForDay(row, 1), // 周二
  getEntriesForDay(row, 2), // 周三
  getEntriesForDay(row, 3), // 周四
  getEntriesForDay(row, 4), // 周五
  getEntriesForDay(row, 5), // 周六
  getEntriesForDay(row, 6) // 周日
]
```

**改进点**：

- ✅ 增加周六和周日的数据收集
- ✅ 保持原有的汇总计算逻辑（用于统计报表）

---

## 📊 数据计算变化

### 1. 计划时间计算

**公式变化**：

```
修改前：默认计划时间 = 5天 × 8小时 = 40小时
修改后：默认计划时间 = 7天 × 8小时 = 56小时
```

**实际使用**：

```typescript
// 如果没有任何日志条目，默认7天56小时
// 如果有日志条目，按实际有日志的天数计算（每天8小时）
const totalPlannedHours = totalDaysWithEntries === 0 ? 56 : totalDaysWithEntries * 8
```

**示例**：| 工作情况 | 计划时间 | 说明 | |---------|---------|------| | 无日志条目 | 56小时 | 默认7天 | | 工作3天 | 24小时 | 3天 × 8小时 | | 工作5天 | 40小时 | 5天 × 8小时 | | 工作7天 | 56小时 | 7天 × 8小时 |

---

### 2. 完成率计算

**计算公式（未变化）**：

```typescript
// 完成率：(实际工作时长 - 请假时长) / (计划时长 - 请假时长) * 100
const effectivePlannedHours = Math.max(totalPlannedHours - totalLeaveHours, 0.01)
const workCompletionRate =
  effectivePlannedHours > 0
    ? ((totalActualHours - totalLeaveHours) / effectivePlannedHours) * 100
    : 0
```

**特性**：

- ✅ 请假时长不影响完成率计算
- ✅ 最高完成率为100%
- ✅ 避免除以0的情况

---

### 3. 提交天数统计

**统计逻辑（未变化）**：

```typescript
// 如果当天至少有一个条目已提交或通过，则算作已提交
if (dayEntries.some((e) => ['submitted', 'approved'].includes(e.status))) {
  submittedDays++
}
```

**说明**：

- ✅ 统计所有7天的提交情况
- ✅ 每天至少有一条提交或通过的日志即算作已提交

---

## 🎯 使用场景

### 场景1：正常工作周（周一到周五）

**工作安排**：

- 周一到周五：正常上班
- 周六、周日：休息

**日志填写**：

- 周一到周五：填写工作日志
- 周六、周日：不填写（或填写学习、总结等）

**计划时间**：

- 实际工作5天 × 8小时 = 40小时

---

### 场景2：调休工作周（周六补班）

**工作安排**：

- 周一到周五：正常上班
- 周六：调休补班
- 周日：休息

**日志填写**：

- 周一到周六：填写工作日志
- 周日：不填写

**计划时间**：

- 实际工作6天 × 8小时 = 48小时

---

### 场景3：特殊工作安排

**工作安排**：

- 周一到周四：正常上班
- 周五：请假
- 周六、周日：加班

**日志填写**：

- 周一到周四：填写工作日志
- 周五：填写请假日志
- 周六、周日：填写加班日志

**计划时间**：

- 实际工作6天（周一到周四 + 周六、周日）× 8小时 = 48小时
- 请假1天 × 8小时 = 8小时
- 完成率计算时会扣除请假时间

---

## 🔄 修改文件列表

### 修改的文件（1个）

**`src/views/work-log/week-detail.vue`**

**修改内容**：

1. ✅ **删除本周汇总列**（Line 111-133）

   - 移除整个 `<el-table-column>` 组件
   - 简化表格显示

2. ✅ **扩展工作日定义**（Line 278）

   - 增加"周六"和"周日"到 `dayNames` 数组
   - 修改循环次数从5到7

3. ✅ **更新数据收集**（Line 407-413）

   - 增加周六和周日的数据收集
   - 保持汇总计算的完整性

4. ✅ **调整计划时间**（Line 449）
   - 默认计划时间从40小时改为56小时
   - 更新注释说明

---

## 📝 技术细节

### 1. 日期计算

**工作周开始日期**：

```typescript
const startDate = new Date(workWeek.value.week_start_date)
```

**每天日期计算**：

```typescript
for (let i = 0; i < 7; i++) {
  const date = new Date(startDate)
  date.setDate(startDate.getDate() + i) // 从周一开始，依次加1天

  days.push({
    date: date.toISOString().split('T')[0], // YYYY-MM-DD格式
    label: `${dayNames[i]} (${date.getMonth() + 1}/${date.getDate()})` // 周几 (月/日)
  })
}
```

**示例**：

```
week_start_date: 2025-10-13（周一）

生成的日期：
- 周一: 2025-10-13
- 周二: 2025-10-14
- 周三: 2025-10-15
- 周四: 2025-10-16
- 周五: 2025-10-17
- 周六: 2025-10-18
- 周日: 2025-10-19
```

---

### 2. 数组索引映射

**索引映射关系**：

```typescript
// 数组索引 => 星期几
0 => 周一
1 => 周二
2 => 周三
3 => 周四
4 => 周五
5 => 周六
6 => 周日
```

**用于数据收集**：

```typescript
getEntriesForDay(row, 0) // 获取周一的所有日志条目
getEntriesForDay(row, 5) // 获取周六的所有日志条目
getEntriesForDay(row, 6) // 获取周日的所有日志条目
```

---

### 3. 响应式更新

**计算属性自动更新**：

```typescript
const workDays = computed(() => {
  if (!workWeek.value) return []
  // ... 计算逻辑
  return days
})
```

**特性**：

- ✅ `workWeek.value` 变化时自动重新计算
- ✅ 返回的 `days` 数组驱动表格列渲染
- ✅ 无需手动触发更新

---

## 🚀 验证步骤

### 1. 查看表格结构

1. **进入工作日志列表**
2. **点击某个工作周**，进入周详情页
3. **验证表格列数**：
   - ✅ 应显示8列：姓名 + 7个工作日
   - ✅ 无"本周汇总"列
4. **验证列标题**：
   - ✅ 周一 (10/13)
   - ✅ 周二 (10/14)
   - ✅ 周三 (10/15)
   - ✅ 周四 (10/16)
   - ✅ 周五 (10/17)
   - ✅ 周六 (10/18)
   - ✅ 周日 (10/19)

---

### 2. 测试日志填写

1. **周一到周五**：

   - ✅ 填写正常工作日志
   - ✅ 验证保存成功

2. **周六**：

   - ✅ 填写调休工作日志
   - ✅ 验证保存成功

3. **周日**：
   - ✅ 填写加班工作日志
   - ✅ 验证保存成功

---

### 3. 测试数据统计

1. **打开统计报表**
2. **验证计划时间**：

   - ✅ 无日志时：默认56小时
   - ✅ 工作3天：24小时
   - ✅ 工作5天：40小时
   - ✅ 工作7天：56小时

3. **验证完成率**：
   - ✅ 正常工作：(实际工作时长 / 计划时长) × 100%
   - ✅ 有请假：((实际工作时长 - 请假时长) / (计划时长 - 请假时长)) × 100%

---

## 💡 使用建议

### 1. 日志填写规范

**工作日（周一到周五）**：

- ✅ 必须填写工作日志
- ✅ 如果请假，填写请假类型日志

**周末（周六、周日）**：

- ✅ 如果加班/调休，填写工作日志
- ✅ 如果休息，可以不填写
- ✅ 可以填写学习、总结等非工作内容

---

### 2. 请假处理

**请假类型**：

- 请假
- 病假
- 年假

**注意事项**：

- ✅ 请假日志的"工作类型"选择对应的请假类型
- ✅ 请假时长会在完成率计算时自动扣除
- ✅ 请假不影响完成率（合理缺席）

---

### 3. 调休和加班

**调休（周六补班）**：

- ✅ 在周六填写正常工作日志
- ✅ 计划时间自动计算为6天 × 8小时 = 48小时

**加班（周末加班）**：

- ✅ 在周六/周日填写工作日志
- ✅ 可以在备注中说明是加班
- ✅ 计划时间会相应增加

---

## 🔮 未来优化方向

### 1. 灵活的工作日配置

支持为每个工作周配置不同的工作日：

```typescript
// 工作周配置
{
  workWeekId: 'xxx',
  workDays: [1, 2, 3, 4, 5, 6],  // 周一到周六
  restDays: [0]                   // 周日休息
}
```

---

### 2. 假期标记

自动标记法定节假日和调休日：

```vue
<el-tag v-if="isHoliday(day.date)" type="danger" size="small">
  法定假日
</el-tag>
<el-tag v-if="isCompensation(day.date)" type="warning" size="small">
  调休补班
</el-tag>
```

---

### 3. 工作时长配置

支持自定义每天的工作时长：

```typescript
// 默认每天8小时，但可以配置为其他值
const dailyWorkHours = 8
const totalPlannedHours = totalDaysWithEntries * dailyWorkHours
```

---

## 📚 相关文档

- [工作日志导航栏优化](./WORK_LOG_NAV_OPTIMIZATION.md)
- [工作日志批量管理](./WORK_LOG_BATCH_MANAGEMENT.md)

---

**版本**: v1.0  
**更新时间**: 2025-10-17  
**优化人员**: AI Assistant
