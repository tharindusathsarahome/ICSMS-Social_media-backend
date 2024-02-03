# app/api/models/social_media.py

from typing import List
from pydantic import BaseModel

class FacebookPostCreate(BaseModel):
    message: str
    created_time: str

class FacebookPost(BaseModel):
    id: str
    message: str
    created_time: str

class FacebookPostsList(BaseModel):
    items: List[FacebookPost]
