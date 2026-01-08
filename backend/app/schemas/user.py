from pydantic import BaseModel, EmailStr, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime, date
import json


class UserProfileUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None
    hire_date: Optional[date] = None


class UserProfileResponse(BaseModel):
    id: str
    username: str
    real_name: str
    email: EmailStr
    role: str
    avatar_url: Optional[str] = None
    department: Optional[str] = None
    status: str
    tags: Optional[List[str]] = None
    hire_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """将 JSON 字符串转换为列表"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return []
        if isinstance(v, list):
            return v
        return []
    
    @field_serializer('hire_date')
    def serialize_hire_date(self, hire_date: Optional[date], _info):
        """序列化hire_date为字符串"""
        if hire_date is None:
            return None
        return hire_date.isoformat()

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    real_name: str
    email: EmailStr
    role: str
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    hire_date: Optional[date] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[str] = None
    hire_date: Optional[date] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: str
    status: str
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """将 JSON 字符串转换为列表"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return []
        if isinstance(v, list):
            return v
        return []
    
    @field_serializer('hire_date')
    def serialize_hire_date(self, hire_date: Optional[date], _info):
        """序列化hire_date为字符串"""
        if hire_date is None:
            return None
        return hire_date.isoformat()
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse 