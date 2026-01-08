"""
更新用户入职日期的脚本
"""
import sys
import os
from datetime import date

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User

def update_hire_dates():
    """为所有没有入职日期的用户设置默认入职日期"""
    db = SessionLocal()
    try:
        # 查询所有用户
        users = db.query(User).all()
        
        updated_count = 0
        for user in users:
            if user.hire_date is None:
                # 如果没有入职日期，设置为创建日期或默认日期
                if user.created_at:
                    user.hire_date = user.created_at.date()
                else:
                    # 默认设置为2023年1月1日
                    user.hire_date = date(2023, 1, 1)
                
                updated_count += 1
                print(f"✅ 更新用户 {user.username} ({user.real_name}) 的入职日期为: {user.hire_date}")
        
        if updated_count > 0:
            db.commit()
            print(f"\n🎉 成功更新 {updated_count} 个用户的入职日期")
        else:
            print("✓ 所有用户都已有入职日期")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

def set_specific_hire_date(username: str, hire_date: date):
    """为指定用户设置入职日期"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ 用户 {username} 不存在")
            return
        
        user.hire_date = hire_date
        db.commit()
        print(f"✅ 成功设置用户 {user.username} ({user.real_name}) 的入职日期为: {hire_date}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("更新用户入职日期")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 如果提供了用户名参数，只更新指定用户
        username = sys.argv[1]
        if len(sys.argv) > 2:
            # 如果提供了日期参数 (格式: YYYY-MM-DD)
            hire_date_str = sys.argv[2]
            try:
                year, month, day = hire_date_str.split('-')
                hire_date = date(int(year), int(month), int(day))
                set_specific_hire_date(username, hire_date)
            except ValueError:
                print(f"❌ 日期格式错误，请使用 YYYY-MM-DD 格式，例如: 2023-06-15")
        else:
            print(f"❌ 请提供入职日期，例如: python update_user_hire_date.py {username} 2023-06-15")
    else:
        # 批量更新所有用户
        update_hire_dates()
    
    print("=" * 50)

