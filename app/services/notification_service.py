# app/tasks/notification_service.py

from pymongo import MongoClient
from typing import List, Dict
from app.db.notification_data import add_notification


def send_alerts_push_notifications(db: MongoClient, alerts_within_range: List[Dict]) -> None:
    for alert in alerts_within_range:
        add_notification(db, "Product Sentiment Alert", f"Product {alert['identified_product_name']} has a total sentiment score of {alert['total_sentiment_score']} which is outside the range of {alert['alert_range'][0]} to {alert['alert_range'][1]}")

    return {"Push Notifications Sent": len(alerts_within_range)}


def send_sentiment_shift_push_notifications(db: MongoClient, results_within_range: List[Dict]) -> None:
    for alert in results_within_range:
        add_notification(db, "Platform Sentiment Alert", f"Sentiment for {alert['platform']} has shifted to {alert['total_sentiment']} which is outside the range of {alert['alert_range'][0]} to {alert['alert_range'][1]}")
    
    return {"Push Notifications Sent": len(results_within_range)}