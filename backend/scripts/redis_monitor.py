"""
Redis监控脚本
显示Redis运行状态和缓存统计信息
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.services.cache_service import cache_service
import redis


def monitor_redis():
    """监控Redis运行状态"""
    print("=" * 70)
    print(f"🔍 Redis 监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if not cache_service.enabled:
        print("❌ Redis 未连接")
        print("\n💡 请确保 Redis 服务正在运行：")
        print("   - Windows: 直接运行 redis-server.exe")
        print("   - Linux/Mac: redis-server")
        print("=" * 70)
        return
    
    try:
        # 获取Redis统计信息
        stats = cache_service.get_stats()
        
        print("\n📊 连接状态:")
        print(f"   ✅ Redis 已连接")
        print(f"   🖥️  服务器: localhost:6379")
        print(f"   📦 数据库: 0")
        
        print("\n💾 内存使用:")
        print(f"   已用内存: {stats.get('used_memory', 'N/A')}")
        
        print("\n🔑 数据统计:")
        print(f"   总Key数: {stats.get('total_keys', 0)}")
        
        print("\n⚡ 性能指标:")
        print(f"   命中率: {stats.get('hit_rate', 0):.2f}%")
        print(f"   每秒操作: {stats.get('ops_per_sec', 0)}")
        print(f"   连接数: {stats.get('connected_clients', 0)}")
        
        # 分析缓存key分布wanc
        print("\n🗂️  缓存Key分布:")
        analyze_keys()
        
        print("\n" + "=" * 70)
        print("✅ 监控完成")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 监控失败: {e}")
        print("=" * 70)


def analyze_keys():
    """分析缓存key的分布情况"""
    try:
        client = cache_service.redis_client
        
        # 统计各类型key的数量
        patterns = {
            "任务列表": "tasks:list:*",
            "任务详情": "tasks:detail:*",
            "项目列表": "projects:list:*",
            "项目详情": "projects:detail:*",
            "项目统计": "projects:stats:*",
            "用户信息": "users:info:*",
            "用户列表": "users:list:*",
        }
        
        for name, pattern in patterns.items():
            keys = client.keys(pattern)
            if keys:
                print(f"   📁 {name}: {len(keys)} 个")
        
    except Exception as e:
        print(f"   ⚠️  分析失败: {e}")


def clear_all_cache():
    """清除所有缓存"""
    print("\n⚠️  即将清除所有Redis缓存")
    confirm = input("确认清除？(yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            cache_service.redis_client.flushdb()
            print("✅ 所有缓存已清除")
        except Exception as e:
            print(f"❌ 清除失败: {e}")
    else:
        print("❌ 已取消")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_all_cache()
    else:
        monitor_redis()


if __name__ == '__main__':
    main()

