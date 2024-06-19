from typing import List
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from datetime import datetime

class CustomProducts(BaseModel):
    product: str

class IdentifiedProducts(BaseModel):
    sm_id: str
    post_id: ObjectId
    identified_product: str
    date: datetime
    class Config:
        arbitrary_types_allowed = True