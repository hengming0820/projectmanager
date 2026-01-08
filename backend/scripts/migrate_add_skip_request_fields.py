#!/usr/bin/env python3
"""
数据库迁移脚本：为任务表添加跳过申请相关字段
支持多数据库类型：PostgreSQL、MySQL、SQLite
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_columns(session: Session):
    """确保跳过申请相关列存在"""
    dialect = engine.dialect.name
    logger.info(f"检测到数据库类型: {dialect}")
    
    if dialect == 'postgresql':
        session.execute(text("""
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_requested_at TIMESTAMP;
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_request_reason TEXT;
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_request_images JSON;
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_requested_by VARCHAR(36);
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_reviewed_at TIMESTAMP;
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_reviewed_by VARCHAR(36);
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_review_comment TEXT;
        """))
    elif dialect == 'mysql':
        # MySQL 支持 IF NOT EXISTS
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_requested_at DATETIME;"))
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_request_reason TEXT;"))
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_request_images JSON;"))
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_requested_by VARCHAR(36);"))
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_reviewed_at DATETIME;"))
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_reviewed_by VARCHAR(36);"))
        session.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS skip_review_comment TEXT;"))
    else:
        # SQLite: 检查列是否存在
        def has_col(col: str) -> bool:
            rows = session.execute(text("PRAGMA table_info(tasks)")).fetchall()
            return any(r[1] == col for r in rows)
        
        if not has_col('skip_requested_at'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_requested_at DATETIME"))
        if not has_col('skip_request_reason'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_request_reason TEXT"))
        if not has_col('skip_request_images'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_request_images TEXT"))  # SQLite用TEXT存储JSON
        if not has_col('skip_requested_by'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_requested_by TEXT"))
        if not has_col('skip_reviewed_at'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_reviewed_at DATETIME"))
        if not has_col('skip_reviewed_by'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_reviewed_by TEXT"))
        if not has_col('skip_review_comment'):
            session.execute(text("ALTER TABLE tasks ADD COLUMN skip_review_comment TEXT"))

def main():
    """主函数"""
    logger.info('🚀 开始迁移: 为 tasks 表添加跳过申请相关字段...')
    session = SessionLocal()
    try:
        ensure_columns(session)
        session.commit()
        logger.info('✅ 跳过申请字段添加完成')
    except Exception as e:
        logger.error(f'❌ 迁移失败: {e}')
        session.rollback()
        raise
    finally:
        session.close()
    logger.info('🎉 迁移完成')

if __name__ == "__main__":
    main()
