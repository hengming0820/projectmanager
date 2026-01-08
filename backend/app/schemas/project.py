from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, datetime

# 定义分类类型
ProjectCategory = Literal["case", "ai_annotation"]
CaseSubCategory = Literal["trial", "research", "paid"] 
AISubCategory = Literal["research_ai", "daily"]

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    priority: str = "medium"
    category: Optional[ProjectCategory] = None
    sub_category: Optional[str] = None  # 使用字符串类型，因为子分类取决于主分类
    start_date: date
    end_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[ProjectCategory] = None
    sub_category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectResponse(ProjectBase):
    id: str
    created_by: str
    total_tasks: int
    completed_tasks: int
    assigned_tasks: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 