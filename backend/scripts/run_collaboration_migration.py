#!/usr/bin/env python3
"""
运行团队协作文档表迁移的脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    print("🚀 [协作迁移] 开始执行团队协作文档表迁移...")
    
    try:
        # 导入并运行迁移脚本
        from scripts.migrate_add_collaboration_tables import main as run_migration
        
        success = run_migration()
        
        if success:
            print("\n✅ [协作迁移] 迁移执行成功！")
            print("\n📋 [协作迁移] 后续步骤:")
            print("1. 执行权限更新SQL（参考 backend/scripts/README_permissions.md）")
            print("2. 重新登录系统以刷新权限缓存")
            print("3. 访问导航栏 '项目管理' → '团队协作' 开始使用")
            return True
        else:
            print("\n❌ [协作迁移] 迁移执行失败！")
            return False
            
    except ImportError as e:
        print(f"❌ [协作迁移] 导入迁移模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ [协作迁移] 执行失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
