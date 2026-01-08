"""
文章/知识库缓存服务
用于缓存文章列表、详情、导航树等，提升文章页面加载速度
"""
from typing import Optional, Dict, Any, List
import logging
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class ArticleCacheService:
    """文章缓存服务"""
    
    def __init__(self):
        self.cache = cache_service
        
        # 缓存过期时间（秒）
        self.ARTICLE_DETAIL_TTL = 1200  # 20分钟
        self.ARTICLE_LIST_TTL = 600  # 10分钟
        self.ARTICLE_TREE_TTL = 1800  # 30分钟
        self.ARTICLE_HISTORY_TTL = 900  # 15分钟
    
    # ==================== 文章详情缓存 ====================
    
    def get_article_detail(self, article_id: str) -> Optional[Dict]:
        """获取文章详情缓存"""
        cache_key = f"article:detail:{article_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 文章详情缓存命中: {article_id}")
        return cached
    
    def set_article_detail(self, article_id: str, data: Dict):
        """设置文章详情缓存"""
        cache_key = f"article:detail:{article_id}"
        self.cache.set(cache_key, data, expire=self.ARTICLE_DETAIL_TTL)
        logger.info(f"💾 文章详情已缓存: {article_id}, TTL={self.ARTICLE_DETAIL_TTL}s")
    
    def invalidate_article_detail(self, article_id: str):
        """清除文章详情缓存"""
        cache_key = f"article:detail:{article_id}"
        self.cache.delete(cache_key)
        logger.info(f"🗑️ 文章详情缓存已清除: {article_id}")
    
    # ==================== 文章列表缓存 ====================
    
    def get_article_list(
        self, 
        article_type: str = None,
        status: str = None,
        project_id: str = None,
        page: int = 1,
        page_size: int = 20
    ) -> Optional[Dict]:
        """获取文章列表缓存"""
        cache_key = self._generate_list_cache_key(
            article_type, status, project_id, page, page_size
        )
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 文章列表缓存命中: {cache_key}")
        return cached
    
    def set_article_list(
        self,
        data: Dict,
        article_type: str = None,
        status: str = None,
        project_id: str = None,
        page: int = 1,
        page_size: int = 20
    ):
        """设置文章列表缓存"""
        cache_key = self._generate_list_cache_key(
            article_type, status, project_id, page, page_size
        )
        self.cache.set(cache_key, data, expire=self.ARTICLE_LIST_TTL)
        logger.info(f"💾 文章列表已缓存: {cache_key}, TTL={self.ARTICLE_LIST_TTL}s")
    
    def _generate_list_cache_key(
        self,
        article_type: str = None,
        status: str = None,
        project_id: str = None,
        page: int = 1,
        page_size: int = 20
    ) -> str:
        """生成文章列表缓存键"""
        type_part = article_type or "all"
        status_part = status or "all"
        project_part = project_id or "all"
        return f"article:list:{type_part}:{status_part}:{project_part}:{page}:{page_size}"
    
    def invalidate_article_list(
        self,
        article_type: str = None,
        project_id: str = None
    ):
        """清除文章列表缓存"""
        if article_type and project_id:
            # 清除特定类型和项目的列表
            pattern = f"article:list:{article_type}:*:{project_id}:*"
        elif article_type:
            # 清除特定类型的所有列表
            pattern = f"article:list:{article_type}:*"
        elif project_id:
            # 清除特定项目的所有列表
            pattern = f"article:list:*:*:{project_id}:*"
        else:
            # 清除所有文章列表
            pattern = "article:list:*"
        
        self.cache.delete_pattern(pattern)
        logger.info(f"🗑️ 文章列表缓存已清除: {pattern}")
    
    # ==================== 文章导航树缓存 ====================
    
    def get_article_tree(self, article_type: str) -> Optional[Dict]:
        """获取文章导航树缓存"""
        cache_key = f"article:tree:{article_type}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 文章导航树缓存命中: {article_type}")
        return cached
    
    def set_article_tree(self, article_type: str, data: Dict):
        """设置文章导航树缓存"""
        cache_key = f"article:tree:{article_type}"
        self.cache.set(cache_key, data, expire=self.ARTICLE_TREE_TTL)
        logger.info(f"💾 文章导航树已缓存: {article_type}, TTL={self.ARTICLE_TREE_TTL}s")
    
    def invalidate_article_tree(self, article_type: str = None):
        """清除文章导航树缓存"""
        if article_type:
            cache_key = f"article:tree:{article_type}"
            self.cache.delete(cache_key)
            logger.info(f"🗑️ 文章导航树缓存已清除: {article_type}")
        else:
            self.cache.delete_pattern("article:tree:*")
            logger.info("🗑️ 所有文章导航树缓存已清除")
    
    # ==================== 文章编辑历史缓存 ====================
    
    def get_article_history(self, article_id: str) -> Optional[List]:
        """获取文章编辑历史缓存"""
        cache_key = f"article:history:{article_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"🎯 文章编辑历史缓存命中: {article_id}")
        return cached
    
    def set_article_history(self, article_id: str, data: List):
        """设置文章编辑历史缓存"""
        cache_key = f"article:history:{article_id}"
        self.cache.set(cache_key, data, expire=self.ARTICLE_HISTORY_TTL)
        logger.info(f"💾 文章编辑历史已缓存: {article_id}, TTL={self.ARTICLE_HISTORY_TTL}s")
    
    def invalidate_article_history(self, article_id: str):
        """清除文章编辑历史缓存"""
        cache_key = f"article:history:{article_id}"
        self.cache.delete(cache_key)
        logger.info(f"🗑️ 文章编辑历史缓存已清除: {article_id}")
    
    # ==================== 综合缓存清除 ====================
    
    def invalidate_article_all(self, article_id: str):
        """清除文章相关的所有缓存"""
        # 清除详情
        self.invalidate_article_detail(article_id)
        # 清除编辑历史
        self.invalidate_article_history(article_id)
        # 清除所有列表（因为不知道文章在哪个列表中）
        self.invalidate_article_list()
        # 清除所有导航树
        self.invalidate_article_tree()
        logger.info(f"🗑️ 文章所有相关缓存已清除: {article_id}")
    
    def invalidate_all_articles(self):
        """清除所有文章缓存"""
        self.cache.delete_pattern("article:*")
        logger.info("🗑️ 所有文章缓存已清除")


# 全局实例
article_cache_service = ArticleCacheService()

