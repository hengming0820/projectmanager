#!/usr/bin/env python3
"""
团队协作功能一键安装脚本
包含数据库表创建和权限配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🤝 团队协作功能安装程序")
    print("=" * 60)
    print("此脚本将为您的系统安装团队协作文档功能")
    print("包括：数据库表创建、权限配置、示例数据")
    print("=" * 60)

def run_database_migration():
    """运行数据库迁移"""
    print("\n📊 [步骤 1/2] 创建数据库表...")
    
    try:
        from scripts.migrate_add_collaboration_tables import main as run_migration
        success = run_migration()
        
        if success:
            print("✅ [步骤 1/2] 数据库表创建成功")
            return True
        else:
            print("❌ [步骤 1/2] 数据库表创建失败")
            return False
            
    except Exception as e:
        print(f"❌ [步骤 1/2] 数据库迁移失败: {e}")
        return False

def run_permissions_update():
    """运行权限更新"""
    print("\n🔐 [步骤 2/2] 更新用户权限...")
    
    try:
        from scripts.update_collaboration_permissions import update_collaboration_permissions
        update_collaboration_permissions()
        print("✅ [步骤 2/2] 用户权限更新成功")
        return True
        
    except Exception as e:
        print(f"❌ [步骤 2/2] 权限更新失败: {e}")
        print("💡 您可以手动执行 SQL 来更新权限（参考 README_permissions.md）")
        return False

def print_success_message():
    """打印成功消息"""
    print("\n" + "=" * 60)
    print("🎉 团队协作功能安装完成！")
    print("=" * 60)
    print("📋 使用步骤:")
    print("1. 重新登录系统以刷新权限缓存")
    print("2. 在导航栏中找到 '项目管理' → '团队协作'")
    print("3. 开始创建和编辑协作文档")
    print("\n🔧 功能特性:")
    print("• 富文本协作编辑")
    print("• 多人实时协作")
    print("• 权限管理（所有者/编辑者/查看者）")
    print("• 版本历史记录")
    print("• 文档分类和标签")
    print("• 搜索和筛选")
    print("=" * 60)

def print_failure_message():
    """打印失败消息"""
    print("\n" + "=" * 60)
    print("❌ 团队协作功能安装失败")
    print("=" * 60)
    print("🛠️  手动安装步骤:")
    print("1. 运行数据库迁移:")
    print("   cd backend && python scripts/migrate_add_collaboration_tables.py")
    print("\n2. 更新用户权限:")
    print("   cd backend && python scripts/update_collaboration_permissions.py")
    print("   或执行 SQL（参考 scripts/README_permissions.md）")
    print("\n3. 重新登录系统")
    print("=" * 60)

def main():
    """主函数"""
    print_banner()
    
    # 确认安装
    try:
        confirm = input("\n是否继续安装团队协作功能？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("安装已取消")
            return False
    except KeyboardInterrupt:
        print("\n安装已取消")
        return False
    
    success = True
    
    # 步骤1: 数据库迁移
    if not run_database_migration():
        success = False
    
    # 步骤2: 权限更新
    if success and not run_permissions_update():
        success = False
    
    # 显示结果
    if success:
        print_success_message()
    else:
        print_failure_message()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n安装已被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生错误: {e}")
        sys.exit(1)
