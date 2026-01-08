#!/usr/bin/env python3
"""
运行工作日志相关的迁移脚本
"""

import subprocess
import sys
import os

def run_migration_script(script_name: str) -> bool:
    """运行迁移脚本"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ 迁移脚本不存在: {script_path}")
        return False
    
    try:
        print(f"🚀 运行迁移脚本: {script_name}")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {script_name} 执行成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {script_name} 执行失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            if result.stdout:
                print(f"输出信息: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ 执行 {script_name} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始运行工作日志迁移脚本...")
    
    # 迁移脚本列表（按执行顺序）
    migration_scripts = [
        "migrate_add_work_log_tables.py"
    ]
    
    success_count = 0
    total_count = len(migration_scripts)
    
    for script in migration_scripts:
        if run_migration_script(script):
            success_count += 1
        else:
            print(f"⚠️  跳过后续迁移脚本")
            break
        print("-" * 50)
    
    print(f"\n📊 迁移结果: {success_count}/{total_count} 个脚本执行成功")
    
    if success_count == total_count:
        print("🎉 所有工作日志迁移脚本执行完成！")
        return True
    else:
        print("❌ 部分迁移脚本执行失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

