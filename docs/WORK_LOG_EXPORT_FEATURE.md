# 📊 工作周统计报告导出功能

> 🗓️ **实施日期**: 2025-10-27  
> 🎯 **功能**: 工作周统计报告 PDF 导出

---

## 🎨 功能概述

为工作周详情页面添加了完整的 PDF 导出功能，用户可以导出包含图表和数据的统计报告。

### ✅ 已实现功能

1. **后端 PDF 生成服务** (`backend/app/services/pdf_export_service.py`)

   - 新增 `WorkLogWeekPDFService` 类
   - 支持生成完整的工作周统计报告 PDF
   - 包含图表（饼图、柱状图）和详细数据表格

2. **后端导出 API** (`backend/app/api/work_logs.py`)

   - 新增 `GET /api/work-logs/weeks/{week_id}/export` 端点
   - 自动统计工作周数据
   - 返回 PDF 文件流

3. **前端导出功能** (`src/views/work-log/week-detail.vue`)
   - 实现 `exportWorkLog` 函数
   - 调用后端 API 生成并下载 PDF
   - 提供用户友好的加载提示和错误处理

---

## 📋 PDF 报告内容

### 1. 工作周信息

- 工作周期（开始日期 ~ 结束日期）
- 年度/周数
- 状态（进行中/已归档）

### 2. 整体工时统计

- 参与人数
- 计划工时（每人 40 小时）
- 实际工时
- 工时完成率

### 3. 工作类型分布饼图

- 各工作类型的工时占比
- 可视化展示工作类型分布

### 4. 计划工时 vs 实际工时对比柱状图

- 每个员工的计划工时和实际工时对比
- 直观展示工作完成情况

### 5. 用户详细统计表格

- 姓名
- 计划工时
- 实际工时
- 完成率
- 工作类型分布
- 日志条目数

---

## 🔧 技术实现

### 后端实现

#### 1. PDF 生成服务 (`WorkLogWeekPDFService`)

```python
class WorkLogWeekPDFService:
    """工作周统计报告PDF导出服务"""

    def generate_work_week_report(
        self,
        work_week_info: Dict[str, Any],
        overall_stats: Dict[str, Any],
        user_summaries: List[Dict[str, Any]],
        work_type_stats: Dict[str, Any]
    ) -> BytesIO:
        """生成工作周统计报告PDF"""
        # ...
```

**主要方法：**

- `_create_title()`: 创建报告标题
- `_create_week_info()`: 创建工作周信息表格
- `_create_overall_stats()`: 创建整体统计概览
- `_create_work_type_chart()`: 创建工作类型分布饼图
- `_create_hours_compare_chart()`: 创建计划工时 vs 实际工时对比柱状图
- `_create_user_detail_table()`: 创建用户详细统计表格

**使用的库：**

- `reportlab`: PDF 生成
- `matplotlib`: 图表生成
- 支持中文字体（Windows: SimHei, Linux/Docker: WQYZenHei）

#### 2. 导出 API 端点

```python
@router.get("/weeks/{week_id}/export")
async def export_work_week_report(
    week_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出工作周统计报告PDF"""
    # ...
```

**处理流程：**

1. 查询工作周信息
2. 查询所有工作日志条目
3. 计算整体统计数据
4. 计算用户详细统计
5. 计算工作类型统计
6. 生成 PDF
7. 返回文件流

### 前端实现

#### `exportWorkLog` 函数

```typescript
const exportWorkLog = async () => {
  try {
    // 1. 显示加载提示
    ElMessage.info('正在生成PDF报告，请稍候...')

    // 2. 调用后端API
    const response = await fetch(`/api/work-logs/weeks/${workWeekId.value}/export`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })

    // 3. 检查响应
    if (!response.ok) {
      throw new Error('导出失败')
    }

    // 4. 获取文件blob
    const blob = await response.blob()

    // 5. 解析文件名
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = '工作周统计报告.pdf'
    // ... 解析文件名 ...

    // 6. 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()

    // 7. 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('PDF报告导出成功')
  } catch (error) {
    ElMessage.error(`导出失败: ${error.message}`)
  }
}
```

---

## 📸 使用方法

### 1. 进入工作周详情页面

- 在工作日志页面左侧导航选择一个工作周
- 右侧显示该工作周的详细信息和表格

### 2. 点击"导出数据"按钮

- 位于页面右上角，黄色按钮
- 图标：下载图标 📥

### 3. 等待 PDF 生成

- 系统会显示"正在生成PDF报告，请稍候..."
- 生成时间取决于数据量（通常 2-5 秒）

### 4. 自动下载

- PDF 生成完成后会自动下载
- 文件名格式：`{工作周标题}_统计报告.pdf`
- 例如：`2025W44标注组工作计划_统计报告.pdf`

---

## 🎨 PDF 报告样式

### 设计特点

- **专业配色**：蓝色主题（#1a73e8）
- **清晰结构**：分章节展示，层次分明
- **丰富图表**：饼图、柱状图可视化展示
- **详细数据**：完整的用户统计表格
- **中文支持**：完美支持中文字体显示

### 布局

- **页面尺寸**：A4
- **边距**：上下左右各 2cm
- **字体**：
  - 标题：24pt，蓝色
  - 副标题：16pt
  - 正文：10pt
- **图表尺寸**：
  - 饼图：14cm × 10cm
  - 柱状图：16cm × 10cm（分页显示）

---

## 🔍 数据统计说明

### 计划工时计算

- **标准工作周**：周一到周五，共 5 个工作日
- **每日工时**：8 小时
- **每周工时**：40 小时/人
- **总计划工时**：参与人数 × 40 小时

### 实际工时统计

- 统计所有工作日志条目中的实际工时
- 按用户汇总
- 按工作类型汇总

### 工时完成率

```
工时完成率 = (实际工时 / 计划工时) × 100%
```

### 工作类型统计

- 统计每种工作类型的总工时
- 计算占比
- 展示为饼图

---

## 🐛 错误处理

### 前端错误处理

1. **网络错误**：显示"导出失败: 网络错误"
2. **权限错误**：显示"导出失败: 权限不足"
3. **数据错误**：显示"导出失败: 数据异常"
4. **未知错误**：显示"导出失败: 未知错误"

### 后端错误处理

1. **工作周不存在**：返回 404
2. **权限不足**：返回 403
3. **PDF 生成失败**：返回 500，记录详细日志
4. **数据库查询失败**：返回 500，记录异常堆栈

### 日志记录

```python
logger.info(f"📊 [WorkLogExport] 开始生成工作周报告: 用户={username}, 工作周ID={week_id}")
logger.info(f"📋 [WorkLogExport] 查询到工作日志条目数: {count}")
logger.info(f"✅ [WorkLogExport] 报告生成成功: {filename}")
logger.error(f"❌ [WorkLogExport] 生成报告失败: {error}", exc_info=True)
```

---

## 📊 性能优化

### 后端优化

1. **使用 joinedload**：预加载关联数据，减少数据库查询

   ```python
   entries = db.query(WorkLogEntry).filter(...).options(
       joinedload(WorkLogEntry.user),
       joinedload(WorkLogEntry.work_type)
   ).all()
   ```

2. **一次性统计**：单次遍历完成所有统计
3. **四舍五入**：统一精度，减少计算误差

### 前端优化

1. **加载提示**：提前告知用户正在处理
2. **错误捕获**：完整的 try-catch 处理
3. **资源清理**：及时释放 Blob URL

---

## 🔐 权限控制

### 导出权限

- **所有登录用户**：可以导出自己有权限查看的工作周报告
- **管理员**：可以导出所有工作周报告
- **审核员**：可以导出所有工作周报告

### API 权限检查

```python
current_user: User = Depends(get_current_user)
```

- 需要登录才能访问
- 未登录返回 401

---

## 📝 文件命名规则

### 文件名格式

```
{工作周标题}_统计报告.pdf
```

### 示例

- `2025W44标注组工作计划_统计报告.pdf`
- `2025W45算法组工作计划_统计报告.pdf`
- `2025年第44周工作计划_统计报告.pdf`

### 中文文件名处理

```python
filename = f"{work_week.title}_统计报告.pdf"
filename = filename.encode('utf-8').decode('latin1')
```

- 使用 UTF-8 编码
- 在 HTTP 头中使用 `filename*=UTF-8''` 格式

---

## 🧪 测试建议

### 功能测试

1. ✅ 导出一个有数据的工作周
2. ✅ 导出一个空工作周（无日志条目）
3. ✅ 导出一个只有部分用户填写的工作周
4. ✅ 检查 PDF 中的图表是否正确
5. ✅ 检查 PDF 中的中文是否正常显示

### 边界测试

1. 只有 1 个用户的工作周
2. 有 50+ 个用户的工作周
3. 所有用户工时都为 0
4. 有的用户工时超过 40 小时

### 兼容性测试

1. Chrome 浏览器
2. Firefox 浏览器
3. Safari 浏览器
4. Edge 浏览器

---

## 🎯 未来改进方向

### 功能增强

1. ⭐ 支持导出多个工作周的对比报告
2. ⭐ 支持自定义导出内容（选择要包含的章节）
3. ⭐ 支持导出为 Excel 格式
4. ⭐ 支持邮件发送报告

### 性能优化

1. 🚀 使用缓存加速重复导出
2. 🚀 异步生成 PDF，支持大数据量
3. 🚀 前端预览功能

### 用户体验

1. 💡 导出前预览
2. 💡 导出历史记录
3. 💡 自定义报告模板

---

## 🐛 已知问题

### 无已知问题 ✅

---

## 📚 相关文件

### 后端

- `backend/app/services/pdf_export_service.py` - PDF 生成服务
- `backend/app/api/work_logs.py` - 工作日志 API（包含导出端点）

### 前端

- `src/views/work-log/week-detail.vue` - 工作周详情页面（包含导出按钮）
- `src/views/work-log/components/WorkLogStatistics.vue` - 统计报表组件（参考）

### 文档

- `WORK_LOG_EXPORT_FEATURE.md` - 本文档

---

## 📖 参考资料

### 相关导出功能

- 个人绩效报告导出：`backend/app/api/performance_export.py` (line 24-135)
- 团队绩效报告导出：`backend/app/api/performance_export.py` (line 291-391)
- 项目报告导出：`backend/app/api/performance_export.py` (line 558-813)

### 使用的技术

- [ReportLab](https://www.reportlab.com/): Python PDF 生成库
- [Matplotlib](https://matplotlib.org/): Python 绘图库
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/): 文件流响应

---

## ✨ 总结

工作周统计报告导出功能已完整实现，包括：

- ✅ 后端 PDF 生成服务
- ✅ 后端导出 API 端点
- ✅ 前端导出功能
- ✅ 完整的错误处理
- ✅ 用户友好的交互

用户现在可以方便地导出包含图表和详细数据的工作周统计报告 PDF！

---

**🎉 功能实现完成！**
