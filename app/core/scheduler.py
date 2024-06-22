# app/core/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tasks.post_tasks import run_fetch_and_store_facebook, run_calculate_post_overview_by_date
from app.tasks.product_tasks import run_get_identified_products
import asyncio


def start_scheduler():
    scheduler = BackgroundScheduler()

    def run_async_task():
        asyncio.run(run_fetch_and_store_facebook())
        asyncio.run(run_calculate_post_overview_by_date())
        asyncio.run(run_get_identified_products())

    scheduler.add_job(run_async_task, CronTrigger(hour=14, minute=45))
    scheduler.start()
    print("Scheduler started")

    return scheduler
