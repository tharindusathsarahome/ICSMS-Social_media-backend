# app/routers/handle_campaign_analysis.py

import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.mongo_client import MongoClient

from app.models.product_keyword_models import FilteredKeywordsByDate
from app.dependencies.mongo_db_authentication import get_database
from app.services.social_media_service import fetch_filtered_keywords_by_date
from app.db.campaign_analysis_data import (
    create_campaign,
    get_created_campaign,
    get_campaign_analysis_details,
    delete_campaign
    )


router = APIRouter()


@router.post("/create-campaign", response_description="Create a campaign", response_model=str)
async def create_campaign(
    db: MongoClient = Depends(get_database),
    post_id: str = Query(..., description="The post id"),
):
    campaign = create_campaign(db, post_id)
    return JSONResponse(content=json.dumps(campaign), status_code=200)


@router.get("/created_campaigns", response_model=dict)
async def get_created_campaign(
    db: MongoClient = Depends(get_database),
):
    result = get_created_campaign(db)
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts, status_code=200)


@router.get("/campaign_analysis_details", response_model=dict)
async def get_campaign_analysis_details(
    db: MongoClient = Depends(get_database),
):
    result = get_campaign_analysis_details(db)
    serialized_data = jsonable_encoder(result)
    return JSONResponse(content=serialized_data, status_code=200)


@router.delete("/campaigns/{campaign_id}", response_model=dict)
async def delete_campaign(
    campaign_id: str,
    db: MongoClient = Depends(get_database)
):
    result = delete_campaign(campaign_id, db)
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts, status_code=200)


@router.get("/filtered_keywords_by_date", response_model=List[FilteredKeywordsByDate])
async def get_filtered_keywords_by_date(
    start_date: datetime = Query(..., description="Start date for filtering keywords"),
    end_date: datetime = Query(..., description="End date for filtering keywords"),
    db: MongoClient = Depends(get_database)
):
    result = await fetch_filtered_keywords_by_date(db, start_date, end_date)
    return JSONResponse(content=result)