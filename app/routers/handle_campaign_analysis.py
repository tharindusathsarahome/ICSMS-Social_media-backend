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

from app.models.post_models import FilteredKeywordsByDate
from app.dependencies.mongo_db_authentication import get_database
from app.services.social_media_service import fetch_filtered_keywords_by_date
from app.db.campaign_analysis_data import (
    create_campaign, 
    calculate_post_overview_by_date, 
    calculate_post_overview_by_date_all,
    get_campaign_details,
    get_campaign_analysis_details,
    delete_campaign_from_db
    )


router = APIRouter()


@router.get("/create-campaign", response_description="Create a campaign", response_model=str)
async def create_campaign_endpoint(
    db: MongoClient = Depends(get_database),
    post_id: str = Query(..., description="The post id"),
):
    campaign = create_campaign(db, post_id)
    return JSONResponse(content=json.dumps(campaign), status_code=200)


@router.get("/calculate-post-overview-by-date", response_description="Calculate post overview by date", response_model=str)
async def calculate_post_overview_by_date_endpoint(
    db: MongoClient = Depends(get_database),
    post_id: str = Query(..., description="The post id"),
):
    post_overview = calculate_post_overview_by_date(db, post_id)
    return JSONResponse(content=json.dumps(post_overview), status_code=200)


@router.get("/calculate-post-overview-by-date-all", response_description="Calculate post overview by date for all posts", response_model=str)
async def calculate_post_overview_by_date_all_endpoint(
    db: MongoClient = Depends(get_database),
):
    post_overview = calculate_post_overview_by_date_all(db)
    return JSONResponse(content=json.dumps(post_overview), status_code=200)


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