"""
通知 API
提供通知的查询、标记已读、删除等功能
基于 Redis 存储，通知 7 天自动过期
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from app.services.redis_notification_storage import redis_notification_storage
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["通知"])


@router.get("/")
def get_notifications(
    limit: int = Query(50, le=200, description="返回数量限制"),
    current_user = Depends(get_current_user)
):
    """
    获取当前用户的未读通知列表（从 Redis）
    注意：Redis 中只保存未读通知，读取后自动删除
    """
    try:
        # 从 Redis 获取未读通知
        notifications = redis_notification_storage.get_unread_notifications(
            user_id=current_user.id,
            limit=limit
        )
        
        logger.info(f"📬 [NotificationAPI] 用户 {current_user.username} 查询通知: count={len(notifications)}")
        
        return {
            "success": True,
            "total": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"❌ [NotificationAPI] 查询通知失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询通知失败: {str(e)}")


@router.get("/unread-count")
def get_unread_count(
    current_user = Depends(get_current_user)
):
    """
    获取未读通知数量（从 Redis）
    """
    try:
        count = redis_notification_storage.get_unread_count(user_id=current_user.id)
        
        logger.info(f"📬 [NotificationAPI] 用户 {current_user.username} 未读通知数: {count}")
        
        return {
            "success": True,
            "count": count
        }
    except Exception as e:
        logger.error(f"❌ [NotificationAPI] 查询未读通知数失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """
    标记通知为已读（从 Redis 中删除）
    """
    try:
        success = redis_notification_storage.mark_as_read(
            user_id=current_user.id,
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        return {
            "success": True,
            "message": "已标记为已读"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [NotificationAPI] 标记已读失败: {e}")
        raise HTTPException(status_code=500, detail=f"标记失败: {str(e)}")


@router.post("/read-all")
def mark_all_as_read(
    current_user = Depends(get_current_user)
):
    """
    标记所有通知为已读（清空 Redis 中的通知列表）
    """
    try:
        # 先获取数量
        count = redis_notification_storage.get_unread_count(user_id=current_user.id)
        
        # 标记全部已读（清空列表）
        success = redis_notification_storage.mark_all_as_read(user_id=current_user.id)
        
        if success:
            logger.info(f"✅ [NotificationAPI] 用户 {current_user.username} 标记全部已读，共 {count} 条")
        
        return {
            "success": True,
            "message": f"已标记 {count} 条通知为已读",
            "count": count
        }
    except Exception as e:
        logger.error(f"❌ [NotificationAPI] 全部标记已读失败: {e}")
        raise HTTPException(status_code=500, detail=f"标记失败: {str(e)}")


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """
    删除通知（从 Redis 中移除）
    """
    try:
        success = redis_notification_storage.delete_notification(
            user_id=current_user.id,
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        logger.info(f"✅ [NotificationAPI] 通知已删除: {notification_id}")
        
        return {
            "success": True,
            "message": "通知已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [NotificationAPI] 删除通知失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.delete("/clear-read")
def clear_read_notifications(
    current_user = Depends(get_current_user)
):
    """
    清空所有已读通知
    注意：在 Redis 实现中，读取后的通知会自动删除，此接口等同于 mark_all_as_read
    """
    try:
        # 先获取数量
        count = redis_notification_storage.get_unread_count(user_id=current_user.id)
        
        # 清空所有通知
        success = redis_notification_storage.mark_all_as_read(user_id=current_user.id)
        
        if success:
            logger.info(f"✅ [NotificationAPI] 用户 {current_user.username} 清空通知，共 {count} 条")
        
        return {
            "success": True,
            "message": f"已清空 {count} 条通知",
            "count": count
        }
    except Exception as e:
        logger.error(f"❌ [NotificationAPI] 清空通知失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空失败: {str(e)}")

