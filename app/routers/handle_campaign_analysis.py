#app/routers/handle_campaign_analysis.py

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from collections import defaultdict  

from app.dependencies.mongo_db_authentication import get_database
from app.db.campaign_analysis_data import get_campaign_details
from app.db.campaign_analysis_data import get_campaign_analysis_details 
from app.services.social_media_service import fetch_filtered_keywords_by_date
from app.db.campaign_analysis_data import delete_campaign_from_db
from app.models.post_models import FilteredKeywordsByDate
import json

router = APIRouter()

@router.get("/get_campaign_details", response_model=dict)
async def get_campaign_details_endpoint(
    db: MongoClient = Depends(get_database),
):
    result = get_campaign_details(db)
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts)


@router.get("/get_campaign_analysis_details", response_model=dict)
async def campaign_analysis_details_endpoint(
    db: MongoClient = Depends(get_database),
):
    result = get_campaign_analysis_details(db)
    serialized_data = jsonable_encoder(result)
    return JSONResponse(content=serialized_data)

@router.delete("/campaigns/{campaign_id}", response_model=dict)
def delete_campaign(campaign_id: str, db: MongoClient = Depends(get_database)):
    return delete_campaign_from_db(campaign_id, db)

@router.get("/filtered_keywords_by_date", response_model=List[FilteredKeywordsByDate])
async def filtered_keywords_by_date(
    start_date: datetime = Query(..., description="Start date for filtering keywords"),
    end_date: datetime = Query(..., description="End date for filtering keywords"),
    db: MongoClient = Depends(get_database)
):
    result = await fetch_filtered_keywords_by_date(db, start_date, end_date)
    return JSONResponse(content=result)


