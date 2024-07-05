# app/tasks/notification_tasks.py

from fastapi.concurrency import run_in_threadpool
from app.dependencies.mongo_db_authentication import get_database
from app.database.notification_alert_data import check_product_alerts, check_sentiment_shifts
from app.services.notification_service import send_alerts_push_notifications, send_sentiment_shift_push_notifications


async def run_check_product_alerts():
    print("Running check_product_alerts")
    try:
        db = get_database()
        alert_results = await run_in_threadpool(check_product_alerts, db)
        result = send_alerts_push_notifications(db, alert_results)
        print(result)
    except Exception as e:
        print(f"Error[check_product_alerts]: {str(e)}")
    

async def run_check_sentiment_shifts():
    print("Running check_sentiment_shifts")
    try:
        db = get_database()
        sentiment_results = await run_in_threadpool(check_sentiment_shifts, db)
        result = send_sentiment_shift_push_notifications(db, sentiment_results)
        print(result)
    except Exception as e:
        print(f"Error[check_sentiment_shifts]: {str(e)}")