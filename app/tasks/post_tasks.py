# app/tasks/post_tasks.py

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.facebook_authentication import authenticate_with_facebook
from app.db.facebook_data import fetch_and_store_facebook_data, analyze_and_update_comments, analyze_and_update_subcomments
from app.db.campaign_analysis_data import calculate_post_overview_by_date


async def run_fetch_and_store_facebook():
    print("Running fetch_and_store_facebook")
    try:
        db = get_database()
        graph = await authenticate_with_facebook()
        await fetch_and_store_facebook_data(db, graph)
    except Exception as e:
        print(f"Error[fetch_and_store_data]: {str(e)}")


async def run_calculate_post_overview_by_date():
    print("Running calculate_post_overview_by_date")
    try:
        db = get_database()
        await calculate_post_overview_by_date(db)
    except Exception as e:
        print(f"Error[calculate_post_overview_by_date]: {str(e)}")


async def run_analyze_unread_comments():
    print("Running analyze_unread_comments")
    try:
        db = get_database()
        await analyze_and_update_comments(db)
        await analyze_and_update_subcomments(db)
    except Exception as e:
        print(f"Error[analyze_unread_comments]: {str(e)}")
