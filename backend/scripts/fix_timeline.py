#!/usr/bin/env python3
"""
修复任务timeline数据的脚本
为缺少创建事件的任务补充timeline数据
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models.task import Task
from app.models.user import User

def fix_timeline_data():
    """修复timeline数据"""
    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔧 开始修复timeline数据...")
        
        # 获取所有任务
        tasks = db.query(Task).all()
        print(f"📋 找到 {len(tasks)} 个任务")
        
        fixed_count = 0
        
        for task in tasks:
            timeline = task.timeline or []
            needs_fix = False
            
            # 检查是否缺少创建事件
            has_created = any(event.get('type') == 'created' for event in timeline)
            
            if not has_created:
                print(f"🔍 任务 {task.id} 缺少创建事件，正在修复...")
                
                # 获取创建者信息
                creator = db.query(User).filter(User.id == task.created_by).first()
                creator_name = creator.username if creator else "系统"
                
                # 创建创建事件
                created_event = {
                    "type": "created",
                    "time": task.created_at.isoformat() if task.created_at else datetime.now().isoformat(),
                    "user_id": task.created_by,
                    "user_name": creator_name
                }
                
                # 将创建事件插入到timeline开头
                timeline.insert(0, created_event)
                needs_fix = True
            
            # 检查是否有分配事件但缺少领取事件
            if task.assigned_to and task.assigned_at:
                has_claimed = any(event.get('type') == 'claimed' for event in timeline)
                if not has_claimed:
                    print(f"🔍 任务 {task.id} 缺少领取事件，正在修复...")
                    
                    # 获取分配者信息
                    assignee = db.query(User).filter(User.id == task.assigned_to).first()
                    assignee_name = assignee.username if assignee else "未知用户"
                    
                    # 创建领取事件
                    claimed_event = {
                        "type": "claimed",
                        "time": task.assigned_at.isoformat() if task.assigned_at else datetime.now().isoformat(),
                        "user_id": task.assigned_to,
                        "user_name": assignee_name
                    }
                    
                    # 找到合适的位置插入领取事件（在创建事件之后，提交事件之前）
                    insert_index = 1  # 默认在创建事件之后
                    for i, event in enumerate(timeline):
                        if event.get('type') in ['submitted', 'reviewed']:
                            insert_index = i
                            break
                    
                    timeline.insert(insert_index, claimed_event)
                    needs_fix = True
            
            # 检查是否有审核结果但缺少审核事件
            if task.reviewed_at and task.reviewed_by:
                has_reviewed = any(event.get('type') == 'reviewed' for event in timeline)
                if not has_reviewed:
                    print(f"🔍 任务 {task.id} 缺少审核事件，正在修复...")
                    
                    # 获取审核者信息
                    reviewer = db.query(User).filter(User.id == task.reviewed_by).first()
                    reviewer_name = reviewer.username if reviewer else "未知审核者"
                    
                    # 创建审核事件
                    reviewed_event = {
                        "type": "reviewed",
                        "time": task.reviewed_at.isoformat(),
                        "user_id": task.reviewed_by,
                        "user_name": reviewer_name,
                        "action": "approve" if task.status == "approved" else "reject",
                        "comment": task.review_comment
                    }
                    
                    timeline.append(reviewed_event)
                    needs_fix = True
            
            # 如果需要修复，更新数据库
            if needs_fix:
                # 按时间排序timeline事件
                timeline.sort(key=lambda x: x.get('time', ''))
                
                task.timeline = timeline
                fixed_count += 1
                
                print(f"✅ 任务 {task.id} timeline已修复，现有 {len(timeline)} 个事件:")
                for i, event in enumerate(timeline):
                    print(f"   {i+1}. {event.get('type')} - {event.get('time')} - {event.get('user_name')}")
        
        # 提交更改
        db.commit()
        print(f"🎉 修复完成！共修复了 {fixed_count} 个任务的timeline数据")
        
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_timeline_data()
