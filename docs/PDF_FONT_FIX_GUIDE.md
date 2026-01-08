# PDF中文字体修复指南

## 问题描述

在Docker生产环境中，PDF导出功能的中文显示为乱码或黑点。

## 原因

Docker容器默认没有安装中文字体，导致reportlab无法正确渲染中文。

## 解决方案

### 已修改的文件

1. **`backend/Dockerfile`** - 添加中文字体安装
2. **`backend/app/services/pdf_export_service.py`** - 改进字体加载逻辑

### 部署步骤

#### 方式一：重新构建并启动（推荐）

```bash
# 1. 停止当前运行的容器
cd deploy-htttps  # 或 deploy-local
docker-compose down

# 2. 删除旧的后端镜像（重要！）
docker rmi deploy-htttps-backend
# 或
docker rmi deploy-local-backend

# 3. 重新构建并启动
docker-compose up -d --build

# 4. 查看后端日志，确认字体加载成功
docker-compose logs -f backend
# 应该看到类似这样的日志：
# ✅ 成功加载字体: WQYZenHei from /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
# 📝 使用字体: WQYZenHei (正文), WQYZenHei (宋体)
```

#### 方式二：强制重新构建

```bash
# 1. 停止并删除所有容器
docker-compose down

# 2. 删除后端镜像
docker rmi deploy-htttps-backend -f

# 3. 清理构建缓存（可选，但推荐）
docker builder prune

# 4. 重新构建（不使用缓存）
docker-compose build --no-cache backend

# 5. 启动所有服务
docker-compose up -d
```

### Windows快捷脚本

创建一个 `rebuild-backend.bat` 文件：

```batch
@echo off
echo 🔨 重新构建后端服务（修复PDF中文字体）...
echo.

cd deploy-htttps
echo 📦 停止服务...
docker-compose down

echo 🗑️ 删除旧镜像...
docker rmi deploy-htttps-backend -f

echo 🏗️ 重新构建后端...
docker-compose build --no-cache backend

echo 🚀 启动所有服务...
docker-compose up -d

echo.
echo ✅ 完成！等待5秒后查看日志...
timeout /t 5 /nobreak >nul

echo.
echo 📋 后端日志（Ctrl+C退出）：
docker-compose logs -f backend
```

### Linux/Mac快捷脚本

创建一个 `rebuild-backend.sh` 文件：

```bash
#!/bin/bash
echo "🔨 重新构建后端服务（修复PDF中文字体）..."
echo ""

cd deploy-htttps || exit 1

echo "📦 停止服务..."
docker-compose down

echo "🗑️ 删除旧镜像..."
docker rmi deploy-htttps-backend -f

echo "🏗️ 重新构建后端..."
docker-compose build --no-cache backend

echo "🚀 启动所有服务..."
docker-compose up -d

echo ""
echo "✅ 完成！等待5秒后查看日志..."
sleep 5

echo ""
echo "📋 后端日志（Ctrl+C退出）："
docker-compose logs -f backend
```

## 验证修复

1. **查看后端启动日志**

   ```bash
   docker-compose logs backend | grep "字体"
   ```

   应该看到：

   ```
   ✅ 成功加载字体: WQYZenHei from /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
   📝 使用字体: WQYZenHei (正文), WQYZenHei (宋体)
   ```

2. **测试PDF导出**

   - 导出个人绩效报告
   - 导出团队绩效报告
   - 导出项目报告
   - 检查PDF中的中文是否正常显示

3. **如果仍有问题**
   - 进入容器检查字体文件：
     ```bash
     docker-compose exec backend ls -la /usr/share/fonts/truetype/wqy/
     ```
   - 应该看到 `wqy-zenhei.ttc` 和 `wqy-microhei.ttc` 文件

## 技术细节

### 安装的字体

- **文泉驿正黑体** (`fonts-wqy-zenhei`) - 主要使用
- **文泉驿微米黑** (`fonts-wqy-microhei`) - 备用字体

### 字体路径

容器中的字体位置：

- `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`
- `/usr/share/fonts/truetype/wqy/wqy-microhei.ttc`

### 字体加载优先级

1. Windows环境：SimHei（黑体）/ SimSun（宋体）
2. Linux/Docker环境：WQYZenHei（文泉驿正黑体）
3. 降级方案：Helvetica（英文字体，中文会显示为方框）

## 常见问题

### Q: 重新构建后还是乱码？

A:

1. 确认是否使用了 `--no-cache` 选项
2. 确认旧镜像已被删除：`docker images | grep backend`
3. 查看容器内字体文件是否存在

### Q: 构建速度很慢？

A:

- 第一次安装字体包需要下载约15-20MB数据
- 后续构建会使用缓存，速度会快很多
- 建议在网络良好的环境下进行首次构建

### Q: 本地开发环境需要修改吗？

A:

- Windows本地开发不需要修改，会自动使用系统字体
- Linux本地开发建议安装文泉驿字体：
  ```bash
  sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei
  ```

## 回滚方案

如果出现问题需要回滚：

```bash
# 1. 停止服务
docker-compose down

# 2. 还原Dockerfile和pdf_export_service.py到之前的版本
git checkout HEAD^ backend/Dockerfile
git checkout HEAD^ backend/app/services/pdf_export_service.py

# 3. 重新构建
docker-compose build backend
docker-compose up -d
```

## 联系支持

如有问题，请提供以下信息：

1. Docker版本：`docker --version`
2. 后端日志：`docker-compose logs backend | tail -100`
3. 字体文件列表：`docker-compose exec backend ls -la /usr/share/fonts/`
4. PDF导出错误信息（如果有）

---

**更新日期**: 2025-10-21  
**维护者**: AI Assistant
