#!/usr/bin/env python3
"""
数据库迁移：为 articles 表新增封面/分类/可见性字段
新增列：cover_url(TEXT/VARCHAR), category(TEXT/VARCHAR), is_public(BOOLEAN)
支持 SQLite / PostgreSQL / MySQL，重复执行安全。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal


def column_exists_sqlite(session: Session, table: str, column: str) -> bool:
    rows = session.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def ensure_columns(session: Session):
    dialect = engine.dialect.name

    if dialect == 'postgresql':
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS cover_url VARCHAR(500);
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS category VARCHAR(50);
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT TRUE;
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS editable_user_ids JSONB DEFAULT '[]'::jsonb;
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS editable_roles JSONB DEFAULT '[]'::jsonb;
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS departments JSONB DEFAULT '[]'::jsonb;
        """))
    elif dialect == 'mysql':
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS cover_url VARCHAR(500) COMMENT '封面图片URL';
        """))
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS category VARCHAR(50) COMMENT '文章分类标签';
        """))
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_public TINYINT(1) DEFAULT 1 COMMENT '是否公开可见';
        """))
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS editable_user_ids JSON NULL COMMENT '可编辑用户ID列表';
        """))
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS editable_roles JSON NULL COMMENT '可编辑角色编码列表';
        """))
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS departments JSON NULL COMMENT '所属部门列表';
        """))
    else:
        # SQLite
        if not column_exists_sqlite(session, 'articles', 'cover_url'):
            session.execute(text("ALTER TABLE articles ADD COLUMN cover_url TEXT"))
            print("✅ 已添加 articles.cover_url")
        else:
            print("ℹ️  articles.cover_url 已存在")

        if not column_exists_sqlite(session, 'articles', 'category'):
            session.execute(text("ALTER TABLE articles ADD COLUMN category TEXT"))
            print("✅ 已添加 articles.category")
        else:
            print("ℹ️  articles.category 已存在")

        if not column_exists_sqlite(session, 'articles', 'is_public'):
            session.execute(text("ALTER TABLE articles ADD COLUMN is_public INTEGER DEFAULT 1"))
            print("✅ 已添加 articles.is_public")
        else:
            print("ℹ️  articles.is_public 已存在")
        if not column_exists_sqlite(session, 'articles', 'editable_user_ids'):
            session.execute(text("ALTER TABLE articles ADD COLUMN editable_user_ids TEXT"))
            print("✅ 已添加 articles.editable_user_ids")
        else:
            print("ℹ️  articles.editable_user_ids 已存在")
        if not column_exists_sqlite(session, 'articles', 'editable_roles'):
            session.execute(text("ALTER TABLE articles ADD COLUMN editable_roles TEXT"))
            print("✅ 已添加 articles.editable_roles")
        else:
            print("ℹ️  articles.editable_roles 已存在")
        if not column_exists_sqlite(session, 'articles', 'departments'):
            session.execute(text("ALTER TABLE articles ADD COLUMN departments TEXT"))
            print("✅ 已添加 articles.departments")
        else:
            print("ℹ️  articles.departments 已存在")


def main() -> bool:
    print("START: 文章扩展字段迁移 cover_url/category/is_public + editable/departments")
    session = SessionLocal()
    try:
        ensure_columns(session)
        session.commit()
        print("DONE: 迁移完成")
        return True
    except Exception as e:
        print(f"ERROR: 迁移失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)


