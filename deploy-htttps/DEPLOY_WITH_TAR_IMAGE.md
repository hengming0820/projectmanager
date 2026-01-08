# 使用 TAR 镜像部署生产环境指南

## 📋 概述

本指南说明如何使用预先打包的 Docker 镜像（tar 文件）在生产环境部署系统。

---

## 🔧 开发环境：打包镜像

### 1. 构建 Backend 镜像

```bash
# 在项目根目录执行
cd /path/to/project_manager

# 构建镜像
docker build -t pm-backend:latest -f backend/Dockerfile .

# 或者如果已经在运行，可以从容器创建镜像
docker commit pm-backend2 pm-backend:latest
```

### 2. 保存镜像为 TAR 文件

```bash
# 保存镜像
docker save -o pm-backend-latest.tar pm-backend:latest

# 检查文件
ls -lh pm-backend-latest.tar
```

### 3. 打包前端文件（如果需要）

```bash
# 构建前端
npm run build

# 打包 dist 目录
tar -czf dist.tar.gz dist/
```

### 4. 打包配置文件

```bash
# 创建部署包目录
mkdir -p deploy-package

# 复制必要文件
cp pm-backend-latest.tar deploy-package/
cp dist.tar.gz deploy-package/
cp -r deploy-htttps deploy-package/
cp -r deploy/db-init deploy-package/

# 打包所有文件
tar -czf medical-annotation-deploy.tar.gz deploy-package/
```

---

## 🚀 生产环境：部署步骤

### 1. 传输文件到生产服务器

```bash
# 方式1：使用 scp
scp medical-annotation-deploy.tar.gz user@production-server:/opt/

# 方式2：使用 rsync
rsync -avz medical-annotation-deploy.tar.gz user@production-server:/opt/

# 方式3：使用 U盘/移动硬盘
# 直接拷贝到生产服务器
```

### 2. 解压部署包

```bash
# SSH 登录到生产服务器
ssh user@production-server

# 进入部署目录
cd /opt

# 解压部署包
tar -xzf medical-annotation-deploy.tar.gz
cd deploy-package

# 解压前端文件
tar -xzf dist.tar.gz
```

### 3. 加载 Docker 镜像

```bash
# 加载 backend 镜像
docker load -i pm-backend-latest.tar

# 验证镜像已加载
docker images | grep pm-backend
# 应该看到：pm-backend   latest   xxxxx   xxx MB
```

### 4. 配置环境变量（可选）

```bash
# 编辑 docker-compose-prod.yml 中的环境变量
cd deploy-htttps
nano docker-compose-prod.yml

# 修改敏感信息：
# - POSTGRES_PASSWORD
# - MINIO_ROOT_PASSWORD
# - JWT_SECRET
# - ALLOWED_ORIGINS（添加生产域名）
```

### 5. 启动服务

```bash
# 使用生产配置启动
docker-compose -f docker-compose-prod.yml up -d

# 查看日志
docker-compose -f docker-compose-prod.yml logs -f

# 查看服务状态
docker-compose -f docker-compose-prod.yml ps
```

### 6. 验证部署

```bash
# 检查 backend 健康状态
curl http://localhost:8000/docs

# 检查数据库连接
docker exec pm-backend2 python -c "from app.database import engine; engine.connect()"

# 检查前端访问
curl http://localhost
curl https://localhost  # 如果配置了 HTTPS
```

---

## 📝 docker-compose-prod.yml 关键变化

### 对比原版本的主要修改

```yaml
# 原版（开发环境）
backend:
  build:
    context: ..
    dockerfile: backend/Dockerfile
  volumes:
    - ../backend/app:/app/app:ro  # 挂载源码

# 新版（生产环境）
backend:
  image: pm-backend:latest  # ✅ 使用已加载的镜像
  volumes:
    - ../uploads:/app/uploads  # ✅ 只挂载数据目录
  healthcheck:  # ✅ 添加健康检查
    test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
    interval: 30s
```

### 新增配置

1. **移除 build 配置** - 使用 `image` 替代
2. **移除代码挂载** - 代码已打包在镜像中
3. **添加 healthcheck** - 自动健康检查
4. **添加 networks** - 更好的网络隔离
5. **优化环境变量** - 生产环境专用配置

---

## 🔄 更新镜像流程

### 当需要更新 Backend 代码时

**开发环境：**

```bash
# 1. 修改代码
# 2. 重新构建镜像
docker build -t pm-backend:latest -f backend/Dockerfile .

# 3. 保存新镜像
docker save -o pm-backend-latest-v2.tar pm-backend:latest

# 4. 传输到生产环境
scp pm-backend-latest-v2.tar user@production-server:/opt/
```

**生产环境：**

```bash
# 1. 停止当前服务
cd /opt/deploy-package/deploy-htttps
docker-compose -f docker-compose-prod.yml down

# 2. 加载新镜像（会覆盖旧镜像）
docker load -i /opt/pm-backend-latest-v2.tar

# 3. 启动服务
docker-compose -f docker-compose-prod.yml up -d

# 4. 查看日志确认启动成功
docker-compose -f docker-compose-prod.yml logs -f backend
```

---

## 🛠️ 常用命令

### 服务管理

```bash
# 进入部署目录
cd /opt/deploy-package/deploy-htttps

# 启动所有服务
docker-compose -f docker-compose-prod.yml up -d

# 停止所有服务
docker-compose -f docker-compose-prod.yml down

# 重启某个服务
docker-compose -f docker-compose-prod.yml restart backend

# 查看服务状态
docker-compose -f docker-compose-prod.yml ps

# 查看日志
docker-compose -f docker-compose-prod.yml logs -f backend
docker-compose -f docker-compose-prod.yml logs -f frontend

# 进入容器
docker exec -it pm-backend2 bash
docker exec -it pm-postgres2 psql -U admin -d medical_annotation
```

### 镜像管理

```bash
# 查看已加载的镜像
docker images

# 删除旧镜像（释放空间）
docker image prune -a

# 查看镜像详情
docker inspect pm-backend:latest

# 查看镜像历史
docker history pm-backend:latest
```

### 数据备份

```bash
# 备份数据库
docker exec pm-postgres2 pg_dump -U admin medical_annotation > backup_$(date +%Y%m%d).sql

# 备份 uploads 目录
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz ../uploads/

# 备份 MinIO 数据
docker exec pm-minio2 mc alias set local http://localhost:9000 minioadmin minioadmin123
docker exec pm-minio2 mc mirror local/medical-annotations /backup/
```

---

## 🔐 安全建议

### 1. 修改默认密码

```yaml
# docker-compose-prod.yml
environment:
  POSTGRES_PASSWORD: <strong-password-here>
  MINIO_ROOT_PASSWORD: <strong-password-here>
  JWT_SECRET: <generate-random-secret>
```

### 2. 限制端口暴露

```yaml
# 只对内网开放数据库端口
ports:
  - '127.0.0.1:5432:5432' # 只允许本地访问
```

### 3. 使用环境变量文件

```bash
# 创建 .env 文件
cat > .env << EOF
POSTGRES_PASSWORD=your-secure-password
MINIO_ROOT_PASSWORD=your-secure-password
JWT_SECRET=your-jwt-secret
EOF

# 在 docker-compose 中引用
env_file:
  - .env
```

---

## 📊 监控和维护

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a
```

### 日志管理

```bash
# 限制日志大小（在 docker-compose 中添加）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## ❓ 常见问题

### Q1: 镜像加载后找不到？

**A:** 检查镜像名称和标签

```bash
docker images
# 确认镜像名称是 pm-backend:latest
# 如果不是，需要重新 tag
docker tag <实际镜像名> pm-backend:latest
```

### Q2: 容器启动失败？

**A:** 检查日志

```bash
docker-compose -f docker-compose-prod.yml logs backend
# 查看具体错误信息
```

### Q3: 数据库连接失败？

**A:** 检查网络和依赖

```bash
# 确保 postgres 容器已启动
docker-compose -f docker-compose-prod.yml ps

# 测试数据库连接
docker exec pm-postgres2 psql -U admin -d medical_annotation -c "SELECT 1"
```

### Q4: 前端访问 API 失败？

**A:** 检查 CORS 配置

```yaml
# 确保 ALLOWED_ORIGINS 包含前端域名
ALLOWED_ORIGINS: '["https://your-domain.com"]'
```

---

## 📚 相关文档

- `docker-compose-prod.yml` - 生产环境配置文件
- `docker-compose.yml` - 开发环境配置文件
- `../README.md` - 项目总体说明
- `INTRANET_HTTPS.md` - HTTPS 配置指南

---

## ✅ 部署检查清单

部署前请确认：

- [ ] 已在开发环境构建并打包镜像
- [ ] 已传输所有必要文件到生产服务器
- [ ] 已加载 Docker 镜像（`docker images` 可见）
- [ ] 已修改敏感配置（密码、密钥）
- [ ] 已配置 CORS（添加生产域名）
- [ ] 已准备 SSL 证书（如使用 HTTPS）
- [ ] 已解压前端 dist 文件
- [ ] 已测试数据库连接
- [ ] 已检查防火墙规则
- [ ] 已配置日志限制

部署后请验证：

- [ ] 所有容器正常运行（`docker-compose ps`）
- [ ] Backend API 可访问（`/docs` 端点）
- [ ] 前端页面正常加载
- [ ] 登录功能正常
- [ ] 数据库连接正常
- [ ] 文件上传功能正常（MinIO）
- [ ] WebSocket 连接正常（如有）
- [ ] HTTPS 证书有效（如配置）

---

**部署完成！** 🎉

如有问题，请查看日志：

```bash
docker-compose -f docker-compose-prod.yml logs -f
```
