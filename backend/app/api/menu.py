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
        # 项目管理
        {
            "path": "/project",
            "name": "Project",
            "component": "/index/index",
            "meta": {"title": "项目管理", "icon": "&#xe761;", "keepAlive": True},
            "children": [
                {"path": "dashboard", "name": "ProjectDashboard", "component": "/project/dashboard/index", "meta": {"title": "项目仪表板", "keepAlive": True}},
                {"path": "management", "name": "ProjectManagement", "component": "/project/management/index-new", "meta": {"title": "项目列表", "keepAlive": True}}
            ]
        },
        # 标注任务
        {
            "path": "/task",
            "name": "Task",
            "component": "/index/index",
            "meta": {"title": "标注任务", "icon": "&#xe70f;", "keepAlive": True},
            "children": [
                {"path": "task-pool", "name": "TaskPool", "component": "/project/task-pool/index", "meta": {"title": "任务池", "keepAlive": True}},
                {"path": "my-workspace", "name": "MyWorkspace", "component": "/project/my-workspace/index", "meta": {"title": "我的工作台", "keepAlive": True}},
                {"path": "task-review", "name": "TaskReview", "component": "/project/task-review/index", "meta": {"title": "任务审核", "keepAlive": True}}
            ]
        },
        # 工作日志
        {"path": "/work-log", "name": "WorkLog", "component": "/index/index", "meta": {"title": "工作日志", "icon": "&#xe7d9;", "keepAlive": True},
            "children": [
                {"path": "index", "name": "WorkLogManagement", "component": "/work-log/index", "meta": {"title": "工作计划", "keepAlive": True}},
                {"path": "records", "name": "WorkRecords", "component": "/work-log/records/index", "meta": {"title": "工作记录", "keepAlive": True}},
                {"path": "week-detail/:weekId", "name": "WorkLogWeekDetail", "component": "/work-log/week-detail", "meta": {"title": "工作周详情", "keepAlive": False, "isHide": True}}
            ]
        },
        # 知识与文章
        {"path": "/articles", "name": "Articles", "component": "/index/index", "meta": {"title": "知识与文章", "icon": "&#xe63a;", "keepAlive": True},
            "children": [
                {"path": "meeting", "name": "MeetingNotes", "component": "/project/articles/meeting/index", "meta": {"title": "会议记录", "keepAlive": True}},
                {"path": "model-test", "name": "ModelTests", "component": "/project/articles/model-test/index", "meta": {"title": "模型测试", "keepAlive": True}},
                {"path": "collaboration", "name": "CollaborationManagement", "component": "/collaboration/index", "meta": {"title": "团队协作", "keepAlive": True}},
                {"path": "create/:type", "name": "ArticleCreate", "component": "/project/articles/create/index", "meta": {"title": "发布文章", "keepAlive": False, "isHide": True}},
                {"path": "detail/:articleId", "name": "ArticleDetail", "component": "/project/articles/detail/index", "meta": {"title": "文章详情", "keepAlive": False, "isHide": True}},
                {"path": "collaboration/create", "name": "CollaborationCreate", "component": "/collaboration/create/index", "meta": {"title": "创建协作文档", "keepAlive": False, "isHide": True}},
                {"path": "collaboration/document/:documentId", "name": "CollaborationDocument", "component": "/collaboration/document", "meta": {"title": "协作文档", "keepAlive": False, "isHide": True}}
            ]
        },
        # 标注绩效
        {
            "path": "/performance",
            "name": "Performance",
            "component": "/index/index",
            "meta": {
                "title": "标注绩效",
                "icon": "&#xe860;",
                "keepAlive": True
            },
            "children": [
                {
                    "path": "personal",
                    "name": "PersonalPerformance",
                    "component": "/project/performance/personal",
                    "meta": {
                        "title": "个人绩效",
                        "keepAlive": True
                    }
                },
                {
                    "path": "team",
                    "name": "TeamPerformance",
                    "component": "/project/performance/team",
                    "meta": {
                        "title": "团队绩效",
                        "keepAlive": True
                    }
                }
            ]
        },
        {
            "path": "/system",
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
                    "component": "/system/user/index",
                    "meta": {
                        "title": "用户管理",
                        "icon": "&#xe753",
                        "keepAlive": True
                    }
                },
                {
                    "path": "role-management",
                    "name": "RoleManagement",
                    "component": "/system/role/index",
                    "meta": {
                        "title": "角色管理",
                        "icon": "&#xe84f;",
                        "keepAlive": True
                    }
                },
                {
                    "path": "user-center",
                    "name": "UserCenter",
                    "component": "/system/user-center/index",
                    "meta": {
                        "title": "个人中心",
                        "icon": "&#xe734",
                        "keepAlive": True,
                        "isHide": True
                    }
                }
            ]
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
                    # 隐藏路由（isHide: True）不受权限限制，始终保留
                    is_hidden = item.get("meta", {}).get("isHide", False)
                    keep_self = is_hidden or (item.get("name") in allowed)
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