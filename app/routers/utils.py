# app/routers/utils.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.services.sentiment_analysis import analyze_sentiment
from app.utils.s_analysis_helper import scale_score
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


@router.get("/analyse_sentiments")
async def analyse_sentiments(
    sentence: str = Query(..., title="Sentence to be analyzed"),
):
    try:
        sentiment_score = analyze_sentiment(sentence)
        scaled_sentiment_score = scale_score(sentiment_score)
        return JSONResponse(content={"sentiment_score": scaled_sentiment_score})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[analyse_sentiments]: {str(e)}")


@router.get("/execute_mongodb_query")
async def execute_mongodb_query(
    query: str = Query(..., title="MongoDB Query"),
    db: MongoClient = Depends(get_database),
):
    try:
        query_dict = json.loads(query)
        result = db.command(query_dict)
        return result
    except Exception as e:
        return {"error": str(e)}


# http://127.0.0.1:8000/execute_mongodb_query?query={"insert":"SocialMedia","documents":[{"sm_id":"SM01","name":"Facebook"},{"sm_id":"SM02","name":"Instagram"}]}