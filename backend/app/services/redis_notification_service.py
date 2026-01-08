"""
Redis Pub/Sub 实时通知服务
使用Redis的发布订阅功能实现实时通知，支持多服务器部署
"""
import redis
import json
import asyncio
from typing import Callable, Dict, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class RedisNotificationService:
    """基于Redis Pub/Sub的通知服务"""
    
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
            logger.info(f"✅ Redis通知服务初始化成功 ({settings.REDIS_URL})")
        except Exception as e:
            self.enabled = False
            logger.warning(f"⚠️ Redis通知服务不可用，将使用直接WebSocket: {e}")
        
        self.pubsub = None
        self.subscribers: Dict[str, Callable] = {}
        self.running = False
    
    # ==================== 发布消息 ====================
    
    def publish_to_user(self, user_id: str, message: dict) -> int:
        """
        发布消息到用户个人频道
        
        Args:
            user_id: 用户ID
            message: 消息内容
            
        Returns:
            接收到消息的订阅者数量
        """
        if not self.enabled:
            logger.debug(f"⚠️ Redis不可用，跳过发布到用户 {user_id}")
            return 0
        
        channel = f"notify:user:{user_id}"
        return self._publish(channel, message)
    
    def publish_to_role(self, role: str, message: dict) -> int:
        """
        发布消息到角色频道
        
        Args:
            role: 角色名称（如 reviewer, admin, annotator）
            message: 消息内容
            
        Returns:
            接收到消息的订阅者数量
        """
        if not self.enabled:
            logger.debug(f"⚠️ Redis不可用，跳过发布到角色 {role}")
            return 0
        
        channel = f"notify:role:{role.lower()}"
        return self._publish(channel, message)
    
    def publish_to_project(self, project_id: str, message: dict) -> int:
        """
        发布消息到项目频道
        
        Args:
            project_id: 项目ID
            message: 消息内容
            
        Returns:
            接收到消息的订阅者数量
        """
        if not self.enabled:
            logger.debug(f"⚠️ Redis不可用，跳过发布到项目 {project_id}")
            return 0
        
        channel = f"notify:project:{project_id}"
        return self._publish(channel, message)
    
    def publish_global(self, message: dict) -> int:
        """
        发布全局广播
        
        Args:
            message: 消息内容
            
        Returns:
            接收到消息的订阅者数量
        """
        if not self.enabled:
            logger.debug("⚠️ Redis不可用，跳过全局广播")
            return 0
        
        channel = "notify:global"
        return self._publish(channel, message)
    
    def _publish(self, channel: str, message: dict) -> int:
        """
        内部发布方法
        
        Args:
            channel: 频道名称
            message: 消息内容
            
        Returns:
            接收到消息的订阅者数量
        """
        try:
            message_str = json.dumps(message, ensure_ascii=False, default=str)
            # 返回接收到消息的订阅者数量
            receivers = self.redis_client.publish(channel, message_str)
            logger.info(f"📤 发布消息到 {channel}, 接收者: {receivers}")
            return receivers
        except Exception as e:
            logger.error(f"❌ 发布消息失败 {channel}: {e}")
            return 0
    
    # ==================== 订阅频道 ====================
    
    async def subscribe_user_channel(self, user_id: str, callback: Callable):
        """
        订阅用户个人频道
        
        Args:
            user_id: 用户ID
            callback: 回调函数 async def callback(channel, message)
        """
        channel = f"notify:user:{user_id}"
        await self._subscribe(channel, callback)
    
    async def subscribe_role_channel(self, role: str, callback: Callable):
        """
        订阅角色频道
        
        Args:
            role: 角色名称
            callback: 回调函数 async def callback(channel, message)
        """
        channel = f"notify:role:{role.lower()}"
        await self._subscribe(channel, callback)
    
    async def subscribe_project_channel(self, project_id: str, callback: Callable):
        """
        订阅项目频道
        
        Args:
            project_id: 项目ID
            callback: 回调函数 async def callback(channel, message)
        """
        channel = f"notify:project:{project_id}"
        await self._subscribe(channel, callback)
    
    async def subscribe_global(self, callback: Callable):
        """
        订阅全局广播
        
        Args:
            callback: 回调函数 async def callback(channel, message)
        """
        await self._subscribe("notify:global", callback)
    
    async def _subscribe(self, channel: str, callback: Callable):
        """
        内部订阅方法
        
        Args:
            channel: 频道名称
            callback: 回调函数
        """
        if not self.enabled:
            logger.debug(f"⚠️ Redis不可用，跳过订阅 {channel}")
            return
        
        try:
            if not self.pubsub:
                self.pubsub = self.redis_client.pubsub()
            
            self.subscribers[channel] = callback
            self.pubsub.subscribe(channel)
            logger.info(f"📥 订阅频道: {channel}")
        except Exception as e:
            logger.error(f"❌ 订阅失败 {channel}: {e}")
    
    # ==================== 监听消息 ====================
    
    async def listen(self):
        """
        启动消息监听循环
        这个方法应该在后台任务中运行
        """
        if not self.enabled:
            logger.warning("⚠️ Redis不可用，监听循环未启动")
            return
        
        self.running = True
        logger.info("👂 开始监听Redis消息...")
        
        try:
            while self.running:
                # 获取消息（非阻塞）
                message = self.pubsub.get_message(ignore_subscribe_messages=True)
                
                if message and message['type'] == 'message':
                    channel = message['channel']
                    data = json.loads(message['data'])
                    
                    # 调用回调函数
                    if channel in self.subscribers:
                        callback = self.subscribers[channel]
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(channel, data)
                            else:
                                callback(channel, data)
                        except Exception as e:
                            logger.error(f"❌ 回调函数执行失败 {channel}: {e}")
                
                # 短暂休眠，避免CPU占用过高
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"❌ 监听消息出错: {e}")
        finally:
            self.running = False
            logger.info("🛑 停止监听Redis消息")
    
    def stop(self):
        """停止监听"""
        self.running = False
        if self.pubsub:
            try:
                self.pubsub.close()
            except Exception as e:
                logger.error(f"❌ 关闭pubsub失败: {e}")
        logger.info("🛑 Redis通知服务已停止")
    
    # ==================== 辅助方法 ====================
    
    def create_notification_message(
        self,
        notification_type: str,
        title: str,
        content: str,
        data: dict = None,
        priority: str = "normal"
    ) -> dict:
        """
        创建标准格式的通知消息
        
        Args:
            notification_type: 通知类型（如 task_submitted, task_reviewed）
            title: 通知标题
            content: 通知内容
            data: 附加数据
            priority: 优先级（low, normal, high, urgent）
            
        Returns:
            格式化的通知消息
        """
        import time
        return {
            "type": notification_type,
            "title": title,
            "content": content,
            "data": data or {},
            "priority": priority,
            "timestamp": int(time.time())
        }


# 全局实例
redis_notifier = RedisNotificationService()


# ==================== 便捷函数 ====================

def notify_user(user_id: str, notification_type: str, title: str, content: str, data: dict = None):
    """
    便捷函数：通知指定用户
    
    Example:
        notify_user("user123", "task_reviewed", "任务审核结果", "你的任务已通过", {"task_id": "task456"})
    """
    message = redis_notifier.create_notification_message(
        notification_type, title, content, data
    )
    return redis_notifier.publish_to_user(user_id, message)


def notify_role(role: str, notification_type: str, title: str, content: str, data: dict = None):
    """
    便捷函数：通知指定角色的所有用户
    
    Example:
        notify_role("reviewer", "task_submitted", "新任务待审核", "有1个新任务待审核", {"task_id": "task456"})
    """
    message = redis_notifier.create_notification_message(
        notification_type, title, content, data
    )
    return redis_notifier.publish_to_role(role, message)


def notify_global(notification_type: str, title: str, content: str, data: dict = None, priority: str = "high"):
    """
    便捷函数：全局广播通知
    
    Example:
        notify_global("system_maintenance", "系统维护通知", "系统将于今晚23:00进行维护", priority="urgent")
    """
    message = redis_notifier.create_notification_message(
        notification_type, title, content, data, priority
    )
    return redis_notifier.publish_global(message)

