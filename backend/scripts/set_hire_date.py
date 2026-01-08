"""
设置用户入职时间的脚本

使用方法：
1. 设置特定用户的入职时间：
   python set_hire_date.py --username admin --date 2025-08-29

2. 为所有未设置入职时间的用户设置为其创建日期：
   python set_hire_date.py --set-all-from-created

3. 查看所有用户的入职时间状态：
   python set_hire_date.py --list
"""

import sys
import os
from datetime import datetime, date

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import settings

def get_db_session():
    """获取数据库会话"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def list_users_hire_date(db):
    """列出所有用户的入职时间状态"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    print("\n" + "="*80)
    print("用户入职时间状态")
    print("="*80)
    print(f"{'用户名':<15} {'姓名':<15} {'入职时间':<15} {'状态':<10} {'创建时间':<20}")
    print("-"*80)
    
    for user in users:
        hire_date_str = user.hire_date.strftime('%Y-%m-%d') if user.hire_date else '未设置'
        status = '✅ 已设置' if user.hire_date else '❌ 未设置'
        created_str = user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{user.username:<15} {user.real_name:<15} {hire_date_str:<15} {status:<10} {created_str:<20}")
    
    print("="*80)
    
    # 统计
    total = len(users)
    set_count = sum(1 for u in users if u.hire_date is not None)
    unset_count = total - set_count
    
    print(f"\n📊 统计: 总计 {total} 个用户, 已设置 {set_count} 个, 未设置 {unset_count} 个")
    print()

def set_user_hire_date(db, username: str, hire_date: str):
    """设置特定用户的入职时间"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        print(f"❌ 错误: 找不到用户名为 '{username}' 的用户")
        return False
    
    try:
        # 解析日期
        hire_date_obj = datetime.strptime(hire_date, '%Y-%m-%d').date()
        
        # 更新入职时间
        user.hire_date = hire_date_obj
        db.commit()
        
        print(f"✅ 成功: 已将用户 '{username}' ({user.real_name}) 的入职时间设置为 {hire_date}")
        return True
        
    except ValueError as e:
        print(f"❌ 错误: 日期格式不正确，请使用 YYYY-MM-DD 格式 (如: 2025-08-29)")
        return False
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {str(e)}")
        return False

def set_all_from_created(db):
    """为所有未设置入职时间的用户设置为其创建日期"""
    users = db.query(User).filter(User.hire_date.is_(None)).all()
    
    if not users:
        print("✅ 所有用户都已设置入职时间")
        return
    
    print(f"\n找到 {len(users)} 个未设置入职时间的用户")
    print("将为这些用户设置入职时间为其创建日期...\n")
    
    success_count = 0
    for user in users:
        try:
            # 使用创建日期作为入职时间
            user.hire_date = user.created_at.date()
            db.commit()
            
            print(f"✅ {user.username:<15} ({user.real_name:<15}) 入职时间设置为 {user.hire_date}")
            success_count += 1
            
        except Exception as e:
            db.rollback()
            print(f"❌ {user.username:<15} 设置失败: {str(e)}")
    
    print(f"\n📊 完成: 成功设置 {success_count}/{len(users)} 个用户的入职时间")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='设置用户入职时间')
    parser.add_argument('--list', action='store_true', help='列出所有用户的入职时间状态')
    parser.add_argument('--username', type=str, help='用户名')
    parser.add_argument('--date', type=str, help='入职日期 (YYYY-MM-DD 格式)')
    parser.add_argument('--set-all-from-created', action='store_true', 
                       help='为所有未设置入职时间的用户设置为其创建日期')
    
    args = parser.parse_args()
    
    # 获取数据库会话
    db = get_db_session()
    
    try:
        if args.list:
            list_users_hire_date(db)
        
        elif args.set_all_from_created:
            confirm = input("⚠️  确定要为所有未设置入职时间的用户设置为其创建日期吗? (y/N): ")
            if confirm.lower() == 'y':
                set_all_from_created(db)
            else:
                print("❌ 操作已取消")
        
        elif args.username and args.date:
            set_user_hire_date(db, args.username, args.date)
        
        else:
            parser.print_help()
    
    finally:
        db.close()

if __name__ == '__main__':
    main()

