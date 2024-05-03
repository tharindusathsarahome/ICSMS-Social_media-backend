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
from app.db.schema_update_sample import get_keyword_alerts, get_platform_insights_data, get_highlighted_coments
from app.services.sentiment_analysis import analyze_sentiment
from app.utils.s_analysis_helper import scale_score
from app.models.post_models import Post, Comment, SubComment
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


@router.get("/highlighted_coments", response_model=dict)
async def highlighted_coments(
    db: MongoClient = Depends(get_database),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    result = get_highlighted_coments(db,startDate,endDate)
    serialized_posts = jsonable_encoder({0:result})
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
    try:
        result = get_platform_insights_data(db, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Platform Insights]: {str(e)}")


@router.get("/fetch_and_store_data", response_model=dict)
async def fetch_and_store_data(
    db: MongoClient = Depends(get_database),
    graph: GraphAPI = Depends(authenticate_with_facebook),
):
    try:
        posts = graph.get_object('me/posts', fields='id,message,created_time,from,likes.summary(true),comments.summary(true),full_picture,shares,permalink_url,is_popular')

        for post in posts['data']:
            if 'message' and 'full_picture' not in post:
                continue

            post_model = Post(
                fb_post_id=post['id'],
                description=post.get('message', None),
                img_url=post.get('full_picture', None),
                author = post['from']['name'] if 'from' in post else None,
                total_likes=post['likes']['summary']['total_count'],
                total_comments=post['comments']['summary']['total_count'],
                total_shares=post.get('shares', 0),
                date=datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                is_popular=post['is_popular'],
                post_url=post['permalink_url']
            )

            # https://developers.facebook.com/docs/graph-api/reference/post/
            # me/tagged?fields=id,from,message,target,permalink_url,created_time

            if db.Post.find_one({"fb_post_id": post['id']}) is None:
                db.Post.insert_one(post_model.model_dump())
            db_post_id = db.Post.find_one({"fb_post_id": post['id']})['_id']

            comments = graph.get_object(f"{post['id']}/comments", fields='id,message,created_time,from,likes.summary(true),comments.summary(true)')

            for comment in comments['data']:
                if 'message' not in comment:
                    continue

                comment_model = Comment(
                    fb_comment_id=comment['id'],
                    post_id=db_post_id,
                    description=comment['message'],
                    author = comment['from']['name'] if 'from' in comment else None,
                    total_likes=comment['likes']['summary']['total_count'],
                    date=datetime.strptime(comment['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                )

                if db.Comment.find_one({"fb_comment_id": comment['id']}) is None:
                    db.Comment.insert_one(comment_model.model_dump())
                db_comment_id = db.Comment.find_one({"fb_comment_id": comment['id']})['_id']

                for sub_comment in comment['comments']['data']:
                    if 'message' not in sub_comment:
                        continue

                    sub_comment_model = SubComment(
                        comment_id=db_comment_id,
                        description=sub_comment['message'],
                        author = sub_comment['from']['name'] if 'from' in sub_comment else None,
                        date=datetime.strptime(sub_comment['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                    )
                    
                    if db.SubComment.find_one({"comment_id": db_comment_id, "description": sub_comment['message']}) is None:
                        db.SubComment.insert_one(sub_comment_model.model_dump())

        return {"message": "Data fetched and stored successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[fetch_and_store_data]: {str(e)}")