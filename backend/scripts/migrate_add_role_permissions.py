from sqlalchemy import text
from app.database import engine


def run_migration():
    with engine.connect() as conn:
        dialect = conn.dialect.name.lower()
        print(f"Detected DB dialect: {dialect}")

        if dialect == 'postgresql':
            sql = "ALTER TABLE roles ADD COLUMN IF NOT EXISTS permissions TEXT"
        elif dialect == 'mysql':
            sql = "ALTER TABLE roles ADD COLUMN permissions TEXT"
        else:
            # sqlite & others
            sql = "ALTER TABLE roles ADD COLUMN permissions TEXT"

        try:
            conn.execute(text(sql))
            conn.commit()
            print("✅ Column 'permissions' added (or already exists).")
        except Exception as e:
            # 对于不支持 IF NOT EXISTS 的方言，可能已存在时会报错；尝试忽略已存在错误
            print(f"⚠️ Migration attempt resulted in: {e}")
            print("If this indicates the column already exists, it's safe to ignore.")


if __name__ == '__main__':
    run_migration()


