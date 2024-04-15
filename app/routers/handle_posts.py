# app/routers/social_media.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from facebook import GraphAPI

from app.db.connection import get_database
from app.db.schema_update_sample import list_posts, get_keyword_alerts
from app.models.post_models import FacebookPost, CommentsOfPosts, SubComments
from app.dependencies.facebook_authentication import authenticate_with_facebook
import json

router = APIRouter()


@router.get("/store_posts", response_model=dict)
async def store_posts(
    db: MongoClient = Depends(get_database),
    graph: GraphAPI = Depends(authenticate_with_facebook),
):
    try:
        posts = graph.get_object('me/feed', fields='id,message,created_time,likes.summary(true),comments.summary(true)')

        for post in posts['data']:
            post_model = FacebookPost(
                id=post['id'],
                message=post.get('message', 'No message'),
                created_time=post['created_time'],
                likes=post['likes']['summary']['total_count'],
                comments=[]
            )

            comments = graph.get_object(f"{post['id']}/comments", fields='id,message,created_time,likes.summary(true),comments.summary(true)')

            for comment in comments['data']:
                comment_model = CommentsOfPosts(
                    id=comment['id'],
                    comment=comment.get('message', 'No message'),
                    created_time=comment['created_time'],
                    likes=comment['likes']['summary']['total_count'],
                    sub_comments=[]
                )

                for sub_comment in comment['comments']['data']:
                    sub_comment_model = SubComments(
                        id=sub_comment['id'],
                        sub_comment=sub_comment.get('message', 'No message'),
                        created_time=sub_comment['created_time']
                    )
                    comment_model.sub_comments.append(sub_comment_model)

                post_model.comments.append(comment_model)

            post_dict = post_model.model_dump()
            db["posts_collection"].update_one({"id": post_dict['id']}, {"$set": post_dict}, upsert=True)

        return JSONResponse(content={"message": "Success"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[store_posts]: {str(e)}")


@router.get("/get_posts", response_model=dict)
async def get_posts(
    db: MongoClient = Depends(get_database),
):
    try:
        posts = list_posts(db["posts_collection"].find())
        serialized_posts = jsonable_encoder(posts)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_posts]: {str(e)}")


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

# http://127.0.0.1:8000/execute_mongodb_query?query={"insert":"SocialMedia","documents":[{"sm_id":"SM01","name":"Facebook"},{"sm_id":"SM02","name":"Instagram"}]}


@router.get("/get_keyword_alerts_", response_model=dict)
async def get_keyword_alerts_(
    db: MongoClient = Depends(get_database),
):
    result = get_keyword_alerts(db)
    serialized_posts = jsonable_encoder(result)
    return JSONResponse(content=serialized_posts)