"""
Token 管理服务
使用 Redis 作为 Token 白名单，实现 Token 的存储、验证、续期和撤销
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.utils.redis_client import redis_client
from app.config import settings

logger = logging.getLogger(__name__)

class TokenManager:
    """Token 管理器"""
    
    # Token 在 Redis 中的 key 前缀
    TOKEN_PREFIX = "token:"
    # 用户 Token 映射的 key 前缀（用于单点登录）
    USER_TOKEN_PREFIX = "user_token:"
    # Token 默认过期时间（秒）
    TOKEN_EXPIRE_SECONDS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # Token 自动续期阈值（剩余时间少于此值时自动续期，秒）
    TOKEN_RENEW_THRESHOLD = settings.TOKEN_RENEW_THRESHOLD_MINUTES * 60
    
    @classmethod
    def _get_token_hash(cls, token: str) -> str:
        """
        获取 token 的哈希值（用作 Redis key 的一部分）
        :param token: 原始 token
        :return: token 哈希值
        """
        return hashlib.sha256(token.encode()).hexdigest()[:16]
    
    @classmethod
    def _get_token_key(cls, token: str) -> str:
        """
        获取 token 在 Redis 中的完整 key
        :param token: 原始 token
        :return: Redis key
        """
        token_hash = cls._get_token_hash(token)
        return f"{cls.TOKEN_PREFIX}{token_hash}"
    
    @classmethod
    def _get_user_token_key(cls, user_id: str) -> str:
        """
        获取用户 token 映射的 key
        :param user_id: 用户ID
        :return: Redis key
        """
        return f"{cls.USER_TOKEN_PREFIX}{user_id}"
    
    @classmethod
    def store_token(
        cls,
        token: str,
        user_id: str,
        username: str,
        role: str,
        expire_seconds: Optional[int] = None
    ) -> bool:
        """
        存储 token 到 Redis
        :param token: JWT token
        :param user_id: 用户ID
        :param username: 用户名
        :param role: 角色
        :param expire_seconds: 过期时间（秒），默认使用配置的值
        :return: 是否成功
        """
        if not redis_client.is_connected():
            logger.warning("⚠️ [TokenManager] Redis 未连接，跳过 token 存储")
            return False
        
        try:
            expire = expire_seconds or cls.TOKEN_EXPIRE_SECONDS
            now = datetime.utcnow()
            
            # Token 数据
            token_data = {
                "user_id": user_id,
                "username": username,
                "role": role,
                "created_at": now.isoformat(),
                "last_active": now.isoformat(),
                "expire_at": (now + timedelta(seconds=expire)).isoformat()
            }
            
            # 存储 token
            token_key = cls._get_token_key(token)
            success = redis_client.set(token_key, token_data, expire)
            
            if success:
                # 存储用户 -> token 的映射（用于单点登录控制）
                user_token_key = cls._get_user_token_key(user_id)
                token_hash = cls._get_token_hash(token)
                redis_client.set(user_token_key, token_hash, expire)
                
                logger.info(f"✅ [TokenManager] Token 已存储 - User: {username}, Expire: {expire}s")
            else:
                logger.error(f"❌ [TokenManager] Token 存储失败 - User: {username}")
            
            return success
        except Exception as e:
            logger.error(f"❌ [TokenManager] Token 存储异常: {str(e)}")
            return False
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        验证 token 是否在白名单中
        :param token: JWT token
        :return: Token 数据（如果有效）或 None
        """
        if not redis_client.is_connected():
            logger.warning("⚠️ [TokenManager] Redis 未连接，跳过白名单验证")
            return None
        
        try:
            token_key = cls._get_token_key(token)
            token_data = redis_client.get(token_key)
            
            if token_data is None:
                logger.warning(f"⚠️ [TokenManager] Token 不在白名单中或已过期")
                return None
            
            logger.info(f"✅ [TokenManager] Token 验证通过 - User: {token_data.get('username')}")
            return token_data
        except Exception as e:
            logger.error(f"❌ [TokenManager] Token 验证异常: {str(e)}")
            return None
    
    @classmethod
    def renew_token(cls, token: str) -> bool:
        """
        续期 token（滑动窗口机制）
        :param token: JWT token
        :return: 是否成功续期
        """
        if not redis_client.is_connected():
            return False
        
        try:
            token_key = cls._get_token_key(token)
            
            # 检查 token 是否存在
            if not redis_client.exists(token_key):
                return False
            
            # 获取当前 TTL
            current_ttl = redis_client.ttl(token_key)
            
            # 如果剩余时间少于阈值，则续期
            if 0 < current_ttl < cls.TOKEN_RENEW_THRESHOLD:
                # 更新 last_active 时间
                token_data = redis_client.get(token_key)
                if token_data:
                    token_data['last_active'] = datetime.utcnow().isoformat()
                    redis_client.set(token_key, token_data, cls.TOKEN_EXPIRE_SECONDS)
                    
                    # 同时续期用户 token 映射
                    user_id = token_data.get('user_id')
                    if user_id:
                        user_token_key = cls._get_user_token_key(user_id)
                        redis_client.expire(user_token_key, cls.TOKEN_EXPIRE_SECONDS)
                    
                    logger.info(f"🔄 [TokenManager] Token 已续期 - User: {token_data.get('username')}, NewTTL: {cls.TOKEN_EXPIRE_SECONDS}s")
                    return True
            
            # 剩余时间充足，无需续期
            return True
        except Exception as e:
            logger.error(f"❌ [TokenManager] Token 续期异常: {str(e)}")
            return False
    
    @classmethod
    def revoke_token(cls, token: str) -> bool:
        """
        撤销 token（从白名单中删除）
        :param token: JWT token
        :return: 是否成功
        """
        if not redis_client.is_connected():
            logger.warning("⚠️ [TokenManager] Redis 未连接，跳过 token 撤销")
            return False
        
        try:
            token_key = cls._get_token_key(token)
            
            # 获取 token 数据（用于删除用户映射）
            token_data = redis_client.get(token_key)
            
            # 删除 token
            success = redis_client.delete(token_key)
            
            if success and token_data:
                # 删除用户 -> token 的映射
                user_id = token_data.get('user_id')
                if user_id:
                    user_token_key = cls._get_user_token_key(user_id)
                    redis_client.delete(user_token_key)
                
                logger.info(f"✅ [TokenManager] Token 已撤销 - User: {token_data.get('username')}")
            
            return success
        except Exception as e:
            logger.error(f"❌ [TokenManager] Token 撤销异常: {str(e)}")
            return False
    
    @classmethod
    def revoke_user_tokens(cls, user_id: str) -> bool:
        """
        撤销用户的所有 token（强制登出）
        :param user_id: 用户ID
        :return: 是否成功
        """
        if not redis_client.is_connected():
            logger.warning("⚠️ [TokenManager] Redis 未连接，跳过用户 token 撤销")
            return False
        
        try:
            user_token_key = cls._get_user_token_key(user_id)
            token_hash = redis_client.get(user_token_key)
            
            if token_hash:
                # 删除 token
                token_key = f"{cls.TOKEN_PREFIX}{token_hash}"
                redis_client.delete(token_key)
                
                # 删除用户映射
                redis_client.delete(user_token_key)
                
                logger.info(f"✅ [TokenManager] 用户所有 Token 已撤销 - UserID: {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"❌ [TokenManager] 用户 Token 撤销异常: {str(e)}")
            return False
    
    @classmethod
    def get_token_info(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        获取 token 的详细信息（包括 TTL）
        :param token: JWT token
        :return: Token 信息
        """
        if not redis_client.is_connected():
            return None
        
        try:
            token_key = cls._get_token_key(token)
            token_data = redis_client.get(token_key)
            
            if token_data:
                ttl = redis_client.ttl(token_key)
                token_data['ttl'] = ttl
                return token_data
            
            return None
        except Exception as e:
            logger.error(f"❌ [TokenManager] 获取 Token 信息异常: {str(e)}")
            return None


# 导出单例
token_manager = TokenManager

