# app\models\notification_models.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


class Notification(BaseModel):
    title: str
    description: str
    date: datetime
    class Config:
        arbitrary_types_allowed = True

class NotificationSettings(BaseModel):
    dashboard_notifications: bool
    email_notifications: bool
    notification_emails: List[EmailStr]
    class Config:
        arbitrary_types_allowed = True
