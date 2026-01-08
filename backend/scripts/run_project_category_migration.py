#!/usr/bin/env python3
"""
运行项目分类迁移的简化脚本
参考 migrate_add_task_realname_fields.py 的实现方式
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session

def ensure_project_category_columns(session: Session):
    """确保项目分类字段存在，兼容多种数据库"""
    dialect = engine.dialect.name
    print(f"📊 检测到数据库类型: {dialect}")
    
    if dialect == 'postgresql':
        session.execute(text("""
        ALTER TABLE projects ADD COLUMN IF NOT EXISTS category VARCHAR(50);
        ALTER TABLE projects ADD COLUMN IF NOT EXISTS sub_category VARCHAR(50);
        """))
        print("✅ PostgreSQL: 分类字段检查/创建完成")
    elif dialect == 'mysql':
        # MySQL 8+ 支持 IF NOT EXISTS
        try:
            session.execute(text("""
            ALTER TABLE projects ADD COLUMN IF NOT EXISTS category VARCHAR(50) 
            COMMENT '项目分类: case(病例), ai_annotation(AI标注)';
            """))
            session.execute(text("""
            ALTER TABLE projects ADD COLUMN IF NOT EXISTS sub_category VARCHAR(50) 
            COMMENT '子分类: case(trial试用,research研发,paid收费), ai_annotation(research科研,daily日常)';
            """))
            print("✅ MySQL: 分类字段检查/创建完成")
        except Exception as e:
            print(f"⚠️  MySQL IF NOT EXISTS 不支持，尝试其他方式: {e}")
            # 降级到检查后添加的方式
            check_and_add_mysql_columns(session)
    else:
        # SQLite: 检查列是否存在
        def has_col(col: str) -> bool:
            rows = session.execute(text("PRAGMA table_info(projects)")).fetchall()
            return any(r[1] == col for r in rows)
            
        if not has_col('category'):
            session.execute(text("ALTER TABLE projects ADD COLUMN category TEXT"))
            print("✅ SQLite: 已添加category字段")
        else:
            print("ℹ️  SQLite: category字段已存在")
            
        if not has_col('sub_category'):
            session.execute(text("ALTER TABLE projects ADD COLUMN sub_category TEXT"))
            print("✅ SQLite: 已添加sub_category字段")
        else:
            print("ℹ️  SQLite: sub_category字段已存在")

def check_and_add_mysql_columns(session: Session):
    """MySQL兼容性函数：检查字段后添加"""
    try:
        # 检查字段是否存在
        result = session.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'projects' 
            AND column_name = 'category'
        """))
        if result.scalar() == 0:
            session.execute(text("ALTER TABLE projects ADD COLUMN category VARCHAR(50)"))
            print("✅ MySQL: 已添加category字段")
        else:
            print("ℹ️  MySQL: category字段已存在")
            
        result = session.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'projects' 
            AND column_name = 'sub_category'
        """))
        if result.scalar() == 0:
            session.execute(text("ALTER TABLE projects ADD COLUMN sub_category VARCHAR(50)"))
            print("✅ MySQL: 已添加sub_category字段")
        else:
            print("ℹ️  MySQL: sub_category字段已存在")
    except Exception as e:
        print(f"❌ MySQL字段检查失败: {e}")
        raise

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

def verify_migration(session: Session):
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    # 检查数据
    result = session.execute(text("""
        SELECT COUNT(*) as total,
               COUNT(category) as with_category,
               COUNT(sub_category) as with_sub_category
        FROM projects
    """))
    
    stats = result.fetchone()
    print(f"📈 项目数据统计:")
    print(f"  - 总项目数: {stats[0]}")
    print(f"  - 有主分类的项目: {stats[1]}")
    print(f"  - 有子分类的项目: {stats[2]}")
    
    # 显示分类分布
    try:
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
        else:
            print("\n📊 暂无分类数据")
    except Exception as e:
        print(f"⚠️  分类分布查询失败: {e}")

def main():
    """主函数"""
    print('🚀 开始项目分类字段迁移...')
    session = SessionLocal()
    
    try:
        # 1. 确保字段存在
        ensure_project_category_columns(session)
        session.commit()
        print('✅ 字段检查/创建完成')

        # 2. 设置默认分类
        backfill_default_categories(session)
        session.commit()
        print('✅ 默认分类设置完成')
        
        # 3. 验证结果
        verify_migration(session)
        
        print('\n🎉 项目分类迁移完成！')
        return True
        
    except Exception as e:
        print('❌ 迁移失败:', e)
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == '__main__':
    success = main()
    if success:
        print("\n📝 下一步:")
        print("1. 重启后端服务")
        print("2. 前端现在可以使用项目分类功能")
        print("3. 绩效页面支持分类筛选")
    sys.exit(0 if success else 1)
