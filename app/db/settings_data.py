# app/db/settings_data.py

from bson import ObjectId
from pymongo import MongoClient

from app.models.campaign_models import Campaign
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
    sentiment_shift = list(db.SentimentShifts.find({}, {"_id": 0, "author": 0}))
    for shift in sentiment_shift:
        social_media = db.SocialMedia.find_one(
            {"sm_id": shift["sm_id"]}, {"_id": 0, "name": 1}
        )
        shift["platform"] = social_media["name"]
        shift.pop("sm_id")

    return sentiment_shift


def get_campaign_by_id(db: MongoClient, campaign_id: str) -> dict:
    campaign = db.Campaign.find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        raise ValueError("Campaign not found")
    return campaign


def get_campaigns(db: MongoClient) -> list:
    campaigns = list(db.Campaign.find({}, {"_id": 1, "post_id": 1, "s_score_arr": 1}))
    for campaign in campaigns:
        post = db.Post.find_one({"_id": campaign["post_id"]}, {"_id": 0, "description": 1, "sm_id": 1})
        campaign["description"] = post["description"]
        campaign["platform"] = post["sm_id"]
        campaign["s_score"] = campaign["s_score_arr"][-1]
        campaign["color"] = convert_s_score_to_color(campaign["s_score_arr"][-1])
        campaign["_id"] = str(campaign["_id"])
        campaign.pop("post_id")
        campaign.pop("s_score_arr")
    return campaigns


def delete_campaign(db: MongoClient, campaign_id: str) -> dict:
    try:
        result = db.Campaign.delete_one({"_id": ObjectId(campaign_id)})
        
        if result.deleted_count == 1:
            return {"status": "success", "message": "Campaign deleted successfully."}
        else:
            return {"status": "failure", "message": "Campaign not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ------------------ CRON TASKS ------------------