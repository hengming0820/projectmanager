#!/usr/bin/env python3
"""
工作日志表迁移脚本
创建 work_weeks, work_log_entries, work_log_types 表
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal

def get_db_dialect():
    """获取数据库方言"""
    return engine.dialect.name

def table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_work_weeks_table():
    """创建 work_weeks 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS work_weeks (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'active',
            config JSON,
            created_by VARCHAR(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS work_weeks (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'active',
            config JSON,
            created_by VARCHAR(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS work_weeks (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'active',
            config TEXT,
            created_by VARCHAR(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ work_weeks 表创建成功")

def create_work_log_entries_table():
    """创建 work_log_entries 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS work_log_entries (
            id VARCHAR(36) PRIMARY KEY,
            work_week_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            work_date DATE NOT NULL,
            day_of_week INTEGER NOT NULL,
            work_content TEXT,
            work_type VARCHAR(50),
            priority VARCHAR(20) DEFAULT 'normal',
            planned_hours INTEGER DEFAULT 8,
            actual_hours INTEGER,
            status VARCHAR(20) DEFAULT 'pending',
            completion_rate INTEGER DEFAULT 0,
            difficulties TEXT,
            next_day_plan TEXT,
            remarks TEXT,
            submitted_at TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by VARCHAR(36),
            review_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (work_week_id) REFERENCES work_weeks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS work_log_entries (
            id VARCHAR(36) PRIMARY KEY,
            work_week_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            work_date DATE NOT NULL,
            day_of_week INTEGER NOT NULL,
            work_content TEXT,
            work_type VARCHAR(50),
            priority VARCHAR(20) DEFAULT 'normal',
            planned_hours INTEGER DEFAULT 8,
            actual_hours INTEGER,
            status VARCHAR(20) DEFAULT 'pending',
            completion_rate INTEGER DEFAULT 0,
            difficulties TEXT,
            next_day_plan TEXT,
            remarks TEXT,
            submitted_at TIMESTAMP NULL,
            reviewed_at TIMESTAMP NULL,
            reviewed_by VARCHAR(36),
            review_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (work_week_id) REFERENCES work_weeks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS work_log_entries (
            id VARCHAR(36) PRIMARY KEY,
            work_week_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            work_date DATE NOT NULL,
            day_of_week INTEGER NOT NULL,
            work_content TEXT,
            work_type VARCHAR(50),
            priority VARCHAR(20) DEFAULT 'normal',
            planned_hours INTEGER DEFAULT 8,
            actual_hours INTEGER,
            status VARCHAR(20) DEFAULT 'pending',
            completion_rate INTEGER DEFAULT 0,
            difficulties TEXT,
            next_day_plan TEXT,
            remarks TEXT,
            submitted_at TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by VARCHAR(36),
            review_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (work_week_id) REFERENCES work_weeks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ work_log_entries 表创建成功")

def create_work_log_types_table():
    """创建 work_log_types 表"""
    dialect = get_db_dialect()
    
    sql = """
    CREATE TABLE IF NOT EXISTS work_log_types (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        color VARCHAR(7) DEFAULT '#409EFF',
        icon VARCHAR(50),
        is_active BOOLEAN DEFAULT TRUE,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    if dialect == 'mysql':
        sql = sql.replace('BOOLEAN', 'TINYINT(1)')
        sql = sql.replace('updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 
                         'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ work_log_types 表创建成功")

def create_indexes():
    """创建索引"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_work_weeks_status ON work_weeks(status);",
        "CREATE INDEX IF NOT EXISTS idx_work_weeks_dates ON work_weeks(week_start_date, week_end_date);",
        "CREATE INDEX IF NOT EXISTS idx_work_log_entries_week_user ON work_log_entries(work_week_id, user_id);",
        "CREATE INDEX IF NOT EXISTS idx_work_log_entries_date ON work_log_entries(work_date);",
        "CREATE INDEX IF NOT EXISTS idx_work_log_entries_status ON work_log_entries(status);",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
            except Exception as e:
                print(f"⚠️  索引创建可能失败（可能已存在）: {e}")
        conn.commit()
    print("✅ 索引创建完成")

def insert_default_work_log_types():
    """插入默认工作类型"""
    default_types = [
        {
            'id': str(uuid.uuid4()),
            'name': '开发',
            'description': '软件开发相关工作',
            'color': '#67C23A',
            'icon': 'Code',
            'sort_order': 1
        },
        {
            'id': str(uuid.uuid4()),
            'name': '测试',
            'description': '软件测试相关工作',
            'color': '#E6A23C',
            'icon': 'TestTube',
            'sort_order': 2
        },
        {
            'id': str(uuid.uuid4()),
            'name': '会议',
            'description': '各类会议和讨论',
            'color': '#409EFF',
            'icon': 'Meeting',
            'sort_order': 3
        },
        {
            'id': str(uuid.uuid4()),
            'name': '学习',
            'description': '技术学习和培训',
            'color': '#9C27B0',
            'icon': 'Reading',
            'sort_order': 4
        },
        {
            'id': str(uuid.uuid4()),
            'name': '文档',
            'description': '文档编写和整理',
            'color': '#FF9800',
            'icon': 'Document',
            'sort_order': 5
        },
        {
            'id': str(uuid.uuid4()),
            'name': '其他',
            'description': '其他工作内容',
            'color': '#909399',
            'icon': 'More',
            'sort_order': 6
        }
    ]
    
    with engine.connect() as conn:
        # 检查是否已有数据
        result = conn.execute(text("SELECT COUNT(*) as count FROM work_log_types"))
        count = result.fetchone()[0]
        
        if count == 0:
            for work_type in default_types:
                sql = text("""
                INSERT INTO work_log_types (id, name, description, color, icon, is_active, sort_order, created_at, updated_at)
                VALUES (:id, :name, :description, :color, :icon, :is_active, :sort_order, :created_at, :updated_at)
                """)
                
                conn.execute(sql, {
                    **work_type,
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            conn.commit()
            print("✅ 默认工作类型插入成功")
        else:
            print("ℹ️  工作类型数据已存在，跳过插入")

def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    tables_to_check = ['work_weeks', 'work_log_entries', 'work_log_types']
    
    with engine.connect() as conn:
        for table in tables_to_check:
            if table_exists(table):
                result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                count = result.fetchone()[0]
                print(f"✅ {table} 表存在，记录数: {count}")
            else:
                print(f"❌ {table} 表不存在")

def main():
    """主函数"""
    print("🚀 开始工作日志表迁移...")
    
    try:
        # 创建表
        create_work_weeks_table()
        create_work_log_entries_table()
        create_work_log_types_table()
        
        # 创建索引
        create_indexes()
        
        # 插入默认数据
        insert_default_work_log_types()
        
        # 验证结果
        verify_migration()
        
        print("\n🎉 工作日志表迁移完成！")
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

