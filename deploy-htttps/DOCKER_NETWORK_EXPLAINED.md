# Docker 网络与端口映射详解

## 🤔 问题：使用 Bridge 网络还能通过 IP 访问吗？

**答案：可以！**

Bridge 网络和 IP 访问是两个独立的概念，它们**协同工作**而非互相排斥。

---

## 📊 网络架构图

```
                    局域网其他设备
                    (192.168.200.10)
                            │
                            │ ① 通过 IP 访问
                            ↓
                ┌─────────────────────────┐
                │   宿主机 (服务器)         │
                │   IP: 192.168.200.20    │
                │                         │
                │   ② 端口映射             │
                │   0.0.0.0:80 → 容器:80  │
                │                         │
                │ ┌─────────────────────┐ │
                │ │  Docker Bridge 网络  │ │
                │ │  (pm-network)       │ │
                │ │                     │ │
                │ │  ┌──────────────┐   │ │
                │ │  │  Frontend    │   │ │
                │ │  │  :80         │   │ │
                │ │  └──────┬───────┘   │ │
                │ │         │           │ │
                │ │         │ ③ 容器间   │ │
                │ │         │   通信     │ │
                │ │         ↓           │ │
                │ │  ┌──────────────┐   │ │
                │ │  │  Backend     │   │ │
                │ │  │  :8000       │   │ │
                │ │  └──────┬───────┘   │ │
                │ │         │           │ │
                │ │         ↓           │ │
                │ │  ┌──────────────┐   │ │
                │ │  │  PostgreSQL  │   │ │
                │ │  │  :5432       │   │ │
                │ │  └──────────────┘   │ │
                │ └─────────────────────┘ │
                └─────────────────────────┘
```

---

## 🔑 两个关键概念

### 1️⃣ Bridge 网络（容器内部通信）

**作用范围：** Docker 内部

**配置：**

```yaml
networks:
  pm-network:
    driver: bridge # 容器间通信
```

**效果：**

- ✅ `pm-backend` 可以访问 `postgres`（通过容器名）
- ✅ `pm-frontend` 可以访问 `pm-backend`（通过容器名）
- ✅ 容器之间形成一个**虚拟局域网**
- ❌ 外部**无法直接访问**这个网络

**类比：** 就像一个封闭的办公室内部局域网，员工之间可以互相访问，但外人进不来。

---

### 2️⃣ 端口映射（暴露到外部）

**作用范围：** 宿主机 → Docker 容器

**配置：**

```yaml
frontend:
  ports:
    - '0.0.0.0:80:80' # 端口映射
    #   ^^^^^^^ ^^
    #   宿主机   容器
```

**效果：**

- ✅ 将容器的 80 端口映射到宿主机的 80 端口
- ✅ `0.0.0.0` 表示监听**所有网络接口**（包括局域网）
- ✅ 外部可以通过宿主机 IP 访问容器服务
- ✅ 这是**打通内外的桥梁**

**类比：** 就像办公室的前台接待，虽然办公室是封闭的，但前台可以接待外来访客并引导到相应部门。

---

## 🎯 在你的配置中

### docker-compose-prod.yml 解析

```yaml
services:
  frontend:
    image: deploy-https-frontend:v1.0
    container_name: pm-frontend

    # ① Bridge 网络配置（容器间通信）
    networks:
      - pm-network # 加入内部网络，可以访问其他容器

    # ② 端口映射配置（对外暴露）
    ports:
      - '0.0.0.0:80:80' # 暴露到局域网
      - '0.0.0.0:443:443' # 暴露到局域网

  backend:
    image: deploy-https-backend:v1.0
    container_name: pm-backend

    # ① 同样加入内部网络
    networks:
      - pm-network

    # ② 暴露 API 端口
    ports:
      - '0.0.0.0:8000:8000'

    # ③ 环境变量使用容器名（因为在同一 bridge 网络）
    environment:
      DATABASE_URL: postgresql://admin:password123@postgres:5432/...
      #                                             ^^^^^^^^
      #                                             容器名（不是 IP）
      REDIS_URL: redis://redis:6379
      #                  ^^^^^
      #                  容器名

  postgres:
    image: deploy-https-postgres:v1.0
    container_name: pm-postgres

    # ① 加入内部网络
    networks:
      - pm-network

    # ② 端口映射（可选，用于外部工具连接）
    ports:
      - '0.0.0.0:5432:5432'

# 定义 bridge 网络
networks:
  pm-network:
    driver: bridge # 这只影响容器间如何通信
```

---

## 🚀 数据流向示例

### 场景1: 局域网访问前端

```
1. 用户在手机浏览器输入: http://192.168.200.20
   ↓
2. 请求到达服务器的 80 端口（宿主机网络接口）
   ↓
3. 通过端口映射 "0.0.0.0:80:80"
   ↓
4. 转发到 pm-frontend 容器的 80 端口
   ↓
5. Nginx 返回前端页面
```

**关键点：**

- Bridge 网络在这里**不起作用**
- 起作用的是**端口映射**（`ports`）
- `0.0.0.0` 确保了可以从局域网访问

---

### 场景2: 前端调用后端 API

```
1. 前端 JavaScript 发起请求: fetch('http://192.168.200.20:8000/api/...')
   ↓
2. 请求到达服务器的 8000 端口
   ↓
3. 通过端口映射 "0.0.0.0:8000:8000"
   ↓
4. 转发到 pm-backend 容器的 8000 端口
   ↓
5. Backend 返回数据
```

---

### 场景3: Backend 访问数据库

```
1. Backend 代码: connect('postgresql://...@postgres:5432/...')
                                          ^^^^^^^^
                                          使用容器名
   ↓
2. Docker 内部 DNS 解析 "postgres" → 容器 IP (如 172.18.0.3)
   ↓
3. 通过 Bridge 网络（pm-network）直接连接
   ↓
4. 到达 pm-postgres 容器的 5432 端口
```

**关键点：**

- 这里**不经过宿主机**
- 完全在 Bridge 网络内部通信
- 不需要端口映射也能访问
- 使用容器名而非 IP（自动解析）

---

## 🔍 端口映射的三种写法

### 写法1: 监听所有接口（推荐用于前端）

```yaml
ports:
  - '0.0.0.0:80:80'
```

**效果：**

- ✅ 本机可访问（localhost:80）
- ✅ 局域网可访问（192.168.200.20:80）
- ✅ 外网可访问（如果有公网 IP）

---

### 写法2: 仅监听本机

```yaml
ports:
  - '127.0.0.1:5432:5432'
```

**效果：**

- ✅ 本机可访问（localhost:5432）
- ❌ 局域网**不能**访问
- ❌ 外网**不能**访问

**适用场景：** 数据库等敏感服务，只允许本机管理

---

### 写法3: 简写形式（等同于 0.0.0.0）

```yaml
ports:
  - '80:80'
```

**效果：** 与 `"0.0.0.0:80:80"` 相同

---

## 🧪 实验验证

### 实验1: 查看 Bridge 网络

```bash
# 查看网络列表
docker network ls

# 查看 pm-network 详情
docker network inspect project_maneger_pm-network

# 输出示例：
# {
#   "Name": "project_maneger_pm-network",
#   "Driver": "bridge",
#   "Containers": {
#     "pm-frontend": { "IPv4Address": "172.18.0.2/16" },
#     "pm-backend":  { "IPv4Address": "172.18.0.3/16" },
#     "pm-postgres": { "IPv4Address": "172.18.0.4/16" }
#   }
# }
```

**发现：**

- 容器在 `172.18.0.x` 网段（Docker 内部）
- 这个网段**与宿主机网络（192.168.200.x）不同**

---

### 实验2: 验证容器间通信

```bash
# 进入 backend 容器
docker exec -it pm-backend bash

# 测试访问其他容器（通过容器名）
curl postgres:5432  # ✅ 可以连接
curl redis:6379     # ✅ 可以连接

# 测试访问宿主机（通过 host.docker.internal）
curl host.docker.internal:80  # ✅ 可以访问宿主机端口

exit
```

---

### 实验3: 验证外部访问

```bash
# 在服务器本地测试
curl http://localhost:80      # ✅ 通过端口映射访问
curl http://192.168.200.20:80 # ✅ 通过局域网 IP 访问

# 在其他设备测试
curl http://192.168.200.20:80 # ✅ 通过局域网访问
```

---

## 📋 常见误区

### ❌ 误区1: Bridge 网络会阻止外部访问

**错误理解：**

> "使用 bridge 网络后，容器就在一个封闭网络里，外部无法访问"

**正确理解：**

> Bridge 网络只影响容器**之间**的通信，不影响通过端口映射从外部访问

---

### ❌ 误区2: 必须用 host 网络才能被访问

**错误理解：**

> "要让局域网访问，必须使用 `network_mode: host`"

**正确理解：**

> 只需要正确配置端口映射即可，`bridge` 网络完全支持

```yaml
# ✅ 正确 - 使用 bridge + 端口映射
networks:
  - pm-network
ports:
  - '0.0.0.0:80:80'

# ❌ 不推荐 - 使用 host 模式
network_mode: host # 失去网络隔离，安全性降低
```

---

### ❌ 误区3: 容器名只能在容器内使用

**错误理解：**

> "容器名（如 postgres）只能在 Docker 内部使用，外部必须用 IP"

**正确理解：**

- 容器名 → 容器内部使用 ✅
- IP:端口 → 外部访问使用 ✅

```yaml
# Backend 容器内访问数据库
DATABASE_URL: postgresql://...@postgres:5432/... # ✅ 用容器名

# 外部工具（如 Navicat）连接数据库
Host: 192.168.200.20 # ✅ 用宿主机 IP
Port: 5432 # ✅ 用映射后的端口
```

---

## 🎯 最佳实践

### 推荐配置（安全性 + 可访问性）

```yaml
services:
  # 前端 - 完全开放到局域网
  frontend:
    ports:
      - '0.0.0.0:80:80' # ✅ 公开访问
      - '0.0.0.0:443:443' # ✅ 公开访问
    networks:
      - pm-network

  # 后端 - 通过前端 Nginx 代理（推荐）或直接暴露
  backend:
    ports:
      - '0.0.0.0:8000:8000' # ⚠️ 可选：直接暴露 API
      # 或不写 ports，只通过 Nginx 代理访问
    networks:
      - pm-network

  # 数据库 - 仅本机访问（安全）
  postgres:
    ports:
      - '127.0.0.1:5432:5432' # ✅ 仅本机，防止直接暴露
    networks:
      - pm-network

  # Redis - 不暴露端口（最安全）
  redis:
    # 不写 ports，只能容器间访问
    networks:
      - pm-network

  # MinIO - 仅本机访问
  minio:
    ports:
      - '127.0.0.1:9000:9000' # ✅ 仅本机
      - '127.0.0.1:9001:9001' # ✅ 仅本机
    networks:
      - pm-network

networks:
  pm-network:
    driver: bridge # ✅ 容器间通信
```

---

## 💡 总结

### 关键要点

1. **Bridge 网络** 和 **端口映射** 是两个独立的概念

   - Bridge 网络 → 容器**内部**通信
   - 端口映射 → 容器**对外**暴露

2. **可以同时使用**

   - ✅ 容器加入 bridge 网络（容器间通信）
   - ✅ 同时映射端口（对外提供服务）

3. **`0.0.0.0` 是关键**

   - `0.0.0.0:80:80` → 局域网可访问 ✅
   - `127.0.0.1:80:80` → 仅本机可访问 ❌

4. **你的配置完全正确**
   ```yaml
   ports:
     - '0.0.0.0:80:80' # ✅ 已经可以从局域网访问
   networks:
     - pm-network # ✅ 容器间可以互相通信
   ```

---

## 🔗 数据流总结

```
外部访问流程（局域网 → 容器）:
  局域网设备 → 宿主机 IP:端口 → 端口映射 → 容器服务
  ✅ 与 bridge 网络无关

容器间通信流程（容器 → 容器）:
  容器A → Bridge 网络 → 容器B
  ✅ 不需要端口映射
  ✅ 使用容器名直接访问
```

---

**你的配置使用 Bridge 网络 + 端口映射，完全支持局域网访问！** 🎉
