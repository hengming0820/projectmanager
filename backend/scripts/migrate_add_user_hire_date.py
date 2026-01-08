#!/usr/bin/env python3
"""
为 users 表增加入职日期字段：
- hire_date DATE - 入职日期
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session

def ensure_hire_date_column(session: Session):
    """确保hire_date列存在"""
    dialect = engine.dialect.name
    print(f"📊 数据库类型: {dialect}")
    
    if dialect == 'postgresql':
        session.execute(text("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS hire_date DATE;
        """))
        print("✅ PostgreSQL: hire_date 列检查/创建完成")
        
    elif dialect == 'mysql':
        try:
            session.execute(text("""
            ALTER TABLE users ADD COLUMN hire_date DATE;
            """))
            print("✅ MySQL: hire_date 列创建完成")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✅ MySQL: hire_date 列已存在")
            else:
                raise
                
    else:  # SQLite
        # 检查列是否存在
        result = session.execute(text("PRAGMA table_info(users)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'hire_date' not in columns:
            session.execute(text("ALTER TABLE users ADD COLUMN hire_date TEXT"))
            print("✅ SQLite: hire_date 列创建完成")
        else:
            print("✅ SQLite: hire_date 列已存在")

def backfill_default_hire_dates(session: Session):
    """为现有用户回填默认入职日期"""
    try:
        # 统计需要回填的用户数量
        result = session.execute(text("""
        SELECT COUNT(*) FROM users WHERE hire_date IS NULL
        """)).fetchone()
        
        null_count = result[0] if result else 0
        print(f"📊 需要回填入职日期的用户数量: {null_count}")
        
        if null_count > 0:
            # 为没有入职日期的用户设置默认值（创建时间的日期部分）
            session.execute(text("""
            UPDATE users 
            SET hire_date = DATE(created_at) 
            WHERE hire_date IS NULL AND created_at IS NOT NULL
            """))
            
            # 如果创建时间也为空，设置为当前日期
            session.execute(text("""
            UPDATE users 
            SET hire_date = DATE('now') 
            WHERE hire_date IS NULL
            """))
            
            print(f"✅ 已为 {null_count} 个用户回填默认入职日期")
        else:
            print("✅ 所有用户都已有入职日期")
            
    except Exception as e:
        print(f"⚠️ 回填入职日期时出现警告: {e}")
        # 非关键错误，继续执行

def verify_migration(session: Session):
    """验证迁移结果"""
    try:
        # 检查列是否存在
        dialect = engine.dialect.name
        if dialect == 'sqlite':
            result = session.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [row[1] for row in result]
            has_hire_date = 'hire_date' in columns
        else:
            # PostgreSQL 和 MySQL
            if dialect == 'postgresql':
                result = session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'hire_date'
                """)).fetchone()
            else:  # MySQL
                result = session.execute(text("""
                SELECT COLUMN_NAME FROM information_schema.COLUMNS 
                WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'hire_date'
                """)).fetchone()
            has_hire_date = result is not None
        
        if has_hire_date:
            print("✅ hire_date 列验证成功")
            
            # 统计数据分布
            stats = session.execute(text("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(hire_date) as users_with_hire_date,
                COUNT(*) - COUNT(hire_date) as users_without_hire_date
            FROM users
            """)).fetchone()
            
            print(f"📊 用户统计:")
            print(f"   - 总用户数: {stats[0]}")
            print(f"   - 有入职日期: {stats[1]}")
            print(f"   - 无入职日期: {stats[2]}")
            
        else:
            print("❌ hire_date 列验证失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

def main():
    print('🚀 开始迁移: 为 users 表增加入职日期字段...')
    
    session = SessionLocal()
    try:
        # 1. 确保列存在
        ensure_hire_date_column(session)
        session.commit()
        
        # 2. 回填默认数据
        backfill_default_hire_dates(session)
        session.commit()
        
        # 3. 验证迁移结果
        if verify_migration(session):
            print('🎉 hire_date 字段迁移成功！')
        else:
            print('❌ 迁移验证失败')
            return False
            
    except Exception as e:
        print(f'❌ 迁移失败: {e}')
        session.rollback()
        raise
    finally:
        session.close()
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
