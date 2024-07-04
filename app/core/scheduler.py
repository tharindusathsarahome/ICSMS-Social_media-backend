# app/core/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tasks.post_tasks import run_fetch_and_store_facebook, run_calculate_post_overview_by_date, run_analyze_comments
from app.tasks.product_keyword_tasks import run_add_identified_products, run_add_identified_keywords
from app.tasks.campaign_tasks import run_update_campaigns
from app.tasks.notification_tasks import run_check_product_alerts, run_check_sentiment_shifts
import asyncio


def start_scheduler():
    scheduler = BackgroundScheduler()

    def run_async_task():
        asyncio.run(run_fetch_and_store_facebook())
        asyncio.run(run_calculate_post_overview_by_date())
        asyncio.run(run_add_identified_products())
        asyncio.run(run_add_identified_keywords())
        asyncio.run(run_update_campaigns())
        asyncio.run(run_analyze_comments())

    scheduler.add_job(run_async_task, CronTrigger(hour=0, minute=0))
    scheduler.start()
    print("Scheduler started")

    return scheduler


def start_alert_scheduler():
    scheduler = BackgroundScheduler()

    def run_async_task():
        asyncio.run(run_check_product_alerts())
        asyncio.run(run_check_sentiment_shifts())

    scheduler.add_job(run_async_task, CronTrigger(hour='*/6'))
    scheduler.start()
    print("Alert Scheduler started")

    return scheduler