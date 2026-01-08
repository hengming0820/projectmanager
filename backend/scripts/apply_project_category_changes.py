#!/usr/bin/env python3
"""
应用项目分类相关的所有更改
1. 运行数据库迁移
2. 重新初始化测试数据（可选）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("🚀 应用项目分类更改")
    print("=" * 50)
    
    # 1. 运行数据库迁移
    print("\n📊 步骤 1: 应用数据库迁移...")
    try:
        from run_project_category_migration import main as run_migration
        migration_success = run_migration()
        if migration_success:
            print("✅ 数据库迁移完成")
        else:
            print("❌ 数据库迁移失败")
            return False
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False
    
    # 2. 询问是否重新初始化数据
    print("\n📋 步骤 2: 数据初始化（可选）")
    response = input("是否重新初始化测试数据？这将清除所有现有数据并创建新的测试数据。(y/N): ")
    
    if response.lower() in ['y', 'yes']:
        try:
            from init_db import init_db
            init_db()
            print("✅ 测试数据初始化完成")
        except Exception as e:
            print(f"❌ 数据初始化失败: {e}")
            return False
    else:
        print("ℹ️  跳过数据初始化")
    
    print("\n🎉 所有更改应用完成！")
    print("\n📝 更改摘要:")
    print("- ✅ 项目模型添加了 category 和 sub_category 字段")
    print("- ✅ 项目API支持分类筛选和统计")
    print("- ✅ Pydantic模式已更新")
    print("- ✅ 测试数据包含各种分类示例")
    
    print("\n🔧 使用方法:")
    print("1. 前端项目表单现在支持分类选择")
    print("2. 绩效页面支持按分类筛选统计")
    print("3. API端点 /projects/categories/stats 提供分类统计")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
