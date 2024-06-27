# app/db/settings_data.py

from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime

from app.models.post_models import Post, Comment, SubComment
from app.utils.common import convert_s_score_to_color

def get_keyword_alerts(db: MongoClient) -> dict:
    keyword_alerts_cursor = db.KeywordAlert.find({}, {'_id':0})
    keyword_alerts = list(keyword_alerts_cursor)
    
    keyword_alerts_with_keywords = []
    
    for alert in keyword_alerts:
        keyword_ids = alert.get("keyword_ids", [])
        object_ids = [ObjectId(id_str) for id_str in keyword_ids]
        
        keywordsAll = list(db.Keyword.find({"_id": {"$in": object_ids}}, { 'keyword': 1 }))
        keywords = [Keyword['keyword'] for Keyword in keywordsAll]
        
        alert['keywords'] = keywords
        alert.pop('keyword_ids')
        
        keyword_alerts_with_keywords.append(alert)
    
    return keyword_alerts_with_keywords


def get_sentiment_shift(db: MongoClient) -> list:
    sentiment_shift_cursor = db.SentimentShifts.find({}, {"_id": 0, "author": 0})
    sentiment_shift = list(sentiment_shift_cursor)
    for shift in sentiment_shift:
        social_media = db.SocialMedia.find_one(
            {"sm_id": shift["sm_id"]}, {"_id": 0, "name": 1}
        )
        shift["platform"] = social_media["name"]
        shift.pop("sm_id")

    return {0: sentiment_shift} if sentiment_shift else {0: []}

#settings-campaigns
def add_campaign(db: MongoClient, platform: str, post_title: str, company: str) -> dict:
    existing_campaign = db.Campaign.find_one({
        "platform": platform,
        "post_title": post_title,
        "company": company
    })
    
    if existing_campaign:
        raise ValueError("Campaign already exists")
    
    new_campaign = {
        "platform": platform,
        "post_title": post_title,
    }
    
    db.Campaign.insert_one(new_campaign)
    return new_campaign

def get_campaign_by_id(db: MongoClient, campaign_id: str) -> dict:
    campaign = db.Campaign.find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        raise ValueError("Campaign not found")
    return campaign

def update_campaign(db: MongoClient, campaign_id: str, platform: str, post_title: str, company: str) -> dict:
    existing_campaign = db.Campaign.find_one({
        "platform": platform,
        "post_title": post_title,
        "company": company,
        "_id": {"$ne": ObjectId(campaign_id)}
    })
    
    if existing_campaign:
        raise ValueError("Another campaign with the same details already exists")
    
    updated_campaign = {
        "platform": platform,
        "post_title": post_title,
        "company": company
    }
    
    result = db.Campaign.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": updated_campaign}
    )
    
    if result.matched_count == 0:
        raise ValueError("Campaign not found or update failed")
    
    return db.Campaign.find_one({"_id": ObjectId(campaign_id)})


def delete_campaign(db: MongoClient, campaign_id: str) -> bool:
    result = db.Campaign.delete_one({"_id": ObjectId(campaign_id)})
    if result.deleted_count == 0:
        raise ValueError("Campaign not found or deletion failed")
    return True

#settings-alerts
def add_topic_alert(db: MongoClient, topic: str, alert_type: str, min_val: int, max_val: int) -> dict:
    # Find the topic_id using the topic
    identified_topic = db.IdentifiedTopics.find_one({"topic": topic}, {"_id": 1})
    if not identified_topic:
        raise ValueError("Topic not found")
    
    topic_id = str(identified_topic["_id"])
    

    existing_alert = db.TopicAlert.find_one({
        "IdentifiedTopics_topic_id": topic_id,
        "alert_type": alert_type
    })
    
    if existing_alert:
        raise ValueError("Topic alert with the same topic and alert type already exists")
    

    new_alert = {
        "IdentifiedTopics_topic_id": topic_id,
        "alert_type": alert_type,
        "min_val": min_val,
        "max_val": max_val
    }
    
    db.TopicAlert.insert_one(new_alert)
    return new_alert

def get_topic_alert_by_id(db: MongoClient, alert_id: str) -> dict:
    alert = db.TopicAlert.find_one({"_id": ObjectId(alert_id)})
    if not alert:
        raise ValueError("Topic alert not found")
    return alert

def update_topic_alert(db: MongoClient, alert_id: str, topic: str, alert_type: str, min_val: int, max_val: int) -> dict:
    # Find the topic_id using the topic
    identified_topic = db.IdentifiedTopics.find_one({"topic": topic}, {"_id": 1})
    if not identified_topic:
        raise ValueError("Topic not found")
    
    topic_id = str(identified_topic["_id"])
    
    # Check for existing topic alerts with different IDs
    existing_alert = db.TopicAlert.find_one({
        "IdentifiedTopics_topic_id": topic_id,
        "alert_type": alert_type,
        "_id": {"$ne": ObjectId(alert_id)}
    })
    
    if existing_alert:
        raise ValueError("Another topic alert with the same topic and alert type already exists")

    updated_alert = {
        "IdentifiedTopics_topic_id": topic_id,
        "alert_type": alert_type,
        "min_val": min_val,
        "max_val": max_val
    }
    
    result = db.TopicAlert.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": updated_alert}
    )
    
    if result.matched_count == 0:
        raise ValueError("Topic alert not found or update failed")
    
    return db.TopicAlert.find_one({"_id": ObjectId(alert_id)})

def delete_topic_alert(db: MongoClient, alert_id: str) -> bool:
    result = db.TopicAlert.delete_one({"_id": ObjectId(alert_id)})
    if result.deleted_count == 0:
        raise ValueError("Topic alert not found or deletion failed")
    return True

#settings-sentiment shift thresholds
def add_sentiment_shift_threshold(db: MongoClient, sm_id: str, alert_type: str, min_val: int = None, max_val: int = None) -> dict:

    existing_threshold = db.SentimentShift.find_one({
        "SocialMedia_sm_id": sm_id,
        "alert_type": alert_type
    })
    
    if existing_threshold:
        if min_val is None or max_val is None:
            raise ValueError("Sentiment shift threshold with the same platform and alert type already exists")
        return existing_threshold
    
   
    new_threshold = {
        "SocialMedia_sm_id": sm_id,
        "alert_type": alert_type,
        "min_val": min_val,
        "max_val": max_val
    }
    
    db.SentimentShift.insert_one(new_threshold)
    return new_threshold

def get_sentiment_shift_threshold_by_id(db: MongoClient, threshold_id: str) -> dict:
    threshold = db.SentimentShift.find_one({"_id": ObjectId(threshold_id)})
    if not threshold:
        raise ValueError("Sentiment shift threshold not found")
    return threshold


def update_sentiment_shift_threshold(db: MongoClient, threshold_id: str, sm_id: str, alert_type: str, min_val: int, max_val: int) -> dict:
    # Check for existing sentiment shift thresholds with different IDs
    existing_threshold = db.SentimentShift.find_one({
        "SocialMedia_sm_id": sm_id,
        "alert_type": alert_type,
        "_id": {"$ne": ObjectId(threshold_id)}
    })
    
    if existing_threshold:
        raise ValueError("Another sentiment shift threshold with the same platform and alert type already exists")
    

    updated_threshold = {
        "SocialMedia_sm_id": sm_id,
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
    
    return db.SentimentShift.find_one({"_id": ObjectId(threshold_id)})


def delete_sentiment_shift_threshold(db: MongoClient, threshold_id: str) -> bool:
    result = db.SentimentShift.delete_one({"_id": ObjectId(threshold_id)})
    if result.deleted_count == 0:
        raise ValueError("Sentiment shift threshold not found or deletion failed")
    return True