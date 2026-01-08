"""
基于 Redis 的离线通知存储服务
使用 Redis List 存储用户未读通知，支持 TTL 自动过期
"""
import redis
import json
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class RedisNotificationStorage:
    """Redis 通知存储服务"""
    
    def __init__(self):
        try:
            # 从配置文件读取 Redis URL
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # 测试连接
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"✅ Redis通知存储服务初始化成功 ({settings.REDIS_URL})")
        except Exception as e:
            self.enabled = False
            logger.warning(f"⚠️ Redis通知存储服务不可用: {e}")
        
        # ✅ 分级TTL策略：不同类型通知有不同的过期时间
        self.NOTIFICATION_TTL_MAP = {
            "work_end_reminder": 12 * 60 * 60,      # 12小时（当天有效）
            "task_assigned": 3 * 24 * 60 * 60,      # 3天
            "task_completed": 1 * 24 * 60 * 60,     # 1天
            "task_due_soon": 2 * 24 * 60 * 60,      # 2天
            "article_assigned": 3 * 24 * 60 * 60,   # 3天
            "article_reviewed": 1 * 24 * 60 * 60,   # 1天
            "system_announcement": 7 * 24 * 60 * 60,  # 7天
            "urgent": 6 * 60 * 60,                   # 6小时
            "default": 7 * 24 * 60 * 60              # 默认7天
        }
        # 通知过期时间：7天（默认值，兼容旧代码）
        self.NOTIFICATION_TTL = 7 * 24 * 60 * 60  # 604800 秒
        # 每个用户最多保留的通知数量
        self.MAX_NOTIFICATIONS_PER_USER = 50
    
    def _get_user_notification_key(self, user_id: str) -> str:
        """获取用户通知的 Redis key"""
        return f"notifications:user:{user_id}"
    
    def save_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        content: str,
        data: Optional[Dict] = None,
        priority: str = "normal",
        custom_ttl: Optional[int] = None,  # ✅ 允许自定义TTL
        dedup_key: Optional[str] = None    # ✅ 去重键
    ) -> bool:
        """
        保存通知到 Redis，支持分级TTL和去重
        
        Args:
            user_id: 用户ID
            notification_type: 通知类型
            title: 标题
            content: 内容
            data: 附加数据
            priority: 优先级 (low/normal/high/urgent)
            custom_ttl: 自定义TTL（秒），如果不提供则使用类型对应的TTL
            dedup_key: 去重键，例如 "task_assigned:task_id_123"
                       如果24小时内已存在相同key的通知，则跳过
            
        Returns:
            是否保存成功
        """
        if not self.enabled:
            logger.warning(f"⚠️ Redis不可用，无法保存通知")
            return False
        
        try:
            # ✅ 1. 检查是否需要去重
            if dedup_key:
                dedup_cache_key = f"notif_dedup:{user_id}:{dedup_key}"
                if self.redis_client.exists(dedup_cache_key):
                    logger.info(f"⏭️ [Redis] 跳过重复通知: user={user_id}, dedup_key={dedup_key}")
                    return True  # 视为成功
                # 设置去重缓存，24小时过期
                self.redis_client.setex(dedup_cache_key, 24 * 60 * 60, "1")
            
            # 2. 构建通知对象
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
            
            # 3. 添加到列表头部（最新的通知在前面）
            self.redis_client.lpush(key, json.dumps(notification, ensure_ascii=False))
            
            # ✅ 4. 使用类型特定的TTL
            if custom_ttl is not None:
                ttl = custom_ttl
            else:
                ttl = self.NOTIFICATION_TTL_MAP.get(
                    notification_type, 
                    self.NOTIFICATION_TTL_MAP["default"]
                )
            
            # 设置过期时间（每次添加都刷新）
            self.redis_client.expire(key, ttl)
            
            # 5. 限制列表长度（保留最新的 N 条）
            self.redis_client.ltrim(key, 0, self.MAX_NOTIFICATIONS_PER_USER - 1)
            
            logger.info(
                f"💾 [Redis] 通知已保存: user={user_id}, type={notification_type}, "
                f"ttl={ttl}s ({ttl/3600:.1f}h), dedup={dedup_key or 'N/A'}, id={notification['id']}"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ [Redis] 保存通知失败: {e}", exc_info=True)
            return False
    
    def get_unread_notifications(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        获取用户的未读通知
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            通知列表
        """
        if not self.enabled:
            logger.warning(f"⚠️ Redis不可用，无法获取通知")
            return []
        
        try:
            key = self._get_user_notification_key(user_id)
            
            # 获取所有通知（从头部开始，即最新的）
            notifications_json = self.redis_client.lrange(key, 0, limit - 1)
            
            notifications = []
            for notif_json in notifications_json:
                try:
                    notification = json.loads(notif_json)
                    notifications.append(notification)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ [Redis] 解析通知失败: {e}")
                    continue
            
            logger.info(f"📬 [Redis] 获取未读通知: user={user_id}, count={len(notifications)}")
            return notifications
            
        except Exception as e:
            logger.error(f"❌ [Redis] 获取通知失败: {e}", exc_info=True)
            return []
    
    def get_unread_count(self, user_id: str) -> int:
        """
        获取用户未读通知数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            未读通知数量
        """
        if not self.enabled:
            return 0
        
        try:
            key = self._get_user_notification_key(user_id)
            count = self.redis_client.llen(key)
            logger.info(f"📬 [Redis] 未读通知数: user={user_id}, count={count}")
            return count
        except Exception as e:
            logger.error(f"❌ [Redis] 获取未读通知数失败: {e}")
            return 0
    
    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """
        标记通知为已读（从列表中删除）
        
        Args:
            user_id: 用户ID
            notification_id: 通知ID
            
        Returns:
            是否成功
        """
        if not self.enabled:
            return False
        
        try:
            key = self._get_user_notification_key(user_id)
            
            # 获取所有通知
            notifications_json = self.redis_client.lrange(key, 0, -1)
            
            # 找到并删除指定的通知
            for notif_json in notifications_json:
                try:
                    notification = json.loads(notif_json)
                    if notification.get('id') == notification_id:
                        # 从列表中删除这条通知
                        self.redis_client.lrem(key, 1, notif_json)
                        logger.info(f"✅ [Redis] 通知已标记为已读: user={user_id}, id={notification_id}")
                        return True
                except json.JSONDecodeError:
                    continue
            
            logger.warning(f"⚠️ [Redis] 未找到通知: user={user_id}, id={notification_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ [Redis] 标记已读失败: {e}", exc_info=True)
            return False
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """
        标记所有通知为已读（清空列表）
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        if not self.enabled:
            return False
        
        try:
            key = self._get_user_notification_key(user_id)
            count = self.redis_client.llen(key)
            
            # 删除整个列表
            self.redis_client.delete(key)
            
            logger.info(f"✅ [Redis] 所有通知已标记为已读: user={user_id}, count={count}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [Redis] 标记所有已读失败: {e}", exc_info=True)
            return False
    
    def delete_notification(self, user_id: str, notification_id: str) -> bool:
        """
        删除通知（从列表中移除）
        
        Args:
            user_id: 用户ID
            notification_id: 通知ID
            
        Returns:
            是否成功
        """
        # 删除和标记已读是同一个操作
        return self.mark_as_read(user_id, notification_id)
    
    def get_ttl(self, user_id: str) -> int:
        """
        获取用户通知列表的剩余 TTL
        
        Args:
            user_id: 用户ID
            
        Returns:
            剩余秒数，-1 表示没有过期时间，-2 表示 key 不存在
        """
        if not self.enabled:
            return -2
        
        try:
            key = self._get_user_notification_key(user_id)
            ttl = self.redis_client.ttl(key)
            return ttl
        except Exception as e:
            logger.error(f"❌ [Redis] 获取TTL失败: {e}")
            return -2


# 全局实例
redis_notification_storage = RedisNotificationStorage()

