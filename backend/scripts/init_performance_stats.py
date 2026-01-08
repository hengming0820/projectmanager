#!/usr/bin/env python3
"""
根据任务CSV数据初始化performance_stats表的脚本
"""

import csv
import sys
import os
from datetime import datetime
from decimal import Decimal

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.performance import PerformanceStats
import uuid

def read_tasks_csv(file_path):
    """读取任务CSV文件"""
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tasks.append(row)
    return tasks

def analyze_user_performance(tasks):
    """分析用户绩效数据"""
    # 按用户统计数据
    user_stats = {}
    
    print("📊 分析任务数据...")
    
    # 统计每个用户的任务情况
    for task in tasks:
        assigned_to = task['assigned_to'].strip()
        status = task['status'].strip()
        score = int(task['score']) if task['score'].strip() else 0
        
        # 跳过未分配的任务
        if not assigned_to:
            continue
        
        if assigned_to not in user_stats:
            user_stats[assigned_to] = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'approved_tasks': 0,
                'rejected_tasks': 0,
                'in_progress_tasks': 0,
                'submitted_tasks': 0,
                'total_score': 0
            }
        
        stats = user_stats[assigned_to]
        
        # 统计总任务数（已分配的任务）
        stats['total_tasks'] += 1
        
        # 统计各种状态的任务
        if status == 'approved':
            stats['approved_tasks'] += 1
            stats['completed_tasks'] += 1
            stats['total_score'] += score
        elif status == 'submitted':
            stats['submitted_tasks'] += 1
            stats['completed_tasks'] += 1
            stats['total_score'] += score
        elif status == 'rejected':
            stats['rejected_tasks'] += 1
        elif status == 'in_progress':
            stats['in_progress_tasks'] += 1
    
    return user_stats

def create_performance_records(user_stats):
    """创建绩效统计记录"""
    records = []
    period_date = "2025-08"  # 使用当前月份
    
    for user_id, stats in user_stats.items():
        if stats['total_tasks'] > 0:  # 只为有任务的用户创建记录
            # 计算平均分
            avg_score = (stats['total_score'] / stats['completed_tasks']) if stats['completed_tasks'] > 0 else 0
            
            record = PerformanceStats(
                id=str(uuid.uuid4()),
                user_id=user_id,
                period='monthly',
                date=period_date,
                total_tasks=stats['total_tasks'],
                completed_tasks=stats['completed_tasks'],
                approved_tasks=stats['approved_tasks'],
                rejected_tasks=stats['rejected_tasks'],
                total_score=stats['total_score'],
                average_score=Decimal(str(round(avg_score, 2))),
                total_hours=Decimal('0.00'),  # 暂时设为0
                average_hours=Decimal('0.00'),  # 暂时设为0
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            records.append(record)
            
            completion_rate = (stats['completed_tasks'] / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            print(f"✅ 创建记录: 用户 {user_id} | 总任务: {stats['total_tasks']} | 完成: {stats['completed_tasks']} ({completion_rate:.1f}%) | 审核通过: {stats['approved_tasks']} | 总分: {stats['total_score']}")
    
    return records

def init_performance_stats(csv_file_path):
    """初始化绩效统计表"""
    print("🚀 开始初始化绩效统计表...")
    
    # 1. 读取任务数据
    print(f"📄 读取任务CSV文件: {csv_file_path}")
    tasks = read_tasks_csv(csv_file_path)
    print(f"📊 共读取 {len(tasks)} 条任务记录")
    
    # 2. 分析用户绩效
    user_stats = analyze_user_performance(tasks)
    print(f"👥 分析了 {len(user_stats)} 个用户的绩效数据")
    
    # 3. 创建绩效记录
    performance_records = create_performance_records(user_stats)
    print(f"📝 生成了 {len(performance_records)} 条绩效统计记录")
    
    # 4. 保存到数据库
    db = SessionLocal()
    try:
        print("🗄️ 清空现有绩效统计数据...")
        db.query(PerformanceStats).delete()
        
        print("💾 插入新的绩效统计数据...")
        db.bulk_save_objects(performance_records)
        db.commit()
        
        print("✅ 绩效统计表初始化完成！")
        
        # 验证数据
        count = db.query(PerformanceStats).count()
        print(f"🎯 验证: 数据库中现有 {count} 条绩效统计记录")
        
        # 显示统计摘要
        print("\n📈 绩效统计摘要:")
        for record in performance_records:
            completion_rate = (record.completed_tasks / record.total_tasks * 100) if record.total_tasks > 0 else 0
            print(f"  👤 用户 {record.user_id}: 总任务 {record.total_tasks}, 完成 {record.completed_tasks} ({completion_rate:.1f}%), 总分 {record.total_score}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # CSV文件路径 - 请根据实际路径修改
    csv_file_path = r"d:\project_maneger\art-design-pro\tasks_202508271039.csv"
    
    # 检查文件是否存在
    if not os.path.exists(csv_file_path):
        print(f"❌ 错误: CSV文件不存在: {csv_file_path}")
        sys.exit(1)
    
    try:
        init_performance_stats(csv_file_path)
        print("\n🎉 初始化完成！现在可以重启后端服务测试绩效管理功能。")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)