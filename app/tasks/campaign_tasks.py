# app\tasks\campaign_tasks.py

from fastapi.concurrency import run_in_threadpool
from app.dependencies.mongo_db_authentication import get_database
from app.database.campaign_analysis_data import update_campaigns


async def run_update_campaigns():
    print("Running update_campaigns")
    try:
        db = get_database()
        result = await run_in_threadpool(update_campaigns, db)
        print(result)
    except Exception as e:
        print(f"Error[fetch_and_store_data]: {str(e)}")