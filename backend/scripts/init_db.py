#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建初始用户和示例数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Project, Task
from app.models.role import Role
from app.models.performance import PerformanceStats
from app.database import engine, Base  # 从database模块导入Base

from app.utils.security import get_password_hash
from datetime import date, datetime

def init_db():
    """初始化数据库"""
    # 创建表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("🗑️ 清理现有数据...")

        # 删除现有数据（按依赖关系顺序，先删除引用表）
        db.query(PerformanceStats).delete()  # 先删除性能统计数据
        db.query(Task).delete()              # 删除任务
        db.query(Project).delete()           # 删除项目
        db.query(User).delete()              # 删除用户
        db.query(Role).delete()              # 删除角色

        print("✅ 现有数据已清理")

        # 先确保基础角色存在
        print("📝 创建基础角色...")
        base_roles = [
            {"name": "管理员", "role": "admin", "description": "系统管理员，拥有所有权限"},
            {"name": "标注员", "role": "annotator", "description": "负责图像标注的普通用户"},
            {"name": "审核员", "role": "reviewer", "description": "负责标注审核的用户"}
        ]
        for r in base_roles:
            db.add(Role(name=r["name"], role=r["role"], description=r["description"]))

        print("✅ 基础角色创建完成")


        print("👥 创建用户...")
        # 创建管理员用户
        admin_user = User(
            id="user1",
            username="admin",
            real_name="系统管理员",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            department="技术部",
            status="active"
        )
        db.add(admin_user)
        
        # 创建标注员用户
        annotator1 = User(
            id="user2",
            username="annotator1",
            real_name="张医生",
            email="zhang@example.com",
            password_hash=get_password_hash("annotator123"),
            role="annotator",
            department="放射科",
            status="active"
        )
        db.add(annotator1)
        
        annotator2 = User(
            id="user3",
            username="annotator2",
            real_name="李医生",
            email="li@example.com",
            password_hash=get_password_hash("annotator123"),
            role="annotator",
            department="放射科",
            status="active"
        )
        db.add(annotator2)
        
        annotator3 = User(
            id="user4",
            username="annotator3",
            real_name="王医生",
            email="wang@example.com",
            password_hash=get_password_hash("annotator123"),
            role="annotator",
            department="放射科",
            status="active"
        )
        db.add(annotator3)

        print("✅ 用户创建完成")

        # 便捷映射：根据用户ID获取真实姓名/用户名
        users_by_id = {
            "user1": {"username": admin_user.username, "real_name": admin_user.real_name},
            "user2": {"username": annotator1.username, "real_name": annotator1.real_name},
            "user3": {"username": annotator2.username, "real_name": annotator2.real_name},
            "user4": {"username": annotator3.username, "real_name": annotator3.real_name},
        }
        print("📁 创建项目...")

        # 创建示例项目
        project1 = Project(
            id="proj1",
            name="20241201_泌尿系统CT标注项目",
            description="泌尿系统CT影像的精确标注，包括肾脏、膀胱、输尿管等器官的识别和标注",
            status="active",
            priority="high",
            category="case",
            sub_category="research",
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            created_by="user1",
            total_tasks=8,
            completed_tasks=3,
            assigned_tasks=3
        )
        db.add(project1)
        
        project2 = Project(
            id="proj2",
            name="20241205_胸部X光片标注项目",
            description="胸部X光片的肺部疾病检测标注，包括肺炎、结核、肿瘤等病变的识别",
            status="active",
            priority="medium",
            category="case",
            sub_category="paid",
            start_date=date(2024, 12, 5),
            end_date=date(2025, 1, 15),
            created_by="user1",
            total_tasks=7,
            completed_tasks=2,
            assigned_tasks=2
        )
        db.add(project2)
        
        project3 = Project(
            id="proj3",
            name="20241210_脑部MRI标注项目",
            description="脑部MRI影像的神经结构标注，包括脑肿瘤、脑梗塞、脑出血等病变的精确标注",
            status="active",
            priority="high",
            category="ai_annotation",
            sub_category="research_ai",
            start_date=date(2024, 12, 10),
            end_date=date(2025, 1, 20),
            created_by="user1",
            total_tasks=5,
            completed_tasks=1,
            assigned_tasks=1
        )
        db.add(project3)
        
        # 添加一个试用分类的项目
        project4 = Project(
            id="proj20251101",  # 使用新的ID格式
            name="20250101_AI辅助诊断日常标注",
            description="AI辅助诊断系统的日常标注工作，提升诊断准确性",
            status="active",
            priority="medium",
            category="ai_annotation",
            sub_category="daily",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            created_by="user1",
            total_tasks=10,
            completed_tasks=4,
            assigned_tasks=5
        )
        db.add(project4)
        
        # 添加一个试用分类的项目
        project5 = Project(
            id="proj20251102",  # 使用新的ID格式
            name="20250101_新设备试用标注",
            description="新引进标注设备的试用阶段，测试设备性能和标注效果",
            status="active",
            priority="low",
            category="case",
            sub_category="trial",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 2, 28),
            created_by="user1",
            total_tasks=6,
            completed_tasks=2,
            assigned_tasks=3
        )
        db.add(project5)

        print("✅ 项目创建完成")
        print("📋 创建任务（包含完整timeline与覆盖各状态，含真实姓名）...")

        # 创建示例任务（覆盖 approved/submitted/in_progress/pending/rejected/skipped 各状态）
        tasks = [
            # 项目1的任务
            Task(
                id="task1",
                title="肾脏CT标注任务001",
                description="标注左肾CT影像中的病变区域",
                project_id="proj1",
                status="approved",
                priority="high",
                assigned_to="user2",
                created_by="user1",
                image_url="/api/images/kidney001.jpg",
                annotation_data={"lesions": [{"x": 100, "y": 150, "type": "tumor"}]},
                score=50,
                submitted_at=datetime(2024, 12, 3, 16, 0, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 3, 16, 0, 0),
                review_comment="标注准确，质量良好",
                timeline=[
                    {"type": "created", "time": datetime(2024, 12, 1, 9, 0, 0).isoformat(), "user_id": "user1"},
                    {"type": "claimed", "time": datetime(2024, 12, 2, 10, 30, 0).isoformat(), "user_id": "user2"},
                    {"type": "submitted", "time": datetime(2024, 12, 3, 15, 45, 0).isoformat(), "user_id": "user2", "comment": "已完成肾脏病变区域标注", "organ_count": 1},
                    {"type": "reviewed", "time": datetime(2024, 12, 3, 16, 0, 0).isoformat(), "user_id": "user1", "action": "approve", "comment": "标注准确，质量良好", "score": 5}
                ]
            ),
            Task(
                id="task2",
                title="膀胱CT标注任务002",
                description="标注膀胱CT影像中的异常区域",
                project_id="proj1",
                status="approved",
                priority="medium",
                assigned_to="user2",
                created_by="user1",
                image_url="/api/images/bladder002.jpg",
                annotation_data={"lesions": [{"x": 200, "y": 180, "type": "stone"}]},
                score=40,
                submitted_at=datetime(2024, 12, 4, 14, 30, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 4, 14, 30, 0),
                review_comment="标注正确",
                timeline=[
                    {"type": "created", "time": datetime(2024, 12, 1, 9, 15, 0).isoformat(), "user_id": "user1"},
                    {"type": "claimed", "time": datetime(2024, 12, 2, 11, 0, 0).isoformat(), "user_id": "user2"},
                    {"type": "submitted", "time": datetime(2024, 12, 4, 14, 15, 0).isoformat(), "user_id": "user2", "comment": "已完成膀胱结石标注", "organ_count": 1},
                    {"type": "reviewed", "time": datetime(2024, 12, 4, 14, 30, 0).isoformat(), "user_id": "user1", "action": "approve", "comment": "标注正确", "score": 4}
                ]
            ),
            Task(
                id="task3",
                title="输尿管CT标注任务003",
                description="标注输尿管CT影像中的狭窄区域",
                project_id="proj1",
                status="approved",
                priority="high",
                assigned_to="user2",
                created_by="user1",
                image_url="/api/images/ureter003.jpg",
                annotation_data={"lesions": [{"x": 150, "y": 120, "type": "stricture"}]},
                score=60,
                submitted_at=datetime(2024, 12, 5, 11, 20, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 5, 11, 20, 0),
                review_comment="标注详细，质量优秀",
                timeline=[
                    {"type": "created", "time": datetime(2024, 12, 1, 9, 30, 0).isoformat(), "user_id": "user1"},
                    {"type": "claimed", "time": datetime(2024, 12, 2, 14, 0, 0).isoformat(), "user_id": "user2"},
                    {"type": "submitted", "time": datetime(2024, 12, 5, 11, 0, 0).isoformat(), "user_id": "user2", "comment": "已完成输尿管狭窄区域标注", "organ_count": 1},
                    {"type": "reviewed", "time": datetime(2024, 12, 5, 11, 20, 0).isoformat(), "user_id": "user1", "action": "approve", "comment": "标注详细，质量优秀", "score": 5}
                ]
            ),
            Task(
                id="task4",
                title="肾脏CT标注任务004",
                description="标注右肾CT影像中的囊肿区域",
                project_id="proj1",
                status="in_progress",
                priority="medium",
                assigned_to="user3",
                created_by="user1",
                image_url="/api/images/kidney004.jpg",
                score=45,
                timeline=[
                    {"type": "created", "time": datetime(2024, 12, 1, 10, 0, 0).isoformat(), "user_id": "user1"},
                    {"type": "claimed", "time": datetime(2024, 12, 3, 9, 0, 0).isoformat(), "user_id": "user3"},
                    {"type": "started", "time": datetime(2024, 12, 3, 9, 30, 0).isoformat(), "user_id": "user3", "comment": "开始标注右肾囊肿区域"}
                ]
            ),
            Task(
                id="task5",
                title="膀胱CT标注任务005",
                description="标注膀胱CT影像中的肿瘤区域",
                project_id="proj1",
                status="pending",
                priority="high",
                created_by="user1",
                image_url="/api/images/bladder005.jpg",
                score=55,
                timeline=[
                    {
                        "type": "created",
                        "time": datetime(2024, 12, 1, 10, 15, 0).isoformat(),
                        "user_id": "user1",
                        "user_name": "admin"
                    }
                ]
            ),
            Task(
                id="task6",
                title="输尿管CT标注任务006",
                description="标注输尿管CT影像中的结石区域",
                project_id="proj1",
                status="pending",
                priority="medium",
                created_by="user1",
                image_url="/api/images/ureter006.jpg",
                score=40
            ),
            Task(
                id="task7",
                title="肾脏CT标注任务007",
                description="标注左肾CT影像中的感染区域",
                project_id="proj1",
                status="pending",
                priority="low",
                created_by="user1",
                image_url="/api/images/kidney007.jpg",
                score=35
            ),
            Task(
                id="task8",
                title="膀胱CT标注任务008",
                description="标注膀胱CT影像中的炎症区域",
                project_id="proj1",
                status="pending",
                priority="low",
                created_by="user1",
                image_url="/api/images/bladder008.jpg",
                score=30
            ),
            
            # 项目2的任务
            Task(
                id="task9",
                title="肺炎X光片标注任务001",
                description="标注胸部X光片中的肺炎病变区域",
                project_id="proj2",
                status="approved",
                priority="high",
                assigned_to="user3",
                created_by="user1",
                image_url="/api/images/chest001.jpg",
                annotation_data={"lesions": [{"x": 120, "y": 200, "type": "pneumonia"}]},
                score=50,
                submitted_at=datetime(2024, 12, 7, 15, 45, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 7, 15, 45, 0),
                review_comment="标注准确"
            ),
            Task(
                id="task10",
                title="结核X光片标注任务002",
                description="标注胸部X光片中的结核病变区域",
                project_id="proj2",
                status="approved",
                priority="high",
                assigned_to="user3",
                created_by="user1",
                image_url="/api/images/chest002.jpg",
                annotation_data={"lesions": [{"x": 180, "y": 160, "type": "tuberculosis"}]},
                score=60,
                submitted_at=datetime(2024, 12, 8, 16, 30, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 8, 16, 30, 0),
                review_comment="标注详细，质量良好"
            ),
            Task(
                id="task11",
                title="肿瘤X光片标注任务003",
                description="标注胸部X光片中的肿瘤病变区域",
                project_id="proj2",
                status="in_progress",
                priority="high",
                assigned_to="user4",
                created_by="user1",
                image_url="/api/images/chest003.jpg",
                score=70
            ),
            Task(
                id="task12",
                title="气胸X光片标注任务004",
                description="标注胸部X光片中的气胸区域",
                project_id="proj2",
                status="approved",
                priority="medium",
                assigned_to="user4",
                created_by="user1",
                image_url="/api/images/chest004.jpg",
                annotation_data={"lesions": [{"x": 160, "y": 140, "type": "pneumothorax"}]},
                score=45,
                submitted_at=datetime(2024, 12, 9, 14, 20, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 9, 15, 0, 0),
                review_comment="气胸区域标注准确",
                timeline=[
                    {"type": "created", "time": datetime(2024, 12, 5, 11, 0, 0).isoformat(), "user_id": "user1"},
                    {"type": "claimed", "time": datetime(2024, 12, 6, 9, 30, 0).isoformat(), "user_id": "user4"},
                    {"type": "started", "time": datetime(2024, 12, 6, 10, 0, 0).isoformat(), "user_id": "user4", "comment": "开始标注气胸区域"},
                    {"type": "submitted", "time": datetime(2024, 12, 9, 14, 20, 0).isoformat(), "user_id": "user4", "comment": "已完成气胸区域标注", "organ_count": 1},
                    {"type": "reviewed", "time": datetime(2024, 12, 9, 15, 0, 0).isoformat(), "user_id": "user1", "action": "approve", "comment": "气胸区域标注准确", "score": 4}
                ]
            ),
            # 新增：已跳过（skipped）案例（带原因/截图）
            Task(
                id="task21",
                title="肾脏CT标注任务009-已跳过",
                description="示例：任务被跳过，提供跳过原因和截图",
                project_id="proj1",
                status="skipped",
                priority="low",
                created_by="user1",
                image_url="/api/images/kidney009.jpg",
                skipped_at=datetime(2024, 12, 6, 10, 0, 0),
                skip_reason="影像质量不达标，无法标注",
                skip_images=["http://minio.local/bucket/skip_001.jpg"],
                timeline=[
                    {"type": "created", "time": datetime(2024, 12, 5, 9, 0, 0).isoformat(), "user_id": "user1"},
                    {"type": "skipped", "time": datetime(2024, 12, 6, 10, 0, 0).isoformat(), "user_id": "user1", "reason": "影像质量不达标，无法标注", "images": ["http://minio.local/bucket/skip_001.jpg"]}
                ]
            ),
            # 新增：rejected → restarted → in_progress
            Task(
                id="task22",
                title="膀胱CT标注任务010-打回后重启",
                description="被审核打回后，重新开始",
                project_id="proj1",
                status="in_progress",
                priority="medium",
                assigned_to="user3",
                created_by="user1",
                image_url="/api/images/bladder010.jpg",
                timeline=[
                    {"type": "created", "time": datetime(2024,12,5,8,0,0).isoformat(), "user_id": "user1"},
                    {"type": "claimed", "time": datetime(2024,12,5,9,0,0).isoformat(), "user_id": "user3"},
                    {"type": "submitted", "time": datetime(2024,12,6,9,0,0).isoformat(), "user_id": "user3", "comment": "已完成"},
                    {"type": "reviewed", "time": datetime(2024,12,6,10,0,0).isoformat(), "user_id": "user1", "action": "reject", "comment": "边界不清晰"},
                    {"type": "restarted", "time": datetime(2024,12,7,9,0,0).isoformat(), "user_id": "user3"}
                ]
            ),
            Task(
                id="task13",
                title="积液X光片标注任务005",
                description="标注胸部X光片中的胸腔积液区域",
                project_id="proj2",
                status="submitted",
                priority="medium",
                assigned_to="user3",
                created_by="user1",
                image_url="/api/images/chest005.jpg",
                annotation_data={"lesions": [{"x": 140, "y": 200, "type": "pleural_effusion"}]},
                score=40,
                submitted_at=datetime(2024, 12, 10, 16, 30, 0),
                timeline=[
                    {
                        "type": "created",
                        "time": datetime(2024, 12, 5, 11, 30, 0).isoformat(),
                        "user_id": "user1",
                        "user_name": "admin"
                    },
                    {
                        "type": "claimed",
                        "time": datetime(2024, 12, 7, 14, 0, 0).isoformat(),
                        "user_id": "user3",
                        "user_name": "annotator2"
                    },
                    {
                        "type": "started",
                        "time": datetime(2024, 12, 7, 14, 30, 0).isoformat(),
                        "user_id": "user3",
                        "user_name": "annotator2",
                        "comment": "开始标注胸腔积液区域"
                    },
                    {
                        "type": "submitted",
                        "time": datetime(2024, 12, 10, 16, 30, 0).isoformat(),
                        "user_id": "user3",
                        "user_name": "annotator2",
                        "comment": "已完成胸腔积液区域标注，请审核",
                        "organ_count": 1
                    }
                ]
            ),
            Task(
                id="task14",
                title="肺炎X光片标注任务006",
                description="标注胸部X光片中的肺炎病变区域",
                project_id="proj2",
                status="pending",
                priority="low",
                created_by="user1",
                image_url="/api/images/chest006.jpg",
                score=35
            ),
            Task(
                id="task15",
                title="结核X光片标注任务007",
                description="标注胸部X光片中的结核病变区域",
                project_id="proj2",
                status="pending",
                priority="low",
                created_by="user1",
                image_url="/api/images/chest007.jpg",
                score=30
            ),
            
            # 项目3的任务
            Task(
                id="task16",
                title="脑肿瘤MRI标注任务001",
                description="标注脑部MRI影像中的肿瘤区域",
                project_id="proj3",
                status="approved",
                priority="high",
                assigned_to="user4",
                created_by="user1",
                image_url="/api/images/brain001.jpg",
                annotation_data={"lesions": [{"x": 100, "y": 100, "type": "tumor"}]},
                score=80,
                submitted_at=datetime(2024, 12, 12, 17, 0, 0),
                reviewed_by="user1",
                reviewed_at=datetime(2024, 12, 12, 17, 0, 0),
                review_comment="标注精确，质量优秀"
            ),
            Task(
                id="task17",
                title="脑梗塞MRI标注任务002",
                description="标注脑部MRI影像中的梗塞区域",
                project_id="proj3",
                status="pending",
                priority="high",
                created_by="user1",
                image_url="/api/images/brain002.jpg",
                score=70
            ),
            Task(
                id="task18",
                title="脑出血MRI标注任务003",
                description="标注脑部MRI影像中的出血区域",
                project_id="proj3",
                status="pending",
                priority="high",
                created_by="user1",
                image_url="/api/images/brain003.jpg",
                score=75
            ),
            Task(
                id="task19",
                title="脑萎缩MRI标注任务004",
                description="标注脑部MRI影像中的萎缩区域",
                project_id="proj3",
                status="pending",
                priority="medium",
                created_by="user1",
                image_url="/api/images/brain004.jpg",
                score=60
            ),
            Task(
                id="task20",
                title="脑积水MRI标注任务005",
                description="标注脑部MRI影像中的积水区域",
                project_id="proj3",
                status="pending",
                priority="medium",
                created_by="user1",
                image_url="/api/images/brain005.jpg",
                score=65
            )
        ]
        
        # 补齐姓名字段，并将timeline中的 user_name 替换为真实姓名
        def resolve_name(uid: str) -> str:
            info = users_by_id.get(uid, {})
            return info.get("real_name") or info.get("username") or uid

        for task in tasks:
            # 冗余姓名字段
            if task.created_by:
                task.created_by_name = resolve_name(task.created_by)
            if task.assigned_to:
                task.assigned_to_name = resolve_name(task.assigned_to)
            if getattr(task, 'reviewed_by', None):
                task.reviewed_by_name = resolve_name(task.reviewed_by)

            # timeline 姓名替换
            if task.timeline:
                for ev in task.timeline:
                    if isinstance(ev, dict) and ev.get("user_id"):
                        ev["user_name"] = resolve_name(ev["user_id"])

            db.add(task)

        print("✅ 任务创建完成")
        print("💾 提交数据到数据库...")

        db.commit()

        print("🎉 数据库初始化完成！")
        print("\n📊 数据统计:")
        print(f"   - 用户: {len([admin_user, annotator1, annotator2, annotator3])} 个")
        print(f"   - 项目: {len([project1, project2, project3])} 个")
        print(f"   - 任务: {len(tasks)} 个")

        print("\n👥 默认用户账号:")
        print("   管理员: admin / admin123")
        print("   标注员: annotator1 / annotator123")
        print("   标注员: annotator2 / annotator123")
        print("   标注员: annotator3 / annotator123")

        print("\n⏰ Timeline测试任务:")
        print("   - task1, task2, task3: 完整生命周期 (created → claimed → submitted → reviewed)")
        print("   - task4: 进行中 (created → claimed → started)")
        print("   - task12: 完整生命周期 (created → claimed → started → submitted → reviewed)")
        print("   - task13: 待审核 (created → claimed → started → submitted)")
        print("   - task5: 待分配 (created)")

        print("\n🔗 访问地址:")
        print("   前端: http://localhost:3008")
        print("   后端API: http://localhost:8000")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 