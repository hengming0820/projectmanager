"""
测试缓存失效问题修复
验证任务状态变化时，用户的任务列表缓存是否被正确清除
"""
import redis
import sys

def check_redis_connection():
    """检查Redis连接"""
    try:
        client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        client.ping()
        print("✅ Redis连接成功")
        return client
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("   请确保Redis服务正在运行")
        return None

def list_cache_keys(client, pattern="*"):
    """列出所有缓存Key"""
    try:
        keys = client.keys(pattern)
        return keys
    except Exception as e:
        print(f"❌ 获取Key失败: {e}")
        return []

def test_task_list_cache_pattern(client):
    """测试任务列表缓存Key模式"""
    print("\n" + "="*60)
    print("📋 测试任务列表缓存Key模式")
    print("="*60)
    
    # 查找所有任务列表缓存
    task_keys = list_cache_keys(client, "tasks:list:*")
    
    if not task_keys:
        print("⚠️  当前没有任务列表缓存")
        print("   建议：打开前端，访问任务池页面，生成一些缓存")
        return
    
    print(f"\n✅ 找到 {len(task_keys)} 个任务列表缓存Key:")
    for i, key in enumerate(task_keys[:10], 1):
        # 解析Key
        parts = key.split(':')
        if len(parts) >= 7:
            project_id = parts[2]
            status = parts[3]
            assigned_to = parts[4]
            skip = parts[5]
            limit = parts[6]
            
            print(f"\n{i}. {key}")
            print(f"   项目: {project_id}")
            print(f"   状态: {status}")
            print(f"   用户: {assigned_to}")
            print(f"   分页: skip={skip}, limit={limit}")
            
            # 检查TTL
            ttl = client.ttl(key)
            if ttl > 0:
                minutes = ttl // 60
                seconds = ttl % 60
                print(f"   过期时间: {minutes}分{seconds}秒")
            elif ttl == -1:
                print(f"   过期时间: 永不过期 ⚠️")
            else:
                print(f"   过期时间: 已过期")
        else:
            print(f"\n{i}. {key} (格式不匹配)")
    
    if len(task_keys) > 10:
        print(f"\n... 还有 {len(task_keys) - 10} 个Key未显示")

def test_cache_invalidation_pattern(client):
    """测试缓存清除模式"""
    print("\n" + "="*60)
    print("🗑️  测试缓存清除模式")
    print("="*60)
    
    # 测试不同的清除模式
    test_patterns = [
        ("tasks:list:proj1:*:user123:*", "项目1 + 用户123的任务"),
        ("tasks:list:proj1:*:all:*", "项目1的所有任务"),
        ("tasks:list:all:*:user123:*", "用户123的所有任务"),
        ("tasks:list:*", "所有任务列表"),
    ]
    
    for pattern, description in test_patterns:
        keys = list_cache_keys(client, pattern)
        print(f"\n模式: {pattern}")
        print(f"描述: {description}")
        print(f"匹配: {len(keys)} 个Key")
        if keys:
            print(f"示例: {keys[0] if len(keys) > 0 else ''}")

def test_user_specific_cache(client):
    """测试用户特定的缓存"""
    print("\n" + "="*60)
    print("👤 测试用户特定缓存")
    print("="*60)
    
    # 查找所有用户相关的缓存
    all_keys = list_cache_keys(client, "tasks:list:*")
    
    # 按用户分组
    user_cache_map = {}
    for key in all_keys:
        parts = key.split(':')
        if len(parts) >= 5:
            assigned_to = parts[4]
            if assigned_to != 'all':
                if assigned_to not in user_cache_map:
                    user_cache_map[assigned_to] = []
                user_cache_map[assigned_to].append(key)
    
    if not user_cache_map:
        print("⚠️  当前没有用户特定的任务缓存")
        return
    
    print(f"\n✅ 找到 {len(user_cache_map)} 个用户的任务缓存:")
    for user_id, keys in list(user_cache_map.items())[:5]:
        print(f"\n用户: {user_id}")
        print(f"缓存数: {len(keys)}")
        for key in keys[:3]:
            print(f"  - {key}")
        if len(keys) > 3:
            print(f"  ... 还有 {len(keys) - 3} 个")
    
    if len(user_cache_map) > 5:
        print(f"\n... 还有 {len(user_cache_map) - 5} 个用户未显示")

def check_statistics_cache(client):
    """检查统计缓存"""
    print("\n" + "="*60)
    print("📊 检查统计缓存")
    print("="*60)
    
    patterns = [
        ("stats:performance:*", "绩效统计"),
        ("stats:dashboard:*", "仪表板统计"),
        ("stats:project:*", "项目统计"),
    ]
    
    for pattern, description in patterns:
        keys = list_cache_keys(client, pattern)
        print(f"\n{description}: {len(keys)} 个缓存")
        if keys:
            for key in keys[:3]:
                ttl = client.ttl(key)
                if ttl > 0:
                    minutes = ttl // 60
                    print(f"  - {key} (剩余 {minutes}分钟)")
                else:
                    print(f"  - {key}")

def simulate_cache_invalidation(client):
    """模拟缓存清除（测试模式）"""
    print("\n" + "="*60)
    print("🧪 模拟缓存清除测试")
    print("="*60)
    
    print("\n注意：这是模拟测试，不会真正删除缓存")
    
    # 假设场景
    project_id = "proj1"
    user_id = "user123"
    
    print(f"\n场景：管理员审核任务")
    print(f"  项目ID: {project_id}")
    print(f"  标注员ID: {user_id}")
    
    print(f"\n需要清除的缓存模式:")
    patterns_to_clear = [
        f"tasks:list:{project_id}:*:{user_id}:*",
        f"tasks:list:{project_id}:*:all:*",
        f"tasks:list:all:*:{user_id}:*",
    ]
    
    total_keys = 0
    for pattern in patterns_to_clear:
        keys = list_cache_keys(client, pattern)
        print(f"\n  模式: {pattern}")
        print(f"  匹配: {len(keys)} 个Key")
        total_keys += len(keys)
        for key in keys[:3]:
            print(f"    - {key}")
        if len(keys) > 3:
            print(f"    ... 还有 {len(keys) - 3} 个")
    
    print(f"\n✅ 总共需要清除: {total_keys} 个Key")
    
    if total_keys > 0:
        print("\n💡 提示: 这些Key在实际操作中会被自动清除")
    else:
        print("\n⚠️  提示: 当前没有匹配的缓存，可能需要先生成一些测试数据")

def main():
    """主函数"""
    print("🔍 Redis缓存失效测试工具")
    print("用于验证任务状态变化时的缓存清除机制")
    
    # 连接Redis
    client = check_redis_connection()
    if not client:
        return
    
    try:
        # 1. 测试任务列表缓存模式
        test_task_list_cache_pattern(client)
        
        # 2. 测试缓存清除模式
        test_cache_invalidation_pattern(client)
        
        # 3. 测试用户特定缓存
        test_user_specific_cache(client)
        
        # 4. 检查统计缓存
        check_statistics_cache(client)
        
        # 5. 模拟缓存清除
        simulate_cache_invalidation(client)
        
        # 总结
        print("\n" + "="*60)
        print("📝 测试总结")
        print("="*60)
        
        all_keys = list_cache_keys(client, "*")
        task_keys = list_cache_keys(client, "tasks:*")
        
        print(f"\nRedis缓存统计:")
        print(f"  总Key数: {len(all_keys)}")
        print(f"  任务相关: {len(task_keys)}")
        
        info = client.info('stats')
        print(f"\nRedis性能指标:")
        print(f"  命中次数: {info.get('keyspace_hits', 0)}")
        print(f"  未命中次数: {info.get('keyspace_misses', 0)}")
        
        if info.get('keyspace_hits', 0) > 0:
            hit_rate = info['keyspace_hits'] / (info['keyspace_hits'] + info.get('keyspace_misses', 1)) * 100
            print(f"  命中率: {hit_rate:.2f}%")
        
        print("\n✅ 测试完成")
        print("\n💡 使用建议:")
        print("  1. 在前端操作（提交、审核任务）后运行此脚本")
        print("  2. 查看日志确认缓存已被清除")
        print("  3. 再次访问前端，验证数据已更新")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()

