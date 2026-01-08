from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False, index=True)  # 角色名称
    role = Column(String(50), unique=True, nullable=False, index=True)  # 角色编码
    description = Column(Text)  # 描述
    is_active = Column(Boolean, default=True)  # 是否启用
    # 存储角色的菜单/按钮权限（JSON 字符串，前端使用 keys 列表即可）
    permissions = Column(Text)  # 可为空，格式如: '["RouteName_btn_add", "RouteName_btn_edit"]'
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Role(id='{self.id}', name='{self.name}', role='{self.role}')>"