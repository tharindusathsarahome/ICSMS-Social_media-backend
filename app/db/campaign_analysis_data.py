#app/db/campaign_analysis_data.py

from datetime import datetime
from typing import List
from collections import defaultdict 
from pymongo import MongoClient


def get_campaign_details(db: MongoClient) -> dict:
    campaign_collection = db.Campaign
    pipeline = [
        {
            "$lookup": {
                "from": "Post",
                "localField": "post_id",
                "foreignField": "post_id",
                "as": "postDetails"
            }
        },
        {
            "$unwind": "$postDetails"
        },
        {
            "$project": {
                "_id": 0,
                "campaign_id": "$campaign_id",
                "title": "$postDetails.title",
                "company": "$postDetails.author",
                "min_val": "$min_val",
                "max_val": "$max_val",
                "overall_sentiment": "$overall_score",
                "social_media": "$sm_id"
            }
        }
    ]
    campaign_details = list(campaign_collection.aggregate(pipeline))

    campaigns_by_sm = defaultdict(list)
    for campaign in campaign_details:
        campaigns_by_sm[campaign["social_media"]].append(campaign)

    return campaigns_by_sm


def get_campaign_analysis_details(db: MongoClient) -> dict:
    campaign_analysis_collection = db.Campaign
    pipeline = [
        {
            "$lookup": {
                "from": "Post",
                "localField": "post_id",
                "foreignField": "post_id",
                "as": "postDetails"
            }
        },
        {
            "$unwind": "$postDetails"
        },
        {
            "$project": {
                "_id": 0,
                "campaign_id": "$campaign_id",
                "total_likes": "$postDetails.total_likes",
                "total_comments": "$postDetails.total_comments",
                "title": "$postDetails.title",
                "company": "$postDetails.author",
                "img_url": "$postDetails.img_url",
                "min_val": "$min_val",
                "max_val": "$max_val",
                "overall_sentiment": "$overall_score",
                "description": "$postDetails.description",
                "social_media": "$sm_id"
            }
        }
    ]
    campaign_analysis_details = list(campaign_analysis_collection.aggregate(pipeline))

    campaigns_analysis_by_sm = defaultdict(list)
    for campaign in campaign_analysis_details:
        campaigns_analysis_by_sm[campaign["social_media"]].append(campaign)

    return dict(campaigns_analysis_by_sm)

def get_filtered_keywords_by_date(db: MongoClient, start_date: datetime, end_date: datetime) -> List[dict]:
    filtered_keywords_collection = db.FilteredKeywordsByDate
    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$lookup": {
                "from": "Keyword",
                "localField": "Keywords_keyword_id",
                "foreignField": "keyword_id",
                "as": "keywordDetails"
            }
        },
        {
            "$unwind": "$keywordDetails"
        },
        {
            "$project": {
                "_id": 0,
                "keyword_id": "$Keywords_keyword_id",
                "date": "$date",
                "total_count": "$total_count",
                "keyword": "$keywordDetails.keyword",
                "author": "$keywordDetails.author"
            }
        }
    ]
    filtered_keywords = list(filtered_keywords_collection.aggregate(pipeline))
    return filtered_keywords

def delete_campaign_from_db(campaign_id: str, db: MongoClient) -> dict:
    campaign_collection = db.Campaign
    posts_collection = db.Post

    campaign = campaign_collection.find_one({"campaign_id": campaign_id})
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    post_id = campaign.get("post_id")

    campaign_result = campaign_collection.delete_one({"campaign_id": campaign_id})
    if campaign_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Failed to delete the campaign")

    post_result = posts_collection.delete_one({"post_id": post_id})

    return {
        "status": "success",
        "message": f"Campaign deleted successfully. Related post deleted: {post_result.deleted_count > 0}"
    }