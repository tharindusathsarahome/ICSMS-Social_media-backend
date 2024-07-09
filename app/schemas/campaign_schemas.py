# app\models\campaign_models.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.schemas.post_schemas import Post


class Campaign(BaseModel):
    post_id: ObjectId
    s_score_arr: List[float]
    class Config:
        arbitrary_types_allowed = True