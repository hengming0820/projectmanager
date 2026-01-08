创建根组件
// # root.component.tsx
import { Component, ContentType } from '@textbus/core'
import { ViewComponentProps } from '@textbus/adapter-viewfly'

// 定义 Textbus 根组件数据模型
export class RootComponent extends Component {
  static componentName = 'RootComponent'
  static type = ContentType.BlockComponent
}

// 创建 RootComponentView 组件用于渲染 Textbus 根组件
export const RootComponentView = (props: ViewComponentProps<RootComponent>) => {
  return () => {
    return <div ref={props.rootRef}>这是 Textbus 富文本编辑器，我是 {props.component.name} 组件！</div>
  }
// # editor.ts
import { ContentType, Textbus } from '@textbus/core'
import { ViewflyAdapter } from '@textbus/adapter-viewfly'
import { BrowserModule } from '@textbus/platform-browser'
import { createApp } from '@viewfly/platform-browser'

import { RootComponentView, RootComponent } from './root.component'

// 创建 Viewfly 适配器，用于桥接 Textbus 和 Viewfly
const adapter = new ViewflyAdapter({
  [RootComponent.componentName]: RootComponentView // 声明 Textbus 根组件用 RootComponentView 组件渲染
}, (host, root, textbus) => {
  // host 为 Textbus 创建的用于渲染文档的容器
  // root 为 Viewfly 的根组件，即 RootComponentView 组件

  // 使用 Viewfly 创建一个编辑器视图
  const app = createApp(root, {
    // 使用 Textbus 实例作为 Viewfly App 的上下文，这样
    // 我们就可以在 Viewfly 组件内通过 inject 函数注入 Textbus 实例
    // 中包含的内部对象了
    context: textbus
  }).mount(host)
  // 返回一个函数，当 Textbus 销毁时，同时销毁 Viewlfy 实例
  return () => {
    app.destroy()
  }
})

// 创建 Textbus 浏览器平台运行环境模块
const browserModule = new BrowserModule({
  adapter, // 添加 Viewfly 适配器
  renderTo() {
    return document.getElementById('editor')!
  }
})

// 创建 Textbus 实例
const textbus = new Textbus({
  imports: [
    browserModule // 添加浏览器支持模块
  ]
})

// 创建一个数据模型
const rootModel = new RootComponent(textbus, {})
// 渲染数据模型
textbus.render(rootModel)

<div id="editor"></div>

import { useEffect } from 'react'
import { Editor } from '@textbus/xnote'
import 'katex/dist/katex.css'
import '@textbus/xnote/bundles/index.css'

function App() {
  const editorRef = useRef()
  useEffect(() => {
    const editor = new Editor()
    editor.mount(editorRef.current).then(() => {
      console.log('编辑器创建完成')
    })
    return () => {
      editor.destroy()
    }
  }, [])

  return (
    <div ref={editorRef}></div>
  )
}

配置项
XNote  继承自 Textbus，并在 Textbus 配置项的基础上增加了以下配置。
/**
 * XNote 配置项
 */
export interface EditorConfig extends TextbusConfig {
  /** 默认 HTML 内容*/
  content?: string,
  /** 协作服务配置 */
  collaborateConfig?: XNoteCollaborateConfig,
  /** 视图配置项 */
  viewOptions?: Partial<ViewOptions>



#工具条
XNote 默认创建一个行内工具条和左侧快捷工具，我们还提供了静态工具条和悬浮工具条，你可以通过配置项覆盖默认的工具条配置。
import {
  InlineToolbarPlugin,
  LeftToolbarPlugin,
  StaticToolbarPlugin,
  SuspensionToolbarPlugin,
  Editor
} from '@textbus/xnote'

// 行内工具条，会根据用户的框选自动弹出
const inlineToolbarPlugin = new InlineToolbarPlugin({
  // 主题：可选，可配置 dark，默认为 light
  theme: 'light'
})

// 左侧工具条，会根据用户的鼠标指针，自动在文档左侧弹出操作
const leftToolbarPlugin = new LeftToolbarPlugin()

// 静态工具条，适用于普通编辑器顶部的工具条
const staticToolbarPlugin = new StaticToolbarPlugin({
  // 静态工具条需要一个放置工具的容器，
  host: document.getElementById('toolbar'),
  // 主题：可选，可配置 dark，默认为 light
  theme: 'light'
})

// 悬浮工具条，会根据用户的滚动，自动展示在文档可视区域的顶部
const suspensionToolbarPlugin = new SuspensionToolbarPlugin({
  // 主题：可选，可配置 dark，默认为 light
  theme: 'light'
})

const editor = new Editor({
  plugins: [
    inlineToolbarPlugin,
    leftToolbarPlugin,
    staticToolbarPlugin,
    suspensionToolbarPlugin
  ]
