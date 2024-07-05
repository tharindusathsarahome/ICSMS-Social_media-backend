# app/routers/handle_campaign_analysis.py

import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.mongo_client import MongoClient

from app.models.product_keyword_models import FilteredKeywordsByDate
from app.dependencies.mongo_db_authentication import get_database
from app.database.campaign_analysis_data import (
    check_adding_campaign,
    get_campaign_analysis_details
    )


router = APIRouter()


@router.post("/create-campaign", response_model=dict)
async def new_campaign(
    platform: str = Body(...),
    post_description_part: str = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        new_campaign = check_adding_campaign(db, platform, post_description_part)
        serialized_campaign = jsonable_encoder(new_campaign)
        return JSONResponse(content=serialized_campaign)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[add_campaign]: {str(e)}")


@router.get("/campaign_analysis_details", response_model=dict)
async def campaign_analysis_details(
    db: MongoClient = Depends(get_database),
    platform: str = Query(..., title="Platform"),
):
    result = get_campaign_analysis_details(db, platform)
    serialized_data = jsonable_encoder(result)
    return JSONResponse(content=serialized_data, status_code=200)
