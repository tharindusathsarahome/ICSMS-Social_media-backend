# app/routers/handle_settings.py

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.database.settings_data import (
    get_campaigns,
    delete_campaign, 
    add_product_alert, 
    get_product_alert_by_id,
    get_all_product_alerts, 
    update_product_alert, 
    delete_product_alert, 
    add_sentiment_shift_threshold, 
    get_sentiment_shift_threshold_by_id, 
    get_sentiment_shift_threshold, 
    update_sentiment_shift_threshold, 
    delete_sentiment_shift_threshold
)
import json

router = APIRouter()



#settings-campaigns

@router.get("/campaigns", response_model=dict)
async def all_campaigns(
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
    


#setting - product- alerts
@router.post("/add_product_alert", response_model=dict)
async def add_product_alert_(
    product: str = Body(...),
    alert_type: str = Body(...),
    min_val: int = Body(...),
    max_val: int = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        new_alert = add_product_alert(db, product, alert_type, min_val, max_val)
        serialized_alert = jsonable_encoder(new_alert)
        return JSONResponse(content=serialized_alert)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[add_product_alert]: {str(e)}")
    

@router.get("/product_alert/{alert_id}", response_model=dict)
async def get_product_alert_(
    alert_id: str = Path(..., description="The ID of the product alert to retrieve"),
    db: MongoClient = Depends(get_database)
):
    try:
        alert = get_product_alert_by_id(db, alert_id)
        serialized_alert = jsonable_encoder(alert)
        return JSONResponse(content=serialized_alert)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_product_alert_by_id]: {str(e)}")


@router.get("/product_alerts", response_model=dict)
async def get_all_product_alerts_(
    db: MongoClient = Depends(get_database)
):
    try:
        alerts = get_all_product_alerts(db)
        serialized_alerts = jsonable_encoder(alerts)
        return JSONResponse(content=serialized_alerts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_all_product_alerts]: {str(e)}")
    

@router.put("/product_alert/{alert_id}", response_model=dict)
async def update_product_alert_(
    alert_id: str = Path(..., description="The ID of the product alert to update"),
    alert_type: str = Body(...),
    min_val: int = Body(...),
    max_val: int = Body(...),
    db: MongoClient = Depends(get_database)
):
    try:
        updated_alert = update_product_alert(db, alert_id, alert_type, min_val, max_val)
        serialized_alert = jsonable_encoder(updated_alert)
        return JSONResponse(content=serialized_alert)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[update_product_alert]: {str(e)}")
    

@router.delete("/product_alert/{alert_id}", response_model=dict)
async def delete_product_alert_(
    alert_id: str = Path(..., description="The ID of the product alert to delete"),
    db: MongoClient = Depends(get_database)
):
    try:
        delete_product_alert(db, alert_id)
        return JSONResponse(content={"message": "Product alert deleted successfully"})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[delete_product_alert]: {str(e)}")
    

#settings-sentiment shift thresholds
@router.get("/sentiment_shifts", response_model=dict)
async def sentiment_shift(
    db: MongoClient = Depends(get_database),
    # current_user=Depends(role_required("Admin")),
):
    try:
        result = get_sentiment_shift_threshold(db)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_sentiment_shift_threshold]: {str(e)}")


@router.post("/add_sentiment_shift_threshold", response_model=dict)
async def add_sentiment_shift_threshold_(
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
async def get_sentiment_shift_threshold_(
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
async def update_sentiment_shift_threshold_(
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
async def delete_sentiment_shift_threshold_(
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