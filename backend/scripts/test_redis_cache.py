"""
Redis缓存测试脚本
测试缓存服务的基本功能和性能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cache_service import cache_service
from app.database import SessionLocal
from app.models.task import Task
from app.models.project import Project
from app.models.user import User


def test_basic_operations():
    """测试基本缓存操作"""
    print("\n" + "=" * 70)
    print("🧪 测试1: 基本缓存操作")
    print("=" * 70)
    
    # 测试SET/GET
    print("\n📝 测试 SET/GET...")
    test_data = {"name": "测试数据", "value": 123, "items": [1, 2, 3]}
    cache_service.set("test:basic", test_data, expire=60)
    
    cached_data = cache_service.get("test:basic")
    assert cached_data == test_data, "❌ 数据不匹配"
    print("✅ SET/GET 测试通过")
    
    # 测试EXISTS
    print("\n📝 测试 EXISTS...")
    assert cache_service.exists("test:basic") == True, "❌ 存在检查失败"
    assert cache_service.exists("test:nonexistent") == False, "❌ 不存在检查失败"
    print("✅ EXISTS 测试通过")
    
    # 测试DELETE
    print("\n📝 测试 DELETE...")
    cache_service.delete("test:basic")
    assert cache_service.get("test:basic") is None, "❌ 删除失败"
    print("✅ DELETE 测试通过")
    
    # 测试批量DELETE
    print("\n📝 测试批量 DELETE...")
    cache_service.set("test:batch:1", "data1")
    cache_service.set("test:batch:2", "data2")
    cache_service.set("test:batch:3", "data3")
    count = cache_service.delete_pattern("test:batch:*")
    assert count >= 3, "❌ 批量删除失败"
    print(f"✅ 批量DELETE 测试通过 (删除了{count}个key)")


def test_performance():
    """测试缓存性能"""
    print("\n" + "=" * 70)
    print("🧪 测试2: 缓存性能测试")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 测试任务查询性能
        print("\n📊 测试任务查询性能...")
        
        # 第一次查询（无缓存）
        cache_service.delete_pattern("tasks:list:*")
        start = time.time()
        tasks = db.query(Task).limit(100).all()
        db_time = (time.time() - start) * 1000
        print(f"   ⏱️  数据库查询时间: {db_time:.2f}ms")
        
        # 模拟缓存写入
        task_list = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
        cache_service.set("tasks:list:test", task_list)
        
        # 第二次查询（从缓存）
        start = time.time()
        cached_tasks = cache_service.get("tasks:list:test")
        cache_time = (time.time() - start) * 1000
        print(f"   ⚡ 缓存查询时间: {cache_time:.2f}ms")
        
        # 计算性能提升
        if db_time > 0:
            improvement = ((db_time - cache_time) / db_time) * 100
            print(f"   📈 性能提升: {improvement:.1f}%")
        
        # 测试项目查询性能
        print("\n📊 测试项目查询性能...")
        
        cache_service.delete_pattern("projects:list:*")
        start = time.time()
        projects = db.query(Project).limit(50).all()
        db_time = (time.time() - start) * 1000
        print(f"   ⏱️  数据库查询时间: {db_time:.2f}ms")
        
        project_list = [{"id": p.id, "name": p.name, "status": p.status} for p in projects]
        cache_service.set("projects:list:test", project_list)
        
        start = time.time()
        cached_projects = cache_service.get("projects:list:test")
        cache_time = (time.time() - start) * 1000
        print(f"   ⚡ 缓存查询时间: {cache_time:.2f}ms")
        
        if db_time > 0:
            improvement = ((db_time - cache_time) / db_time) * 100
            print(f"   📈 性能提升: {improvement:.1f}%")
        
        # 清理测试数据
        cache_service.delete("tasks:list:test")
        cache_service.delete("projects:list:test")
        
    finally:
        db.close()


def test_cache_invalidation():
    """测试缓存失效机制"""
    print("\n" + "=" * 70)
    print("🧪 测试3: 缓存失效机制")
    print("=" * 70)
    
    print("\n📝 测试任务缓存失效...")
    cache_service.set("tasks:list:proj1:all:all:0:100:False", {"count": 10})
    cache_service.set("tasks:detail:task1", {"id": "task1", "title": "测试"})
    
    # 测试单项目缓存失效
    cache_service.invalidate_tasks_cache("proj1")
    assert cache_service.get("tasks:list:proj1:all:all:0:100:False") is None
    assert cache_service.get("tasks:detail:task1") is None
    print("✅ 任务缓存失效测试通过")
    
    print("\n📝 测试项目缓存失效...")
    cache_service.set("projects:list:active:all:all:0:100", {"count": 5})
    cache_service.set("projects:detail:proj1", {"id": "proj1", "name": "测试项目"})
    cache_service.set("projects:stats:proj1", {"total": 100})
    
    cache_service.invalidate_project_detail_cache("proj1")
    assert cache_service.get("projects:detail:proj1") is None
    assert cache_service.get("projects:stats:proj1") is None
    print("✅ 项目缓存失效测试通过")
    
    print("\n📝 测试用户缓存失效...")
    cache_service.set("users:info:user1", {"id": "user1", "name": "测试用户"})
    cache_service.set("users:list:active", [{"id": "user1"}])
    
    cache_service.invalidate_user_detail_cache("user1")
    assert cache_service.get("users:info:user1") is None
    print("✅ 用户缓存失效测试通过")


def test_stress():
    """压力测试"""
    print("\n" + "=" * 70)
    print("🧪 测试4: 压力测试 (1000次读写)")
    print("=" * 70)
    
    print("\n📝 开始压力测试...")
    
    # 写入测试
    start = time.time()
    for i in range(1000):
        cache_service.set(f"stress:test:{i}", {"index": i, "data": "test"})
    write_time = time.time() - start
    print(f"   ✍️  1000次写入耗时: {write_time:.2f}秒 (平均 {write_time/1000*1000:.2f}ms/次)")
    
    # 读取测试
    start = time.time()
    for i in range(1000):
        cache_service.get(f"stress:test:{i}")
    read_time = time.time() - start
    print(f"   📖 1000次读取耗时: {read_time:.2f}秒 (平均 {read_time/1000*1000:.2f}ms/次)")
    
    # 清理
    cache_service.delete_pattern("stress:test:*")
    print("✅ 压力测试完成")


def main():
    """主函数"""
    print("\n🚀 Redis缓存功能测试")
    
    if not cache_service.enabled:
        print("\n❌ Redis未连接，无法执行测试")
        print("\n💡 请确保 Redis 服务正在运行：")
        print("   - Windows: 直接运行 redis-server.exe")
        print("   - Linux/Mac: redis-server")
        return
    
    print("✅ Redis已连接，开始测试...\n")
    
    try:
        # 执行所有测试
        test_basic_operations()
        test_performance()
        test_cache_invalidation()
        test_stress()
        
        print("\n" + "=" * 70)
        print("🎉 所有测试通过！Redis缓存服务运行正常")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

