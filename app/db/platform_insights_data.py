# app/db/platform_insights_data.py

from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime

from app.models.post_models import Post, Comment, SubComment
from app.utils.common import convert_s_score_to_color


def get_platform_insights_data(db: MongoClient, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    total_results = {}

    ############## 0: Keyword Trend Count ##############
    keyword_by_date = list( db.FilteredKeywordsByDate.find({ "date": {"$gte": start_datetime, "$lte": end_datetime} }) )

    keyword_trend_count = {}
    for keyword in keyword_by_date:
        keyword_name = db.Keyword.find_one({"_id": ObjectId(keyword['keyword_id']['$oid'])}, {"keyword": 1})['keyword']
        total_count = keyword['total_count']

        if keyword_name in keyword_trend_count:
            keyword_trend_count[keyword_name] += total_count
        else:
            keyword_trend_count[keyword_name] = total_count

    total_results['0'] = keyword_trend_count


    ############## 1: Get total reactions of posts ##############

    posts_by_date = list( db.Post.find({ "date": {"$gte": start_datetime, "$lte": end_datetime} }) )

    total_reactions = {}
    for post in posts_by_date:
        date = post['date']
        total_likes = post['total_likes']

        if date in total_reactions:
            total_reactions[date] += total_likes
        else:
            total_reactions[date] = total_likes

    total_results['1'] = total_reactions


    ############## 2: Get total comments of posts ##############

    total_comments = {}
    for post in posts_by_date:
        date = post['date']
        comments_count = post['total_comments']

        if date in total_comments:
            total_comments[date] += comments_count
        else:
            total_comments[date] = comments_count

    total_results['2'] = total_comments


    ############## 3: Get Highlighted comments ##############
    
    highlighted_comments = []

    comment_sentiments = list(db.CommentSentiment.find({
        "date_calculated": {"$gte": start_datetime, "$lte": end_datetime}
    }))

    comment_ids = [comment["comment_id"]["$oid"] for comment in comment_sentiments]
    object_ids = [ObjectId(id_str) for id_str in comment_ids]

    comments = list(db.Comment.find({"_id": {"$in": object_ids}}))

    for comment in comments:
        sentiment = next((s for s in comment_sentiments if ObjectId(s["comment_id"]["$oid"]) == comment["_id"]), None)
        if sentiment and (sentiment["s_score"] > 0.7 or sentiment["s_score"] < -0.7):
            highlighted_comments.append({
                "description": comment.get("description", ""),
                "author": comment.get("author", ""),
                "date": comment["date"].strftime("%Y-%m-%d"),
                "comment_url": comment["comment_url"],
                "s_score": sentiment["s_score"],
                "color": convert_s_score_to_color(sentiment["s_score"])
            })

    total_results['3'] = highlighted_comments


    ############## 4: Get average sentiment score of comments and reacts ##############

    post_sentiments = list( db.PostSentiment.find({ "date_calculated": {"$gte": start_datetime, "$lte": end_datetime} }) )
    comment_sentiments = list( db.CommentSentiment.find({ "date_calculated": {"$gte": start_datetime, "$lte": end_datetime} }) )

    post_sentiment_scores = {}
    for sentiment in post_sentiments:
        date = sentiment['date_calculated'].strftime("%Y-%m-%d")
        s_score = sentiment['s_score']

        if date in post_sentiment_scores:
            post_sentiment_scores[date] += s_score
        else:
            post_sentiment_scores[date] = s_score

    comment_sentiment_scores = {}
    for sentiment in comment_sentiments:
        date = sentiment['date_calculated'].strftime("%Y-%m-%d")
        s_score = sentiment['s_score']

        if date in comment_sentiment_scores:
            comment_sentiment_scores[date] += s_score
        else:
            comment_sentiment_scores[date] = s_score

    total_results['4'] = {
        'post_sentiment_scores': post_sentiment_scores,
        'comment_sentiment_scores': comment_sentiment_scores
    }

    return total_results




# ------------------ CRON TASKS ------------------