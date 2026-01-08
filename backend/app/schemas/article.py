from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ArticleBase(BaseModel):
    title: str
    content: str = ""
    summary: Optional[str] = None
    type: str  # 支持任意文章类型，不再限制为meeting/model_test
    status: str = Field(default="draft")
    tags: List[str] = []
    # 新增字段（可选）：封面、分类、公开性
    cover_url: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = True
    # 新增：可编辑成员与所属部门
    editable_user_ids: Optional[List[str]] = None
    editable_roles: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    # 项目关联
    project_id: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    cover_url: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    editable_user_ids: Optional[List[str]] = None
    editable_roles: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    project_id: Optional[str] = None


class ArticleResponse(ArticleBase):
    id: str
    author_id: str
    author_name: str
    view_count: int
    edit_count: int
    version: int
    # 编辑锁字段
    is_locked: bool = False
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # 项目关联（响应时包含）
    project_id: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleQueryParams(BaseModel):
    page: int = 1
    page_size: int = 20
    type: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    # 新增筛选：年份、月份、作者（按姓名模糊匹配）
    year: Optional[int] = None
    month: Optional[int] = None
    author_name: Optional[str] = None
    # 项目筛选
    project_id: Optional[str] = None


class ArticleListResponse(BaseModel):
    items: List[ArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ArticleEditHistoryItem(BaseModel):
    id: str
    article_id: str
    editor_id: str
    editor_name: str
    action: str
    changes_summary: Optional[str]
    version_before: Optional[int]
    version_after: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


