#!/usr/bin/env python3
"""
更新角色权限，添加团队协作功能的访问权限
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.role import Role
except ImportError as e:
    print(f"❌ [权限更新] 导入模块失败: {e}")
    print("💡 请确保在 backend 目录下运行此脚本")
    sys.exit(1)


def update_collaboration_permissions():
    """更新角色权限，添加团队协作相关权限"""
    
    db: Session = SessionLocal()
    
    try:
        print("🔧 [权限更新] 开始更新团队协作权限...")
        
        # 需要添加协作权限的角色列表
        target_roles = [
            'R_SUPER',      # 超级管理员
            'R_ADMIN',      # 管理员
            'R_ANNOTATOR',  # 标注员
            'R_REVIEWER',   # 审核员
            'super',        # 超级管理员（备用）
            'admin',        # 管理员（备用）
            'annotator',    # 标注员（备用）
            'reviewer'      # 审核员（备用）
        ]
        
        # 需要添加的权限列表
        collaboration_permissions = [
            'CollaborationManagement',  # 团队协作管理页面
            'CollaborationDocument'     # 协作文档详情页面
        ]
        
        updated_count = 0
        
        for role_code in target_roles:
            # 查找角色
            role = db.query(Role).filter(Role.role == role_code).first()
            
            if not role:
                print(f"⚠️  [权限更新] 角色不存在: {role_code}")
                continue
            
            # 解析现有权限
            existing_permissions = []
            if role.permissions:
                try:
                    existing_permissions = json.loads(role.permissions)
                    if not isinstance(existing_permissions, list):
                        existing_permissions = []
                except (json.JSONDecodeError, ValueError):
                    existing_permissions = []
            
            # 添加新权限
            updated_permissions = existing_permissions.copy()
            added_permissions = []
            
            for perm in collaboration_permissions:
                if perm not in updated_permissions:
                    updated_permissions.append(perm)
                    added_permissions.append(perm)
            
            # 如果有新权限需要添加
            if added_permissions:
                role.permissions = json.dumps(updated_permissions, ensure_ascii=False)
                updated_count += 1
                
                print(f"✅ [权限更新] 角色 {role_code} ({role.name}) 添加权限: {', '.join(added_permissions)}")
            else:
                print(f"ℹ️  [权限更新] 角色 {role_code} ({role.name}) 已有协作权限，无需更新")
        
        # 提交更改
        if updated_count > 0:
            db.commit()
            print(f"🎉 [权限更新] 成功更新 {updated_count} 个角色的权限")
        else:
            print("ℹ️  [权限更新] 所有角色权限已是最新，无需更新")
        
        # 显示更新后的权限
        print("\n📋 [权限更新] 当前角色权限状态:")
        print("-" * 80)
        
        for role_code in target_roles:
            role = db.query(Role).filter(Role.role == role_code).first()
            if role:
                permissions = []
                if role.permissions:
                    try:
                        permissions = json.loads(role.permissions)
                    except:
                        permissions = []
                
                collab_perms = [p for p in permissions if 'Collaboration' in p]
                status = "✅" if collab_perms else "❌"
                
                print(f"{status} {role_code:12} | {role.name:15} | 协作权限: {', '.join(collab_perms) if collab_perms else '无'}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ [权限更新] 更新失败: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    try:
        update_collaboration_permissions()
        print("\n🎉 权限更新完成！现在用户应该可以在导航栏中看到团队协作功能了。")
        print("💡 如果仍然看不到，请尝试重新登录以刷新权限缓存。")
    except Exception as e:
        print(f"\n❌ 权限更新失败: {e}")
        sys.exit(1)
