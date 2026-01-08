from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 数据库配置
    # Docker环境：postgresql://admin:password123@postgres:5432/medical_annotation
    # 本地开发：postgresql://admin:password123@localhost:5432/medical_annotation
    DATABASE_URL: str = "postgresql://admin:password123@localhost:5432/medical_annotation"
    
    # Redis配置
    # Docker环境：redis://redis:6379 (通过 docker-compose 环境变量设置)
    # 本地开发：redis://localhost:6379 (使用默认值)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # MinIO配置（ENDPOINT 用于后端连接；PUBLIC_ENDPOINT/签名链接用于前端访问）
    # Docker环境：minio:9000
    # 本地开发：localhost:9000
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "medical-annotations"
    # 前端可访问的 MinIO 地址（如浏览器访问的域名:端口）。
    # 若后端运行在容器内，ENDPOINT 可能是 'minio:9000'，但前端应使用 'localhost:9000' 或网关域名
    MINIO_PUBLIC_ENDPOINT: str = "192.168.200.20:9000"
    # 若 >0，则返回可直接访问的预签名URL，单位秒；否则返回基于 PUBLIC_ENDPOINT 的直链
    MINIO_PRESIGNED_SECONDS: int = 0
    # 若启用代理，前端访问走 /api/files/{object_path}
    MINIO_PROXY_PUBLIC: bool = False
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600
    # Token 自动续期阈值（分钟）- 剩余时间少于此值时触发续期
    TOKEN_RENEW_THRESHOLD_MINUTES: int = 5
    
    # 应用配置
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3006", "http://localhost:3007", "http://localhost:3008", "http://localhost:3009", "http://localhost:3010", "http://localhost:3011"]
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"
        # 允许环境变量覆盖默认值
        env_file_encoding = 'utf-8'
        case_sensitive = False
        # 环境变量优先级高于 .env 文件
        env_nested_delimiter = '__'

settings = Settings()

# 启动时打印配置（用于调试）
if os.getenv("DEBUG", "false").lower() == "true":
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Redis URL: {settings.REDIS_URL}")
    logger.info(f"🔧 Database URL: {settings.DATABASE_URL[:50]}...")
    logger.info(f"🔧 MinIO Endpoint: {settings.MINIO_ENDPOINT}")