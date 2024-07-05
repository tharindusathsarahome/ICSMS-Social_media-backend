# app\db\notification_data.py

from pymongo import MongoClient
from datetime import datetime
from app.models.notification_models import Notification


def add_notification(db: MongoClient, title: str, description: str) -> None:

    new_notification = Notification(
        title=title,
        description=description,
        date=datetime.now()
    )

    result = db.Notification.insert_one(new_notification.model_dump())

    return {"Notification Added": str(result.inserted_id)}