from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Set, Optional

from app.database import get_db
from app.utils.security import get_current_user
from app.models.role import Role
from typing import Union, Iterable


def _load_role_permissions(db: Session, role_code: Optional[str] = None, role_id: Optional[str] = None) -> Set[str]:
    """Load permissions (as a set of menu `name` strings) for a role from DB."""
    role: Optional[Role] = None
    if role_id:
        role = db.query(Role).filter(getattr(Role, 'id') == role_id).first()
    if role is None and role_code:
        # try by role code, then by name
        by_code = db.query(Role).filter(getattr(Role, 'role') == role_code).first()
        role = by_code or db.query(Role).filter(getattr(Role, 'name') == role_code).first()

    if role is None or not getattr(role, 'permissions', None):
        return set()

    raw = getattr(role, 'permissions', '')
    try:
        import json
        data = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(data, list):
            return set(str(x) for x in data)
        return set()
    except Exception:
        return set()


def check_permission(db: Session, current_user, permission_name: Union[str, Iterable[str]]) -> bool:
    """Check if current user has the specified permission(s).
    
    Returns True if user has permission, False otherwise.
    """
    role_id = getattr(current_user, 'role_id', None)
    role_code = getattr(current_user, 'role', None)
    permissions = _load_role_permissions(db, role_code=role_code, role_id=role_id)
    
    # support multiple permission names (any pass)
    if isinstance(permission_name, str):
        return permission_name in permissions
    else:
        for p in permission_name:
            if p in permissions:
                return True
        return False


def require_permission(permission_name: Union[str, Iterable[str]]):
    """FastAPI dependency factory to enforce a page/API permission by menu name.

    It reads the current user's role, loads its permissions from `roles.permissions`,
    and ensures `permission_name` is present. Otherwise, raises 403.
    """

    def _dep(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        if check_permission(db, current_user, permission_name):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，缺少访问权限: {permission_name}"
        )

    return _dep


