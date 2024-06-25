# app/models/post_models.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class Post(BaseModel):
    fb_post_id: str
    sm_id: str
    description: Optional[str]
    img_url: Optional[str]
    author: Optional[str]
    total_likes: int
    total_comments: int
    total_shares: int
    date: datetime
    is_popular: bool
    post_url: str

class Comment(BaseModel):
    fb_comment_id: str
    post_id: str  # Changed from ObjectId for simplicity
    description: str
    author: Optional[str] = None
    total_likes: int
    date: datetime
    comment_url: str

    class Config:
        arbitrary_types_allowed = True

class SubComment(BaseModel):
    comment_id: str  # Changed from ObjectId for simplicity
    description: str
    author: Optional[str] = None
    date: datetime

    class Config:
        arbitrary_types_allowed = True


class CommentSentiment(BaseModel):
    comment_id: ObjectId
    s_score: float
    date_calculated: datetime
    class Config:
        arbitrary_types_allowed = True

class SubCommentSentiment(BaseModel):
    sub_comment_id: ObjectId
    s_score: float
    date_calculated: datetime
    class Config:
        arbitrary_types_allowed = True


class PostOverviewByDate(BaseModel):
    post_id: ObjectId
    date: datetime
    total_likes: int
    total_comments: int
    class Config:
        arbitrary_types_allowed = True
