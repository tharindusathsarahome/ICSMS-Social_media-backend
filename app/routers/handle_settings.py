# app/routers/handle_settings.py

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.db.settings_data import get_keyword_alerts, get_sentiment_shift, add_campaign, get_campaign_by_id, update_campaign, delete_campaign
import json

router = APIRouter()


@router.get("/keyword_alerts", response_model=dict)
async def get_keyword_alerts(
    db: MongoClient = Depends(get_database),
    current_user=Depends(role_required("Admin")),
):
    result = get_keyword_alerts(db) 
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts)


# sentiment shift
@router.get("/sentiment_shifts", response_model=dict)
async def get_sentiment_shift(
    db: MongoClient = Depends(get_database),
    current_user=Depends(role_required("Admin")),
):
    try:
        result = get_sentiment_shift(db)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_sentiment_shift]: {str(e)}")

#settings-campaigns
@router.post("/add_campaign", response_model=dict)
async def add_campaign_endpoint(
    platform: str = Body(...),
    post_title: str = Body(...),
    company: str = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        new_campaign = add_campaign(db, platform, post_title, company)
        serialized_campaign = jsonable_encoder(new_campaign)
        return JSONResponse(content=serialized_campaign)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[add_campaign]: {str(e)}")
       
@router.get("/campaign/{campaign_id}", response_model=dict)
async def get_campaign_endpoint(
    campaign_id: str = Path(..., description="The ID of the campaign to retrieve"),
    db: MongoClient = Depends(get_database)
):
    try:
        campaign = get_campaign_by_id(db, campaign_id)
        serialized_campaign = jsonable_encoder(campaign)
        return JSONResponse(content=serialized_campaign)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_campaign_by_id]: {str(e)}")

@router.put("/campaign/{campaign_id}", response_model=dict)
async def update_campaign_endpoint(
    campaign_id: str = Path(..., description="The ID of the campaign to update"),
    platform: str = Body(...),
    post_title: str = Body(...),
    company: str = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        updated_campaign = update_campaign(db, campaign_id, platform, post_title, company)
        serialized_campaign = jsonable_encoder(updated_campaign)
        return JSONResponse(content=serialized_campaign)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[update_campaign]: {str(e)}")
    
@router.delete("/campaign/{campaign_id}", response_model=dict)
async def delete_campaign_endpoint(
    campaign_id: str = Path(..., description="The ID of the campaign to delete"),
    db: MongoClient = Depends(get_database)
):
    try:
        delete_campaign(db, campaign_id)
        return JSONResponse(content={"message": "Campaign deleted successfully"})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[delete_campaign]: {str(e)}")    
    