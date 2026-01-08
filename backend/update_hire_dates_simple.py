"""
简化版：更新用户入职日期
直接连接数据库执行SQL
"""
import psycopg2
from datetime import date

# 数据库配置（从.env文件读取或直接配置）
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'medical_annotation',
    'user': 'admin',
    'password': 'admin666'
}

def update_hire_dates():
    """为所有没有入职日期的用户设置默认入职日期"""
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 查询所有没有入职日期的用户
        cursor.execute("""
            SELECT id, username, real_name, created_at 
            FROM users 
            WHERE hire_date IS NULL
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("✓ 所有用户都已有入职日期")
            return
        
        print(f"找到 {len(users)} 个没有入职日期的用户\n")
        
        # 更新每个用户的入职日期
        for user_id, username, real_name, created_at in users:
            # 使用创建日期作为入职日期
            hire_date = created_at.date() if created_at else date(2023, 1, 1)
            
            cursor.execute("""
                UPDATE users 
                SET hire_date = %s 
                WHERE id = %s
            """, (hire_date, user_id))
            
            print(f"✅ 更新用户 {username} ({real_name}) 的入职日期为: {hire_date}")
        
        # 提交更改
        conn.commit()
        print(f"\n🎉 成功更新 {len(users)} 个用户的入职日期")
        
    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("更新用户入职日期")
    print("=" * 50)
    update_hire_dates()
    print("=" * 50)

