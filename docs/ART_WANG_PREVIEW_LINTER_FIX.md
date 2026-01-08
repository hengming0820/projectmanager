# ArtWangPreview 组件 TypeScript 错误修复

## 修复时间

2025-11-06

## 问题描述

`ArtWangPreview`组件出现3个TypeScript linter错误：

```
应有 2 个参数，但获得 1 个。
未提供 "listener" 的自变量。

位置：
- 第67行：editor.off('change')
- 第68行：editor.off('focus')
- 第69行：editor.off('blur')
```

---

## 根本原因

### `editor.off()` 方法签名不匹配

根据WangEditor的类型定义：

```typescript
// @wangeditor/core/dist/core/src/editor/interface.d.ts
interface IDomEditor {
  off: (type: string, listener: ee.EventListener) => void
  //     ^^^^^^^^^^^^^^ 需要两个参数
}
```

**问题代码**：

```typescript
// ❌ 错误：只提供了1个参数
editor.off('change') // 缺少 listener 参数
editor.off('focus') // 缺少 listener 参数
editor.off('blur') // 缺少 listener 参数
```

**为什么会有这个问题？**

`off`方法用于移除特定的事件监听器，需要：

1. **事件类型** (type: string) - 例如 'change', 'focus', 'blur'
2. **监听器引用** (listener: EventListener) - 之前注册的具体函数

如果只提供事件类型，TypeScript会报错，因为：

- 无法知道要移除哪个具体的监听器
- 一个事件可能有多个监听器
- 必须提供监听器的引用才能精确移除

---

## 解决方案

### 删除不必要的 `off()` 调用

**为什么可以删除？**

在`ArtWangPreview`预览组件中，我们已经通过以下方式确保了只读模式：

1. **配置层面** - `readOnly: true`

```typescript
const editorConfig: Partial<IEditorConfig> = {
  readOnly: true, // ✅ 配置为只读
  scroll: true,
  placeholder: ''
}
```

2. **API层面** - `editor.disable()`

```typescript
const onCreateEditor = (editor: IDomEditor) => {
  editor.disable() // ✅ 禁用编辑器
}
```

3. **CSS层面** - 隐藏工具栏

```scss
:deep(.w-e-toolbar) {
  display: none; // ✅ 隐藏所有工具
}
```

**结论**：

- ✅ 已经有3层保护确保只读模式
- ✅ 不需要手动移除事件监听器
- ✅ 删除`off()`调用不会影响功能

---

## 修复代码

**修复前** ❌：

```typescript
const onCreateEditor = (editor: IDomEditor) => {
  editorRef.value = editor

  // 确保禁用编辑（双重保险）
  editor.disable()

  // 移除所有事件监听（防止意外交互）
  editor.off('change') // ❌ TypeScript错误：缺少参数
  editor.off('focus') // ❌ TypeScript错误：缺少参数
  editor.off('blur') // ❌ TypeScript错误：缺少参数

  console.log('📖 [ArtWangPreview] 预览组件已创建（只读模式）')
}
```

**修复后** ✅：

```typescript
const onCreateEditor = (editor: IDomEditor) => {
  editorRef.value = editor

  // 确保禁用编辑（双重保险）
  editor.disable() // ✅ 这就足够了

  console.log('📖 [ArtWangPreview] 预览组件已创建（只读模式）')
}
```

---

## 技术细节

### WangEditor 事件系统

#### 正确使用 `off()` 方法

```typescript
// 1️⃣ 首先保存监听器引用
const changeHandler = (editor: IDomEditor) => {
  console.log('内容变化')
}

// 2️⃣ 注册监听器
editor.on('change', changeHandler)

// 3️⃣ 移除监听器时提供引用
editor.off('change', changeHandler) // ✅ 正确
```

#### 错误使用示例

```typescript
// ❌ 错误：没有监听器引用
editor.off('change')

// ❌ 错误：使用匿名函数（无法移除）
editor.on('change', () => {
  /* ... */
})
editor.off('change', () => {
  /* ... */
}) // 这是不同的函数引用！
```

### 为什么在预览组件中不需要 `off()`？

1. **没有注册自定义监听器**

   - 预览组件不监听任何事件
   - 只是显示内容

2. **`readOnly` 模式已经禁用交互**

   - WangEditor内部不会触发编辑相关事件
   - 不需要手动移除

3. **`disable()` 提供额外保护**
   - 禁用所有编辑功能
   - 防止任何交互

---

## 修改的文件

| 文件 | 修改内容 | 状态 |
| --- | --- | --- |
| `src/components/core/forms/art-wang-preview/index.vue` | 删除3行不必要的`editor.off()`调用 | ✅ |

---

## 测试清单

### 功能测试

- [x] 预览组件正常显示内容
- [x] 内容确实不可编辑
- [x] 工具栏正确隐藏
- [x] 光标无法聚焦到编辑器
- [x] 点击内容无反应

### TypeScript检查

- [x] 无linter错误
- [x] 类型检查通过
- [x] 构建成功

### 各页面预览功能

- [x] 工作记录预览
- [x] 会议记录预览
- [x] 项目文档预览
- [x] 模型测试预览
- [x] 协作文档预览

---

## 总结

✅ **修复完成**

通过删除不必要的`editor.off()`调用：

- ✅ 解决了3个TypeScript错误
- ✅ 简化了代码逻辑
- ✅ 功能完全不受影响
- ✅ 预览模式的3层保护依然有效

🎯 **核心要点**

- `readOnly: true` + `editor.disable()` 已经足够确保只读
- 不需要手动移除事件监听器
- `off()` 方法需要监听器引用，不能只传事件类型

🎉 **所有TypeScript错误已修复！**
