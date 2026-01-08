"""
定时任务服务
使用 APScheduler 管理系统定时任务
"""
import asyncio
import logging
from datetime import datetime
from app.utils.datetime_utils import utc_now
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.notification_ws import manager as ws_manager

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务服务"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
        self._loop = None
        
    def start(self):
        """启动定时任务调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("⏰ [Scheduler] 定时任务调度器已启动")
            
            # 添加下班提醒任务：每天 17:10
            self.add_work_end_reminder()
            
            # 可以在这里添加更多定时任务
            # self.add_other_task()
    
    def shutdown(self):
        """关闭定时任务调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏰ [Scheduler] 定时任务调度器已关闭")
    
    def set_event_loop(self, loop):
        """设置事件循环（用于异步任务）"""
        self._loop = loop
    
    def add_work_end_reminder(self):
        """添加下班提醒任务：每天 17:10"""
        try:
            self.scheduler.add_job(
                func=self._send_work_end_reminder,
                trigger=CronTrigger(hour=17, minute=10, timezone='Asia/Shanghai'),
                id='work_end_reminder',
                name='下班提醒',
                replace_existing=True,
                misfire_grace_time=300  # 如果错过执行时间，5分钟内仍然执行
            )
            logger.info("⏰ [Scheduler] 已添加下班提醒任务：每天 17:10")
            
            # 打印下次执行时间
            next_run = self.scheduler.get_job('work_end_reminder').next_run_time
            logger.info(f"⏰ [Scheduler] 下次执行时间：{next_run}")
        except Exception as e:
            logger.error(f"❌ [Scheduler] 添加下班提醒任务失败: {e}")
    
    def _send_work_end_reminder(self):
        """发送下班提醒（保存给所有用户，包括离线用户）"""
        try:
            logger.info("⏰ [Scheduler] 开始执行下班提醒任务")
            
            # 创建通知消息
            message = {
                "type": "work_end_reminder",
                "title": "🏃 下班提醒",
                "content": "请及时保存文件，填写好今天的工作日志，下班请关电脑！",
                "timestamp": utc_now().isoformat(),
                "priority": "high",
                "category": "daily_reminder"  # ✅ 新增：方便后续分类处理
            }
            
            # 在事件循环中执行异步广播
            if self._loop and self._loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    ws_manager.broadcast_to_all(
                        message,
                        save_offline=True  # ✅ 保存给离线用户
                    ),
                    self._loop
                )
                logger.info("✅ [Scheduler] 下班提醒已发送并保存给所有用户（包括离线）")
            else:
                logger.warning("⚠️ [Scheduler] 事件循环未运行，无法发送通知")
                
        except Exception as e:
            logger.error(f"❌ [Scheduler] 发送下班提醒失败: {e}", exc_info=True)
    
    def trigger_work_end_reminder_now(self):
        """
        立即触发下班提醒（用于测试）
        注意：这是一个同步方法，直接调用 _send_work_end_reminder
        """
        logger.info("🧪 [Scheduler] 手动触发下班提醒（测试）")
        self._send_work_end_reminder()
    
    def list_jobs(self):
        """列出所有定时任务"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger)
            })
        return jobs


# 创建全局调度器实例
scheduler_service = SchedulerService()

