#app/db/campaign_analysis_data.py

from datetime import datetime
from typing import List
from collections import defaultdict 
from bson import ObjectId
from pymongo import MongoClient
from app.models.post_models import PostOverviewByDate
from app.models.campaign_models import Campaign
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



def get_created_campaign(db: MongoClient) -> dict:
    pipeline = [
        {
            "$lookup": {
                "from": "Post",
                "localField": "post_id",
                "foreignField": "_id",
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
                "s_score_arr": "$s_score_arr[-1]",
                "social_media": "$sm_id"
            }
        }
    ]
    campaign_details = list(db.Campaign.aggregate(pipeline))

    campaigns_by_sm = defaultdict(list)
    for campaign in campaign_details:
        campaigns_by_sm[campaign["social_media"]].append(campaign)

    return campaigns_by_sm



def get_campaign_analysis_details(db: MongoClient) -> dict:
    campaign_analysis_collection = db.Campaign
    post_collection = db.Post
    post_overview_collection = db.PostOverviewByDate
    
    campaigns = list(campaign_analysis_collection.find())
    
    campaign_details = []
    
    for campaign in campaigns:
        post_id = campaign['post_id']
        
        post_details = post_collection.find_one({'_id': post_id})
        
        post_overviews = list(post_overview_collection.find({'post_id': post_id}))
        
        now = datetime.now()
        last_7_days = [overview for overview in post_overviews if overview['date'] >= now - timedelta(days=7)]
        previous_7_14_days = [overview for overview in post_overviews if now - timedelta(days=14) <= overview['date'] < now - timedelta(days=7)]
        
        likes_last_7_days = sum(overview['total_likes'] for overview in last_7_days)
        likes_previous_7_14_days = sum(overview['total_likes'] for overview in previous_7_14_days)
        
        comments_last_7_days = sum(overview['total_comments'] for overview in last_7_days)
        comments_previous_7_14_days = sum(overview['total_comments'] for overview in previous_7_14_days)
        
        like_increment = likes_last_7_days - likes_previous_7_14_days
        comment_increment = comments_last_7_days - comments_previous_7_14_days
        
        campaign_details.append({
            "campaign_id": campaign.get("campaign_id"),
            "total_likes": post_details.get("total_likes"),
            "total_comments": post_details.get("total_comments"),
            "like_increment": like_increment,
            "comment_increment": comment_increment,
            "title": post_details.get("title"),
            "company": post_details.get("author"),
            "img_url": post_details.get("img_url"),
            "s_score_arr": campaign.get("s_score_arr"),
            "description": post_details.get("description"),
            "social_media": post_details.get("sm_id")
        })
    
    campaigns_analysis_by_sm = defaultdict(list)
    for campaign in campaign_details:
        campaigns_analysis_by_sm[campaign["social_media"]].append(campaign)
    
    return dict(campaigns_analysis_by_sm)


# def get_campaign_analysis_details(db: MongoClient) -> dict:
#     campaign_analysis_collection = db.Campaign
#     pipeline = [
#         {
#             "$lookup": {
#                 "from": "Post",
#                 "localField": "post_id",
#                 "foreignField": "_id",
#                 "as": "postDetails"
#             }
#         },
#         {
#             "$lookup": {
#                 "from": "PostOverviewByDate",
#                 "localField": "post_id",
#                 "foreignField": "post_id",
#                 "as": "postOverview"
#             }
#         },
#         {
#             "$unwind": "$postDetails"
#         },
#         {
#             "$addFields": {
#                 "last_7_days": {
#                     "$filter": {
#                         "input": "$postOverview",
#                         "as": "overview",
#                         "cond": {
#                             "$gte": ["$$overview.date", {"$dateSubtract": {"startDate": "$$NOW", "unit": "day", "amount": 7}}]
#                         }
#                     }
#                 },
#                 "previous_7_14_days": {
#                     "$filter": {
#                         "input": "$postOverview",
#                         "as": "overview",
#                         "cond": {
#                             "$and": [
#                                 {"$lt": ["$$overview.date", {"$dateSubtract": {"startDate": "$$NOW", "unit": "day", "amount": 7}}]},
#                                 {"$gte": ["$$overview.date", {"$dateSubtract": {"startDate": "$$NOW", "unit": "day", "amount": 14}}]}
#                             ]
#                         }
#                     }
#                 }
#             }
#         },
#         {
#             "$addFields": {
#                 "likes_last_7_days": {"$sum": "$last_7_days.total_likes"},
#                 "likes_previous_7_14_days": {"$sum": "$previous_7_14_days.total_likes"},
#                 "comments_last_7_days": {"$sum": "$last_7_days.total_comments"},
#                 "comments_previous_7_14_days": {"$sum": "$previous_7_14_days.total_comments"}
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,
#                 "campaign_id": "$campaign_id",
#                 "total_likes": "$postDetails.total_likes",
#                 "total_comments": "$postDetails.total_comments",
#                 "like_increment": {
#                     "$subtract": [
#                         "$likes_last_7_days",
#                         "$likes_previous_7_14_days"
#                     ]
#                 },
#                 "comment_increment": {
#                     "$subtract": [
#                         "$comments_last_7_days",
#                         "$comments_previous_7_14_days"
#                     ]
#                 },
#                 "title": "$postDetails.title",
#                 "company": "$postDetails.author",
#                 "img_url": "$postDetails.img_url",
#                 "s_score_arr": "$s_score_arr",
#                 "description": "$postDetails.description",
#                 "social_media": "$postDetails.sm_id"
#             }
#         }
#     ]

#     campaign_analysis_details = list(campaign_analysis_collection.aggregate(pipeline))

#     campaigns_analysis_by_sm = defaultdict(list)
#     for campaign in campaign_analysis_details:
#         campaigns_analysis_by_sm[campaign["social_media"]].append(campaign)

#     return dict(campaigns_analysis_by_sm)



def delete_campaign(db: MongoClient, campaign_id: str) -> dict:
    try:
        campaign_obj_id = ObjectId(campaign_id)
        
        result = db.Campaign.delete_one({"_id": campaign_obj_id})
        
        if result.deleted_count == 1:
            return {"status": "success", "message": "Campaign deleted successfully."}
        else:
            return {"status": "failure", "message": "Campaign not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}



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




# ------------------ CRON TASKS ------------------


def calculate_post_overview_by_date(db: MongoClient) -> str:
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

    print("Post overview calculated successfully.")


def update_campaigns(db: MongoClient) -> str:
    campaigns = list(db.Campaign.find({}))

    for campaign in campaigns:
        post_id = campaign["post_id"]

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

        newCampaign = Campaign(post_id=post_id, s_score_arr=s_score_arr)

        db.Campaign.update_one({"_id": campaign["_id"]}, {"$set": newCampaign.dict()})

    return "Campaigns updated successfully"