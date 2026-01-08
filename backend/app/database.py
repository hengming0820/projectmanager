from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

# 配置日志
logger = logging.getLogger(__name__)

try:
    # 创建数据库引擎
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # 设置为True可以查看SQL语句
    )
    
    # 测试数据库连接
    with engine.connect() as conn:
        logger.info("✅ [数据库] 数据库连接成功")
except Exception as e:
    logger.error(f"❌ [数据库] 数据库连接失败: {str(e)}")
    logger.error(f"❌ [数据库] 请检查数据库服务是否启动和配置是否正确")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 