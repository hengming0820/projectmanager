# 生产环境部署文件说明

## 📁 目录结构

```
deploy-htttps/
├── README.md                      # 本文件
├── QUICK_START.md                 # 快速启动指南 ⭐
├── DEPLOY_WITH_TAR_IMAGE.md       # TAR 镜像部署完整指南 📖
├── INTRANET_HTTPS.md              # HTTPS 配置指南
│
├── docker-compose.yml             # 开发环境配置（使用 build）
├── docker-compose-prod.yml        # 生产环境配置（使用 tar 镜像）⭐
│
├── load-and-start.sh              # Linux/Mac 启动脚本 🔧
├── load-and-start.bat             # Windows 启动脚本 🔧
├── start-prod.bat                 # Windows 开发启动脚本
├── deploy-yjs.sh                  # Yjs 服务器部署脚本 (Linux/Mac) 🆕
├── deploy-yjs.bat                 # Yjs 服务器部署脚本 (Windows) 🆕
│
├── nginx/
│   └── default.conf               # Nginx 配置文件
│
└── ssl/                           # SSL 证书目录（需自行创建）
    ├── cert.pem
    └── key.pem
```

---

## 🎯 两种部署方式对比

### 方式 1: 使用 Dockerfile 构建（开发环境）

**适用场景：**

- 开发环境
- 有源代码访问权限
- 需要频繁修改代码

**使用文件：** `docker-compose.yml`

**启动命令：**

```bash
docker-compose up -d
```

**优点：**

- 实时代码更新（挂载源码）
- 便于调试
- 灵活修改

**缺点：**

- 需要完整源码
- 构建时间较长
- 不适合生产环境

---

### 方式 2: 使用 TAR 镜像（生产环境）⭐ 推荐

**适用场景：**

- 生产环境
- 内网部署
- 不需要源码
- 快速部署

**使用文件：** `docker-compose-prod.yml`

**启动命令：**

```bash
# 自动化脚本（推荐）
./load-and-start.sh

# 或手动启动
docker load -i pm-backend-latest.tar
docker-compose -f docker-compose-prod.yml up -d
```

**优点：**

- ✅ 无需源码
- ✅ 快速部署
- ✅ 镜像可离线传输
- ✅ 生产环境优化配置
- ✅ 更安全（代码已打包）

**缺点：**

- 更新需要重新打包镜像

---

## 🚀 快速开始

### 方式 1: 使用自动化脚本（最简单）

**Linux/Mac:**

```bash
# 1. 准备镜像文件
# 确保 pm-backend-latest.tar 在当前目录

# 2. 运行脚本
chmod +x load-and-start.sh
./load-and-start.sh

# 3. 访问系统
# http://localhost
```

**Windows:**

```cmd
REM 1. 准备镜像文件
REM 确保 pm-backend-latest.tar 在当前目录

REM 2. 运行脚本
load-and-start.bat

REM 3. 访问系统
REM http://localhost
```

### 方式 2: 手动部署

```bash
# 1. 加载镜像
docker load -i pm-backend-latest.tar

# 2. 验证镜像
docker images | grep pm-backend

# 3. 启动服务
docker-compose -f docker-compose-prod.yml up -d

# 4. 查看状态
docker-compose -f docker-compose-prod.yml ps

# 5. 查看日志
docker-compose -f docker-compose-prod.yml logs -f
```

---

## 📚 文档索引

### 快速参考

- **[QUICK_START.md](./QUICK_START.md)** - 快速启动，3 步部署 ⚡

### 详细指南

- **[DEPLOY_WITH_TAR_IMAGE.md](./DEPLOY_WITH_TAR_IMAGE.md)** - 完整部署文档 📖
  - 开发环境打包流程
  - 生产环境部署步骤
  - 更新镜像流程
  - 常见问题解答

### 配置指南

- **[INTRANET_HTTPS.md](./INTRANET_HTTPS.md)** - HTTPS 配置指南 🔒
  - SSL 证书生成
  - Nginx HTTPS 配置
  - 证书更新流程

---

## 🔧 配置文件说明

### docker-compose.yml vs docker-compose-prod.yml

| 配置项         | docker-compose.yml (开发) | docker-compose-prod.yml (生产) |
| -------------- | ------------------------- | ------------------------------ |
| Backend 来源   | `build: Dockerfile`       | `image: pm-backend:latest`     |
| 代码挂载       | ✅ 挂载源码目录           | ❌ 不挂载（代码在镜像中）      |
| 健康检查       | ❌ 无                     | ✅ 有                          |
| 网络隔离       | ❌ 默认网络               | ✅ 自定义网络                  |
| 环境变量       | 开发配置                  | 生产优化配置                   |
| Token 过期时间 | 30 分钟                   | 60 分钟                        |
| 日志限制       | ❌ 无                     | ✅ 建议添加                    |

---

## 🛠️ 常用操作

### 服务管理

```bash
# 使用生产配置
COMPOSE_FILE="docker-compose-prod.yml"

# 启动
docker-compose -f $COMPOSE_FILE up -d

# 停止
docker-compose -f $COMPOSE_FILE down

# 重启
docker-compose -f $COMPOSE_FILE restart backend

# 状态
docker-compose -f $COMPOSE_FILE ps

# 日志
docker-compose -f $COMPOSE_FILE logs -f backend
```

### 镜像管理

```bash
# 查看镜像
docker images | grep pm-backend

# 删除旧镜像
docker rmi pm-backend:old

# 清理未使用镜像
docker image prune -a
```

### 数据管理

```bash
# 备份数据库
docker exec pm-postgres2 pg_dump -U admin medical_annotation > backup.sql

# 恢复数据库
cat backup.sql | docker exec -i pm-postgres2 psql -U admin -d medical_annotation

# 备份上传文件
tar -czf uploads_backup.tar.gz ../uploads/
```

---

## 🔐 安全建议

### 生产环境必须修改

在 `docker-compose-prod.yml` 中：

1. **数据库密码**

```yaml
POSTGRES_PASSWORD: <strong-password> # 修改这里
```

2. **MinIO 密码**

```yaml
MINIO_ROOT_PASSWORD: <strong-password> # 修改这里
```

3. **JWT 密钥**

```yaml
JWT_SECRET: <random-secret-key> # 修改这里
```

4. **CORS 配置**

```yaml
ALLOWED_ORIGINS: '["https://your-domain.com"]' # 添加你的域名
```

### 端口限制

```yaml
# 只对内网开放
ports:
  - '127.0.0.1:5432:5432' # 数据库仅本地访问
  - '0.0.0.0:80:80' # HTTP 公开
  - '0.0.0.0:443:443' # HTTPS 公开
```

---

## 📊 监控和维护

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df

# 清理未使用资源
docker system prune -a
```

### 日志配置

在 `docker-compose-prod.yml` 中添加：

```yaml
logging:
  driver: 'json-file'
  options:
    max-size: '10m'
    max-file: '3'
```

---

## ❓ 常见问题

### Q1: 两种 docker-compose 文件有什么区别？

**A:**

- `docker-compose.yml`: 开发环境，从 Dockerfile 构建，挂载源码
- `docker-compose-prod.yml`: 生产环境，使用预构建镜像，不挂载源码

### Q2: 如何从开发切换到生产模式？

**A:**

```bash
# 1. 停止开发环境
docker-compose down

# 2. 打包镜像
docker build -t pm-backend:latest -f backend/Dockerfile .
docker save -o pm-backend-latest.tar pm-backend:latest

# 3. 加载并启动生产环境
docker load -i pm-backend-latest.tar
docker-compose -f docker-compose-prod.yml up -d
```

### Q3: 如何更新生产环境的代码？

**A:**

1. 开发环境重新构建镜像
2. 保存为新的 tar 文件
3. 传输到生产环境
4. 停止服务 → 加载新镜像 → 启动服务

详见 [DEPLOY_WITH_TAR_IMAGE.md](./DEPLOY_WITH_TAR_IMAGE.md) 的"更新镜像流程"章节

### Q4: 为什么生产环境不挂载源码？

**A:**

- 更安全：代码打包在镜像中，不暴露源码
- 更稳定：避免误修改代码导致服务异常
- 更快速：不需要挂载文件系统，性能更好

---

## 🎯 部署检查清单

### 部署前

- [ ] 已准备 Backend 镜像 tar 文件
- [ ] 已准备前端 dist 文件
- [ ] 已准备数据库初始化脚本
- [ ] 已修改默认密码和密钥
- [ ] 已配置 CORS（添加域名）
- [ ] 已准备 SSL 证书（如使用 HTTPS）

### 部署后

- [ ] 所有容器正常运行
- [ ] Backend API 可访问 (/docs)
- [ ] 前端页面正常显示
- [ ] 登录功能正常
- [ ] 数据库连接正常
- [ ] 文件上传功能正常
- [ ] WebSocket 连接正常（如有）

---

## 🤝 Yjs 协作服务器部署

### 服务说明

Yjs 协作服务器是支持 XNote 编辑器实时多人协作的 WebSocket 服务。

### 快速部署

#### Linux/Mac:

```bash
cd deploy-htttps
chmod +x deploy-yjs.sh
./deploy-yjs.sh
```

#### Windows:

```batch
cd deploy-htttps
deploy-yjs.bat
```

### 服务配置

在 `docker-compose-prod.yml` 中包含了 Yjs 服务：

```yaml
yjs-server:
  image: deploy-https-yjs:v1.0
  container_name: pm-yjs-server
  ports:
    - '0.0.0.0:1234:1234'
  restart: unless-stopped
  networks:
    - pm-network
```

### 服务管理

```bash
# 启动服务
docker-compose -f docker-compose-prod.yml up -d yjs-server

# 查看状态
docker-compose -f docker-compose-prod.yml ps yjs-server

# 查看日志
docker-compose -f docker-compose-prod.yml logs -f yjs-server

# 重启服务
docker-compose -f docker-compose-prod.yml restart yjs-server

# 停止服务
docker-compose -f docker-compose-prod.yml stop yjs-server
```

### 健康检查

```bash
curl http://localhost:1234
# 应返回: {"status":"ok","service":"Yjs WebSocket Collaboration Server",...}
```

### 详细文档

查看完整部署文档：`../yjs-collab-server/DOCKER_DEPLOY.md`

---

## 📞 获取支持

- **项目文档**: 查看 `../README.md`
- **API 文档**: http://localhost:8000/docs
- **Yjs 文档**: `../yjs-collab-server/DOCKER_DEPLOY.md`
- **问题反馈**: 查看项目 issue 或联系管理员

---

## 📝 版本说明

- **v1.0** - 初始版本，支持 Dockerfile 构建
- **v2.0** - 新增 TAR 镜像部署方式
- **v3.0** - 添加自动化部署脚本
- **v3.1** - 完善文档和健康检查

---

**选择适合你的部署方式，开始使用吧！** 🚀
