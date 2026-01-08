"""
统计数据缓存服务
用于缓存复杂的统计查询结果，提升性能
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import logging
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class StatsCacheService:
    """统计数据缓存服务"""
    
    def __init__(self):
        self.cache = cache_service
        
        # 缓存过期时间（秒）
        self.DASHBOARD_STATS_TTL = 900  # 15分钟
        self.PERFORMANCE_STATS_TTL = 900  # 15分钟
        self.PROJECT_STATS_TTL = 600  # 10分钟
        self.WORKLOG_STATS_TTL = 900  # 15分钟
    
    # ==================== 项目仪表板缓存 ====================
    
    def get_dashboard_stats(self, cache_key_suffix: str = "") -> Optional[Dict]:
        """获取仪表板统计缓存"""
        cache_key = f"stats:dashboard:general{':' + cache_key_suffix if cache_key_suffix else ''}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 仪表板统计缓存命中: {cache_key}")
        return cached
    
    def set_dashboard_stats(self, data: Dict, cache_key_suffix: str = ""):
        """设置仪表板统计缓存"""
        cache_key = f"stats:dashboard:general{':' + cache_key_suffix if cache_key_suffix else ''}"
        self.cache.set(cache_key, data, expire=self.DASHBOARD_STATS_TTL)
        logger.info(f"💾 仪表板统计已缓存: {cache_key}, TTL={self.DASHBOARD_STATS_TTL}s")
    
    def invalidate_dashboard_stats(self):
        """清除仪表板统计缓存"""
        self.cache.delete_pattern("stats:dashboard:*")
        logger.info("🗑️ 仪表板统计缓存已清除")
    
    # ==================== 项目统计缓存 ====================
    
    def get_project_stats(self, project_id: str) -> Optional[Dict]:
        """获取项目统计缓存"""
        cache_key = f"stats:project:{project_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 项目统计缓存命中: {cache_key}")
        return cached
    
    def set_project_stats(self, project_id: str, data: Dict):
        """设置项目统计缓存"""
        cache_key = f"stats:project:{project_id}"
        self.cache.set(cache_key, data, expire=self.PROJECT_STATS_TTL)
        logger.info(f"💾 项目统计已缓存: {cache_key}, TTL={self.PROJECT_STATS_TTL}s")
    
    def invalidate_project_stats(self, project_id: str = None):
        """清除项目统计缓存"""
        if project_id:
            cache_key = f"stats:project:{project_id}"
            self.cache.delete(cache_key)
            logger.info(f"🗑️ 项目统计缓存已清除: {project_id}")
        else:
            self.cache.delete_pattern("stats:project:*")
            logger.info("🗑️ 所有项目统计缓存已清除")
    
    # ==================== 绩效统计缓存 ====================
    
    def get_performance_stats(self, user_id: str = None, period: str = "monthly") -> Optional[Dict]:
        """获取绩效统计缓存"""
        if user_id:
            cache_key = f"stats:performance:user:{user_id}:{period}"
        else:
            cache_key = f"stats:performance:team:{period}"
        
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 绩效统计缓存命中: {cache_key}")
        return cached
    
    def set_performance_stats(self, data: Dict, user_id: str = None, period: str = "monthly"):
        """设置绩效统计缓存"""
        if user_id:
            cache_key = f"stats:performance:user:{user_id}:{period}"
        else:
            cache_key = f"stats:performance:team:{period}"
        
        self.cache.set(cache_key, data, expire=self.PERFORMANCE_STATS_TTL)
        logger.info(f"💾 绩效统计已缓存: {cache_key}, TTL={self.PERFORMANCE_STATS_TTL}s")
    
    def invalidate_performance_stats(self, user_id: str = None, period: str = None):
        """清除绩效统计缓存"""
        if user_id and period:
            cache_key = f"stats:performance:user:{user_id}:{period}"
            self.cache.delete(cache_key)
            logger.info(f"🗑️ 用户绩效缓存已清除: {user_id}, {period}")
        elif user_id:
            self.cache.delete_pattern(f"stats:performance:user:{user_id}:*")
            logger.info(f"🗑️ 用户所有绩效缓存已清除: {user_id}")
        elif period:
            self.cache.delete_pattern(f"stats:performance:*:{period}")
            logger.info(f"🗑️ {period} 周期绩效缓存已清除")
        else:
            self.cache.delete_pattern("stats:performance:*")
            logger.info("🗑️ 所有绩效统计缓存已清除")
    
    # ==================== 工作日志统计缓存 ====================
    
    def get_worklog_stats(self, week_id: str = None, user_id: str = None) -> Optional[Dict]:
        """获取工作日志统计缓存"""
        if week_id:
            cache_key = f"stats:worklog:week:{week_id}"
        elif user_id:
            cache_key = f"stats:worklog:user:{user_id}"
        else:
            cache_key = "stats:worklog:summary"
        
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 工作日志统计缓存命中: {cache_key}")
        return cached
    
    def set_worklog_stats(self, data: Dict, week_id: str = None, user_id: str = None):
        """设置工作日志统计缓存"""
        if week_id:
            cache_key = f"stats:worklog:week:{week_id}"
        elif user_id:
            cache_key = f"stats:worklog:user:{user_id}"
        else:
            cache_key = "stats:worklog:summary"
        
        self.cache.set(cache_key, data, expire=self.WORKLOG_STATS_TTL)
        logger.info(f"💾 工作日志统计已缓存: {cache_key}, TTL={self.WORKLOG_STATS_TTL}s")
    
    def invalidate_worklog_stats(self, week_id: str = None, user_id: str = None):
        """清除工作日志统计缓存"""
        if week_id:
            cache_key = f"stats:worklog:week:{week_id}"
            self.cache.delete(cache_key)
            logger.info(f"🗑️ 工作周统计缓存已清除: {week_id}")
        elif user_id:
            self.cache.delete_pattern(f"stats:worklog:user:{user_id}")
            logger.info(f"🗑️ 用户工作日志缓存已清除: {user_id}")
        else:
            self.cache.delete_pattern("stats:worklog:*")
            logger.info("🗑️ 所有工作日志统计缓存已清除")
    
    # ==================== 通用统计辅助方法 ====================
    
    def get_or_compute(
        self, 
        cache_key: str, 
        compute_func: callable, 
        ttl: int = 900
    ) -> Any:
        """
        通用缓存模式：先检查缓存，未命中则计算并缓存
        
        Args:
            cache_key: 缓存键
            compute_func: 计算函数（无参数）
            ttl: 过期时间（秒）
        
        Returns:
            计算结果
        """
        # 尝试从缓存获取
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"🎯 缓存命中: {cache_key}")
            return cached
        
        # 缓存未命中，执行计算
        logger.info(f"💨 缓存未命中，执行计算: {cache_key}")
        result = compute_func()
        
        # 写入缓存
        self.cache.set(cache_key, result, expire=ttl)
        logger.info(f"💾 计算结果已缓存: {cache_key}, TTL={ttl}s")
        
        return result


# 全局实例
stats_cache_service = StatsCacheService()

