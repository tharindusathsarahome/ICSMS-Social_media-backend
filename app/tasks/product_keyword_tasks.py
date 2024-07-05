# app\tasks\product_keyword_tasks.py

from fastapi.concurrency import run_in_threadpool
from app.dependencies.mongo_db_authentication import get_database
from app.database.products_keywords_data import add_identified_products, add_identified_keywords


async def run_add_identified_products():
    print("Running add_identified_products")
    try:
        db = get_database()
        result = await run_in_threadpool(add_identified_products, db)
        print(result)
    except Exception as e:
        print(f"Error[fetch_and_store_data]: {str(e)}")


async def run_add_identified_keywords():
    print("Running add_identified_keywords")
    try:
        db = get_database()
        result = await run_in_threadpool(add_identified_keywords, db)
        print(result)
    except Exception as e:
        print(f"Error[fetch_and_store_data]: {str(e)}")