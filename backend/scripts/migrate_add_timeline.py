#!/usr/bin/env python3
"""
One-off migration: add timeline column to tasks (JSONB, default [])
Usage:
  python backend/scripts/migrate_add_timeline.py
  or inside docker: docker-compose exec backend python scripts/migrate_add_timeline.py
"""

from sqlalchemy import text
from app.database import engine


def main() -> None:
    with engine.begin() as conn:
        # Add column if not exists (PostgreSQL)
        conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS timeline JSONB"))
        # Backfill nulls to []
        conn.execute(text("UPDATE tasks SET timeline = '[]'::jsonb WHERE timeline IS NULL"))
        # Set default
        conn.execute(text("ALTER TABLE tasks ALTER COLUMN timeline SET DEFAULT '[]'::jsonb"))
    print("✅ Migration completed: tasks.timeline (JSONB) added with default []")


if __name__ == "__main__":
    main()

