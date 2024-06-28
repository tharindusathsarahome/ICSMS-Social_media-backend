# app/routers/handle_settings.py

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.db.settings_data import get_keyword_alerts, get_sentiment_shift, get_campaign_by_id, delete_campaign, get_campaigns
import json

router = APIRouter()


@router.get("/keyword_alerts", response_model=dict)
async def keyword_alerts(
    db: MongoClient = Depends(get_database),
    # current_user=Depends(role_required("Admin")),
):
    result = get_keyword_alerts(db) 
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts)


# sentiment shift
@router.get("/sentiment_shifts", response_model=dict)
async def sentiment_shift(
    db: MongoClient = Depends(get_database),
    # current_user=Depends(role_required("Admin")),
):
    try:
        result = get_sentiment_shift(db)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_sentiment_shift]: {str(e)}")


#settings-campaigns
@router.get("/campaign/{campaign_id}", response_model=dict)
async def campaigns(
    campaign_id: str = Path(..., description="The ID of the campaign to retrieve"),
    db: MongoClient = Depends(get_database)
):
    try:
        campaign = get_campaign_by_id(db, campaign_id)
        serialized_campaign = jsonable_encoder(campaign)
        return JSONResponse(content=serialized_campaign)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_campaign_by_id]: {str(e)}")


@router.get("/campaigns", response_model=dict)
async def campaigns(
    db: MongoClient = Depends(get_database)
):
    try:
        campaigns = get_campaigns(db)
        serialized_campaigns = jsonable_encoder(campaigns)
        return JSONResponse(content=serialized_campaigns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_campaigns]: {str(e)}")
    
    
@router.delete("/campaign/{campaign_id}", response_model=dict)
async def campaign(
    campaign_id: str = Path(..., description="The ID of the campaign to delete"),
    db: MongoClient = Depends(get_database)
):
    try:
        delete_campaign(db, campaign_id)
        return JSONResponse(content={"message": "Campaign deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[delete_campaign]: {str(e)}")    
    