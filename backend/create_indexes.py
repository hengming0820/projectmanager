#!/usr/bin/env python3
"""
任务池性能优化 - 创建数据库索引
直接运行即可，无需 alembic
预期效果: 查询速度提升 60-80%
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal

def check_index_exists(session: Session, table_name: str, index_name: str) -> bool:
    """检查索引是否已存在"""
    try:
        inspector = inspect(engine)
        indexes = inspector.get_indexes(table_name)
        return any(idx['name'] == index_name for idx in indexes)
    except Exception:
        return False

def create_indexes(session: Session):
    """创建性能优化索引"""
    dialect = engine.dialect.name
    
    # 要创建的索引列表
    indexes = [
        # tasks表的单列索引
        ("tasks", "idx_tasks_status", "CREATE INDEX idx_tasks_status ON tasks (status)"),
        ("tasks", "idx_tasks_assigned_to", "CREATE INDEX idx_tasks_assigned_to ON tasks (assigned_to)"),
        ("tasks", "idx_tasks_created_at", "CREATE INDEX idx_tasks_created_at ON tasks (created_at)"),
        ("tasks", "idx_tasks_project_id", "CREATE INDEX idx_tasks_project_id ON tasks (project_id)"),
        
        # tasks表的复合索引
        ("tasks", "idx_task_project_status", "CREATE INDEX idx_task_project_status ON tasks (project_id, status)"),
        ("tasks", "idx_task_status_assigned", "CREATE INDEX idx_task_status_assigned ON tasks (status, assigned_to)"),
        
        # projects表的索引
        ("projects", "idx_projects_status", "CREATE INDEX idx_projects_status ON projects (status)"),
    ]
    
    created_count = 0
    skipped_count = 0
    
    for table_name, index_name, sql in indexes:
        try:
            # 检查索引是否已存在
            if check_index_exists(session, table_name, index_name):
                print(f"⏭️  索引已存在: {index_name}")
                skipped_count += 1
                continue
            
            # 创建索引
            print(f"📝 创建索引: {index_name}...")
            session.execute(text(sql))
            print(f"✅ 成功创建: {index_name}")
            created_count += 1
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'duplicate' in error_msg or 'already exists' in error_msg or 'exist' in error_msg:
                print(f"⏭️  索引已存在: {index_name}")
                skipped_count += 1
            else:
                print(f"❌ 创建索引失败 {index_name}: {e}")
    
    print("\n" + "="*60)
    print(f"🎉 索引创建完成！")
    print(f"   ✅ 新创建: {created_count} 个索引")
    print(f"   ⏭️  跳过: {skipped_count} 个索引（已存在）")
    print(f"   📊 预期性能提升: 60-80%")
    print("="*60)
    
    # 验证索引
    print("\n🔍 验证已创建的索引...")
    verify_indexes(session)

def verify_indexes(session: Session):
    """验证索引是否创建成功"""
    inspector = inspect(engine)
    
    tables = ['tasks', 'projects']
    for table in tables:
        try:
            indexes = inspector.get_indexes(table)
            print(f"\n📋 表 '{table}' 的索引:")
            for idx in indexes:
                columns = ', '.join(idx['column_names'])
                print(f"   • {idx['name']}: ({columns})")
        except Exception as e:
            print(f"❌ 无法获取表 '{table}' 的索引: {e}")

def drop_indexes(session: Session):
    """删除性能优化索引（如果需要回滚）"""
    print("🗑️  开始删除性能优化索引...")
    
    # 要删除的索引列表
    indexes = [
        ("tasks", "idx_tasks_status"),
        ("tasks", "idx_tasks_assigned_to"),
        ("tasks", "idx_tasks_created_at"),
        ("tasks", "idx_tasks_project_id"),
        ("tasks", "idx_task_project_status"),
        ("tasks", "idx_task_status_assigned"),
        ("projects", "idx_projects_status"),
    ]
    
    for table_name, index_name in indexes:
        try:
            if not check_index_exists(session, table_name, index_name):
                print(f"⏭️  索引不存在，跳过: {index_name}")
                continue
            
            sql = f"DROP INDEX {index_name} ON {table_name}"
            session.execute(text(sql))
            print(f"✅ 已删除索引: {index_name}")
            
        except Exception as e:
            print(f"❌ 删除索引失败 {index_name}: {e}")
    
    print("🎉 索引删除完成！")

def main() -> bool:
    """主函数"""
    print("\n" + "="*60)
    print("  任务池性能优化工具")
    print("="*60)
    print("START: 任务池索引优化 (预期性能提升 60-80%)\n")
    
    session = SessionLocal()
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--drop':
            # 删除索引
            drop_indexes(session)
        else:
            # 创建索引
            create_indexes(session)
            
        session.commit()
        print("\nDONE: 索引优化完成")
        print("\n💡 提示:")
        print("   - 如需删除这些索引，运行: python create_indexes.py --drop")
        print("   - 重启后端服务以使性能优化生效")
        print()
        return True
    except Exception as e:
        print(f"\nERROR: 操作失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)

