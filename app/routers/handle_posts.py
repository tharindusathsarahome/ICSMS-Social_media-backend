# app/routers/social_media.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from facebook import GraphAPI

from app.db.connection import get_database
from app.db.schema_update_sample import list_posts
from app.models.post_models import FacebookPost, CommentsOfPosts, SubComments
from app.dependencies.facebook_authentication import authenticate_with_facebook

router = APIRouter()


@router.post("/store_posts", response_model=dict)
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
            criteria = {"id": post_dict['id']}
            db["posts_collection"].update_one(criteria, {"$set": post_dict}, upsert=True)

        return JSONResponse(content={"message": "Success"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[store_posts]: {str(e)}")


@router.get("/get_posts", response_model=dict)
async def get_posts(
    db: MongoClient = Depends(get_database),
):
    try:
        collection = db["posts_collection"]
        posts = list_posts(collection.find())
        serialized_posts = jsonable_encoder(posts)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[get_posts]: {str(e)}")
