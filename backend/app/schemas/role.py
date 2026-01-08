from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    role: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class RoleCreate(RoleBase):
    permissions: Optional[str] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[str] = None

class RoleResponse(RoleBase):
    id: str
    created_at: datetime
    updated_at: datetime
    permissions: Optional[str] = None
    
    class Config:
        from_attributes = True