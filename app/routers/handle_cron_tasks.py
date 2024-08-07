# app/routers/handle_cron_tasks.py

from fastapi import APIRouter, BackgroundTasks

from app.tasks.post_tasks import run_fetch_and_store_facebook, run_fetch_and_store_instagram, run_calculate_post_overview_by_date, run_analyze_comments
from app.tasks.product_keyword_tasks import run_add_identified_products, run_add_identified_keywords
from app.tasks.campaign_tasks import run_update_campaigns
from app.tasks.notification_tasks import run_check_product_alerts, run_check_sentiment_shifts


router = APIRouter()

def run_all_tasks(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fetch_and_store_facebook)
    background_tasks.add_task(run_fetch_and_store_instagram)
    background_tasks.add_task(run_analyze_comments)
    background_tasks.add_task(run_update_campaigns)
    background_tasks.add_task(run_check_product_alerts)
    background_tasks.add_task(run_check_sentiment_shifts)
    return {"message": "All tasks started."}


@router.get("/fetch_and_store_facebook", response_model=dict)
async def fetch_and_store_facebook(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fetch_and_store_facebook)
    return {"message": "Fetching and storing Facebook data started."}

@router.get("/fetch_and_store_instagram", response_model=dict)
async def fetch_and_store_instagram(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fetch_and_store_instagram)
    return {"message": "Fetching and storing Instagram data started."}

@router.get("/calculate_post_overview_by_date", response_model=dict)
async def calculate_post_overview_by_date(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_calculate_post_overview_by_date)
    return {"message": "Calculating post overview by date started."}

@router.get("/analyze_comments", response_model=dict)
async def analyze_comments(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_analyze_comments)
    return {"message": "Analyzing unread comments started."}

@router.get("/add_identified_products", response_model=dict)
async def add_identified_products(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_add_identified_products)
    return {"message": "Adding identified products started."}

@router.get("/add_identified_keywords", response_model=dict)
async def add_identified_keywords(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_add_identified_keywords)
    return {"message": "Adding identified keywords started."}

@router.get("/update_campaigns", response_model=dict)
async def update_campaigns(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_update_campaigns)
    return {"message": "Updating campaigns started."}

@router.get("/check_product_alerts", response_model=dict)
async def check_product_alerts(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_check_product_alerts)
    return {"message": "Checking product alerts started."}

@router.get("/check_sentiment_shifts", response_model=dict)
async def check_sentiment_shifts(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_check_sentiment_shifts)
    return {"message": "Checking sentiment shifts started."}

@router.get("/all", response_model=dict)
async def all(background_tasks: BackgroundTasks):
    return run_all_tasks(background_tasks)