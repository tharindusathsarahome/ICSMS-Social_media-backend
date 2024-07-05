# app/db/settings_data.py

from bson import ObjectId
from pymongo import MongoClient
from collections import defaultdict 

from app.models.product_keyword_models import ProductAlert
from app.models.campaign_models import Campaign
from app.models.notification_settings_model import NotificationSettings
from app.utils.common import convert_s_score_to_color



# Setting - Campaigns

def get_campaigns(db: MongoClient) -> list:
    campaigns = list(db.Campaign.find({}, {"_id": 1, "post_id": 1, "s_score_arr": 1}))
    for campaign in campaigns:
        post = db.Post.find_one({"_id": campaign["post_id"]}, {"_id": 0, "description": 1, "sm_id": 1, "author": 1})
        campaign["description"] = post["description"]
        campaign["platform"] = post["sm_id"]
        campaign["s_score"] = round((campaign["s_score_arr"][-1] + 1) / 2, 1)
        campaign["company"] = post["author"]
        campaign["color"] = convert_s_score_to_color(campaign["s_score_arr"][-1])
        campaign["_id"] = str(campaign["_id"])
        campaign.pop("post_id")
        campaign.pop("s_score_arr")

    campaigns_by_sm = defaultdict(list)
    for campaign in campaigns:
        campaigns_by_sm[campaign["platform"]].append(campaign)
        campaign.pop("platform")
    
    return campaigns_by_sm


def delete_campaign(db: MongoClient, campaign_id: str) -> dict:
    try:
        result = db.Campaign.delete_one({"_id": ObjectId(campaign_id)})
        
        if result.deleted_count == 1:
            return {"status": "success", "message": "Campaign deleted successfully."}
        else:
            return {"status": "failure", "message": "Campaign not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


#settings-alerts

def add_product_alert(db: MongoClient, product: str, alert_type: str, min_val: int, max_val: int) -> dict:
    identified_product = db.IdentifiedProducts.find_one({"identified_product": product}, {"_id": 1})
    if not identified_product:
        raise ValueError("Product not found")
    
    product_id = identified_product["_id"]

    existing_alert = db.ProductAlert.find_one({
        "product_id": product_id,
        "alert_type": alert_type
    })
    
    if existing_alert:
        raise ValueError("Product alert with the same product and alert type already exists")

    new_alert = ProductAlert(
        product_id=product_id,
        alert_type=alert_type,
        min_val=min_val,
        max_val=max_val
    )
    
    result = db.ProductAlert.insert_one(new_alert.model_dump())
    return {"id": str(result.inserted_id)}

def get_product_alert_by_id(db: MongoClient, alert_id: str) -> dict:
    alert = db.ProductAlert.find_one({"_id": ObjectId(alert_id)})
    if not alert:
        raise ValueError("Product alert not found")
    alert["product"] = db.IdentifiedProducts.find_one(
        {"_id": alert["product_id"]}, {"_id": 0, "identified_product": 1, "sm_id":1}
    )["identified_product"]
    alert["id"] = str(alert["_id"])
    alert.pop("_id")
    alert.pop("product_id")
    return alert

def get_all_product_alerts(db: MongoClient) -> list:
    product_alerts = list(db.ProductAlert.find({}, {"_id": 0}))
    for alert in product_alerts:
        product = db.IdentifiedProducts.find_one(
            {"_id": alert["product_id"]}, {"_id": 0, "identified_product": 1}
        )
        alert["product"] = product["identified_product"]
        alert.pop("product_id")
    return product_alerts

def update_product_alert(db: MongoClient, alert_id: str, alert_type: str, min_val: int, max_val: int) -> dict:
    existing_alert = db.ProductAlert.find_one({
        "_id": ObjectId(alert_id)
    })
    
    if not existing_alert:
        raise ValueError("Product alert not found")
    
    updated_alert = {
        "alert_type": alert_type,
        "min_val": min_val,
        "max_val": max_val
    }

    result = db.ProductAlert.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": updated_alert}
    )

    if result.matched_count == 0:
        raise ValueError("Product alert not found or update failed")
    
    result = db.ProductAlert.find_one({"_id": ObjectId(alert_id)}, {"_id": 0})

    return result

def delete_product_alert(db: MongoClient, alert_id: str) -> bool:
    result = db.ProductAlert.delete_one({"_id": ObjectId(alert_id)})
    if result.deleted_count == 0:
        raise ValueError("Product alert not found or deletion failed")
    return True



#settings-sentiment shift thresholds

def add_sentiment_shift_threshold(db: MongoClient, sm_id: str, alert_type: str, min_val: int = None, max_val: int = None) -> dict:

    existing_threshold = db.SentimentShift.find_one({
        "sm_id": sm_id,
        "alert_type": alert_type
    })
    
    if existing_threshold:
        raise ValueError("Sentiment shift threshold with the same platform and alert type already exists")
    
   
    new_threshold = {
        "sm_id": sm_id,
        "alert_type": alert_type,
        "min_val": min_val,
        "max_val": max_val
    }
    
    result = db.SentimentShift.insert_one(new_threshold)
    return {"id": str(result.inserted_id)}

def get_sentiment_shift_threshold_by_id(db: MongoClient, threshold_id: str) -> dict:
    threshold = db.SentimentShift.find_one({"_id": ObjectId(threshold_id)})
    if not threshold:
        raise ValueError("Sentiment shift threshold not found")
    threshold.pop("_id")
    return threshold


def get_sentiment_shift_threshold(db: MongoClient) -> list:
    sentiment_shift = list(db.SentimentShift.find({}))
    for shift in sentiment_shift:
        shift["id"] = str(shift["_id"])
        shift.pop("_id")

    return sentiment_shift


def update_sentiment_shift_threshold(db: MongoClient, threshold_id: str, sm_id: str, alert_type: str, min_val: int, max_val: int) -> dict:
    updated_threshold = {
        "sm_id": sm_id,
        "alert_type": alert_type,
        "min_val": min_val,
        "max_val": max_val
    }
    
    result = db.SentimentShift.update_one(
        {"_id": ObjectId(threshold_id)},
        {"$set": updated_threshold}
    )
    
    if result.matched_count == 0:
        raise ValueError("Sentiment shift threshold not found or update failed")
    
    result = db.SentimentShift.find_one({"_id": ObjectId(threshold_id)}, {"_id": 0})

    return result


def delete_sentiment_shift_threshold(db: MongoClient, threshold_id: str) -> bool:
    result = db.SentimentShift.delete_one({"_id": ObjectId(threshold_id)})
    if result.deleted_count == 0:
        raise ValueError("Sentiment shift threshold not found or deletion failed")
    return True


# Notification Settings

# Initialize default settings
def initialize_default_settings(db: MongoClient):
    default_notification_settings = {
        "dashboard_notifications": False,
        "email_notifications": False,
        "notification_emails": []
    }

    if db.NotificationSettings.count_documents({}) == 0:
        db.NotificationSettings.insert_one(default_notification_settings)
        
def get_notification_settings(db: MongoClient) -> dict:
    settings = db.NotificationSettings.find_one({})
    if not settings:
        initialize_default_settings(db)
        settings = db.NotificationSettings.find_one({})
    settings["_id"] = str(settings["_id"])
    return settings


def update_notification_settings(db: MongoClient, settings: NotificationSettings) -> dict:
    updated_settings = {
        "dashboard_notifications": settings.dashboard_notifications,
        "email_notifications": settings.email_notifications,
        "notification_emails": settings.notification_emails
    }

    result = db.NotificationSettings.update_one(
        {},
        {"$set": updated_settings},
        upsert=True
    )

    return get_notification_settings(db)