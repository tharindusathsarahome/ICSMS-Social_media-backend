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


# ------------------ CRON TASKS ------------------