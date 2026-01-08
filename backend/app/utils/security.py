from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.models.user import User
from app.database import get_db
from app.utils.token_manager import token_manager
from sqlalchemy.orm import Session

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# JWT Bearer认证
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """验证令牌并返回用户ID"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（支持 Redis Token 白名单和自动续期）"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔐 [Security] 开始获取当前用户")
    logger.info(f"📜 [Security] Credentials类型: {type(credentials)}")
    
    if not credentials or not credentials.credentials:
        logger.error("❌ [Security] 没有提供认证凭据")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="没有提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    logger.info(f"🔑 [Security] 接收到的Token: {token[:20]}...")
    
    # 第一步：验证 JWT 签名
    user_id = verify_token(token)
    logger.info(f"🆔 [Security] Token解析结果 - user_id: {user_id}")
    
    if user_id is None:
        logger.warning("❌ [Security] JWT Token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 第二步：检查 Redis 白名单（如果 Redis 可用）
    from app.utils.redis_client import redis_client
    
    # 先检查 Redis 是否连接
    redis_connected = redis_client.is_connected()
    
    if redis_connected:
        # Redis 可用，检查白名单
        token_data = token_manager.verify_token(token)
        if token_data is None:
            # Token 不在白名单中（已被撤销或过期）
            logger.error("❌ [Security] Token 不在 Redis 白名单中，可能已被撤销或过期")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 已失效，请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ [Security] Token 白名单验证通过 - User: {token_data.get('username')}")
        
        # 第三步：自动续期 Token（滑动窗口）
        renewed = token_manager.renew_token(token)
        if renewed:
            logger.info(f"🔄 [Security] Token 已自动续期")
    else:
        # Redis 不可用，降级为纯 JWT 模式
        logger.warning("⚠️ [Security] Redis 未连接，降级为纯 JWT 模式（仅验证 JWT 签名）")
    
    # 第四步：从数据库查询用户
    user = db.query(User).filter(User.id == user_id).first()
    logger.info(f"💾 [Security] 数据库查询结果 - 用户存在: {user is not None}")
    
    if user is None:
        logger.warning(f"❌ [Security] 用户不存在: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        logger.warning(f"❌ [Security] 用户已被禁用: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"✅ [Security] 用户验证成功: {user.username}, 角色: {user.role}, ID: {user.id}")
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"👥 [Security] 检查管理员权限: {current_user.username}, 角色: {current_user.role}")
    
    # 允许多种管理员角色
    admin_roles = ["admin", "super", "administrator"]
    if current_user.role.lower() not in admin_roles:
        logger.warning(f"❌ [Security] 权限不足: {current_user.username}, 角色: {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    logger.info(f"✅ [Security] 管理员权限验证成功: {current_user.username}")
    return current_user 