from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.utils.security import get_current_user
from app.models.role import Role
from app.models.user import User
import json


# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/list")
def get_menu_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    logger.info(f"🍽️ [MenuAPI] 获取菜单列表: {current_user.username}, 角色: {current_user.role}")
    
    # 完整菜单定义（不再包含硬编码的 roles 字段）
    menu_list = [
        {
            "name": "Dashboard",
            "path": "/dashboard",
            "component": "/index/index",
            "meta": {
                "title": "menus.dashboard.title",
                "icon": "&#xe721;",
                "keepAlive": True
            },
            "children": [
                {
                    "path": "console",
                    "name": "Console",
                    "component": "/dashboard/console",
                    "meta": {
                        "title": "menus.dashboard.console",
                        "keepAlive": False,
                        "fixedTab": True
                    }
                }
            ]
        },
        {
            "path": "project",
            "name": "Project",
            "component": "/index/index",
            "meta": {
                "title": "项目管理",
                "icon": "&#xe761",
                "keepAlive": True
            },
            "children": [
                {
                    "path": "dashboard",
                    "name": "ProjectDashboard",
                    "component": "/project/dashboard/index",
                    "meta": {
                        "title": "项目仪表板",
                        "icon": "&#xe77d",
                        "keepAlive": True
                    }
                },
                {
                    "path": "management",
                    "name": "ProjectManagement",
                    "component": "/project/management/index-new",
                    "meta": {
                        "title": "项目管理",
                        "icon": "&#xe77d",
                        "keepAlive": True
                    }
                },
                {
                    "path": "task-pool",
                    "name": "TaskPool",
                    "component": "/project/task-pool/index",
                    "meta": {
                        "title": "任务池",
                        "icon": "&#xe7b6",
                        "keepAlive": True
                    }
                },
                {
                    "path": "my-workspace",
                    "name": "MyWorkspace",
                    "component": "/project/my-workspace/index",
                    "meta": {
                        "title": "我的工作台",
                        "icon": "&#xe7b0",
                        "keepAlive": True
                    }
                },
                {
                    "path": "task-review",
                    "name": "TaskReview",
                    "component": "/project/task-review/index",
                    "meta": {
                        "title": "任务审核",
                        "icon": "&#xe7b0",
                        "keepAlive": True
                    }
                }
            ]
        },
        {
            "path": "performance",
            "name": "Performance",
            "component": "/index/index",
            "meta": {
                "title": "绩效系统",
                "icon": "&#xe860;",
                "keepAlive": True
            },
            "children": [
                {
                    "path": "team",
                    "name": "TeamPerformance",
                    "component": "/project/performance/team",
                    "meta": {
                        "title": "团队绩效",
                        "icon": "&#xe860;",
                        "keepAlive": True
                    }
                },
                {
                    "path": "personal",
                    "name": "PersonalPerformance",
                    "component": "/project/performance/personal",
                    "meta": {
                        "title": "我的绩效",
                        "icon": "&#xe860;",
                        "keepAlive": True
                    }
                }
            ]
        },
        {
            "path": "system",
            "name": "System",
            "component": "/index/index",
            "meta": {
                "title": "系统管理",
                "icon": "&#xe7b9;",
                "keepAlive": True
            },
            "children": [
                {
                    "path": "user-management",
                    "name": "UserManagement",
                    "component": "/system/user-management/index",
                    "meta": {
                        "title": "用户管理",
                        "icon": "&#xe7b9;",
                        "keepAlive": True
                    }
                },
                {
                    "path": "role-management",
                    "name": "RoleManagement",
                    "component": "/system/role-management/index",
                    "meta": {
                        "title": "角色管理",
                        "icon": "&#xe7b9;",
                        "keepAlive": True
                    }
                }
            ]
        },
        {
            "path": "center",
            "name": "UserCenter",
            "component": "/center/index",
            "meta": {
                "title": "个人中心",
                "icon": "&#xe7b9;",
                "keepAlive": True
            }
        }
    ]
    
    # 根据用户角色权限过滤菜单
    try:
        allowed = []
        if current_user.role.lower() in ['admin', 'super', 'administrator']:
            # 管理员可以访问所有菜单
            allowed = None  # None 表示不过滤
        else:
            # 其他角色根据 roles.permissions 过滤
            role_row = db.query(Role).filter(Role.role.ilike(current_user.role)).first()
            if role_row and role_row.permissions:
                try:
                    allowed = json.loads(role_row.permissions)
                    if not isinstance(allowed, list):
                        allowed = []
                except (json.JSONDecodeError, ValueError):
                    allowed = []
                    logger.warning(f"⚠️ [MenuAPI] 角色权限格式错误: {current_user.role}")
            else:
                allowed = []
                logger.warning(f"⚠️ [MenuAPI] 角色权限为空或角色不存在: {current_user.role}")
        
        # 菜单过滤逻辑
        if allowed is not None:  # 如果需要过滤
            def filter_menus(items):
                if not allowed:
                    return []
                filtered = []
                for item in items:
                    children = item.get("children") or []
                    kept_children = filter_menus(children) if children else []
                    keep_self = item.get("name") in allowed
                    if keep_self or kept_children:
                        new_item = dict(item)
                        if kept_children:
                            new_item["children"] = kept_children
                        filtered.append(new_item)
                return filtered

            menu_list = filter_menus(menu_list)
    except Exception as e:
        logger.warning(f"⚠️ [MenuAPI] 角色权限过滤失败: {e}")

    logger.info(f"✅ [MenuAPI] 返回菜单数量: {len(menu_list)}")
    return {"menuList": menu_list}
