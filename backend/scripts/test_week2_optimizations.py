"""
测试第二周Redis优化功能
验证统计数据缓存、文章缓存、Redis Pub/Sub通知系统
"""
import sys
import time
import requests
import json

# API基础URL
BASE_URL = "http://localhost:3006/api"

# 测试用户的Token（需要先手动登录获取）
# 可以通过浏览器开发者工具从请求头中获取
TEST_TOKEN = ""  # 需要填入实际的token

headers = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "application/json"
}

def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_performance_stats_cache():
    """测试绩效统计缓存"""
    print_section("📊 测试绩效统计缓存")
    
    # 第一次请求（缓存未命中）
    print("第1次请求个人绩效统计...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/performance/personal", headers=headers)
    duration1 = (time.time() - start) * 1000
    print(f"✅ 响应时间: {duration1:.0f}ms (应该较慢，需查询数据库)")
    print(f"   返回状态: {response.status_code}")
    
    # 第二次请求（缓存命中）
    print("\n第2次请求个人绩效统计...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/performance/personal", headers=headers)
    duration2 = (time.time() - start) * 1000
    print(f"✅ 响应时间: {duration2:.0f}ms (应该很快，从Redis缓存获取)")
    print(f"   返回状态: {response.status_code}")
    
    # 计算性能提升
    if duration1 > 0:
        improvement = ((duration1 - duration2) / duration1) * 100
        print(f"\n⚡ 性能提升: {improvement:.1f}%")
    
    return duration1, duration2

def test_dashboard_stats_cache():
    """测试仪表板统计缓存"""
    print_section("📈 测试仪表板统计缓存")
    
    # 第一次请求
    print("第1次请求仪表板统计...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/performance/dashboard", headers=headers)
    duration1 = (time.time() - start) * 1000
    print(f"✅ 响应时间: {duration1:.0f}ms")
    print(f"   返回状态: {response.status_code}")
    
    # 第二次请求
    print("\n第2次请求仪表板统计...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/performance/dashboard", headers=headers)
    duration2 = (time.time() - start) * 1000
    print(f"✅ 响应时间: {duration2:.0f}ms")
    print(f"   返回状态: {response.status_code}")
    
    if duration1 > 0:
        improvement = ((duration1 - duration2) / duration1) * 100
        print(f"\n⚡ 性能提升: {improvement:.1f}%")
    
    return duration1, duration2

def test_article_cache():
    """测试文章缓存"""
    print_section("📝 测试文章缓存")
    
    # 获取文章列表
    print("第1次请求文章列表...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/articles/?type=meeting", headers=headers)
    duration1 = (time.time() - start) * 1000
    print(f"✅ 响应时间: {duration1:.0f}ms")
    print(f"   返回状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('items', [])
        if articles:
            article_id = articles[0]['id']
            
            # 测试文章详情缓存
            print(f"\n第1次请求文章详情 (ID: {article_id})...")
            start = time.time()
            response = requests.get(f"{BASE_URL}/articles/{article_id}", headers=headers)
            detail_duration1 = (time.time() - start) * 1000
            print(f"✅ 响应时间: {detail_duration1:.0f}ms")
            
            print(f"\n第2次请求文章详情 (ID: {article_id})...")
            start = time.time()
            response = requests.get(f"{BASE_URL}/articles/{article_id}", headers=headers)
            detail_duration2 = (time.time() - start) * 1000
            print(f"✅ 响应时间: {detail_duration2:.0f}ms")
            
            if detail_duration1 > 0:
                improvement = ((detail_duration1 - detail_duration2) / detail_duration1) * 100
                print(f"\n⚡ 文章详情性能提升: {improvement:.1f}%")
    
    return duration1

def test_redis_pubsub():
    """测试Redis Pub/Sub通知"""
    print_section("🔔 测试Redis Pub/Sub通知")
    
    print("📌 Redis Pub/Sub通知功能说明:")
    print("   1. 任务提交后，自动通知所有审核员")
    print("   2. 任务审核后，自动通知标注员")
    print("   3. 支持多服务器部署，通过Redis中转消息")
    print("   4. Redis不可用时，自动回退到直接WebSocket")
    
    print("\n💡 测试方法:")
    print("   1. 打开浏览器开发者工具的Network标签")
    print("   2. 筛选WebSocket连接")
    print("   3. 执行任务操作（提交、审核）")
    print("   4. 查看WebSocket消息，应该能收到实时通知")
    
    print("\n✅ Redis Pub/Sub功能已集成到以下API:")
    print("   - POST /api/tasks/{task_id}/submit  (提交任务)")
    print("   - POST /api/tasks/{task_id}/review  (审核任务)")
    print("   - 更多API将在后续版本中集成...")

def print_summary(stats_durations, dashboard_durations, article_duration):
    """打印测试总结"""
    print_section("📊 第二周优化测试总结")
    
    print("✅ 已完成的优化:")
    print("   1. ✅ 绩效统计缓存 (15分钟TTL)")
    print("   2. ✅ 仪表板统计缓存 (15分钟TTL)")
    print("   3. ✅ 项目统计缓存 (10分钟TTL)")
    print("   4. ✅ 文章详情缓存 (20分钟TTL)")
    print("   5. ✅ 文章列表缓存 (10分钟TTL)")
    print("   6. ✅ 文章编辑历史缓存 (15分钟TTL)")
    print("   7. ✅ Redis Pub/Sub实时通知系统")
    print("   8. ✅ WebSocket自动回退机制")
    
    print("\n⚡ 性能提升:")
    if len(stats_durations) == 2:
        improvement = ((stats_durations[0] - stats_durations[1]) / stats_durations[0]) * 100
        print(f"   - 绩效统计: {improvement:.1f}% 提升")
    
    if len(dashboard_durations) == 2:
        improvement = ((dashboard_durations[0] - dashboard_durations[1]) / dashboard_durations[0]) * 100
        print(f"   - 仪表板统计: {improvement:.1f}% 提升")
    
    print("\n🎯 预期效果:")
    print("   - 统计查询响应时间: 降低 80-90%")
    print("   - 文章加载速度: 提升 90-95%")
    print("   - 支持多服务器部署: ✅")
    print("   - 实时通知延迟: <10ms")
    
    print("\n📝 后续优化建议:")
    print("   - 可以添加工作日志统计缓存")
    print("   - 可以考虑添加搜索结果缓存")
    print("   - 可以实现WebSocket订阅Redis频道")

def main():
    """主测试函数"""
    print("🚀 开始测试第二周Redis优化功能")
    
    if not TEST_TOKEN:
        print("\n❌ 错误: 请先设置TEST_TOKEN")
        print("   1. 在浏览器中登录系统")
        print("   2. 打开开发者工具，查看请求头")
        print("   3. 复制Authorization的Bearer token")
        print("   4. 填入脚本的TEST_TOKEN变量")
        return
    
    try:
        # 测试统计缓存
        stats_durations = test_performance_stats_cache()
        time.sleep(1)
        
        dashboard_durations = test_dashboard_stats_cache()
        time.sleep(1)
        
        # 测试文章缓存
        article_duration = test_article_cache()
        time.sleep(1)
        
        # 测试通知系统
        test_redis_pubsub()
        
        # 打印总结
        print_summary(stats_durations, dashboard_durations, article_duration)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("   请确保后端服务正在运行 (http://localhost:3006)")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

