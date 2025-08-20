from log_setup import logger
import time
from typing import Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from config.config import config

class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.tz = timezone(config.TIMEZONE)
        
    def schedule_daily_task(self, task: Callable, time_str: str) -> None:
        """Schedule a task to run daily at specific time"""
        hour, minute = map(int, time_str.split(':'))
        trigger = CronTrigger(hour=hour, minute=minute, timezone=self.tz)
        self.scheduler.add_job(task, trigger)
        logger.info(f"Scheduled task for {time_str} {config.TIMEZONE}")
    
    def schedule_retry_tasks(self, task: Callable) -> None:
        """Schedule retry tasks"""
        for retry_time in config.RETRY_TIMES:
            trigger = CronTrigger(hour=retry_time.hour, 
                                minute=retry_time.minute, 
                                timezone=self.tz)
            self.scheduler.add_job(task, trigger)
            logger.info(f"Scheduled retry task for {retry_time.strftime('%H:%M')} {config.TIMEZONE}")
    
    def start(self) -> None:
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Scheduler started")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully"""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")

# Global scheduler instance
scheduler_manager = SchedulerManager()