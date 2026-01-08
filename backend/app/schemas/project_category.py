"""
项目分类相关的 Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCategoryBase(BaseModel):
    """项目分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    type: str = Field(..., min_length=1, max_length=50, description="分类类型标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: int = Field(0, description="排序顺序")


class ProjectCategoryCreate(ProjectCategoryBase):
    """创建项目分类"""
    project_id: str = Field(..., description="所属项目ID")


class ProjectCategoryUpdate(BaseModel):
    """更新项目分类"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    sort_order: Optional[int] = None


class ProjectCategoryResponse(ProjectCategoryBase):
    """项目分类响应模型"""
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectCategoryListResponse(BaseModel):
    """项目分类列表响应"""
    items: list[ProjectCategoryResponse]
    total: int

