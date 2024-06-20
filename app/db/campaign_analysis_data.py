#app/db/campaign_analysis_data.py

from datetime import datetime
from typing import List
from collections import defaultdict 
from bson import ObjectId
from pymongo import MongoClient
from app.models.post_models import Campaign, PostOverviewByDate
from fastapi import HTTPException


comment_sentiment_threshold = 0.7
sub_comment_sentiment_threshold = 0.4


def create_campaign(db: MongoClient, post_id: str) -> str:
    post_id = ObjectId(post_id)

    comments = list(db.Comment.find({"post_id": post_id}))
    comment_ids = [comment["_id"] for comment in comments]

    comment_sentiments = list(db.CommentSentiment.find({"comment_id": {"$in": comment_ids}}))


    sub_comments = list(db.SubComment.find({"comment_id": {"$in": comment_ids}}))
    sub_comment_ids = [sub_comment["_id"] for sub_comment in sub_comments]

    sub_comment_sentiments = list(db.SubCommentSentiment.find({"sub_comment_id": {"$in": sub_comment_ids}}))


    sentiment_by_date = defaultdict(list)

    for comment in comments:
        comment_id = comment["_id"]
        comment_date = comment["date"].date()
        sentiment = next((cs["s_score"] for cs in comment_sentiments if cs["comment_id"] == comment_id), 0)
        sentiment_by_date[comment_date].append(sentiment * comment_sentiment_threshold)

    for sub_comment in sub_comments:
        sub_comment_id = sub_comment["_id"]
        sub_comment_date = sub_comment["date"].date()
        sentiment = next((scs["s_score"] for scs in sub_comment_sentiments if scs["sub_comment_id"] == sub_comment_id), 0)
        sentiment_by_date[sub_comment_date].append(sentiment * sub_comment_sentiment_threshold)


    avg_sentiment_by_date = {}
    for date, sentiments in sentiment_by_date.items():
        avg_sentiment_by_date[date] = sum(sentiments) / len(sentiments)


    sorted_dates = sorted(avg_sentiment_by_date.keys())
    s_score_arr = [avg_sentiment_by_date[date] for date in sorted_dates]


    campaign = Campaign(post_id=post_id, s_score_arr=s_score_arr)
    db.Campaign.insert_one(campaign.dict())
    return "Campaign created successfully"



def calculate_post_overview_by_date(db: MongoClient, post_id: str) -> str:
    post_id = ObjectId(post_id)

    post = db.Post.find_one({"_id": post_id})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    current_date = datetime.now()

    post_overview = PostOverviewByDate(
        post_id=post_id,
        date=current_date,
        total_likes=post.get("total_likes", 0),
        total_comments=post.get("total_comments", 0)
    )

    db.PostOverviewByDate.insert_one(post_overview.dict())
    
    return "Post overview by date calculated and added successfully"



def calculate_post_overview_by_date_all(db: MongoClient) -> str:
    posts = list(db.Post.find({}))

    for post in posts:
        post_id = post["_id"]

        total_likes = post["total_likes"]
        total_comments = post["total_comments"]

        post_overview = PostOverviewByDate(
            post_id=post_id,
            date=datetime.now(),
            total_likes=total_likes,
            total_comments=total_comments
        )

        db.PostOverviewByDate.insert_one(post_overview.dict())

    return "Post overviews by date calculated successfully"


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
