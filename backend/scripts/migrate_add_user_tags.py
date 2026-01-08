#!/usr/bin/env python3
"""
添加用户标签字段的数据库迁移脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import SessionLocal, engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_user_tags():
    """添加用户标签字段"""
    db = SessionLocal()
    try:
        # 检查 tags 列是否已存在
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'tags';
        """))
        
        if result.fetchone():
            logger.info("✅ users.tags 字段已存在，跳过迁移")
            return
        
        # 添加 tags 列
        logger.info("🔄 开始添加 users.tags 字段...")
        db.execute(text("ALTER TABLE users ADD COLUMN tags TEXT;"))
        
        # 为现有用户设置默认标签
        logger.info("🔄 为现有用户设置默认标签...")
        default_tags = '["专注工作", "积极向上", "团队协作"]'  # JSON 格式的默认标签
        db.execute(text(f"UPDATE users SET tags = '{default_tags}' WHERE tags IS NULL;"))
        
        db.commit()
        logger.info("✅ users.tags 字段添加完成")
        
        # 验证迁移结果
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE tags IS NOT NULL;"))
        count = result.fetchone()[0]
        logger.info(f"📊 已更新 {count} 个用户的标签字段")
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 开始用户标签字段迁移...")
    migrate_add_user_tags()
    logger.info("🎉 用户标签字段迁移完成！")
