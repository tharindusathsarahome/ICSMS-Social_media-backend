# app/routers/social_media.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from facebook import GraphAPI
from datetime import datetime

from app.db.connection import get_database
from app.db.schema_update_sample import get_keyword_alerts, get_platform_insights_data, fetch_and_store_facebook_data
from app.services.sentiment_analysis import analyze_sentiment
from app.utils.s_analysis_helper import scale_score
from app.dependencies.facebook_authentication import authenticate_with_facebook
import json

router = APIRouter()


@router.get("/test_database", response_model=dict)
async def test_database(
    db: MongoClient = Depends(get_database),
):
    try:
        db["SocialMedia"].find()
        return JSONResponse(content={"message": "Database is working fine"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[test_database]: {str(e)}")


@router.get("/execute_mongodb_query")
async def execute_mongodb_query(
    query: str = Query(..., title="MongoDB Query"),
    db: MongoClient = Depends(get_database)
):
    try:
        query_dict = json.loads(query)
        result = db.command(query_dict)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/keyword_alerts", response_model=dict)
async def keyword_alerts(
    db: MongoClient = Depends(get_database),
):
    result = get_keyword_alerts(db) 
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts)


@router.get("/analyse_sentiments")
async def analyse_sentiments(
    sentence: str = Query(..., title="Sentence to be analyzed"),
):
    try:
        sentiment_score = analyze_sentiment(sentence)
        sentiment_score = scale_score(sentiment_score)
        return JSONResponse(content={"sentiment_score": sentiment_score})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[analyse_sentiments]: {str(e)}")


@router.get("/platform_insights_data")
async def platform_insights_data(
    db: MongoClient = Depends(get_database),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    # try:
        result = get_platform_insights_data(db, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error[Platform Insights]: {str(e)}")


@router.get("/fetch_and_store_facebook", response_model=dict)
async def fetch_and_store_facebook(
    db: MongoClient = Depends(get_database),
    graph: GraphAPI = Depends(authenticate_with_facebook),
):
    try:
        fetch_and_store_facebook_data(db, graph)
        return {"message": "Data fetched and stored successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[fetch_and_store_data]: {str(e)}")