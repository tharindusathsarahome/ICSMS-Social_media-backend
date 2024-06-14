from typing import List
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
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