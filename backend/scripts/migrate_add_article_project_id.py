#!/usr/bin/env python3
"""
为 articles 表添加 project_id 字段的数据库迁移脚本

运行方法：
cd backend
python scripts/migrate_add_article_project_id.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal


def column_exists(session: Session, table: str, column: str) -> bool:
    """检查列是否已存在（支持 PostgreSQL 和 SQLite）"""
    try:
        # 尝试 PostgreSQL 的方式
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table AND column_name = :column
        """), {"table": table, "column": column})
        return result.fetchone() is not None
    except Exception:
        # 回退到 SQLite 的方式
        try:
            result = session.execute(text(f"PRAGMA table_info({table})"))
            columns = [row[1] for row in result]
            return column in columns
        except Exception:
            # 如果都失败，直接尝试添加列
            return False


def run_migration():
    """执行迁移"""
    print("开始迁移：为 articles 表添加 project_id 字段...")
    
    db = SessionLocal()
    try:
        # 检查列是否已存在
        if column_exists(db, "articles", "project_id"):
            print("✓ project_id 字段已存在，跳过迁移")
            return
        
        print("添加 project_id 字段...")
        db.execute(text("""
            ALTER TABLE articles 
            ADD COLUMN project_id VARCHAR(36)
        """))
        
        print("创建索引...")
        try:
            db.execute(text("""
                CREATE INDEX idx_articles_project_id 
                ON articles(project_id)
            """))
        except Exception as e:
            print(f"  索引可能已存在: {e}")
        
        try:
            db.execute(text("""
                CREATE INDEX idx_articles_project_type 
                ON articles(project_id, type)
            """))
        except Exception as e:
            print(f"  复合索引可能已存在: {e}")
        
        db.commit()
        print("✓ 迁移成功完成！")
        print("\n说明：")
        print("- project_id 为 NULL 表示公共文章（不属于任何项目）")
        print("- project_id 有值表示文章归属于特定项目")
        print("- 当项目被删除时，相关文章也会被级联删除")
        
    except Exception as e:
        db.rollback()
        print(f"✗ 迁移失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()

