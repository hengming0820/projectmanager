from typing import Dict, Set
from fastapi import WebSocket
import logging
from app.services.redis_notification_service import redis_notifier
from app.services.redis_notification_storage import redis_notification_storage

logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self) -> None:
        # 保存连接到其角色与用户信息
        self.active_connections: Set[WebSocket] = set()
        self.ws_role: Dict[WebSocket, str] = {}
        self.ws_user: Dict[WebSocket, Dict[str, str]] = {}
        
        # Redis Pub/Sub 支持
        self.redis_enabled = redis_notifier.enabled
        if self.redis_enabled:
            logger.info("✅ WebSocket管理器已启用Redis Pub/Sub支持")

    async def connect(self, websocket: WebSocket, role: str, user: Dict[str, str]) -> None:
        self.active_connections.add(websocket)
        self.ws_role[websocket] = (role or '').lower()
        self.ws_user[websocket] = user
        logger.info(f"🔔 [WS] 已连接: role={self.ws_role[websocket]} user={user.get('username') or user.get('real_name')}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.ws_role.pop(websocket, None)
        self.ws_user.pop(websocket, None)

    async def broadcast_to_role(self, role: str, message: dict) -> None:
        """
        向指定角色广播消息
        优先使用Redis Pub/Sub，不可用时回退到直接WebSocket
        """
        role_lc = (role or '').lower()
        
        # 优先使用Redis Pub/Sub
        if self.redis_enabled:
            receivers = redis_notifier.publish_to_role(role_lc, message)
            logger.info(f"🔔 [Redis] 向角色 {role_lc} 发布消息，Redis订阅者: {receivers}")
            # 如果有Redis订阅者，就不需要直接发送WebSocket了
            # Redis会自动转发到所有订阅该频道的服务器
            if receivers > 0:
                return
        
        # Redis不可用或无订阅者，回退到直接WebSocket发送
        dead: Set[WebSocket] = set()
        targets = [ws for ws in list(self.active_connections) if self.ws_role.get(ws) == role_lc]
        logger.info(f"🔔 [WS] 向角色 {role_lc} 直接广播，连接数: {len(self.active_connections)}，匹配接收者: {len(targets)}")
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"🔔 [WS] 发送给 {self.ws_user.get(ws)} 失败: {e}")
                dead.add(ws)
        for ws in dead:
            self.disconnect(ws)

    def _save_notification_to_redis(self, user_id: str, message: dict) -> None:
        """
        保存通知到 Redis（用于离线通知）
        通知会在 7 天后自动过期删除
        """
        try:
            redis_notification_storage.save_notification(
                user_id=user_id,
                notification_type=message.get('type', 'unknown'),
                title=message.get('title', '系统通知'),
                content=message.get('content', ''),
                data=message.get('data') or {},
                priority=message.get('priority', 'normal')
            )
        except Exception as e:
            logger.error(f"❌ [Redis] 保存通知到 Redis 失败: {e}", exc_info=True)
    
    async def send_to_user_id(self, user_id: str, message: dict) -> None:
        """
        向指定用户发送消息
        1. 保存到 Redis（用于离线通知，7天自动过期）
        2. 优先使用Redis Pub/Sub，不可用时回退到直接WebSocket
        """
        # 1. 首先保存到 Redis（确保离线也能收到）
        self._save_notification_to_redis(user_id, message)
        
        # 2. 尝试实时推送
        # 优先使用Redis Pub/Sub
        if self.redis_enabled:
            receivers = redis_notifier.publish_to_user(user_id, message)
            logger.info(f"🔔 [Redis] 向用户 {user_id} 发布消息，Redis订阅者: {receivers}")
            # 如果有Redis订阅者，就不需要直接发送WebSocket了
            if receivers > 0:
                return
        
        # Redis不可用或无订阅者，回退到直接WebSocket发送
        dead: Set[WebSocket] = set()
        sent = 0
        for ws in list(self.active_connections):
            try:
                info = self.ws_user.get(ws) or {}
                if info.get('id') == user_id:
                    await ws.send_json(message)
                    sent += 1
            except Exception as e:
                logger.warning(f"🔔 [WS] 发送到用户 {user_id} 失败: {e}")
                dead.add(ws)
        for ws in dead:
            self.disconnect(ws)
        logger.info(f"🔔 [WS] 向用户 {user_id} 直接发送通知，成功连接数: {sent}")

    async def broadcast_to_all(self, message: dict, save_offline: bool = False) -> None:
        """
        广播消息给所有在线用户
        优先使用Redis Pub/Sub，不可用时回退到直接WebSocket
        
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
                    saved_count = 0
                    for user in users:
                        try:
                            self._save_notification_to_redis(str(user.id), message)
                            saved_count += 1
                        except Exception as e:
                            logger.error(f"❌ [Redis] 保存通知给用户 {user.id} 失败: {e}")
                    
                    logger.info(f"✅ [Redis] 定时通知已保存给 {saved_count}/{len(users)} 个用户")
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"❌ [Redis] 批量保存通知失败: {e}", exc_info=True)
        
        # 2. 实时推送给在线用户（原有逻辑保持不变）
        # 优先使用Redis Pub/Sub
        if self.redis_enabled:
            receivers = redis_notifier.publish_global(message)
            logger.info(f"🔔 [Redis] 全局广播消息，Redis订阅者: {receivers}")
            # 如果有Redis订阅者，就不需要直接发送WebSocket了
            if receivers > 0:
                return
        
        # 3. Redis不可用或无订阅者，回退到直接WebSocket发送
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


manager = NotificationManager()


