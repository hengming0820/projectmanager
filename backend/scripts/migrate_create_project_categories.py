"""
数据库迁移脚本：创建项目分类表
运行方式: python scripts/migrate_create_project_categories.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine


def run_migration():
    """执行迁移"""
    print("开始迁移：创建项目分类表...")
    
    try:
        with Session(engine) as session:
            # 读取 SQL 文件
            sql_file = backend_dir / "migrations" / "create_project_categories_table.sql"
            if not sql_file.exists():
                print(f"[ERROR] SQL 文件不存在: {sql_file}")
                return False
            
            sql_content = sql_file.read_text(encoding='utf-8')
            
            # 执行 SQL
            print("执行 SQL 脚本...")
            session.execute(text(sql_content))
            session.commit()
            
            print("[OK] 项目分类表创建成功")
            print("[OK] 已为现有项目插入默认分类（会议记录、模型测试）")
            return True
            
    except Exception as e:
        print(f"[ERROR] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

