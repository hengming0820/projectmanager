from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import auth_service
from app.utils.security import get_current_user

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    logger.info(f"📝 [AuthAPI] 收到注册请求: {user_data.username}")
    try:
        result = auth_service.create_user(db, user_data)
        logger.info(f"✅ [AuthAPI] 注册成功: {user_data.username}")
        return result
    except Exception as e:
        logger.error(f"❌ [AuthAPI] 注册失败: {user_data.username}, 错误: {str(e)}")
        raise

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    logger.info(f"🔐 [AuthAPI] 收到登录请求: {user_data.username}")
    logger.info(f"🔐 [AuthAPI] 请求数据: {user_data}")
    logger.info(f"🔐 [AuthAPI] 请求数据类型: {type(user_data)}")
    
    try:
        logger.info(f"🔄 [AuthAPI] 开始调用auth_service.login")
        result = auth_service.login(db, user_data)
        logger.info(f"✅ [AuthAPI] 登录成功: {user_data.username}")
        logger.info(f"✅ [AuthAPI] 返回结果类型: {type(result)}")
        
        # 详细记录返回的user对象
        if isinstance(result, dict) and 'user' in result:
            from pydantic import BaseModel
            if isinstance(result['user'], BaseModel):
                user_dict = result['user'].model_dump()
                logger.info(f"👤 [AuthAPI] 返回的user对象: {user_dict}")
                logger.info(f"📅 [AuthAPI] user中的hire_date: {user_dict.get('hire_date')}")
        
        return result
    except Exception as e:
        logger.error(f"❌ [AuthAPI] 登录失败: {user_data.username}, 错误: {str(e)}")
        logger.error(f"❌ [AuthAPI] 错误类型: {type(e).__name__}")
        import traceback
        logger.error(f"❌ [AuthAPI] 错误堆栈: {traceback.format_exc()}")
        raise

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    logger.info(f"👤 [AuthAPI] 获取用户信息: {current_user.username}")
    logger.info(f"📅 [AuthAPI] /me接口 - user.hire_date: {current_user.hire_date}")
    logger.info(f"📅 [AuthAPI] /me接口 - user.hire_date类型: {type(current_user.hire_date)}")
    
    # 使用UserResponse确保正确序列化
    from app.schemas.user import UserResponse
    user_response = UserResponse.model_validate(current_user)
    logger.info(f"📋 [AuthAPI] /me接口 - UserResponse.model_dump(): {user_response.model_dump()}")
    
    return user_response

@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    """用户登出（撤销 Token）"""
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi import Request
    from app.utils.token_manager import token_manager
    
    logger.info(f"🚪 [AuthAPI] 收到登出请求: {current_user.username}")
    
    try:
        # 从请求头获取 token
        # 注意：这里需要从 request 中获取原始 token
        # 因为 current_user 依赖已经验证了 token，但我们需要原始 token 来撤销
        
        # 撤销用户的所有 token
        revoked = token_manager.revoke_user_tokens(current_user.id)
        
        if revoked:
            logger.info(f"✅ [AuthAPI] 用户登出成功（Token 已撤销）: {current_user.username}")
            return {"message": "登出成功", "revoked": True}
        else:
            logger.warning(f"⚠️ [AuthAPI] Token 撤销失败（Redis 可能未连接）: {current_user.username}")
            return {"message": "登出成功（Redis 未连接，仅前端清除）", "revoked": False}
    except Exception as e:
        logger.error(f"❌ [AuthAPI] 登出失败: {current_user.username}, 错误: {str(e)}")
        # 即使后端失败，也返回成功，让前端清除 token
        return {"message": "登出成功", "revoked": False} 