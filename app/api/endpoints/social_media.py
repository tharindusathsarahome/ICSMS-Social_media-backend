# app/api/endpoints/social_media.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from app.core.config import PAGE_ID, ACCESS_TOKEN

from app.dependencies import facebook
from app.db.database import get_database

import facebook


router = APIRouter()
graph = facebook.GraphAPI(ACCESS_TOKEN)


@router.get("/fetch_and_store_posts", response_model=dict)
async def fetch_and_store_posts(
    db_client: MongoClient = Depends(get_database),
):
    try:
        posts = graph.get_object(f'{PAGE_ID}/posts', fields='id,message,created_time,likes.summary(true),comments.summary(true)')

        response_data = []

        for post in posts['data']:
            post_data = {
                "Post ID": post['id'],
                "Message": post.get('message', 'No message'),
                "Created Time": post['created_time'],
                "Likes": post['likes']['summary']['total_count'],
                "Comments": post['comments']['summary']['total_count'],
                "Comments Data": []
            }

            comments = graph.get_object(f"{post['id']}/comments", fields='id,message,created_time,likes.summary(true),comments.summary(true)')

            for comment in comments['data']:
                comment_data = {
                    "Comment ID": comment['id'],
                    "Comment Message": comment.get('message', 'No message'),
                    "Comment Created Time": comment['created_time'],
                    "Likes of Comment": comment['likes']['summary']['total_count'],
                    "Comments of Comment": comment['comments']
                }
                post_data["Comments Data"].append(comment_data)

            response_data.append(post_data)

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
