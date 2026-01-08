from sqlalchemy import create_engine, text
import os


def main():
    database_url = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5432/medical_annotation")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # 扩展 task_attachments.attachment_type 字段长度到 50
        conn.execute(text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='task_attachments' 
                    AND column_name='attachment_type'
                ) THEN
                    ALTER TABLE task_attachments ALTER COLUMN attachment_type TYPE VARCHAR(50);
                END IF;
            END$$;
            """
        ))
        conn.commit()
        print("✅ attachment_type 列长度已更新为 50")


if __name__ == "__main__":
    main()

