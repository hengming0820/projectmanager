"""
Redis 缓存服务
提供统一的缓存操作接口，支持降级处理（Redis不可用时自动跳过）
"""

import redis
import json
import hashlib
from typing import Optional, Any, List
from datetime import datetime, date, timezone
from decimal import Decimal
from functools import wraps
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def json_serializer(obj):
    """
    自定义JSON序列化器，确保时间格式一致
    
    将datetime对象统一转换为ISO 8601格式（UTC时间 + Z标识）
    这确保了Redis缓存中的时间格式与Pydantic序列化一致，
    避免前端接收到不同格式的时间字符串导致的时区问题
    
    Args:
        obj: 要序列化的对象
        
    Returns:
        序列化后的字符串
        
    Examples:
        datetime(2025, 10, 31, 10, 0, 0, tzinfo=timezone.utc) → "2025-10-31T10:00:00Z"
        datetime(2025, 10, 31, 10, 0, 0) → "2025-10-31T10:00:00Z" (假定为UTC)
        date(2025, 10, 31) → "2025-10-31"
        Decimal("123.45") → 123.45
    """
    if isinstance(obj, datetime):
        # datetime对象转换为ISO 8601格式（UTC时间 + Z标识）
        if obj.tzinfo is None:
            # naive datetime，假定为UTC，添加Z标识
            return obj.isoformat() + 'Z'
        else:
            # 带时区的datetime，转换为UTC并添加Z标识
            utc_dt = obj.astimezone(timezone.utc)
            # 使用strftime确保格式统一（去除微秒），然后添加Z
            return utc_dt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    elif isinstance(obj, date):
        # date对象转换为YYYY-MM-DD格式
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        # Decimal转换为float（用于数值计算）
        return float(obj)
    else:
        # 其他类型使用str()
        return str(obj)

class CacheService:
    """统一的Redis缓存服务"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.redis_client = None
        self.enabled = False
        self.default_ttl = 300  # 5分钟默认过期时间
        
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
            logger.info(f"✅ Redis连接成功，缓存服务已启用 ({settings.REDIS_URL})")
        except Exception as e:
            logger.warning(f"⚠️ Redis不可用，缓存服务已禁用: {e}")
            self.enabled = False
    
    # ==================== 基础操作 ====================
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据（自动JSON解析），不存在则返回None
        """
        if not self.enabled:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"🎯 缓存命中: {key}")
                return json.loads(data)
            logger.debug(f"❌ 缓存未命中: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis GET失败 {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            value: 要缓存的数据（将自动JSON序列化）
            expire: 过期时间（秒），None则使用默认值
            
        Returns:
            是否设置成功
        """
        if not self.enabled:
            return False
        
        try:
            expire = expire or self.default_ttl
            self.redis_client.setex(
                key,
                expire,
                json.dumps(value, ensure_ascii=False, default=json_serializer)
            )
            logger.debug(f"💾 缓存写入: {key} (过期时间: {expire}秒)")
            return True
        except Exception as e:
            logger.error(f"Redis SET失败 {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除单个缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            logger.debug(f"🗑️ 缓存删除: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis DELETE失败 {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        批量删除匹配的缓存
        
        Args:
            pattern: 匹配模式，如 "tasks:list:*"
            
        Returns:
            删除的数量
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                count = self.redis_client.delete(*keys)
                logger.info(f"🗑️ 批量删除缓存: {pattern} ({count} 个key)")
                return count
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN失败 {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        if not self.enabled:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception:
            return False
    
    # ==================== Hash操作 ====================
    
    def hget(self, key: str, field: str) -> Optional[Any]:
        """获取Hash字段"""
        if not self.enabled:
            return None
        
        try:
            data = self.redis_client.hget(key, field)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis HGET失败: {e}")
            return None
    
    def hset(self, key: str, field: str, value: Any) -> bool:
        """设置Hash字段"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.hset(
                key,
                field,
                json.dumps(value, ensure_ascii=False, default=json_serializer)
            )
            return True
        except Exception as e:
            logger.error(f"Redis HSET失败: {e}")
            return False
    
    def hgetall(self, key: str) -> dict:
        """获取Hash所有字段"""
        if not self.enabled:
            return {}
        
        try:
            data = self.redis_client.hgetall(key)
            return {k: json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Redis HGETALL失败: {e}")
            return {}
    
    def hdel(self, key: str, *fields: str) -> int:
        """删除Hash字段"""
        if not self.enabled:
            return 0
        
        try:
            return self.redis_client.hdel(key, *fields)
        except Exception as e:
            logger.error(f"Redis HDEL失败: {e}")
            return 0
    
    # ==================== List操作 ====================
    
    def lpush(self, key: str, *values: Any) -> bool:
        """列表左侧推入"""
        if not self.enabled:
            return False
        
        try:
            serialized = [json.dumps(v, default=json_serializer) for v in values]
            self.redis_client.lpush(key, *serialized)
            return True
        except Exception as e:
            logger.error(f"Redis LPUSH失败: {e}")
            return False
    
    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表范围"""
        if not self.enabled:
            return []
        
        try:
            data = self.redis_client.lrange(key, start, end)
            return [json.loads(item) for item in data]
        except Exception as e:
            logger.error(f"Redis LRANGE失败: {e}")
            return []
    
    # ==================== 分布式锁 ====================
    
    def acquire_lock(self, key: str, expire: int = 10) -> bool:
        """
        获取分布式锁
        
        Args:
            key: 锁的键
            expire: 锁的过期时间（秒），防止死锁
            
        Returns:
            是否获取成功
        """
        if not self.enabled:
            return True  # Redis不可用时，不阻塞业务
        
        try:
            return self.redis_client.set(key, "1", nx=True, ex=expire)
        except Exception:
            return True  # 失败时不阻塞业务
    
    def release_lock(self, key: str):
        """释放分布式锁"""
        self.delete(key)
    
    # ==================== 缓存失效辅助方法 ====================
    
    def invalidate_tasks_cache(self, project_id: str = None, user_id: str = None):
        """
        清除任务相关缓存
        
        Args:
            project_id: 如果指定，则只清除该项目的任务缓存
            user_id: 如果指定，则清除该用户相关的任务缓存
        """
        if project_id and user_id:
            # 清除特定项目和用户的任务缓存
            self.delete_pattern(f"tasks:list:{project_id}:*:{user_id}:*")
            self.delete_pattern(f"tasks:list:{project_id}:*:all:*")
            self.delete_pattern(f"tasks:list:all:*:{user_id}:*")
            logger.info(f"🗑️ 任务缓存已清除 (项目: {project_id}, 用户: {user_id})")
        elif project_id:
            # 清除特定项目的所有任务缓存
            self.delete_pattern(f"tasks:list:{project_id}:*")
            logger.info(f"🗑️ 任务缓存已清除 (项目: {project_id})")
        elif user_id:
            # 清除特定用户的所有任务缓存
            self.delete_pattern(f"tasks:list:*:*:{user_id}:*")
            logger.info(f"🗑️ 任务缓存已清除 (用户: {user_id})")
        else:
            # 清除所有任务列表缓存
            self.delete_pattern("tasks:list:*")
            logger.info("🗑️ 所有任务缓存已清除")
    
    def invalidate_task_detail_cache(self, task_id: str):
        """清除任务详情缓存"""
        self.delete(f"tasks:detail:{task_id}")
        logger.info(f"🗑️ 任务详情缓存已清除: {task_id}")
    
    def invalidate_projects_cache(self):
        """清除项目相关缓存"""
        self.delete_pattern("projects:*")
        logger.info("🗑️ 项目缓存已清除")
    
    def invalidate_project_detail_cache(self, project_id: str):
        """清除项目详情缓存"""
        self.delete(f"projects:detail:{project_id}")
        self.delete(f"projects:stats:{project_id}")
        logger.info(f"🗑️ 项目详情缓存已清除: {project_id}")
    
    def invalidate_users_cache(self):
        """清除用户相关缓存"""
        self.delete_pattern("users:*")
        logger.info("🗑️ 用户缓存已清除")
    
    def invalidate_user_detail_cache(self, user_id: str):
        """清除用户详情缓存"""
        self.delete(f"users:info:{user_id}")
        self.delete(f"users:detail:{user_id}")
        logger.info(f"🗑️ 用户详情缓存已清除: {user_id}")
    
    # ==================== 装饰器 ====================
    
    def cached(self, key_prefix: str, expire: int = None):
        """
        缓存装饰器
        
        用法:
        @cache_service.cached("tasks:list", expire=300)
        def get_tasks(project_id, status):
            # 函数逻辑
            pass
        
        Args:
            key_prefix: 缓存键前缀
            expire: 过期时间（秒）
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存key
                cache_key = self._generate_cache_key(key_prefix, args, kwargs)
                
                # 尝试从缓存获取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.info(f"🎯 缓存命中: {cache_key}")
                    return cached_result
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 写入缓存
                if result is not None:
                    self.set(cache_key, result, expire)
                    logger.info(f"💾 缓存写入: {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, prefix: str, args: tuple, kwargs: dict) -> str:
        """
        生成缓存key
        
        将函数参数转换为哈希值，确保相同参数生成相同的key
        """
        # 将参数转换为字符串并哈希
        params_str = json.dumps({
            'args': args,
            'kwargs': kwargs
        }, sort_keys=True, default=json_serializer)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"
    
    # ==================== 统计信息 ====================
    
    def get_stats(self) -> dict:
        """获取Redis统计信息"""
        if not self.enabled:
            return {
                "enabled": False,
                "message": "Redis未连接"
            }
        
        try:
            info = self.redis_client.info()
            dbsize = self.redis_client.dbsize()
            
            # 计算命中率
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0
            
            return {
                "enabled": True,
                "used_memory": info.get('used_memory_human', 'N/A'),
                "total_keys": dbsize,
                "hit_rate": round(hit_rate, 2),
                "ops_per_sec": info.get('instantaneous_ops_per_sec', 0),
                "connected_clients": info.get('connected_clients', 0)
            }
        except Exception as e:
            logger.error(f"获取Redis统计信息失败: {e}")
            return {
                "enabled": False,
                "error": str(e)
            }

# 全局单例
cache_service = CacheService()

