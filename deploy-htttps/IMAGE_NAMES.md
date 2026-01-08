# 镜像名称配置指南

## 📋 当前配置的镜像名称

根据你的实际镜像名称，修改 `docker-compose-prod.yml` 中的镜像配置：

### Backend 镜像

```yaml
backend:
  image: deploy-https-backend:v1.0 # ✅ 已配置
```

### PostgreSQL 镜像

```yaml
postgres:
  # 选项1: 使用你打包的镜像
  image: deploy-https-postgres:v1.0

  # 选项2: 使用官方镜像（推荐）
  image: postgres:16-alpine
```

### Redis 镜像

```yaml
redis:
  # 选项1: 使用你打包的镜像
  image: deploy-https-redis:v1.0

  # 选项2: 使用官方镜像（推荐）
  image: redis:7-alpine
```

### MinIO 镜像

```yaml
minio:
  # 选项1: 使用你打包的镜像
  image: deploy-https-minio:v1.0

  # 选项2: 使用官方镜像（推荐）
  image: minio/minio:RELEASE.2024-09-22T00-33-43Z
```

---

## 🔧 快速配置

### 场景1: 只打包了 Backend 镜像

**适用情况：** 你只自定义了 Backend 服务，其他服务使用官方镜像

**配置：**

```yaml
services:
  postgres:
    image: postgres:16-alpine # 官方镜像

  redis:
    image: redis:7-alpine # 官方镜像

  minio:
    image: minio/minio:RELEASE.2024-09-22T00-33-43Z # 官方镜像

  backend:
    image: deploy-https-backend:v1.0 # 你的镜像
```

**加载命令：**

```bash
# 只需加载 Backend 镜像
docker load -i deploy-https-backend-v1.0.tar
docker-compose -f docker-compose-prod.yml up -d
```

---

### 场景2: 打包了所有服务镜像

**适用情况：** 生产环境完全离线，需要所有镜像都打包

**配置：**

```yaml
services:
  postgres:
    image: deploy-https-postgres:v1.0

  redis:
    image: deploy-https-redis:v1.0

  minio:
    image: deploy-https-minio:v1.0

  backend:
    image: deploy-https-backend:v1.0
```

**加载命令：**

```bash
# 加载所有镜像
docker load -i deploy-https-postgres-v1.0.tar
docker load -i deploy-https-redis-v1.0.tar
docker load -i deploy-https-minio-v1.0.tar
docker load -i deploy-https-backend-v1.0.tar

docker-compose -f docker-compose-prod.yml up -d
```

---

## 📦 镜像打包命令参考

### 打包官方镜像（供离线环境使用）

```bash
# PostgreSQL
docker pull postgres:16-alpine
docker tag postgres:16-alpine deploy-https-postgres:v1.0
docker save -o deploy-https-postgres-v1.0.tar deploy-https-postgres:v1.0

# Redis
docker pull redis:7-alpine
docker tag redis:7-alpine deploy-https-redis:v1.0
docker save -o deploy-https-redis-v1.0.tar deploy-https-redis:v1.0

# MinIO
docker pull minio/minio:RELEASE.2024-09-22T00-33-43Z
docker tag minio/minio:RELEASE.2024-09-22T00-33-43Z deploy-https-minio:v1.0
docker save -o deploy-https-minio-v1.0.tar deploy-https-minio:v1.0

# Backend (从 Dockerfile 构建)
docker build -t deploy-https-backend:v1.0 -f backend/Dockerfile .
docker save -o deploy-https-backend-v1.0.tar deploy-https-backend:v1.0
```

---

## 🔄 版本管理建议

### 命名规范

```
项目名-服务名:版本号

例如：
deploy-https-backend:v1.0    # 第一版
deploy-https-backend:v1.1    # 小版本更新
deploy-https-backend:v2.0    # 大版本更新
```

### 更新流程

**开发环境：**

```bash
# 1. 修改代码
# 2. 构建新版本
docker build -t deploy-https-backend:v1.1 -f backend/Dockerfile .

# 3. 保存镜像
docker save -o deploy-https-backend-v1.1.tar deploy-https-backend:v1.1
```

**生产环境：**

```bash
# 1. 停止服务
docker-compose -f docker-compose-prod.yml down

# 2. 加载新镜像
docker load -i deploy-https-backend-v1.1.tar

# 3. 修改 docker-compose-prod.yml
# 将 image: deploy-https-backend:v1.0
# 改为 image: deploy-https-backend:v1.1

# 4. 启动服务
docker-compose -f docker-compose-prod.yml up -d
```

---

## 📝 当前镜像清单

请根据你的实际情况填写：

| 服务 | 镜像名称 | TAR 文件名 | 大小 | 状态 |
| --- | --- | --- | --- | --- |
| Backend | `deploy-https-backend:v1.0` | `deploy-https-backend-v1.0.tar` | ? MB | ✅ 已打包 |
| PostgreSQL | `deploy-https-postgres:v1.0` 或 `postgres:16-alpine` | `deploy-https-postgres-v1.0.tar` | ? MB | ❓ 待确认 |
| Redis | `deploy-https-redis:v1.0` 或 `redis:7-alpine` | `deploy-https-redis-v1.0.tar` | ? MB | ❓ 待确认 |
| MinIO | `deploy-https-minio:v1.0` 或 `minio/minio:...` | `deploy-https-minio-v1.0.tar` | ? MB | ❓ 待确认 |

---

## ⚙️ 批量操作脚本

### 批量加载所有镜像（Linux/Mac）

```bash
#!/bin/bash
echo "开始加载所有镜像..."

IMAGES=(
    "deploy-https-postgres-v1.0.tar"
    "deploy-https-redis-v1.0.tar"
    "deploy-https-minio-v1.0.tar"
    "deploy-https-backend-v1.0.tar"
)

for img in "${IMAGES[@]}"; do
    if [ -f "$img" ]; then
        echo "加载: $img"
        docker load -i "$img"
    else
        echo "警告: 未找到 $img"
    fi
done

echo "镜像加载完成！"
docker images | grep "deploy-https"
```

### 批量加载所有镜像（Windows）

```batch
@echo off
echo 开始加载所有镜像...

set "IMAGES=deploy-https-postgres-v1.0.tar deploy-https-redis-v1.0.tar deploy-https-minio-v1.0.tar deploy-https-backend-v1.0.tar"

for %%i in (%IMAGES%) do (
    if exist "%%i" (
        echo 加载: %%i
        docker load -i "%%i"
    ) else (
        echo 警告: 未找到 %%i
    )
)

echo 镜像加载完成！
docker images | findstr "deploy-https"
pause
```

---

## 💡 建议

### 推荐配置（最佳实践）

**只打包 Backend：**

- ✅ Backend 使用自定义镜像（包含你的代码和配置）
- ✅ PostgreSQL/Redis/MinIO 使用官方镜像（稳定可靠）

**优点：**

- 镜像文件更小（只打包必要的 Backend）
- 官方镜像更稳定、更新及时
- 减少维护成本

**缺点：**

- 生产环境需要能访问 Docker Hub（或提前拉取官方镜像）

---

### 全部打包（离线部署）

**所有服务都打包：**

- ✅ 完全离线部署
- ✅ 版本一致性更好

**优点：**

- 完全不依赖外网
- 版本完全可控

**缺点：**

- 镜像文件更大
- 更新维护成本更高

---

## ❓ 常见问题

### Q1: 如何查看已加载的镜像？

```bash
docker images | grep "deploy-https"
```

### Q2: 镜像名称写错了怎么办？

```bash
# 重新 tag
docker tag deploy-https-backend:v1.0 correct-name:v1.0

# 删除错误的 tag
docker rmi deploy-https-backend:v1.0
```

### Q3: 如何验证镜像是否正常？

```bash
# 查看镜像详情
docker inspect deploy-https-backend:v1.0

# 测试运行
docker run --rm deploy-https-backend:v1.0 python --version
```

---

**请根据你的实际情况，修改 `docker-compose-prod.yml` 中的镜像名称！** 📝
