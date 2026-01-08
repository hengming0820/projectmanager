#!/usr/bin/env python3
"""
One-off migration: add skipped-related columns to tasks
  - skipped_at   TIMESTAMP NULL
  - skip_reason  TEXT NULL
  - skip_images  JSONB/JSON NULL (DB-dependent)

Usage:
  python backend/scripts/migrate_add_skipped_fields.py
  or inside docker: docker-compose exec backend python scripts/migrate_add_skipped_fields.py
"""

from sqlalchemy import text
from app.database import engine


def main() -> None:
    with engine.begin() as conn:
        # Try PostgreSQL first
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skipped_at TIMESTAMP"))
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_reason TEXT"))
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_images JSONB"))
            print("✅ Migration (PostgreSQL): columns added with JSONB")
        except Exception:
            # Fallback for MySQL 8+ (JSON) or SQLite (TEXT)
            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN skipped_at DATETIME"))
            except Exception:
                # already exists or SQLite type
                pass
            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN skip_reason TEXT"))
            except Exception:
                pass
            # Try JSON for MySQL; if fails (e.g., SQLite), use TEXT
            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN skip_images JSON"))
                print("✅ Migration (MySQL): columns added with JSON")
            except Exception:
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN skip_images TEXT"))
                    print("✅ Migration (SQLite): columns added with TEXT for skip_images")
                except Exception:
                    pass

    print("✅ Migration completed: tasks.skipped_at/skip_reason/skip_images added (best effort)")


if __name__ == "__main__":
    main()

