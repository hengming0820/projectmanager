#!/usr/bin/env python3
"""
数据库迁移：为 articles 表添加编辑锁字段
新增列：is_locked(BOOLEAN), locked_by(VARCHAR), locked_at(TIMESTAMP)
目的：防止多人同时编辑同一篇文章导致数据覆盖
支持 SQLite / PostgreSQL / MySQL，重复执行安全。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal


def column_exists_sqlite(session: Session, table: str, column: str) -> bool:
    """检查SQLite表中是否存在指定列"""
    rows = session.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def ensure_lock_columns(session: Session):
    """根据数据库类型添加编辑锁相关字段"""
    dialect = engine.dialect.name
    print(f"📊 检测到数据库类型: {dialect}")

    if dialect == 'postgresql':
        print("🔧 为 PostgreSQL 添加编辑锁字段...")
        
        # 添加 is_locked 字段
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;
        """))
        print("  ✅ is_locked (BOOLEAN)")
        
        # 添加 locked_by 字段
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS locked_by VARCHAR(50);
        """))
        print("  ✅ locked_by (VARCHAR)")
        
        # 添加 locked_at 字段
        session.execute(text("""
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS locked_at TIMESTAMP WITH TIME ZONE;
        """))
        print("  ✅ locked_at (TIMESTAMP)")
        
        # 确保已存在记录的 is_locked 为 FALSE
        session.execute(text("""
        UPDATE articles SET is_locked = FALSE WHERE is_locked IS NULL;
        """))
        print("  ✅ 已将现有记录的 is_locked 设置为 FALSE")
        
        # 添加注释
        session.execute(text("""
        COMMENT ON COLUMN articles.is_locked IS '是否被锁定（有人正在编辑）';
        COMMENT ON COLUMN articles.locked_by IS '锁定者用户ID';
        COMMENT ON COLUMN articles.locked_at IS '锁定时间';
        """))
        print("  ✅ 已添加字段注释")
        
        # 创建索引以提高查询性能
        session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_articles_is_locked ON articles(is_locked);
        CREATE INDEX IF NOT EXISTS idx_articles_locked_by ON articles(locked_by);
        """))
        print("  ✅ 已创建索引")
        
    elif dialect == 'mysql':
        print("🔧 为 MySQL 添加编辑锁字段...")
        
        # MySQL 不支持 IF NOT EXISTS，需要先检查
        # 添加 is_locked 字段
        try:
            session.execute(text("""
            ALTER TABLE articles ADD COLUMN is_locked TINYINT(1) DEFAULT 0 COMMENT '是否被锁定（有人正在编辑）';
            """))
            print("  ✅ is_locked (TINYINT)")
        except Exception as e:
            if 'Duplicate column name' in str(e):
                print("  ℹ️  is_locked 已存在")
            else:
                raise
        
        # 添加 locked_by 字段
        try:
            session.execute(text("""
            ALTER TABLE articles ADD COLUMN locked_by VARCHAR(50) COMMENT '锁定者用户ID';
            """))
            print("  ✅ locked_by (VARCHAR)")
        except Exception as e:
            if 'Duplicate column name' in str(e):
                print("  ℹ️  locked_by 已存在")
            else:
                raise
        
        # 添加 locked_at 字段
        try:
            session.execute(text("""
            ALTER TABLE articles ADD COLUMN locked_at TIMESTAMP NULL COMMENT '锁定时间';
            """))
            print("  ✅ locked_at (TIMESTAMP)")
        except Exception as e:
            if 'Duplicate column name' in str(e):
                print("  ℹ️  locked_at 已存在")
            else:
                raise
        
        # 创建索引
        try:
            session.execute(text("""
            CREATE INDEX idx_articles_is_locked ON articles(is_locked);
            """))
            print("  ✅ 已创建 is_locked 索引")
        except:
            print("  ℹ️  is_locked 索引已存在")
        
        try:
            session.execute(text("""
            CREATE INDEX idx_articles_locked_by ON articles(locked_by);
            """))
            print("  ✅ 已创建 locked_by 索引")
        except:
            print("  ℹ️  locked_by 索引已存在")
        
    else:
        # SQLite
        print("🔧 为 SQLite 添加编辑锁字段...")
        
        if not column_exists_sqlite(session, 'articles', 'is_locked'):
            session.execute(text("ALTER TABLE articles ADD COLUMN is_locked INTEGER DEFAULT 0"))
            print("  ✅ 已添加 is_locked (INTEGER, 0=FALSE, 1=TRUE)")
        else:
            print("  ℹ️  is_locked 已存在")

        if not column_exists_sqlite(session, 'articles', 'locked_by'):
            session.execute(text("ALTER TABLE articles ADD COLUMN locked_by TEXT"))
            print("  ✅ 已添加 locked_by (TEXT)")
        else:
            print("  ℹ️  locked_by 已存在")

        if not column_exists_sqlite(session, 'articles', 'locked_at'):
            session.execute(text("ALTER TABLE articles ADD COLUMN locked_at TEXT"))
            print("  ✅ 已添加 locked_at (TEXT, ISO 8601格式)")
        else:
            print("  ℹ️  locked_at 已存在")
        
        # SQLite 创建索引
        try:
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_is_locked ON articles(is_locked)"))
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_locked_by ON articles(locked_by)"))
            print("  ✅ 已创建索引")
        except Exception as e:
            print(f"  ⚠️  索引创建警告: {e}")


def verify_migration(session: Session):
    """验证迁移是否成功"""
    print("\n🔍 验证迁移结果...")
    
    dialect = engine.dialect.name
    
    if dialect == 'postgresql':
        result = session.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'articles' 
        AND column_name IN ('is_locked', 'locked_by', 'locked_at')
        ORDER BY column_name;
        """)).fetchall()
        
        if len(result) == 3:
            print("  ✅ 所有字段已成功添加:")
            for row in result:
                print(f"     - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
            return True
        else:
            print(f"  ❌ 字段数量不正确，预期3个，实际{len(result)}个")
            return False
            
    elif dialect == 'mysql':
        result = session.execute(text("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'articles' 
        AND TABLE_SCHEMA = DATABASE()
        AND COLUMN_NAME IN ('is_locked', 'locked_by', 'locked_at')
        ORDER BY COLUMN_NAME;
        """)).fetchall()
        
        if len(result) == 3:
            print("  ✅ 所有字段已成功添加:")
            for row in result:
                print(f"     - {row[0]}: {row[1]} (comment: {row[4]})")
            return True
        else:
            print(f"  ❌ 字段数量不正确，预期3个，实际{len(result)}个")
            return False
            
    else:
        # SQLite
        rows = session.execute(text("PRAGMA table_info(articles)")).fetchall()
        lock_columns = [r for r in rows if r[1] in ('is_locked', 'locked_by', 'locked_at')]
        
        if len(lock_columns) == 3:
            print("  ✅ 所有字段已成功添加:")
            for row in lock_columns:
                print(f"     - {row[1]}: {row[2]}")
            return True
        else:
            print(f"  ❌ 字段数量不正确，预期3个，实际{len(lock_columns)}个")
            return False


def main() -> bool:
    print("=" * 70)
    print("🚀 开始执行：文章编辑锁字段迁移")
    print("=" * 70)
    print("📝 目标：为 articles 表添加编辑锁机制")
    print("📋 新增字段:")
    print("   - is_locked: 是否被锁定")
    print("   - locked_by: 锁定者用户ID")
    print("   - locked_at: 锁定时间")
    print("=" * 70)
    print()
    
    session = SessionLocal()
    try:
        ensure_lock_columns(session)
        session.commit()
        print("\n💾 数据库事务已提交")
        
        # 验证迁移
        if verify_migration(session):
            print("\n" + "=" * 70)
            print("✅ 迁移成功完成！")
            print("=" * 70)
            print("📌 后续步骤:")
            print("   1. 重启后端服务以加载新的模型定义")
            print("   2. 测试编辑锁功能是否正常工作")
            print("   3. 检查前端是否正确显示锁定状态")
            print("=" * 70)
            return True
        else:
            print("\n❌ 迁移验证失败，请检查数据库")
            return False
            
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        print(f"📝 错误详情: {type(e).__name__}")
        session.rollback()
        print("🔄 数据库事务已回滚")
        return False
    finally:
        session.close()


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)

