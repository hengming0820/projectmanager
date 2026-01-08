# Redis通知系统快速修复指南 🚀

> **针对问题**：17:10定时通知不保存给离线用户，缺少过期时间策略

## 🔴 核心问题

1. **定时通知只发给在线用户**：17:10下班提醒用`broadcast_to_all()`，不保存到Redis
2. **所有通知统一7天TTL**：没有针对性的过期策略
3. **通知会累积**：用户长期离线会收到大量过时通知

---

## ✅ 快速修复方案（30分钟内完成）

### 步骤1：修复定时通知的离线保存

编辑 `backend/app/services/notification_ws.py`：

```python
# backend/app/services/notification_ws.py

async def broadcast_to_all(
    self, 
    message: dict, 
    save_offline: bool = False  # ✅ 新增参数
) -> None:
    """
    广播消息给所有在线用户
    
    Args:
        message: 消息内容
        save_offline: 是否保存给离线用户（默认False，兼容旧代码）
    """
    # ✅ 1. 如果需要保存给离线用户
    if save_offline:
        try:
            from app.database import get_db
            from app.models.user import User
            
            db = next(get_db())
            try:
                # 获取所有活跃用户
                users = db.query(User).filter(User.is_active == True).all()
                
                logger.info(f"💾 [Redis] 开始保存定时通知给 {len(users)} 个活跃用户")
                
                # 批量保存通知
                for user in users:
                    self._save_notification_to_redis(str(user.id), message)
                
                logger.info(f"✅ [Redis] 定时通知已保存给 {len(users)} 个用户")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"❌ [Redis] 批量保存通知失败: {e}", exc_info=True)
    
    # 2. 实时推送给在线用户（原有逻辑保持不变）
    if self.redis_enabled:
        receivers = redis_notifier.publish_global(message)
        logger.info(f"🔔 [Redis] 全局广播消息，Redis订阅者: {receivers}")
        if receivers > 0:
            return
    
    # 3. Redis不可用时，直接WebSocket发送
    dead: Set[WebSocket] = set()
    total = len(self.active_connections)
    sent = 0
    logger.info(f"🔔 [WS] 开始向所有在线用户直接广播，当前连接数: {total}")
    
    for ws in list(self.active_connections):
        try:
            await ws.send_json(message)
            sent += 1
        except Exception as e:
            user_info = self.ws_user.get(ws, {})
            username = user_info.get('username') or user_info.get('real_name') or 'unknown'
            logger.warning(f"🔔 [WS] 广播到用户 {username} 失败: {e}")
            dead.add(ws)
    
    # 清理失败的连接
    for ws in dead:
        self.disconnect(ws)
    
    logger.info(f"🔔 [WS] 直接广播完成，成功: {sent}/{total}，失败: {len(dead)}")
```

### 步骤2：修改定时任务调用

编辑 `backend/app/services/scheduler_service.py`：

```python
# backend/app/services/scheduler_service.py

def _send_work_end_reminder(self):
    """发送下班提醒（保存给所有用户）"""
    try:
        logger.info("⏰ [Scheduler] 开始执行下班提醒任务")
        
        message = {
            "type": "work_end_reminder",
            "title": "🏃 下班提醒",
            "content": "请及时保存文件，填写好今天的工作日志，下班请关电脑！",
            "timestamp": utc_now().isoformat(),
            "priority": "high",
            "category": "daily_reminder"  # ✅ 方便后续分类
        }
        
        # 在事件循环中执行异步广播
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast_to_all(
                    message,
                    save_offline=True  # ✅ 保存给离线用户
                ),
                self._loop
            )
            logger.info("✅ [Scheduler] 下班提醒已发送并保存给所有用户")
        else:
            logger.warning("⚠️ [Scheduler] 事件循环未运行，无法发送通知")
            
    except Exception as e:
        logger.error(f"❌ [Scheduler] 发送下班提醒失败: {e}", exc_info=True)
```

### 步骤3：实现分级TTL策略

编辑 `backend/app/services/redis_notification_storage.py`：

```python
# backend/app/services/redis_notification_storage.py

class RedisNotificationStorage:
    """Redis 通知存储服务"""
    
    def __init__(self):
        # ... 原有初始化代码 ...
        
        # ✅ 新增：不同类型通知的TTL（秒）
        self.NOTIFICATION_TTL_MAP = {
            "work_end_reminder": 12 * 60 * 60,      # 12小时（当天有效）
            "task_assigned": 3 * 24 * 60 * 60,      # 3天
            "task_completed": 1 * 24 * 60 * 60,     # 1天
            "task_due_soon": 2 * 24 * 60 * 60,      # 2天
            "system_announcement": 7 * 24 * 60 * 60,  # 7天
            "urgent": 6 * 60 * 60,                   # 6小时
            "default": 7 * 24 * 60 * 60              # 默认7天
        }
    
    def save_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        content: str,
        data: Optional[Dict] = None,
        priority: str = "normal",
        custom_ttl: Optional[int] = None  # ✅ 允许自定义TTL
    ) -> bool:
        """保存通知到 Redis，支持分级TTL"""
        if not self.enabled:
            logger.warning(f"⚠️ Redis不可用，无法保存通知")
            return False
        
        try:
            notification = {
                "id": str(uuid.uuid4()),
                "type": notification_type,
                "title": title,
                "content": content,
                "data": data or {},
                "priority": priority,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "created_at": datetime.now().isoformat()
            }
            
            key = self._get_user_notification_key(user_id)
            
            # 添加到列表头部
            self.redis_client.lpush(key, json.dumps(notification, ensure_ascii=False))
            
            # ✅ 使用类型特定的TTL
            if custom_ttl is not None:
                ttl = custom_ttl
            else:
                ttl = self.NOTIFICATION_TTL_MAP.get(
                    notification_type, 
                    self.NOTIFICATION_TTL_MAP["default"]
                )
            
            # 设置过期时间
            self.redis_client.expire(key, ttl)
            
            # 限制列表长度
            self.redis_client.ltrim(key, 0, self.MAX_NOTIFICATIONS_PER_USER - 1)
            
            logger.info(
                f"💾 [Redis] 通知已保存: user={user_id}, type={notification_type}, "
                f"ttl={ttl}s ({ttl/3600:.1f}h), id={notification['id']}"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ [Redis] 保存通知失败: {e}", exc_info=True)
            return False
```

### 步骤4：添加通知去重（可选，但强烈推荐）

在 `redis_notification_storage.py` 中添加：

```python
def save_notification(
    self,
    user_id: str,
    notification_type: str,
    title: str,
    content: str,
    data: Optional[Dict] = None,
    priority: str = "normal",
    custom_ttl: Optional[int] = None,
    dedup_key: Optional[str] = None  # ✅ 去重键
) -> bool:
    """保存通知到 Redis，支持去重"""
    if not self.enabled:
        return False
    
    try:
        # ✅ 1. 检查是否需要去重
        if dedup_key:
            dedup_cache_key = f"notif_dedup:{user_id}:{dedup_key}"
            if self.redis_client.exists(dedup_cache_key):
                logger.info(f"⏭️ [Redis] 跳过重复通知: {dedup_key}")
                return True  # 视为成功
            # 设置去重缓存，24小时过期
            self.redis_client.setex(dedup_cache_key, 24 * 60 * 60, "1")
        
        # 2. 保存通知（原有逻辑）
        notification = {
            "id": str(uuid.uuid4()),
            "type": notification_type,
            "title": title,
            "content": content,
            "data": data or {},
            "priority": priority,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "created_at": datetime.now().isoformat()
        }
        
        key = self._get_user_notification_key(user_id)
        self.redis_client.lpush(key, json.dumps(notification, ensure_ascii=False))
        
        # 使用类型特定的TTL
        if custom_ttl is not None:
            ttl = custom_ttl
        else:
            ttl = self.NOTIFICATION_TTL_MAP.get(
                notification_type, 
                self.NOTIFICATION_TTL_MAP["default"]
            )
        
        self.redis_client.expire(key, ttl)
        self.redis_client.ltrim(key, 0, self.MAX_NOTIFICATIONS_PER_USER - 1)
        
        logger.info(
            f"💾 [Redis] 通知已保存: user={user_id}, type={notification_type}, "
            f"ttl={ttl}s ({ttl/3600:.1f}h), dedup={dedup_key or 'N/A'}, id={notification['id']}"
        )
        return True
        
    except Exception as e:
        logger.error(f"❌ [Redis] 保存通知失败: {e}", exc_info=True)
        return False
```

---

## 🧪 测试修复效果

### 1. 测试定时通知（手动触发）

```bash
# 1. 确保Redis正常运行
redis-cli ping  # 应该返回 PONG

# 2. 手动触发下班提醒
curl -X POST http://localhost:8000/api/scheduler/trigger-work-reminder \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 检查Redis中的通知
redis-cli
> KEYS notifications:user:*
> LRANGE notifications:user:USER_ID 0 -1
> TTL notifications:user:USER_ID  # 检查过期时间
```

### 2. 验证离线用户接收

```python
# test_offline_notification.py
import requests
import time

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "YOUR_ADMIN_TOKEN"
TEST_USER_TOKEN = "YOUR_TEST_USER_TOKEN"

# 1. 触发定时通知（以管理员身份）
response = requests.post(
    f"{BASE_URL}/api/scheduler/trigger-work-reminder",
    headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
)
print(f"✅ 触发通知: {response.status_code}")

# 2. 等待2秒（模拟离线）
time.sleep(2)

# 3. 以测试用户身份获取通知
response = requests.get(
    f"{BASE_URL}/api/notifications",
    headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
)

notifications = response.json()
print(f"📬 通知数量: {len(notifications)}")
print(f"📬 最新通知: {notifications[0] if notifications else 'None'}")

# 4. 检查是否有下班提醒
work_reminder = next((n for n in notifications if n['type'] == 'work_end_reminder'), None)
if work_reminder:
    print("✅ 离线用户成功接收到定时通知！")
    print(f"   标题: {work_reminder['title']}")
    print(f"   内容: {work_reminder['content']}")
else:
    print("❌ 未找到定时通知，修复可能失败")
```

### 3. 验证TTL设置

```python
# test_ttl.py
import redis
from datetime import datetime, timedelta

r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# 检查所有通知key的TTL
pattern = "notifications:user:*"
for key in r.scan_iter(pattern, count=100):
    ttl = r.ttl(key)
    if ttl > 0:
        hours = ttl / 3600
        user_id = key.split(":")[-1]
        print(f"用户 {user_id}: 剩余 {hours:.1f} 小时 ({ttl}秒)")
    elif ttl == -1:
        print(f"⚠️ {key}: 没有过期时间（永久保存）")
    elif ttl == -2:
        print(f"⚠️ {key}: Key不存在")

# 检查特定类型通知的内容和TTL
for key in r.scan_iter(pattern, count=100):
    notifications = r.lrange(key, 0, -1)
    for notif_json in notifications:
        import json
        notif = json.loads(notif_json)
        if notif['type'] == 'work_end_reminder':
            user_id = key.split(":")[-1]
            ttl = r.ttl(key)
            print(f"✅ 下班提醒: 用户 {user_id}, TTL={ttl/3600:.1f}h")
```

---

## 📊 预期效果

### 修复前
```
17:10 定时通知触发
  └─ 只有在线用户收到（通过WebSocket）
  └─ 离线用户永久错过 ❌

所有通知统一7天TTL
  └─ 下班提醒7天后才过期 ❌
  └─ 累积大量过时通知 ❌
```

### 修复后
```
17:10 定时通知触发
  ├─ 在线用户：WebSocket实时推送 ✅
  └─ 离线用户：保存到Redis，12小时后过期 ✅

分级TTL策略
  ├─ 下班提醒：12小时（当天有效）✅
  ├─ 任务分配：3天 ✅
  ├─ 任务完成：1天 ✅
  └─ 系统公告：7天 ✅
```

---

## ⚙️ 配置建议

### 环境变量（可选）

在 `backend/app/config.py` 中添加：

```python
class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # ✅ 通知系统配置
    NOTIFICATION_DEFAULT_TTL: int = 604800  # 7天
    NOTIFICATION_WORK_REMINDER_TTL: int = 43200  # 12小时
    NOTIFICATION_MAX_PER_USER: int = 50
    NOTIFICATION_DEDUP_WINDOW: int = 86400  # 去重窗口24小时
```

然后在 `redis_notification_storage.py` 中使用：

```python
from app.config import settings

class RedisNotificationStorage:
    def __init__(self):
        # ...
        self.NOTIFICATION_TTL_MAP = {
            "work_end_reminder": settings.NOTIFICATION_WORK_REMINDER_TTL,
            # ...
        }
```

---

## 🔄 部署步骤

### 1. 开发环境测试
```bash
cd backend
# 1. 重启后端服务
uvicorn app.main:app --reload

# 2. 测试定时通知
python test_offline_notification.py

# 3. 检查日志
tail -f app/logs/*.log | grep -E "Scheduler|Redis|通知"
```

### 2. 生产环境部署
```bash
# 1. 备份当前代码
git stash save "backup before notification fix"

# 2. 应用修复
# 手动应用上述代码修改

# 3. 重启后端服务
docker-compose -f docker-compose.yml restart backend

# 4. 监控日志
docker-compose logs -f backend | grep -E "Scheduler|Redis|通知"

# 5. 手动触发测试
curl -X POST https://your-domain.com/api/scheduler/trigger-work-reminder \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 验收标准

- ✅ 离线用户在上线后能看到17:10的下班提醒
- ✅ 下班提醒在12小时后自动过期
- ✅ 任务分配通知保留3天
- ✅ 系统不会累积大量过时通知
- ✅ Redis内存占用合理（每用户<50条通知）
- ✅ 日志显示正确的TTL设置

---

## 🐛 常见问题

### Q1：修复后通知还是收不到？
**A**：检查以下几点：
1. Redis是否正常运行：`redis-cli ping`
2. 后端日志是否有错误：`grep "Redis" app/logs/*.log`
3. 用户是否为活跃状态：`User.is_active == True`

### Q2：所有通知都是12小时TTL？
**A**：检查 `notification_type` 是否正确设置。打印日志：
```python
logger.info(f"通知类型: {notification_type}, TTL: {ttl}")
```

### Q3：通知重复发送？
**A**：启用去重机制：
```python
redis_notification_storage.save_notification(
    user_id=user_id,
    notification_type="work_end_reminder",
    title="下班提醒",
    content="...",
    dedup_key=f"work_reminder_{datetime.now().strftime('%Y-%m-%d')}"  # 每天去重
)
```

---

## 📚 相关文档

- [Redis通知系统完整分析](./REDIS_NOTIFICATION_ISSUES_AND_FIXES.md)
- [Redis部署指南](./REDIS_DEPLOYMENT_GUIDE.md)
- [定时任务配置](../backend/README.md#定时任务)

---

## 🎯 下一步优化（可选）

1. **监控面板**：添加通知统计API
   ```python
   @router.get("/statistics")
   def get_notification_statistics():
       # 返回通知数量、TTL分布等
   ```

2. **批量清理**：定时清理过期通知
   ```python
   def cleanup_expired_notifications():
       # 每天凌晨2点运行
   ```

3. **通知历史**：保存通知到数据库（长期归档）

4. **用户偏好**：允许用户设置通知接收偏好

---

**完成时间**：约30分钟  
**测试时间**：约15分钟  
**总计时间**：约45分钟

修复完成后，请运行测试脚本验证效果，并查看日志确认通知正确保存！🎉

