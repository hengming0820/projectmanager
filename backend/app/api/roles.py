from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.models.role import Role
from app.utils.security import get_current_admin_user, get_current_user
from app.utils.permissions import require_permission
from app.models.user import User

# 添加redirect_slashes=False避免重定向问题
router = APIRouter(redirect_slashes=False)

@router.get("/")
def get_roles(
    current: int = 1,
    size: int = 10,
    name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取角色列表（所有登录用户可访问）"""
    actual_skip = (current - 1) * size
    actual_limit = size
    
    query = db.query(Role)
    
    if name:
        query = query.filter(Role.name.contains(name))
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    roles = query.offset(actual_skip).limit(actual_limit).all()
    
    return {
        "code": 200,
        "msg": "成功",
        "data": {
            "list": roles,
            "total": total,
            "current": current,
            "size": size
        }
    }

@router.get("/{role_id}")
def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取角色详情（所有登录用户可访问）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {
        "code": 200,
        "msg": "成功",
        "data": role
    }

@router.post("/")
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("RoleManagement"))
):
    """创建角色（需菜单权限 RoleManagement）"""
    # 检查角色名称是否已存在
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    
    # 检查角色编码是否已存在
    existing_role_code = db.query(Role).filter(Role.role == role_data.role).first()
    if existing_role_code:
        raise HTTPException(status_code=400, detail="角色编码已存在")
    
    # 创建新角色
    db_role = Role(**role_data.dict())
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return {
        "code": 200,
        "msg": "角色创建成功",
        "data": db_role
    }

@router.put("/{role_id}")
def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("RoleManagement"))
):
    """更新角色信息（需菜单权限 RoleManagement）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查角色名称是否已存在（排除自己）
    if role_data.name:
        existing_role = db.query(Role).filter(
            Role.name == role_data.name,
            Role.id != role_id
        ).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="角色名称已存在")
    
    # 检查角色编码是否已存在（排除自己）
    if role_data.role:
        existing_role_code = db.query(Role).filter(
            Role.role == role_data.role,
            Role.id != role_id
        ).first()
        if existing_role_code:
            raise HTTPException(status_code=400, detail="角色编码已存在")
    
    # 更新角色信息
    for field, value in role_data.dict(exclude_unset=True).items():
        setattr(role, field, value)
    
    db.commit()
    db.refresh(role)
    return {
        "code": 200,
        "msg": "角色更新成功",
        "data": role
    }

@router.get("/{role_id}/permissions")
def get_role_permissions(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("RoleManagement"))
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return { "code": 200, "msg": "成功", "data": role.permissions or "[]" }

@router.put("/{role_id}/permissions")
def update_role_permissions(
    role_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("RoleManagement"))
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    # 期望 payload: { "permissions": ["Route_btn_add", ...] }
    import json
    perms = payload.get("permissions", [])
    if not isinstance(perms, list):
        raise HTTPException(status_code=400, detail="permissions 应为数组")
    role.permissions = json.dumps(perms, ensure_ascii=False)
    db.commit()
    db.refresh(role)
    return { "code": 200, "msg": "权限已更新", "data": perms }

@router.delete("/{role_id}")
def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("RoleManagement"))
):
    """删除角色（仅管理员）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查是否有用户使用此角色
    from app.models.user import User
    users_with_role = db.query(User).filter(User.role == role.role).count()
    
    if users_with_role > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"还有 {users_with_role} 个用户使用此角色，无法删除"
        )
    
    db.delete(role)
    db.commit()
    return {
        "code": 200,
        "msg": "角色删除成功",
        "data": None
    }