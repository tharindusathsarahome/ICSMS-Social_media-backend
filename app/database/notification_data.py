# app\db\notification_data.py

from pymongo import MongoClient
from datetime import datetime
from app.schemas.notification_schemas import Notification


def add_notification(db: MongoClient, title: str, description: str) -> None:
    """
    Adds a new notification to the database.

    Parameters:
        db (MongoClient): The MongoDB client instance.
        title (str): The title of the notification.
        description (str): The description or body of the notification.

    Returns:
        None: The function inserts a new notification into the database.
    """

    new_notification = Notification(
        title=title,
        description=description,
        date=datetime.now()
    )

    result = db.Notification.insert_one(new_notification.model_dump())

    return {"Notification Added": str(result.inserted_id)}

def get_mail_list(db: MongoClient) -> list:
    """
    Retrieves the list of email addresses for notification purposes.

    Parameters:
        db (MongoClient): The MongoDB client instance.

    Returns:
        list: A list of email addresses to send notifications to.
    """
    
    notification_emails = db.NotificationSettings.find_one()
    return notification_emails["notification_emails"]

def check_notification_settings(db: MongoClient) -> bool:
    """
    Checks if email and dashboard notifications are enabled in the settings.

    Parameters:
        db (MongoClient): The MongoDB client instance.

    Returns:
        dict: A dictionary with the status of 'dashboard_notifications' and 'email_notifications'.
    """
    
    notification_emails = db.NotificationSettings.find_one()
    return {"app" : notification_emails["dashboard_notifications"], "email": notification_emails["email_notifications"]}