"""
用户缓存服务
提供用户信息的缓存管理
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.services.cache_service import cache_service
from app.models.user import User

logger = logging.getLogger(__name__)

class UserCacheService:
    """用户缓存服务"""
    
    @staticmethod
    def get_user_info(user_id: str, db: Session) -> Optional[dict]:
        """
        获取用户信息（带缓存）
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            用户信息字典，不存在则返回None
        """
        cache_key = f"users:info:{user_id}"
        
        # 从缓存获取
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug(f"🎯 用户信息缓存命中: {user_id}")
            return cached
        
        # 查询数据库
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"⚠️ 用户不存在: {user_id}")
            return None
        
        # 构建用户信息
        user_info = {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role,
            "department": user.department,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "status": user.status
        }
        
        # 写入缓存（30分钟）
        cache_service.set(cache_key, user_info, expire=1800)
        logger.debug(f"💾 用户信息写入缓存: {user_id}")
        
        return user_info
    
    @staticmethod
    def get_active_users(db: Session) -> List[dict]:
        """
        获取活跃用户列表（带缓存）
        
        Args:
            db: 数据库会话
            
        Returns:
            活跃用户列表
        """
        cache_key = "users:list:active"
        
        # 从缓存获取
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug(f"🎯 活跃用户列表缓存命中")
            return cached
        
        # 查询数据库
        users = db.query(User).filter(User.status == "active").all()
        user_list = [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "role": u.role,
                "department": u.department,
                "avatar_url": u.avatar_url
            }
            for u in users
        ]
        
        # 写入缓存（30分钟）
        cache_service.set(cache_key, user_list, expire=1800)
        logger.debug(f"💾 活跃用户列表写入缓存: {len(user_list)} 个用户")
        
        return user_list
    
    @staticmethod
    def get_users_by_role(role: str, db: Session) -> List[dict]:
        """
        按角色获取用户列表（带缓存）
        
        Args:
            role: 角色名称
            db: 数据库会话
            
        Returns:
            用户列表
        """
        cache_key = f"users:list:role:{role}"
        
        # 从缓存获取
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug(f"🎯 角色用户列表缓存命中: {role}")
            return cached
        
        # 查询数据库
        users = db.query(User).filter(
            User.role == role,
            User.status == "active"
        ).all()
        
        user_list = [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "department": u.department
            }
            for u in users
        ]
        
        # 写入缓存（30分钟）
        cache_service.set(cache_key, user_list, expire=1800)
        logger.debug(f"💾 角色用户列表写入缓存: {role} ({len(user_list)} 个用户)")
        
        return user_list
    
    @staticmethod
    def get_users_by_department(department: str, db: Session) -> List[dict]:
        """
        按部门获取用户列表（带缓存）
        
        Args:
            department: 部门名称
            db: 数据库会话
            
        Returns:
            用户列表
        """
        cache_key = f"users:list:dept:{department}"
        
        # 从缓存获取
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug(f"🎯 部门用户列表缓存命中: {department}")
            return cached
        
        # 查询数据库
        users = db.query(User).filter(
            User.department == department,
            User.status == "active"
        ).all()
        
        user_list = [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "role": u.role
            }
            for u in users
        ]
        
        # 写入缓存（30分钟）
        cache_service.set(cache_key, user_list, expire=1800)
        logger.debug(f"💾 部门用户列表写入缓存: {department} ({len(user_list)} 个用户)")
        
        return user_list
    
    @staticmethod
    def invalidate_user_cache(user_id: str):
        """
        清除用户缓存
        
        Args:
            user_id: 用户ID
        """
        # 清除用户详情缓存
        cache_service.invalidate_user_detail_cache(user_id)
        
        # 清除列表缓存（用户信息变更可能影响列表）
        cache_service.delete_pattern("users:list:*")
        
        logger.info(f"🗑️ 用户缓存已清除: {user_id}")
    
    @staticmethod
    def invalidate_all_users_cache():
        """清除所有用户缓存"""
        cache_service.invalidate_users_cache()
        logger.info("🗑️ 所有用户缓存已清除")

# 全局实例
user_cache_service = UserCacheService()

