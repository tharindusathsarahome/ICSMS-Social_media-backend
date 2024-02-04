# app/models/social_media.py

from typing import List
from pydantic import BaseModel

class SubComments(BaseModel):
    id: str
    sub_comment: str
    created_time: str

class CommentsOfPosts(BaseModel):
    id: str
    comment: str
    created_time: str
    likes: int
    sub_comments: List[SubComments]

class FacebookPost(BaseModel):
    id: str
    message: str
    created_time: str
    likes: int
    comments: List[CommentsOfPosts]

class FacebookPostsList(BaseModel):
    items: List[FacebookPost]
