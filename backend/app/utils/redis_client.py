"""
Redis 客户端工具类
提供 Redis 连接和基础操作
"""
import redis
import json
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis 客户端单例"""
    
    _instance: Optional[redis.Redis] = None
    _connected: bool = False
    
    @classmethod
    def get_instance(cls) -> Optional[redis.Redis]:
        """获取 Redis 实例（单例模式）"""
        if cls._instance is None:
            try:
                logger.info(f"🔌 [Redis] 正在连接到 Redis: {settings.REDIS_URL}")
                cls._instance = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # 测试连接
                ping_result = cls._instance.ping()
                cls._connected = True
                logger.info(f"✅ [Redis] Redis 连接成功，PING 响应: {ping_result}")
            except redis.ConnectionError as e:
                logger.error(f"❌ [Redis] Redis 连接失败（连接错误）: {str(e)}")
                logger.error(f"❌ [Redis] 请检查 Redis 服务是否运行在 {settings.REDIS_URL}")
                logger.warning("⚠️ [Redis] 系统将在无 Redis 的情况下运行（仅使用 JWT）")
                cls._instance = None
                cls._connected = False
            except redis.TimeoutError as e:
                logger.error(f"❌ [Redis] Redis 连接超时: {str(e)}")
                logger.error(f"❌ [Redis] Redis URL: {settings.REDIS_URL}")
                logger.warning("⚠️ [Redis] 系统将在无 Redis 的情况下运行（仅使用 JWT）")
                cls._instance = None
                cls._connected = False
            except Exception as e:
                logger.error(f"❌ [Redis] Redis 连接失败（未知错误）: {type(e).__name__}: {str(e)}")
                logger.warning("⚠️ [Redis] 系统将在无 Redis 的情况下运行（仅使用 JWT）")
                cls._instance = None
                cls._connected = False
        
        return cls._instance
    
    @classmethod
    def is_connected(cls) -> bool:
        """检查 Redis 是否连接"""
        # 如果尚未初始化，先尝试获取实例
        if cls._instance is None:
            cls.get_instance()
        
        # 再次检查连接状态
        if not cls._connected or cls._instance is None:
            return False
        
        try:
            cls._instance.ping()
            return True
        except Exception:
            cls._connected = False
            return False
    
    @classmethod
    def set(cls, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对
        :param key: 键
        :param value: 值（会自动序列化为 JSON）
        :param expire: 过期时间（秒）
        :return: 是否成功
        """
        try:
            client = cls.get_instance()
            if client is None:
                return False
            
            # 将值序列化为 JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire:
                client.setex(key, expire, value)
            else:
                client.set(key, value)
            
            return True
        except Exception as e:
            logger.error(f"❌ [Redis] 设置键值失败 - Key: {key}, Error: {str(e)}")
            return False
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """
        获取键值
        :param key: 键
        :return: 值（会自动反序列化 JSON）
        """
        try:
            client = cls.get_instance()
            if client is None:
                return None
            
            value = client.get(key)
            if value is None:
                return None
            
            # 尝试反序列化 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"❌ [Redis] 获取键值失败 - Key: {key}, Error: {str(e)}")
            return None
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """
        删除键
        :param key: 键
        :return: 是否成功
        """
        try:
            client = cls.get_instance()
            if client is None:
                return False
            
            client.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ [Redis] 删除键失败 - Key: {key}, Error: {str(e)}")
            return False
    
    @classmethod
    def exists(cls, key: str) -> bool:
        """
        检查键是否存在
        :param key: 键
        :return: 是否存在
        """
        try:
            client = cls.get_instance()
            if client is None:
                return False
            
            return bool(client.exists(key))
        except Exception as e:
            logger.error(f"❌ [Redis] 检查键存在失败 - Key: {key}, Error: {str(e)}")
            return False
    
    @classmethod
    def expire(cls, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        :param key: 键
        :param seconds: 过期秒数
        :return: 是否成功
        """
        try:
            client = cls.get_instance()
            if client is None:
                return False
            
            client.expire(key, seconds)
            return True
        except Exception as e:
            logger.error(f"❌ [Redis] 设置过期时间失败 - Key: {key}, Error: {str(e)}")
            return False
    
    @classmethod
    def ttl(cls, key: str) -> int:
        """
        获取键的剩余生存时间
        :param key: 键
        :return: 剩余秒数（-1表示永久，-2表示不存在）
        """
        try:
            client = cls.get_instance()
            if client is None:
                return -2
            
            return client.ttl(key)
        except Exception as e:
            logger.error(f"❌ [Redis] 获取TTL失败 - Key: {key}, Error: {str(e)}")
            return -2


# 导出单例
redis_client = RedisClient

# 兼容旧接口：提供 get_redis 函数
def get_redis():
    """
    获取 Redis 实例（兼容旧代码）
    :return: Redis 实例或 None
    """
    return RedisClient.get_instance()


# 兼容旧接口：提供 redis_ping 函数
def redis_ping() -> bool:
    """
    测试 Redis 连接（兼容旧代码）
    :return: 连接是否正常
    """
    return RedisClient.is_connected()
