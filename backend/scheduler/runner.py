from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.scheduler.jobs import job_github_digest, job_email_monitor, job_youtube_curator
import logging

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")

    scheduler.add_job(job_github_digest,  CronTrigger(hour=8,  minute=0),          id="github")
    scheduler.add_job(job_email_monitor,  CronTrigger(minute="*/30"),               id="email")
    scheduler.add_job(job_youtube_curator, CronTrigger(day_of_week="mon,thu", hour=9), id="youtube")

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
