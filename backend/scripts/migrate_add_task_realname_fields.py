#!/usr/bin/env python3
"""
为 tasks 表增加冗余真实姓名字段并回填：
 - assigned_to_name VARCHAR(100)
 - created_by_name  VARCHAR(100)
 - reviewed_by_name VARCHAR(100)

并将 timeline JSON 内所有事件的 user_name 统一回填为用户真实姓名（找不到则回退用户名）。
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.user import User
from sqlalchemy.orm.attributes import flag_modified

def ensure_columns(session: Session):
    dialect = engine.dialect.name
    if dialect == 'postgresql':
        session.execute(text("""
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_to_name VARCHAR(100);
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS created_by_name  VARCHAR(100);
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reviewed_by_name VARCHAR(100);
        """))
    elif dialect == 'mysql':
        # MySQL 8+ 支持 IF NOT EXISTS
        session.execute(text("""
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_to_name VARCHAR(100);
        """))
        session.execute(text("""
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS created_by_name  VARCHAR(100);
        """))
        session.execute(text("""
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reviewed_by_name VARCHAR(100);
        """))
    else:
        # SQLite: 检查列是否存在
        def has_col(col: str) -> bool:
            rows = session.execute(text("PRAGMA table_info(tasks)")).fetchall()
            return any(r[1] == col for r in rows)
        if not has_col('assigned_to_name'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN assigned_to_name TEXT"))
        if not has_col('created_by_name'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN created_by_name TEXT"))
        if not has_col('reviewed_by_name'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN reviewed_by_name TEXT"))

def backfill_names_and_timeline(session: Session):
    users = {u.id: (u.real_name or u.username or u.id) for u in session.query(User).all()}

    def resolve(uid: str | None) -> str | None:
        if not uid:
            return None
        return users.get(uid) or uid

    tasks = session.query(Task).all()
    for t in tasks:
        # 冗余姓名字段
        t.created_by_name = resolve(t.created_by)
        t.assigned_to_name = resolve(t.assigned_to)
        t.reviewed_by_name = resolve(t.reviewed_by)

        # timeline user_name 回填
        if t.timeline:
            changed = False
            for ev in t.timeline:
                if isinstance(ev, dict) and ev.get('user_id'):
                    name = resolve(ev.get('user_id'))
                    if name and ev.get('user_name') != name:
                        ev['user_name'] = name
                        changed = True
            if changed:
                flag_modified(t, 'timeline')

def main():
    print('🚀 开始迁移: 为 tasks 增加真实姓名字段并回填...')
    session = SessionLocal()
    try:
        ensure_columns(session)
        session.commit()
        print('✅ 列检查/创建完成')

        backfill_names_and_timeline(session)
        session.commit()
        print('✅ 回填完成')
    except Exception as e:
        print('❌ 迁移失败:', e)
        session.rollback()
        raise
    finally:
        session.close()
    print('🎉 迁移完成')

if __name__ == '__main__':
    main()


