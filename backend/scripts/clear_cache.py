"""
缓存清理脚本
提供多种缓存清理选项
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cache_service import cache_service


def clear_all():
    """清除所有缓存"""
    try:
        cache_service.redis_client.flushdb()
        print("✅ 所有缓存已清除")
    except Exception as e:
        print(f"❌ 清除失败: {e}")


def clear_tasks():
    """清除任务相关缓存"""
    try:
        cache_service.delete_pattern("tasks:*")
        print("✅ 任务缓存已清除")
    except Exception as e:
        print(f"❌ 清除失败: {e}")


def clear_projects():
    """清除项目相关缓存"""
    try:
        cache_service.delete_pattern("projects:*")
        print("✅ 项目缓存已清除")
    except Exception as e:
        print(f"❌ 清除失败: {e}")


def clear_users():
    """清除用户相关缓存"""
    try:
        cache_service.delete_pattern("users:*")
        print("✅ 用户缓存已清除")
    except Exception as e:
        print(f"❌ 清除失败: {e}")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 50)
    print("🗑️  Redis 缓存清理工具")
    print("=" * 50)
    print("\n请选择清理选项：")
    print("  1. 清除所有缓存")
    print("  2. 清除任务缓存 (tasks:*)")
    print("  3. 清除项目缓存 (projects:*)")
    print("  4. 清除用户缓存 (users:*)")
    print("  0. 退出")
    print()


def main():
    """主函数"""
    if not cache_service.enabled:
        print("\n❌ Redis未连接")
        print("\n💡 请确保 Redis 服务正在运行")
        return
    
    print("✅ Redis已连接")
    
    while True:
        show_menu()
        choice = input("请输入选项 (0-4): ").strip()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        elif choice == '1':
            confirm = input("\n⚠️  确认清除所有缓存？(yes/no): ")
            if confirm.lower() == 'yes':
                clear_all()
            else:
                print("❌ 已取消")
        elif choice == '2':
            clear_tasks()
        elif choice == '3':
            clear_projects()
        elif choice == '4':
            clear_users()
        else:
            print("❌ 无效选项，请重试")
        
        input("\n按回车键继续...")


if __name__ == '__main__':
    main()

