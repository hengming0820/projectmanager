# app/middleware/logging_middleware.py

import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import Message

# 获取一个logger实例
logger = logging.getLogger(__name__)


class RichLoggingMiddleware(BaseHTTPMiddleware):
    """
    一个功能丰富的日志中间件，用于记录请求和响应的详细信息。
    - 为每个请求生成唯一的 request_id 以便追踪。
    - 安全地记录请求体，而不会导致下游处理函数挂起。
    - 使用结构化日志记录关键信息（方法、路径、状态码、耗时）。
    - 记录未处理的异常。
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 为每个请求生成一个唯一的ID
        request_id = str(uuid.uuid4())

        # 将请求ID放入请求状态，方便在应用的任何地方访问（可选）
        request.state.request_id = request_id

        # 准备结构化日志的基础信息
        log_info = {
            "rid": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": f"{request.client.host}:{request.client.port}" if request.client else "unknown",
        }

        logger.info(f"Request started: {log_info}")
        # 以DEBUG级别记录详细的头信息
        logger.debug(f"rid={request_id} headers={dict(request.headers)}")

        # 【核心修复】安全地读取和记录请求体
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > 0:
            # 读取请求体
            body_bytes = await request.body()

            # body()被调用后，流已耗尽。我们必须创建一个新的接收器(receiver)
            # 并替换 request._receive，以便端点可以再次读取它。
            async def receive() -> Message:
                return {"type": "http.request", "body": body_bytes}

            request._receive = receive

            # 以DEBUG级别记录请求体，防止日志过长
            try:
                body_text = body_bytes.decode('utf-8')
                logger.debug(f"rid={request_id} body={body_text}")
            except UnicodeDecodeError:
                logger.debug(f"rid={request_id} body=[non-utf8-data]")

        # 使用 monotonic 时钟来准确测量时间间隔
        start_time = time.monotonic()

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time_ms = (time.monotonic() - start_time) * 1000

            # 记录最终的响应信息
            log_info["status_code"] = response.status_code
            log_info["duration_ms"] = f"{process_time_ms:.2f}"
            logger.info(f"Request finished: {log_info}")

            return response

        except Exception as e:
            # 记录未捕获的异常
            process_time_ms = (time.monotonic() - start_time) * 1000
            log_info["status_code"] = 500
            log_info["duration_ms"] = f"{process_time_ms:.2f}"
            log_info["error"] = str(e)

            # 使用 exc_info=True 会自动附加异常堆栈信息
            logger.error(f"Request failed: {log_info}", exc_info=True)

            # 重新抛出异常，以便FastAPI的默认异常处理器可以捕获并返回一个标准的500错误响应
            raise