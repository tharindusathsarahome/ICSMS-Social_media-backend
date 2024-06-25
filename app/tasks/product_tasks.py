# app\tasks\product_tasks.py

from app.dependencies.mongo_db_authentication import get_database
from app.db.products_keywords_data import get_identified_products


async def run_get_identified_products():
    print("Running get_identified_products")
    try:
        db = get_database()
        await get_identified_products(db)
        print("Data fetched successfully.")
    except Exception as e:
        print(f"Error[fetch_and_store_data]: {str(e)}")