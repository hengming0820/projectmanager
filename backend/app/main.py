# main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import logging
import uvicorn
import json
import asyncio

# 导入你的API路由模块
from app.api import auth, users, projects, tasks, performance, menu, roles, work_logs, collaboration, upload, articles, files, project_categories, performance_export, notifications
from app.utils.redis_client import redis_ping
from app.services.notification_ws import manager as ws_manager
from app.services.scheduler_service import scheduler_service
from app.utils.security import get_current_user
# 导入你的配置和数据库设置
from app.config import settings
from app.database import engine, Base
# 【新增】从我们创建的文件中导入新的日志中间件
from app.middleware.logging_middleware import RichLoggingMiddleware

# 配置日志，建议使用更详细的格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建数据库表
# 在生产环境中，建议使用 Alembic 等工具进行数据库迁移管理
logger.info("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
logger.info("数据库表创建完成。")

# 创建FastAPI应用
app = FastAPI(
    title="医学影像标注管理系统",
    description="专用于医学影像标注的内部项目管理系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加全局验证错误处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.error(f"❌ [ValidationError] 请求验证失败: {request.method} {request.url}")
    logger.error(f"❌ [ValidationError] 验证错误详情: {exc.errors()}")
    
    try:
        # 尝试读取请求体进行调试
        if request.method == "POST":
            body = await request.body()
            logger.error(f"❌ [ValidationError] 请求体: {body.decode() if body else 'Empty'}")
    except Exception as e:
        logger.error(f"❌ [ValidationError] 读取请求体失败: {e}")
    
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求数据验证失败",
            "errors": error_details
        }
    )

# 【移除】旧的日志中间件
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     ... (这里是你的旧代码，现在可以完全删除了)

# 【新增】引入并使用新的日志中间件
# 这个中间件应该放在CORS中间件之前，以确保所有请求都被记录
app.add_middleware(RichLoggingMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
logger.info("正在注册API路由...")
app.include_router(auth, prefix="/auth", tags=["认证"])
app.include_router(users, prefix="/users", tags=["用户管理"])
app.include_router(roles, prefix="/roles", tags=["角色管理"])
app.include_router(projects, prefix="/projects", tags=["项目管理"])
app.include_router(project_categories.router, tags=["项目分类"])
app.include_router(tasks, prefix="/tasks", tags=["任务管理"])
app.include_router(performance, prefix="/performance", tags=["绩效管理"])
app.include_router(performance_export.router, prefix="/performance", tags=["绩效导出"])
app.include_router(work_logs.router, tags=["工作日志"])
app.include_router(collaboration, tags=["团队协作"])
app.include_router(menu, prefix="/menu", tags=["菜单管理"])
app.include_router(upload, tags=["文件上传"])
app.include_router(articles, tags=["文章发布"])
app.include_router(files, tags=["文件代理"])
app.include_router(notifications.router, tags=["通知管理"])
logger.info("API路由注册完成。")

# 启动时初始化 Redis 连接
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    logger.info("=" * 60)
    logger.info("🚀 [Startup] 正在启动医学影像标注管理系统...")
    logger.info("=" * 60)
    
    # 测试 Redis 连接
    logger.info("🔧 [Startup] 正在初始化 Redis 连接...")
    logger.info(f"🔧 [Startup] Redis URL: {settings.REDIS_URL}")
    try:
        redis_status = redis_ping()
        if redis_status:
            logger.info("✅ [Startup] Redis 连接成功！Token 管理功能已启用")
        else:
            logger.warning("⚠️ [Startup] Redis 连接失败，系统将以降级模式运行（仅 JWT）")
            logger.warning("⚠️ [Startup] 请检查上方的 Redis 连接错误日志获取详细信息")
    except Exception as e:
        logger.error(f"❌ [Startup] Redis 初始化异常: {str(e)}")
        logger.warning("⚠️ [Startup] 系统将以降级模式运行（仅 JWT）")
    
    # 初始化定时任务
    logger.info("⏰ [Startup] 正在初始化定时任务...")
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        scheduler_service.set_event_loop(loop)
        scheduler_service.start()
        jobs = scheduler_service.list_jobs()
        logger.info(f"✅ [Startup] 定时任务初始化成功，已加载 {len(jobs)} 个任务")
        for job in jobs:
            logger.info(f"  📅 {job['name']} (ID: {job['id']}) - 下次执行: {job['next_run_time']}")
    except Exception as e:
        logger.error(f"❌ [Startup] 定时任务初始化失败: {e}", exc_info=True)
    
    logger.info("=" * 60)
    logger.info("✅ [Startup] 系统启动完成")
    logger.info(f"📝 [Startup] API 文档: http://0.0.0.0:8000/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的清理任务"""
    logger.info("=" * 60)
    logger.info("🛑 [Shutdown] 系统正在关闭...")
    logger.info("=" * 60)
    
    # 关闭定时任务
    try:
        scheduler_service.shutdown()
        logger.info("✅ [Shutdown] 定时任务已关闭")
    except Exception as e:
        logger.error(f"❌ [Shutdown] 关闭定时任务失败: {e}")
    
    logger.info("✅ [Shutdown] 系统关闭完成")

# --- 保留你的测试和根路由 ---
@app.get("/")
async def root():
    """根路径"""
    logger.info("🏠 [Root] 访问根路径")
    return {
        "message": "欢迎使用医学影像标注管理系统API",
        "version": app.version,
        "docs_url": app.docs_url
    }

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查，用于监控服务是否存活"""
    logger.info("💚 [Health] 健康检查")
    # 附加 Redis 状态，便于排查
    try:
        redis_ok = redis_ping()
    except Exception:
        redis_ok = False
    return {"status": "healthy", "redis": "ok" if redis_ok else "down"}

@app.get("/api/scheduler/jobs", tags=["定时任务"], dependencies=[Depends(get_current_user)])
async def list_scheduled_jobs():
    """获取所有定时任务列表"""
    try:
        jobs = scheduler_service.list_jobs()
        return {
            "success": True,
            "total": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        logger.error(f"❌ [Scheduler] 获取任务列表失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/scheduler/trigger-work-reminder", tags=["定时任务"])
async def trigger_work_reminder(current_user = Depends(get_current_user)):
    """
    立即触发下班提醒（测试用）
    仅管理员可用
    """
    # 检查权限
    if current_user.role != 'admin':
        return {
            "success": False,
            "message": "只有管理员可以触发定时通知"
        }
    
    try:
        scheduler_service.trigger_work_end_reminder_now()
        return {
            "success": True,
            "message": "下班提醒已发送给所有在线用户"
        }
    except Exception as e:
        logger.error(f"❌ [Scheduler] 触发下班提醒失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"发送失败: {str(e)}"
        }

# WebSocket: 审核员通知
@app.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket):
    role = None
    user = {}
    redis_listener_task = None
    
    try:
        # 首条消息应包含 {role, user:{id,username,real_name}}
        await websocket.accept()
        first = await websocket.receive_json()
        role = (first.get("role") or "").lower()
        user = first.get("user") or {}
        user_id = str(user.get("id", ""))
        username = user.get("username", "unknown")
        
        logger.info(f"🔔 [WS] 新连接请求 - 原始数据: {first}")
        logger.info(f"🔔 [WS] 处理后 - role={role}, user={username}, user_id={user_id}")
        
        # 连接到 WebSocket 管理器（用于直接推送）
        await ws_manager.connect(websocket, role=role, user=user)
        
        # 导入 Redis 通知服务
        from app.services.redis_notification_service import redis_notifier
        
        # 如果 Redis 可用，订阅相关频道
        if redis_notifier.enabled:
            logger.info(f"🔔 [WS] Redis 可用，开始订阅频道...")
            
            # 定义消息回调函数
            async def on_redis_message(channel: str, message: dict):
                """处理 Redis 消息并转发到 WebSocket"""
                try:
                    logger.info(f"📨 [WS→Client] 从 Redis 收到消息: {channel} → {username}")
                    # 发送消息到 WebSocket 客户端
                    import json
                    await websocket.send_text(json.dumps(message, ensure_ascii=False))
                except Exception as e:
                    logger.error(f"❌ [WS] 转发 Redis 消息失败: {e}")
            
            # 订阅用户个人频道
            if user_id:
                await redis_notifier.subscribe_user_channel(user_id, on_redis_message)
                logger.info(f"✅ [WS] 已订阅用户频道: notify:user:{user_id}")
            
            # 订阅角色频道
            if role:
                await redis_notifier.subscribe_role_channel(role, on_redis_message)
                logger.info(f"✅ [WS] 已订阅角色频道: notify:role:{role}")
            
            # 订阅全局频道
            await redis_notifier.subscribe_global(on_redis_message)
            logger.info(f"✅ [WS] 已订阅全局频道: notify:global")
            
            # 启动 Redis 监听任务（如果还没有运行）
            if not redis_notifier.running:
                redis_listener_task = asyncio.create_task(redis_notifier.listen())
                logger.info(f"🚀 [WS] 启动 Redis 监听任务")
        else:
            logger.info(f"⚠️ [WS] Redis 不可用，仅使用直接 WebSocket 推送")
        
        # 主循环：处理客户端消息（心跳等）
        while True:
            try:
                # 接收客户端消息
                data = await websocket.receive_text()
                
                # 尝试解析为 JSON
                try:
                    message = json.loads(data)
                    msg_type = message.get("type", "")
                    
                    # 处理心跳消息
                    if msg_type == "ping":
                        logger.debug(f"💓 [WS] 收到心跳 from {username}")
                        # 响应 pong
                        await websocket.send_text(json.dumps({
                            "type": "pong",
                            "timestamp": message.get("timestamp"),
                            "server_time": int(asyncio.get_event_loop().time() * 1000)
                        }))
                    else:
                        logger.debug(f"📨 [WS] 收到消息: {msg_type} from {username}")
                        
                except json.JSONDecodeError:
                    # 非 JSON 消息，当作普通文本处理
                    logger.debug(f"📨 [WS] 收到文本消息 from {username}: {data[:50]}")
                    
            except asyncio.CancelledError:
                logger.info(f"🔔 [WS] 连接被取消 - {username}")
                break
            except Exception as e:
                logger.error(f"🔔 [WS] 处理消息异常 - {username}: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"🔔 [WS] 连接断开 - role={role}, user={user.get('username', 'unknown')}")
    except Exception as e:
        logger.error(f"🔔 [WS] 连接异常: {e}", exc_info=True)
    finally:
        # 清理连接
        ws_manager.disconnect(websocket)
        
        # 取消 Redis 监听任务（如果是我们启动的）
        if redis_listener_task and not redis_listener_task.done():
            redis_listener_task.cancel()
            logger.info(f"🛑 [WS] 取消 Redis 监听任务")
        
        logger.info(f"✅ [WS] 连接清理完成 - {user.get('username', 'unknown')}")

# --- 应用启动 ---
if __name__ == "__main__":
    logger.info("启动Uvicorn服务器...")
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)