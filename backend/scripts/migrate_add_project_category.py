#!/usr/bin/env python3
"""
数据库迁移脚本：为projects表添加分类字段
添加字段：category, sub_category
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.project import Project

def ensure_columns(session: Session):
    """确保分类字段存在，兼容多种数据库"""
    dialect = engine.dialect.name
    
    if dialect == 'postgresql':
        session.execute(text("""
        ALTER TABLE projects ADD COLUMN IF NOT EXISTS category VARCHAR(50);
        ALTER TABLE projects ADD COLUMN IF NOT EXISTS sub_category VARCHAR(50);
        """))
    elif dialect == 'mysql':
        # MySQL 8+ 支持 IF NOT EXISTS
        session.execute(text("""
        ALTER TABLE projects ADD COLUMN IF NOT EXISTS category VARCHAR(50) 
        COMMENT '项目分类: case(病例), ai_annotation(AI标注)';
        """))
        session.execute(text("""
        ALTER TABLE projects ADD COLUMN IF NOT EXISTS sub_category VARCHAR(50) 
        COMMENT '子分类: case(trial试用,research研发,paid收费), ai_annotation(research科研,daily日常)';
        """))
    else:
        # SQLite: 检查列是否存在
        def has_col(col: str) -> bool:
            rows = session.execute(text("PRAGMA table_info(projects)")).fetchall()
            return any(r[1] == col for r in rows)
            
        if not has_col('category'):
            session.execute(text("ALTER TABLE projects ADD COLUMN category TEXT"))
            print("✅ 已添加category字段")
        else:
            print("ℹ️  category字段已存在")
            
        if not has_col('sub_category'):
            session.execute(text("ALTER TABLE projects ADD COLUMN sub_category TEXT"))
            print("✅ 已添加sub_category字段")
        else:
            print("ℹ️  sub_category字段已存在")

def backfill_default_categories(session: Session):
    """为现有项目设置默认分类"""
    # 检查是否有需要设置默认分类的项目
    result = session.execute(text("SELECT COUNT(*) FROM projects WHERE category IS NULL OR category = ''"))
    null_category_count = result.scalar()
    
    if null_category_count > 0:
        # 为现有项目设置默认分类为 case-trial
        session.execute(text("""
            UPDATE projects 
            SET category = 'case', sub_category = 'trial' 
            WHERE category IS NULL OR category = ''
        """))
        print(f"✅ 已为 {null_category_count} 个现有项目设置默认分类 (case-trial)")
    else:
        print("ℹ️  所有项目已有分类设置")

def add_project_category_fields():
    """为projects表添加分类字段"""
    print("🔄 开始为projects表添加分类字段...")
    
    session = SessionLocal()
    try:
        ensure_columns(session)
        session.commit()
        print("✅ 分类字段检查/创建完成")
        
        backfill_default_categories(session)
        session.commit()
        print("✅ 默认分类设置完成")
        
    except Exception as e:
        print(f"❌ 添加分类字段时出错: {e}")
        session.rollback()
        raise e
    finally:
        session.close()

def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    session = SessionLocal()
    
    try:
        # 兼容不同数据库的字段检查
        dialect = engine.dialect.name
        
        if dialect == 'sqlite':
            # SQLite 使用 PRAGMA table_info
            result = session.execute(text("PRAGMA table_info(projects)"))
            columns = result.fetchall()
            category_fields = [col for col in columns if col[1] in ['category', 'sub_category']]
            print("📊 项目表分类字段:")
            for col in category_fields:
                print(f"  - {col[1]}: {col[2]} (nullable: {not col[3]})")
        else:
            # PostgreSQL/MySQL 使用 information_schema
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                AND column_name IN ('category', 'sub_category')
                ORDER BY column_name
            """))
            columns = result.fetchall()
            print("📊 项目表分类字段:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            
        # 检查数据
        result = session.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(category) as with_category,
                   COUNT(sub_category) as with_sub_category
            FROM projects
        """))
        
        stats = result.fetchone()
        print(f"\n📈 项目数据统计:")
        print(f"  - 总项目数: {stats[0]}")
        print(f"  - 有主分类的项目: {stats[1]}")
        print(f"  - 有子分类的项目: {stats[2]}")
        
        # 显示分类分布
        result = session.execute(text("""
            SELECT category, sub_category, COUNT(*) as count
            FROM projects 
            WHERE category IS NOT NULL
            GROUP BY category, sub_category
            ORDER BY category, sub_category
        """))
        
        distributions = result.fetchall()
        if distributions:
            print("\n📊 分类分布:")
            for dist in distributions:
                print(f"  - {dist[0]}-{dist[1]}: {dist[2]} 个项目")
        
    except Exception as e:
        print(f"❌ 验证时出错: {e}")
    finally:
        session.close()

def main():
    """主函数"""
    print("🚀 项目分类字段迁移脚本")
    print("=" * 50)
    
    try:
        add_project_category_fields()
        verify_migration()
        print("\n🎉 迁移完成！")
        print("\n📝 变更摘要:")
        print("- ✅ 为projects表添加了category字段")
        print("- ✅ 为projects表添加了sub_category字段")
        print("- ✅ 为现有项目设置了默认分类")
        print("- ✅ 验证了迁移结果")
        return True
    except Exception as e:
        print(f"\n💥 迁移失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
