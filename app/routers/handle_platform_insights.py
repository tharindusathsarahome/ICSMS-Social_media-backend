# app/routers/handle_platform_insights.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.database.platform_insights_data import keyword_trend_count, total_reactions, total_comments, highlighted_comments, average_sentiment_score
import json

router = APIRouter()


@router.get("/keyword_trend_count")
async def keyword_trend_count_(
    db: MongoClient = Depends(get_database),
    # current_user=Depends(role_required("User")),
    platform: str = Query(..., title="Platform"),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    # try:
        result = keyword_trend_count(db, platform, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error[Keyword Trend Count]: {str(e)}")


@router.get("/total_reactions")
async def total_reactions_(
    db: MongoClient = Depends(get_database),
    platform: str = Query(..., title="Platform"),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = total_reactions(db, platform, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Total Reactions]: {str(e)}")
    

@router.get("/total_comments")
async def total_comments_(
    db: MongoClient = Depends(get_database),
    platform: str = Query(..., title="Platform"),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = total_comments(db, platform, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Total Comments]: {str(e)}")


@router.get("/highlighted_comments")
async def highlighted_comments_(
    db: MongoClient = Depends(get_database),
    platform: str = Query(..., title="Platform"),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = highlighted_comments(db, platform, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Highlighted Comments]: {str(e)}")


@router.get("/average_sentiment_score")
async def average_sentiment_score_(
    db: MongoClient = Depends(get_database),
    platform: str = Query(..., title="Platform"),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = average_sentiment_score(db, platform, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Average Sentiment Score]: {str(e)}")