#!/usr/bin/env python3
"""
为角色添加工作日志相关权限
"""

import sys
import os
import json
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models.role import Role

def add_work_log_permissions():
    """为角色添加工作日志权限"""
    
    try:
        db = SessionLocal()
        
        # 工作日志相关的权限
        work_log_permissions = [
            "WorkLogManagement",
            "WorkLogEdit", 
            "WorkLogView",
            "WorkLogReview"
        ]
        
        print("🔑 开始添加工作日志权限...")
        
        # 获取所有角色
        roles = db.query(Role).all()
        
        for role in roles:
            print(f"📋 处理角色: {role.role}")
            
            # 解析现有权限
            existing_permissions = []
            if role.permissions:
                try:
                    existing_permissions = json.loads(role.permissions)
                    if not isinstance(existing_permissions, list):
                        existing_permissions = []
                except (json.JSONDecodeError, ValueError):
                    existing_permissions = []
            
            # 根据角色类型添加相应权限
            new_permissions = existing_permissions.copy()
            
            if role.role.lower() in ['admin', 'administrator', 'super']:
                # 管理员拥有所有工作日志权限
                for perm in work_log_permissions:
                    if perm not in new_permissions:
                        new_permissions.append(perm)
                print(f"  ✅ 管理员角色，添加所有工作日志权限")
                
            elif role.role.lower() in ['annotator', 'user']:
                # 标注员可以查看和编辑自己的工作日志
                basic_permissions = ["WorkLogView", "WorkLogEdit"]
                for perm in basic_permissions:
                    if perm not in new_permissions:
                        new_permissions.append(perm)
                print(f"  ✅ 普通用户角色，添加基本工作日志权限")
                
            elif role.role.lower() in ['reviewer']:
                # 审核员可以查看和审核工作日志
                reviewer_permissions = ["WorkLogView", "WorkLogReview"]
                for perm in reviewer_permissions:
                    if perm not in new_permissions:
                        new_permissions.append(perm)
                print(f"  ✅ 审核员角色，添加审核工作日志权限")
            
            # 更新权限
            if new_permissions != existing_permissions:
                role.permissions = json.dumps(new_permissions, ensure_ascii=False)
                print(f"  🔄 更新权限: {new_permissions}")
            else:
                print(f"  ℹ️  权限无需更新")
        
        # 提交更改
        db.commit()
        print("\n✅ 工作日志权限添加完成！")
        
        # 显示最终权限状态
        print("\n📊 最终权限状态:")
        roles = db.query(Role).all()
        for role in roles:
            permissions = []
            if role.permissions:
                try:
                    permissions = json.loads(role.permissions)
                except:
                    permissions = []
            
            work_log_perms = [p for p in permissions if p.startswith('WorkLog')]
            print(f"  {role.role}: {work_log_perms}")
        
        db.close()
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 权限添加失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始添加工作日志权限...")
    
    if add_work_log_permissions():
        print("🎉 工作日志权限添加成功！")
        return True
    else:
        print("❌ 工作日志权限添加失败！")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

