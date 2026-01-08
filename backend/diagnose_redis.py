#!/usr/bin/env python3
"""
Redis 诊断脚本 - 在后端环境中测试 Redis 连接
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Redis Connection Diagnostic Tool")
print("=" * 60)

# 1. 显示 Python 环境
print(f"\n[1] Python Environment:")
print(f"    Python: {sys.executable}")
print(f"    Version: {sys.version}")

# 2. 检查 redis 包
print(f"\n[2] Redis Package:")
try:
    import redis
    print(f"    [OK] redis package installed")
    print(f"    Version: {redis.__version__}")
except ImportError as e:
    print(f"    [ERROR] redis package not found: {e}")
    sys.exit(1)

# 3. 加载配置
print(f"\n[3] Configuration:")
try:
    from app.config import settings
    print(f"    [OK] Config loaded")
    print(f"    Redis URL: {settings.REDIS_URL}")
except Exception as e:
    print(f"    [ERROR] Failed to load config: {e}")
    sys.exit(1)

# 4. 测试直接连接
print(f"\n[4] Direct Connection Test:")
try:
    r = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5
    )
    result = r.ping()
    print(f"    [OK] Direct connection successful")
    print(f"    PING response: {result}")
except redis.ConnectionError as e:
    print(f"    [ERROR] Connection failed: {e}")
except redis.TimeoutError as e:
    print(f"    [ERROR] Connection timeout: {e}")
except Exception as e:
    print(f"    [ERROR] Unexpected error: {type(e).__name__}: {e}")

# 5. 测试 RedisClient
print(f"\n[5] RedisClient Test:")
try:
    from app.utils.redis_client import RedisClient, redis_ping
    
    print(f"    Testing get_instance()...")
    instance = RedisClient.get_instance()
    if instance:
        print(f"    [OK] RedisClient instance created")
        print(f"    Instance type: {type(instance)}")
    else:
        print(f"    [ERROR] RedisClient instance is None")
    
    print(f"    Testing is_connected()...")
    connected = RedisClient.is_connected()
    print(f"    Connected: {connected}")
    
    print(f"    Testing redis_ping()...")
    ping_result = redis_ping()
    print(f"    Ping result: {ping_result}")
    
except Exception as e:
    print(f"    [ERROR] RedisClient test failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)

