# app/routers/handle_settings.py

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.db.settings_data import (
    get_campaigns,
    get_keyword_alerts,
    get_sentiment_shift, 
    get_campaign_by_id, 
    delete_campaign, 
    add_topic_alert, 
    get_all_topic_alerts, 
    update_topic_alert, 
    delete_topic_alert, 
    add_sentiment_shift_threshold, 
    get_sentiment_shift_threshold_by_id, 
    update_sentiment_shift_threshold, 
    delete_sentiment_shift_threshold
)
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
    
#settings-campaigns
@router.post("/add_topic_alert", response_model=dict)
async def add_topic_alert_endpoint(
    topic: str = Body(...),
    alert_type: str = Body(...),
    min_val: int = Body(...),
    max_val: int = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        new_alert = add_topic_alert(db, topic, alert_type, min_val, max_val)
        serialized_alert = jsonable_encoder(new_alert)
        return JSONResponse(content=serialized_alert)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[add_topic_alert]: {str(e)}")
    
@router.get("/topic_alerts", response_model=dict)
async def get_all_topic_alerts_endpoint(
    db: MongoClient = Depends(get_database)
):
    try:
        alerts = get_all_topic_alerts(db)
        serialized_alerts = jsonable_encoder(alerts)
        return JSONResponse(content=serialized_alerts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_all_topic_alerts]: {str(e)}")
    

@router.put("/topic_alert/{alert_id}", response_model=dict)
async def update_topic_alert_endpoint(
    alert_id: str = Path(..., description="The ID of the topic alert to update"),
    topic: str = Body(...),
    alert_type: str = Body(...),
    min_val: int = Body(...),
    max_val: int = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        updated_alert = update_topic_alert(db, alert_id, topic, alert_type, min_val, max_val)
        serialized_alert = jsonable_encoder(updated_alert)
        return JSONResponse(content=serialized_alert)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[update_topic_alert]: {str(e)}")
    
@router.delete("/topic_alert/{alert_id}", response_model=dict)
async def delete_topic_alert_endpoint(
    alert_id: str = Path(..., description="The ID of the topic alert to delete"),
    db: MongoClient = Depends(get_database)
):
    try:
        delete_topic_alert(db, alert_id)
        return JSONResponse(content={"message": "Topic alert deleted successfully"})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[delete_topic_alert]: {str(e)}")
    
#settings-sentiment shift thresholds
@router.post("/add_sentiment_shift_threshold", response_model=dict)
async def add_sentiment_shift_threshold_endpoint(
    sm_id: str = Body(...),
    alert_type: str = Body(...),
    min_val: int = Body(...),
    max_val: int = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        new_threshold = add_sentiment_shift_threshold(db, sm_id, alert_type, min_val, max_val)
        serialized_threshold = jsonable_encoder(new_threshold)
        return JSONResponse(content=serialized_threshold)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[add_sentiment_shift_threshold]: {str(e)}")
    
@router.get("/sentiment_shift_threshold/{threshold_id}", response_model=dict)
async def get_sentiment_shift_threshold_endpoint(
    threshold_id: str = Path(..., description="The ID of the sentiment shift threshold to retrieve"),
    db: MongoClient = Depends(get_database)
):
    try:
        threshold = get_sentiment_shift_threshold_by_id(db, threshold_id)
        serialized_threshold = jsonable_encoder(threshold)
        return JSONResponse(content=serialized_threshold)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_sentiment_shift_threshold_by_id]: {str(e)}")

@router.put("/sentiment_shift_threshold/{threshold_id}", response_model=dict)
async def update_sentiment_shift_threshold_endpoint(
    threshold_id: str = Path(..., description="The ID of the sentiment shift threshold to update"),
    sm_id: str = Body(...),
    alert_type: str = Body(...),
    min_val: int = Body(...),
    max_val: int = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        updated_threshold = update_sentiment_shift_threshold(db, threshold_id, sm_id, alert_type, min_val, max_val)
        serialized_threshold = jsonable_encoder(updated_threshold)
        return JSONResponse(content=serialized_threshold)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[update_sentiment_shift_threshold]: {str(e)}")

@router.delete("/sentiment_shift_threshold/{threshold_id}", response_model=dict)
async def delete_sentiment_shift_threshold_endpoint(
    threshold_id: str = Path(..., description="The ID of the sentiment shift threshold to delete"),
    db: MongoClient = Depends(get_database)
):
    try:
        delete_sentiment_shift_threshold(db, threshold_id)
        return JSONResponse(content={"message": "Sentiment shift threshold deleted successfully"})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[delete_sentiment_shift_threshold]: {str(e)}")