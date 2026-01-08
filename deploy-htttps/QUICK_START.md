# 生产环境快速启动指南

## 🚀 快速开始（3 步部署）

### 1️⃣ 加载镜像

```bash
# Linux/Mac
docker load -i pm-backend-latest.tar

# Windows
docker load -i pm-backend-latest.tar
```

### 2️⃣ 启动服务

```bash
# Linux/Mac
cd deploy-htttps
chmod +x load-and-start.sh
./load-and-start.sh

# 或手动启动
docker-compose -f docker-compose-prod.yml up -d
```

```cmd
REM Windows
cd deploy-htttps
load-and-start.bat

REM 或手动启动
docker-compose -f docker-compose-prod.yml up -d
```

### 3️⃣ 访问系统

- **前端**: http://localhost 或 https://localhost
- **API 文档**: http://localhost:8000/docs
- **MinIO 控制台**: http://localhost:9001

---

## 📋 文件清单

部署前确保有以下文件：

```
deploy-htttps/
├── docker-compose-prod.yml      # ✅ 生产环境配置
├── pm-backend-latest.tar        # ✅ Backend 镜像
├── nginx/
│   └── default.conf             # ✅ Nginx 配置
├── ssl/                         # ⚠️  SSL 证书（如使用 HTTPS）
│   ├── cert.pem
│   └── key.pem
└── load-and-start.sh            # 🔧 启动脚本

dist/                            # ✅ 前端构建文件
deploy/db-init/                  # ✅ 数据库初始化脚本
uploads/                         # 📁 上传文件目录（可选）
```

---

## 🔧 常用命令

### 服务管理

```bash
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
```

### 健康检查

```bash
# 检查所有容器
docker ps

# 检查 Backend API
curl http://localhost:8000/docs

# 检查数据库
docker exec pm-postgres2 pg_isready -U admin

# 检查 Redis
docker exec pm-redis2 redis-cli ping
```

### 数据备份

```bash
# 备份数据库
docker exec pm-postgres2 pg_dump -U admin medical_annotation > backup.sql

# 备份上传文件
tar -czf uploads_backup.tar.gz ../uploads/
```

---

## 🔐 安全配置

### 必须修改的默认密码

编辑 `docker-compose-prod.yml`：

```yaml
# 1. 数据库密码
POSTGRES_PASSWORD: your-strong-password-here

# 2. MinIO 密码
MINIO_ROOT_PASSWORD: your-strong-password-here

# 3. JWT 密钥
JWT_SECRET: your-random-secret-key-here

# 4. CORS 配置（添加生产域名）
ALLOWED_ORIGINS: '["https://your-domain.com"]'
```

---

## ❓ 故障排查

### 问题1: 容器无法启动

```bash
# 查看详细日志
docker-compose -f docker-compose-prod.yml logs backend

# 检查端口占用
netstat -an | grep 8000
```

### 问题2: 前端无法访问 API

```bash
# 检查 CORS 配置
docker exec pm-backend2 env | grep ALLOWED_ORIGINS

# 检查网络连接
docker exec pm-frontend2 ping backend
```

### 问题3: 数据库连接失败

```bash
# 检查数据库状态
docker exec pm-postgres2 pg_isready -U admin

# 查看数据库日志
docker-compose -f docker-compose-prod.yml logs postgres
```

---

## 📞 获取帮助

- **详细文档**: 查看 `DEPLOY_WITH_TAR_IMAGE.md`
- **配置说明**: 查看 `docker-compose-prod.yml`
- **项目文档**: 查看 `../README.md`

---

## ⚡ 一键命令

### 完整部署流程

```bash
# 1. 加载镜像并启动（自动化脚本）
./load-and-start.sh pm-backend-latest.tar

# 2. 检查状态
docker-compose -f docker-compose-prod.yml ps

# 3. 查看日志
docker-compose -f docker-compose-prod.yml logs -f
```

### 更新镜像

```bash
# 1. 停止服务
docker-compose -f docker-compose-prod.yml down

# 2. 加载新镜像
docker load -i pm-backend-latest-v2.tar

# 3. 启动服务
docker-compose -f docker-compose-prod.yml up -d
```

---

**🎉 部署完成，开始使用！**
