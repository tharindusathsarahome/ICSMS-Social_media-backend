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
        
class Keyword(BaseModel):
    keyword_id: str
    SocialMedia_sm_id: Optional[str] = None
    author: Optional[str] = None
    keyword: str
    class Config:
        arbitrary_types_allowed = True

class FilteredKeywordsByDate(BaseModel):
    Keywords_keyword_id: str
    date: datetime
    total_count: int
    keyword: str
    author: str
    class Config:
        arbitrary_types_allowed = True
