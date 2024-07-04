# app\models\notification_models.py

from pydantic import BaseModel
from datetime import datetime
from typing import List


class Notification(BaseModel):
    title: str
    description: str
    date: datetime
    class Config:
        arbitrary_types_allowed = True

class NotificationSettings(BaseModel):
    pushNotification: bool
    emailNotification: bool
    emailsList: List[str]
    class Config:
        arbitrary_types_allowed = True