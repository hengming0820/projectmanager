# 本地 Docker 部署指南

## 📋 概述

本目录提供了两种 Docker 部署配置：

1. **docker-compose.yml** - 完整部署（需要预先构建前端）
2. **docker-compose.dev.yml** - 开发模式（仅后端服务，前端本地运行）

### 📜 可用脚本和文档

#### 启动/停止脚本

| 脚本名称         | 平台        | 类型 | 说明                                     |
| ---------------- | ----------- | ---- | ---------------------------------------- |
| `start-dev.bat`  | Windows     | 启动 | 启动后端服务（开发模式），前端需手动启动 |
| `start-dev.sh`   | Linux/macOS | 启动 | 启动后端服务（开发模式），前端需手动启动 |
| `start-prod.bat` | Windows     | 启动 | 自动构建前端并启动所有服务（生产模式）   |
| `start-prod.sh`  | Linux/macOS | 启动 | 自动构建前端并启动所有服务（生产模式）   |
| `stop-all.bat`   | Windows     | 停止 | 停止所有服务，可选择是否删除数据卷       |
| `stop-all.sh`    | Linux/macOS | 停止 | 停止所有服务，可选择是否删除数据卷       |

#### 配置文档

| 文档名称                  | 说明                           |
| ------------------------- | ------------------------------ |
| `README.md`               | 本文档，完整的部署指南         |
| `SCRIPTS_GUIDE.md`        | 脚本详细使用指南               |
| `NETWORK_ACCESS_GUIDE.md` | 网络访问和局域网配置指南       |
| `WINDOWS_BATCH_FIX.md`    | Windows Batch 脚本问题修复说明 |

**新功能**：

- ✅ 所有启动脚本现在都会自动检测并显示局域网访问地址！📱
- ✅ Windows Batch 脚本已修复，避免 "is not recognized" 错误

---

## 🚀 快速开始

### 🎯 一键启动脚本（推荐）

我们提供了自动化启动脚本，让部署变得更简单！

#### Windows 用户

```batch
# 开发模式（支持热重载）
cd deploy-local
start-dev.bat

# 生产模式（完整部署）
cd deploy-local
start-prod.bat
```

#### Linux / macOS 用户

```bash
# 添加可执行权限（首次运行需要）
cd deploy-local
chmod +x start-dev.sh start-prod.sh

# 开发模式（支持热重载）
./start-dev.sh

# 生产模式（完整部署）
./start-prod.sh
```

**脚本功能**：

- ✅ 自动检查环境
- ✅ 自动构建前端（生产模式）
- ✅ 自动启动 Docker 服务
- ✅ 显示详细的服务状态
- ✅ 提供访问地址和登录信息
- ✅ 可选择是否自动打开浏览器

---

### 方式 1：完整 Docker 部署（生产环境测试）

适用于测试完整的生产环境配置。

```bash
# 1. 构建前端
cd ..
npm run build

# 2. 启动所有服务
cd deploy-local
docker-compose up -d

# 3. 访问
# 前端: http://localhost:3006
# 后端: http://localhost:8000
# MinIO: http://localhost:9001
```

### 方式 2：开发模式（推荐）

适用于日常开发，前端支持热重载。

```bash
# 1. 启动后端服务
cd deploy-local
docker-compose -f docker-compose.dev.yml up -d

# 2. 在另一个终端启动前端
cd ..
npm run dev

# 3. 访问
# 前端: http://localhost:3008 (Vite 开发服务器)
# 后端: http://localhost:8000
```

---

## 🔧 服务说明

| 服务           | 端口                       | 说明                 |
| -------------- | -------------------------- | -------------------- |
| **PostgreSQL** | 5432                       | 数据库               |
| **Redis**      | 6379                       | 缓存与 Token 管理    |
| **MinIO**      | 9000, 9001                 | 对象存储（文件上传） |
| **Backend**    | 8000                       | FastAPI 后端         |
| **Frontend**   | 3006 (Docker) / 3008 (Dev) | Vue 前端             |

---

## 📝 常用命令

### 启动服务

```bash
# 完整模式
docker-compose up -d

# 开发模式
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止服务

**使用停止脚本（推荐）**：

```bash
# Linux/macOS
./stop-all.sh

# Windows
stop-all.bat
```

**手动停止**：

```bash
# 停止服务（保留数据）
docker-compose down

# 停止并删除数据卷（⚠️ 会删除数据库数据）
docker-compose down -v
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 重新构建

```bash
# 重新构建并启动
docker-compose up -d --build

# 仅重新构建
docker-compose build
```

---

## 🐛 故障排查

### 问题 1：前端无法访问 (http://localhost:3006)

**可能原因**：

1. ❌ 没有构建前端（dist 目录不存在）
2. ❌ 前端容器启动失败

**解决方案**：

```bash
# 检查 dist 目录
ls -la ../dist

# 如果不存在，构建前端
cd ..
npm run build

# 查看前端容器状态
cd deploy-local
docker-compose ps frontend

# 查看前端容器日志
docker-compose logs frontend

# 重启前端容器
docker-compose restart frontend
```

### 问题 2：后端 API 无法访问

```bash
# 查看后端日志
docker-compose logs backend

# 检查数据库连接
docker-compose exec backend python -c "from app.database import engine; engine.connect()"

# 重启后端
docker-compose restart backend
```

### 问题 3：数据库连接失败

```bash
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 进入数据库容器
docker-compose exec postgres psql -U admin -d medical_annotation

# 检查数据库
\dt
```

### 问题 4：MinIO 无法上传文件

```bash
# 访问 MinIO 控制台
# http://localhost:9001
# 用户名: minioadmin
# 密码: minioadmin123

# 检查 bucket 是否存在
docker-compose exec backend python -c "from app.utils.minio_client import minio_client; print(minio_client.bucket_exists('medical-annotations'))"
```

### 问题 5：Redis 连接失败

```bash
# 检查 Redis 状态
docker-compose exec redis redis-cli ping

# 查看 Redis 日志
docker-compose logs redis
```

### 问题 6：Windows 脚本显示 "is not recognized" 错误

**错误示例**：

```
'前端应用:' is not recognized as an internal or external command
'用户名:' is not recognized as an internal or external command
```

**原因**：Windows Batch 脚本中冒号 `:` 是特殊字符

**解决**：

1. 确保使用最新版本的脚本（已修复）
2. 查看 **`WINDOWS_BATCH_FIX.md`** 了解详细说明
3. 如果问题持续，尝试运行测试脚本：
   ```batch
   cd deploy-local
   test-display.bat
   ```

---

## 📊 环境变量

### 数据库配置

- **用户名**: `admin`
- **密码**: `password123`
- **数据库**: `medical_annotation`
- **端口**: `5432`

### MinIO 配置

- **Access Key**: `minioadmin`
- **Secret Key**: `minioadmin123`
- **API 端口**: `9000`
- **控制台端口**: `9001`

### JWT 配置

- **Secret**: `change-me-in-prod` （⚠️ 生产环境请修改）

---

## 🔄 数据初始化

首次启动时，数据库会自动执行 `../deploy/db-init` 目录中的初始化脚本。

如果需要重新初始化：

```bash
# 1. 停止并删除数据卷
docker-compose down -v

# 2. 重新启动
docker-compose up -d

# 3. 运行初始化脚本
cd ..
cd backend
python scripts/init_db.py
```

---

## 🎯 开发工作流

### 推荐开发流程（使用一键脚本）

```bash
# 1. 启动后端服务
cd deploy-local
./start-dev.sh        # Linux/macOS
# 或
start-dev.bat         # Windows

# 2. 在另一个终端启动前端（按照脚本提示）
cd ..
npm run dev

# 3. 开始开发
# 前端：修改 src/ 目录下的文件，自动热重载
# 后端：修改 backend/app/ 目录下的文件，自动重启（uvicorn --reload）

# 4. 开发完成后，测试生产部署
cd deploy-local
./start-prod.sh       # Linux/macOS
# 或
start-prod.bat        # Windows
```

### 传统开发流程（手动操作）

```bash
# 1. 启动后端服务（数据库、Redis、MinIO、后端 API）
cd deploy-local
docker-compose -f docker-compose.dev.yml up -d

# 2. 在另一个终端启动前端（支持热重载）
cd ..
npm run dev

# 3. 开始开发
# 前端：修改 src/ 目录下的文件，自动热重载
# 后端：修改 backend/app/ 目录下的文件，自动重启（uvicorn --reload）

# 4. 开发完成后，构建测试
npm run build

# 5. 测试完整 Docker 部署
cd deploy-local
docker-compose down
docker-compose up -d
```

---

## 🌐 网络访问配置

### 局域网访问

本部署配置已支持局域网访问！您可以：

✅ 从局域网内其他电脑访问  
✅ 使用手机、平板等移动设备访问  
✅ 团队成员可以访问您的开发环境

**访问方式**：

```
# 本机访问
http://localhost:3006

# 局域网访问（示例）
http://192.168.200.20:3006
```

启动脚本会自动检测并显示您的局域网 IP 地址。

### 详细配置

查看 **`NETWORK_ACCESS_GUIDE.md`** 了解：

- 网络访问原理
- CORS 配置说明
- 防火墙设置
- 常见问题解决
- 安全建议

---

## 📦 生产部署建议

1. **修改密码**：所有默认密码（数据库、MinIO、JWT Secret）
2. **HTTPS**：配置 SSL 证书
3. **数据备份**：定期备份数据库和 MinIO 数据
4. **资源限制**：配置 Docker 容器的 CPU 和内存限制
5. **日志管理**：配置日志轮转
6. **网络安全**：限制 CORS 来源，使用反向代理

---

## 📞 支持

如有问题，请查看：

- **SCRIPTS_GUIDE.md** - 脚本使用详细指南
- **NETWORK_ACCESS_GUIDE.md** - 网络访问配置指南
- 主项目 README
- 提交 Issue 到项目仓库
