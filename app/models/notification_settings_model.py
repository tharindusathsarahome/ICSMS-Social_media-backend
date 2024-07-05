from pydantic import BaseModel, EmailStr
from typing import List, Dict



# Settings Schema
class NotificationSettings(BaseModel):
    dashboard_notifications: bool
    email_notifications: bool
    notification_emails: List[EmailStr]


