# app/routers/handle_facebook.py

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from facebook import GraphAPI
from typing import List, Dict

from app.dependencies.mongo_db_authentication import get_database
from app.db.facebook_data import fetch_and_store_facebook_data, get_unread_comments, get_unread_subcomments, update_comment_sentiment, update_subcomment_sentiment
from app.dependencies.facebook_authentication import authenticate_with_facebook
from app.services.sentiment_analysis import analyze_sentiment
import json

router = APIRouter()


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

@router.post("/analyze_unread_comments")
async def analyze_unread_comments_endpoint(background_tasks: BackgroundTasks, db: MongoClient = Depends(get_database)):
    unread_comments = get_unread_comments(db)
    unread_subcomments = get_unread_subcomments(db)

    background_tasks.add_task(analyze_and_update_comments, db, unread_comments)
    background_tasks.add_task(analyze_and_update_subcomments, db, unread_subcomments)

    return JSONResponse(content={"status": "Sentiment analysis started."})

def analyze_and_update_comments(db: MongoClient, comments: List[Dict]):
    for comment in comments:
        description = comment['description']
        score = analyze_sentiment(description)
        update_comment_sentiment(db, comment['comment_id'], score)

def analyze_and_update_subcomments(db: MongoClient, subcomments: List[Dict]):
    for subcomment in subcomments:
        description = subcomment['description']
        score = analyze_sentiment(description)
        update_subcomment_sentiment(db, subcomment['comment_id'], score)