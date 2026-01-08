# 个人中心入职时间显示功能

## 修改说明

在个人中心的用户资料卡片中添加了入职时间显示，位置在"星像精准－部门－姓名"下方。

## 修改的文件

### `src/views/system/user-center/index.vue` - 个人中心页面

#### 1. 添加入职时间显示（第38-41行）

在用户资料卡片的 `outer-info` 区域新增一行显示入职时间：

```vue
<div>
  <i class="iconfont-sys">&#xe747;</i>
  <span>入职时间：{{ formatHireDate(userInfo.hireDate) }}</span>
</div>
```

**图标说明**：使用 `&#xe747;` (日历图标) 表示入职时间

#### 2. 添加格式化函数（第290-307行）

新增 `formatHireDate` 函数来格式化入职时间：

```typescript
// 格式化入职时间
const formatHireDate = (hireDate?: string) => {
  if (!hireDate) return '未设置'
  try {
    // 支持多种日期格式
    const date = new Date(hireDate)
    if (isNaN(date.getTime())) return '日期格式错误'

    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')

    return `${year}年${month}月${day}日`
  } catch (error) {
    console.error('格式化入职时间失败:', error)
    return '未知'
  }
}
```

## 功能特点

### 1. 显示位置

- 📍 位于"星像精准－部门－姓名"下方
- 📍 与其他信息（邮箱、角色、地址等）保持一致的样式
- 📍 图标 + 文本的展示方式

### 2. 日期格式化

- ✅ 格式：`YYYY年MM月DD日`（如：2025年01月15日）
- ✅ 月份和日期自动补零（如：01月05日）
- ✅ 支持多种日期输入格式（ISO格式、时间戳等）

### 3. 异常处理

| 情况           | 显示内容       |
| -------------- | -------------- |
| 未设置入职时间 | "未设置"       |
| 日期格式错误   | "日期格式错误" |
| 其他异常       | "未知"         |

### 4. 数据来源

- 从 `userStore.getUserInfo` 获取用户信息
- 使用 `userInfo.hireDate` 字段
- 兼容 `hire_date` 和 `hireDate` 两种命名格式

## 页面显示效果

个人中心左侧资料卡片将显示：

```
[头像]
王欢欢
研发部标注组

📧 whh@xxjz.com
👤 annotator
📍 四川省成都市
🏢 星像精准－研发部标注组－王欢欢
📅 入职时间：2025年08月29日         ← 新增
```

## 技术细节

### 数据流向

```
1. 用户登录
   ↓
2. userStore 获取用户信息 (包含 hireDate)
   ↓
3. userInfo computed 属性更新
   ↓
4. formatHireDate 格式化日期
   ↓
5. 页面显示格式化后的入职时间
```

### 依赖的用户数据字段

```typescript
interface UserInfo {
  // ... 其他字段
  hireDate?: string // 入职时间字段（YYYY-MM-DD格式）
}
```

### 格式化逻辑

```typescript
// 输入示例：
'2025-08-29'
'2025-08-29T00:00:00'
'2025/08/29'

// 输出统一为：
'2025年08月29日'
```

## 样式说明

使用现有的样式类，与其他信息项保持一致：

- `.outer-info > div` - 信息行容器
- `.iconfont-sys` - 图标样式
- `span` - 文本内容样式

样式特点：

- 左对齐显示
- 图标与文本间距 8px
- 字体大小 14px
- 行间距 10px

## 验证步骤

### 1. 有入职时间的用户

1. 登录系统
2. 访问"个人中心"页面
3. ✅ 应该看到"入职时间：YYYY年MM月DD日"

### 2. 未设置入职时间的用户

1. 登录系统（新用户或未设置入职时间）
2. 访问"个人中心"页面
3. ✅ 应该看到"入职时间：未设置"

### 3. 响应式更新

1. 管理员在用户管理页面修改用户的入职时间
2. 用户刷新个人中心页面
3. ✅ 应该看到更新后的入职时间

## 相关功能

### 用户管理页面

- 用户管理页面已支持设置和编辑入职时间
- 管理员可以为用户设置或修改入职时间
- 参考文档：之前关于用户管理入职日期的修改

### 数据同步

- 后端API：`GET /api/users/me/profile` 返回用户完整信息
- 用户Store：自动同步 `hire_date` 和 `hireDate` 字段
- 实时更新：用户信息变更后，刷新页面即可看到最新数据

## 潜在改进

### 1. 工龄计算

可以考虑增加工龄显示：

```typescript
const formatHireDate = (hireDate?: string) => {
  if (!hireDate) return '未设置'
  // ... 现有逻辑

  // 计算工龄
  const today = new Date()
  const hire = new Date(hireDate)
  const years = today.getFullYear() - hire.getFullYear()
  const months = today.getMonth() - hire.getMonth()

  let workAge = ''
  if (years > 0) {
    workAge = ` (入职 ${years} 年`
    if (months > 0) workAge += ` ${months} 个月)`
    else workAge += ')'
  } else if (months > 0) {
    workAge = ` (入职 ${months} 个月)`
  } else {
    workAge = ' (新入职)'
  }

  return `${year}年${month}月${day}日${workAge}`
}
```

### 2. 悬停提示

可以添加 Tooltip 显示更详细的信息：

```vue
<div>
  <el-tooltip :content="`入职已 ${calculateWorkDays(userInfo.hireDate)} 天`" placement="top">
    <div>
      <i class="iconfont-sys">&#xe747;</i>
      <span>入职时间：{{ formatHireDate(userInfo.hireDate) }}</span>
    </div>
  </el-tooltip>
</div>
```

### 3. 纪念日提醒

在入职周年纪念日时显示特殊徽章或提示。

## 注意事项

1. **日期格式**：确保后端返回的 `hire_date` 是有效的日期格式
2. **时区问题**：当前使用本地时区，如需UTC时区请调整逻辑
3. **空值处理**：已经处理了空值、undefined等情况
4. **兼容性**：支持所有现代浏览器的 Date 构造函数

## 更新日期

- 2025-10-21: 初始版本 - 添加个人中心入职时间显示

## 维护者

- AI Assistant
