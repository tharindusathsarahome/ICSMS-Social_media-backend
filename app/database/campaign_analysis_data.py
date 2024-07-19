#app/db/campaign_analysis_data.py

from datetime import datetime, timedelta
from typing import List
from collections import defaultdict 
from bson import ObjectId
from pymongo import MongoClient
from app.schemas.post_schemas import PostOverviewByDate
from app.schemas.campaign_schemas import Campaign
from fastapi import HTTPException
from app.utils.common import convert_s_score_to_color
import re


comment_sentiment_threshold = 0.8
sub_comment_sentiment_threshold = 0.3


def check_adding_campaign(db: MongoClient, platform: str, post_description_part: str) -> dict:
    allPosts = list(db.Post.find({"sm_id": platform}, {"_id": 1, "description": 1}))

    for post in allPosts:
        if post["description"]:
            if re.search(post_description_part, post["description"]):
                post_id = post["_id"]

                if db.Campaign.find_one({"post_id": post_id}) is not None:
                    raise ValueError("Post description part already exists in another campaign")
                else:
                    return create_campaign(db, post_id)
    
    raise ValueError("Post not found")


def create_campaign(db: MongoClient, post_id: ObjectId) -> str:

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
        if sentiment:
            sentiment_by_date[comment_date].append(sentiment * comment_sentiment_threshold)

    for sub_comment in sub_comments:
        sub_comment_id = sub_comment["_id"]
        sub_comment_date = sub_comment["date"].date()
        sentiment = next((scs["s_score"] for scs in sub_comment_sentiments if scs["sub_comment_id"] == sub_comment_id), 0)
        if sentiment:
            sentiment_by_date[comment_date].append(sentiment * sub_comment_sentiment_threshold)


    avg_sentiment_by_date = {}
    for date, sentiments in sentiment_by_date.items():
        avg_sentiment_by_date[date] = sum(sentiments) / len(sentiments)


    sorted_dates = sorted(avg_sentiment_by_date.keys())
    s_score_arr = [avg_sentiment_by_date[date] for date in sorted_dates]


    campaign = Campaign(post_id=post_id, s_score_arr=s_score_arr)
    result = db.Campaign.insert_one(campaign.dict())
    return {"id": str(result.inserted_id)}


def get_campaign_analysis_details(db: MongoClient, platform: str) -> dict:
    posts = db.Post.find({"sm_id": platform})
    post_ids = [post["_id"] for post in posts]

    campaigns = db.Campaign.find({"post_id": {"$in": post_ids}})

    campaign_details = []
    
    for campaign in campaigns:
        post_id = campaign['post_id']
        
        post_details = db.Post.find_one({'_id': post_id})
        
        post_overviews = list(db.PostOverviewByDate.find({'post_id': post_id}))
        
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
            "campaign_id": str(campaign.get("_id")),
            "total_likes": post_details.get("total_likes"),
            "total_comments": post_details.get("total_comments"),
            "like_increment": like_increment,
            "comment_increment": comment_increment,
            "company": post_details.get("author"),
            "img_url": post_details.get("img_url"),
            "s_score_arr": campaign.get("s_score_arr"),
            "color": convert_s_score_to_color(campaign.get("s_score_arr")[-1]),
            "description": post_details.get("description"),
            "social_media": post_details.get("sm_id"),
            "post_url": post_details.get("post_url")
        })
    
    return campaign_details



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

    return "Post overview calculated successfully."


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