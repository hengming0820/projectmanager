from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.utils.token_manager import token_manager
from sqlalchemy import text
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    def authenticate_user(self, db: Session, username: str, password: str) -> User:
        """验证用户"""
        logger.info(f"🔐 [AuthService] 开始验证用户: {username}")
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning(f"❌ [AuthService] 用户不存在: {username}")
            return None
            
        logger.info(f"👤 [AuthService] 找到用户: {username}, 角色: {user.role}, 状态: {user.status}")
        logger.info(f"📅 [AuthService] 用户hire_date (数据库): {user.hire_date}")
        logger.info(f"📅 [AuthService] 用户hire_date类型: {type(user.hire_date)}")
        
        if not verify_password(password, user.password_hash):
            logger.warning(f"❌ [AuthService] 密码验证失败: {username}")
            return None
            
        logger.info(f"✅ [AuthService] 用户验证成功: {username}")
        return user
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """创建用户"""
        logger.info(f"👤 [AuthService] 开始创建用户: {user_data.username}")
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            logger.warning(f"❌ [AuthService] 用户名已存在: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            logger.warning(f"❌ [AuthService] 邮箱已存在: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            real_name=user_data.real_name,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
            department=user_data.department,
            avatar_url=user_data.avatar_url
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"✅ [AuthService] 用户创建成功: {user_data.username}")
        return db_user
    
    def login(self, db: Session, user_data: UserLogin):
        """用户登录"""
        logger.info(f"🔐 [AuthService] 开始登录流程: {user_data.username}")
        
        try:
            # 检查数据库连接
            logger.info(f"🔄 [AuthService] 检查数据库连接")
            #db.execute('SELECT 1')
            db.execute(text("SELECT 1")).scalar_one()
            logger.info(f"✅ [AuthService] 数据库连接正常")
        except Exception as e:
            logger.error(f"❌ [AuthService] 数据库连接失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"数据库连接失败: {str(e)}",
            )
        
        user = self.authenticate_user(db, user_data.username, user_data.password)
        if not user:
            logger.error(f"❌ [AuthService] 用户认证失败: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user.status != "active":
            logger.warning(f"⚠️ [AuthService] 用户已被禁用: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": user.id})
        
        # 将 token 存入 Redis 白名单
        token_stored = token_manager.store_token(
            token=access_token,
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        if token_stored:
            logger.info(f"✅ [AuthService] Token 已存入 Redis 白名单")
        else:
            logger.warning(f"⚠️ [AuthService] Token 未存入 Redis（Redis 可能未连接，将使用纯 JWT 模式）")
        
        logger.info(f"✅ [AuthService] 登录成功: {user_data.username}, 角色: {user.role}")
        
        # 导入UserResponse schema
        from app.schemas.user import UserResponse
        
        # 创建UserResponse对象 - 使用from_attributes自动映射所有字段
        user_response = UserResponse.model_validate(user)
        
        # 添加详细的调试日志
        logger.info(f"👤 [AuthService] 用户hire_date (User对象): {user.hire_date}")
        logger.info(f"👤 [AuthService] 用户hire_date类型: {type(user.hire_date)}")
        
        # 获取model_dump的结果
        user_dict = user_response.model_dump()
        logger.info(f"📋 [AuthService] UserResponse.model_dump(): {user_dict}")
        logger.info(f"📅 [AuthService] model_dump中的hire_date: {user_dict.get('hire_date')}")
        logger.info(f"📅 [AuthService] model_dump中hire_date类型: {type(user_dict.get('hire_date'))}")
        
        # 测试JSON序列化
        import json
        try:
            json_str = json.dumps(user_dict, default=str)
            logger.info(f"🔄 [AuthService] JSON序列化后: {json_str}")
        except Exception as e:
            logger.error(f"❌ [AuthService] JSON序列化失败: {e}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }

# 全局认证服务实例
auth_service = AuthService() 