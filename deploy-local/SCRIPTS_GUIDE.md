# 🚀 部署脚本使用指南

本指南详细介绍了 `deploy-local/` 目录下所有可用的自动化脚本。

---

## 📜 脚本总览

| 脚本名称         | 平台        | 类型 | 功能描述                 |
| ---------------- | ----------- | ---- | ------------------------ |
| `start-dev.bat`  | Windows     | 启动 | 启动开发环境（后端服务） |
| `start-dev.sh`   | Linux/macOS | 启动 | 启动开发环境（后端服务） |
| `start-prod.bat` | Windows     | 启动 | 启动生产环境（所有服务） |
| `start-prod.sh`  | Linux/macOS | 启动 | 启动生产环境（所有服务） |
| `stop-all.bat`   | Windows     | 停止 | 停止所有服务             |
| `stop-all.sh`    | Linux/macOS | 停止 | 停止所有服务             |

---

## 🎯 快速开始

### Windows 用户

```batch
# 开发模式
cd deploy-local
start-dev.bat
# 然后在新终端运行: npm run dev

# 生产模式
cd deploy-local
start-prod.bat

# 停止服务
stop-all.bat
```

### Linux / macOS 用户

```bash
# 首次使用：添加可执行权限
cd deploy-local
chmod +x *.sh

# 开发模式
./start-dev.sh
# 然后在新终端运行: npm run dev

# 生产模式
./start-prod.sh

# 停止服务
./stop-all.sh
```

---

## 📋 脚本详细说明

### 1. 开发模式脚本

**文件**: `start-dev.sh` / `start-dev.bat`

**功能**：

- ✅ 启动后端服务（PostgreSQL, Redis, MinIO, Backend API）
- ✅ 不启动前端容器（前端需手动运行 `npm run dev`）
- ✅ 支持前端热重载
- ✅ 显示服务状态和访问地址

**使用场景**：

- 日常开发
- 需要频繁修改前端代码
- 需要实时看到前端变化

**启动的服务**：| 服务 | 端口 | 说明 | |------|------|------| | PostgreSQL | 5432 | 数据库 | | Redis | 6379 | 缓存 | | MinIO API | 9000 | 对象存储 | | MinIO Console | 9001 | MinIO 管理界面 | | Backend API | 8000 | 后端 API |

**后续步骤**：

```bash
# 在新终端窗口运行
cd ..
npm run dev

# 访问前端：http://localhost:3008
```

---

### 2. 生产模式脚本

**文件**: `start-prod.sh` / `start-prod.bat`

**功能**：

- ✅ 自动检查 `dist` 目录是否存在
- ✅ 如果不存在，自动运行 `npm run build`
- ✅ 询问是否重新构建前端（如果 dist 已存在）
- ✅ 启动所有服务（包括 Nginx 前端容器）
- ✅ 显示详细的访问信息
- ✅ 可选择自动打开浏览器

**使用场景**：

- 测试完整的生产环境部署
- 验证构建后的前端是否正常
- 演示或展示项目

**启动的服务**：| 服务 | 端口 | 说明 | |------|------|------| | PostgreSQL | 5432 | 数据库 | | Redis | 6379 | 缓存 | | MinIO API | 9000 | 对象存储 | | MinIO Console | 9001 | MinIO 管理界面 | | Backend API | 8000 | 后端 API | | Frontend (Nginx) | 3006 | 前端应用 |

**执行流程**：

```
1. 检查是否在 deploy-local 目录
   ├─ 不是 → 退出并提示错误
   └─ 是 → 继续

2. 检查 ../dist 目录
   ├─ 不存在 → 自动运行 npm run build
   └─ 存在 → 询问是否重新构建
      ├─ 是 → 运行 npm run build
      └─ 否 → 继续

3. 启动 Docker 服务
   └─ docker-compose up -d

4. 等待服务启动（8秒）

5. 显示服务状态和访问信息

6. 询问是否打开浏览器
   ├─ 是 → 自动打开 http://localhost:3006
   └─ 否 → 结束
```

---

### 3. 停止服务脚本

**文件**: `stop-all.sh` / `stop-all.bat`

**功能**：

- ✅ 停止所有 Docker 服务
- ✅ 询问是否删除数据卷
- ✅ 安全提示防止误操作

**使用场景**：

- 停止开发/测试环境
- 释放系统资源
- 清理测试数据

**选项说明**：

| 选项             | 命令                     | 效果                 | 数据保留                   |
| ---------------- | ------------------------ | -------------------- | -------------------------- |
| **保留数据** (N) | `docker-compose down`    | 停止服务             | ✅ 保留数据库和 MinIO 数据 |
| **删除数据** (y) | `docker-compose down -v` | 停止服务并删除数据卷 | ❌ 删除所有数据            |

**⚠️ 警告**：

- 选择删除数据卷（输入 `y`）会**永久删除**数据库中的所有数据！
- 删除后无法恢复，请谨慎操作
- 建议在日常开发中选择"保留数据"（输入 `N` 或直接回车）

---

## 💡 使用技巧

### 1. 开发工作流

**推荐流程**：

```bash
# 早上到公司
cd deploy-local
./start-dev.sh        # 启动后端服务

# 在新终端
cd ..
npm run dev           # 启动前端（自动打开浏览器）

# 开始愉快地开发...
# 修改代码，保存，浏览器自动刷新

# 下班前
cd deploy-local
./stop-all.sh         # 停止服务（选择 N 保留数据）
```

### 2. 测试生产部署

```bash
# 构建并测试
cd deploy-local
./start-prod.sh       # 自动构建并启动

# 测试完成后停止
./stop-all.sh         # 选择 N 保留数据
```

### 3. 完全清理环境

```bash
# 停止并删除所有数据
cd deploy-local
./stop-all.sh         # 输入 y 删除数据卷

# 重新初始化
./start-prod.sh       # 重新构建并启动
```

---

## 🐛 常见问题

### Q1: 脚本无法执行（Linux/macOS）

**错误**：`Permission denied`

**解决**：

```bash
chmod +x deploy-local/*.sh
```

### Q2: Docker 启动失败

**错误**：`Cannot connect to the Docker daemon`

**解决**：

1. 检查 Docker Desktop 是否运行
2. Windows: 右键任务栏 Docker 图标，确认状态
3. Linux: `sudo systemctl start docker`

### Q3: 端口被占用

**错误**：`Bind for 0.0.0.0:3006 failed: port is already allocated`

**解决**：

```bash
# 查看端口占用
# Windows
netstat -ano | findstr "3006"

# Linux/macOS
lsof -i :3006

# 停止占用端口的进程或修改 docker-compose.yml 中的端口映射
```

### Q4: 前端构建失败

**错误**：`npm run build` 失败

**解决**：

```bash
# 清理依赖并重新安装
rm -rf node_modules package-lock.json
npm install

# 或使用 pnpm
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Q5: dist 目录不存在

**问题**：运行 `docker-compose up -d` 时前端无法访问

**解决**：

```bash
# 方法1: 使用生产脚本（自动构建）
./start-prod.sh

# 方法2: 手动构建
cd ..
npm run build
cd deploy-local
docker-compose up -d
```

---

## 📚 相关文档

- **README.md** - 完整的部署指南
- **docker-compose.yml** - 生产环境配置
- **docker-compose.dev.yml** - 开发环境配置

---

## 🎓 最佳实践

### 开发环境

1. ✅ 使用 `start-dev.sh` 启动后端服务
2. ✅ 使用 `npm run dev` 启动前端（支持热重载）
3. ✅ 每天下班使用 `stop-all.sh` 停止服务（保留数据）
4. ✅ 定期使用 `stop-all.sh` 清理数据（删除数据卷）

### 生产环境测试

1. ✅ 使用 `start-prod.sh` 启动所有服务
2. ✅ 测试完整的部署流程
3. ✅ 验证构建产物是否正常
4. ✅ 测试完成后使用 `stop-all.sh` 停止

### 性能优化

1. ✅ 开发时使用开发模式（内存占用更少）
2. ✅ 不使用时停止服务（释放资源）
3. ✅ 定期清理 Docker 资源：`docker system prune`

---

## 📞 获取帮助

如有问题：

1. 查看 **README.md** 的故障排查部分
2. 查看 Docker 日志：`docker-compose logs -f`
3. 查看特定服务日志：`docker-compose logs -f backend`
4. 提交 Issue 到项目仓库

---

**版本**: 1.0.0  
**最后更新**: 2025-10-17
