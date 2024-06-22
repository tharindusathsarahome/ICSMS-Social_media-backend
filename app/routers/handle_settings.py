# app/routers/handle_settings.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.db.settings_data import get_keyword_alerts, get_sentiment_shift
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
