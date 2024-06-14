# app/routers/handle_campaign_analysis.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.db.campaign_analysis_data import create_campaign, calculate_post_overview_by_date, calculate_post_overview_by_date_all
import json

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