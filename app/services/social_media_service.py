# app/services/social_media_service.py

from typing import List
from datetime import datetime
from pymongo import MongoClient
from fastapi import HTTPException
from app.models.product_keyword_models import FilteredKeywordsByDate
from app.db.campaign_analysis_data import get_filtered_keywords_by_date

async def fetch_filtered_keywords_by_date(db: MongoClient, start_date: datetime, end_date: datetime) -> List[FilteredKeywordsByDate]:
    filtered_keywords = get_filtered_keywords_by_date(db, start_date, end_date)
    
    if not filtered_keywords:
        raise HTTPException(status_code=404, detail="No keywords found for the given date range")
    
    return filtered_keywords
