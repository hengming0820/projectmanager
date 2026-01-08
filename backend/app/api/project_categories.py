"""
项目分类 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.utils.security import get_current_user
from app.models.project_category import ProjectCategory
from app.models.project import Project
from app.models.user import User
from app.schemas.project_category import (
    ProjectCategoryCreate,
    ProjectCategoryUpdate,
    ProjectCategoryResponse,
    ProjectCategoryListResponse,
)

router = APIRouter()


@router.get("/projects/{project_id}/categories", response_model=ProjectCategoryListResponse)
def get_project_categories(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目的所有分类"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 查询分类，按排序顺序
    categories = db.query(ProjectCategory).filter(
        ProjectCategory.project_id == project_id
    ).order_by(ProjectCategory.sort_order, ProjectCategory.created_at).all()
    
    return {
        "items": [cat.to_dict() for cat in categories],
        "total": len(categories)
    }


@router.post("/projects/{project_id}/categories", response_model=ProjectCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_project_category(
    project_id: str,
    payload: ProjectCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建项目分类"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证用户权限（只有管理员可以创建分类）
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="没有权限创建分类")
    
    # 检查同一项目下是否已存在相同 type 的分类
    existing = db.query(ProjectCategory).filter(
        ProjectCategory.project_id == project_id,
        ProjectCategory.type == payload.type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"分类类型 '{payload.type}' 已存在")
    
    # 检查同一项目下是否已存在相同 name 的分类
    existing_name = db.query(ProjectCategory).filter(
        ProjectCategory.project_id == project_id,
        ProjectCategory.name == payload.name
    ).first()
    if existing_name:
        raise HTTPException(status_code=400, detail=f"分类名称 '{payload.name}' 已存在")
    
    # 创建分类
    category = ProjectCategory(
        project_id=project_id,
        name=payload.name,
        type=payload.type,
        icon=payload.icon,
        description=payload.description,
        sort_order=payload.sort_order
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category.to_dict()


@router.put("/categories/{category_id}", response_model=ProjectCategoryResponse)
def update_project_category(
    category_id: str,
    payload: ProjectCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目分类"""
    # 查询分类
    category = db.query(ProjectCategory).filter(ProjectCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 验证用户权限
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="没有权限修改分类")
    
    # 如果修改名称，检查是否重复
    if payload.name is not None and payload.name != category.name:
        existing = db.query(ProjectCategory).filter(
            ProjectCategory.project_id == category.project_id,
            ProjectCategory.name == payload.name,
            ProjectCategory.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"分类名称 '{payload.name}' 已存在")
        category.name = payload.name
    
    # 更新其他字段
    if payload.icon is not None:
        category.icon = payload.icon
    if payload.description is not None:
        category.description = payload.description
    if payload.sort_order is not None:
        category.sort_order = payload.sort_order
    
    db.commit()
    db.refresh(category)
    
    return category.to_dict()


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目分类（同时删除该分类下的所有文章）"""
    # 查询分类
    category = db.query(ProjectCategory).filter(ProjectCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 验证用户权限
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="没有权限删除分类")
    
    # 先删除该分类下的所有文章
    from app.models.article import Article
    deleted_articles = db.query(Article).filter(
        Article.project_id == category.project_id,
        Article.type == category.type
    ).delete(synchronize_session=False)
    
    # 删除分类
    db.delete(category)
    db.commit()
    
    return None

