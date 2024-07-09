# app/db/platform_insights_data.py

from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime

from app.schemas.post_schemas import Post, Comment, SubComment
from app.utils.common import convert_s_score_to_color


def keyword_trend_count(db: MongoClient, platform: str, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    keyword_trend_count = {}

    pipeline = [
        {
            "$match": {
                "date": {"$gte": start_datetime, "$lte": end_datetime},
                "sm_id": platform
            }
        },
        {
            "$group": {
                "_id": "$identified_keyword",  
                "count": {"$sum": 1}  
            }
        },
        {
            "$sort": {"count": -1}  
        },
        {
            "$project": {
                "_id": 0,  
                "identified_keyword": "$_id",
                "count": 1
            }
        }
    ]

    result = list(db.IdentifiedKeywords.aggregate(pipeline))

    for keyword in result:
        word = keyword['identified_keyword']
        if word[0] == "#":
            word = word[1:]
            word = word.title()
        keyword_trend_count[word] = keyword['count']

    keyword_trend_count = dict(list(keyword_trend_count.items())[:5])

    return keyword_trend_count


def total_reactions(db: MongoClient, platform: str, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    posts_by_date = list( db.Post.find({ "date": {"$gte": start_datetime, "$lte": end_datetime}, "sm_id": platform }) )

    total_reactions = {}
    for post in posts_by_date:
        date = post['date']
        total_likes = post['total_likes']

        if date in total_reactions:
            total_reactions[date] += total_likes
        else:
            total_reactions[date] = total_likes

    return total_reactions


def total_comments(db: MongoClient, platform: str, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    posts_by_date = list( db.Post.find({ "date": {"$gte": start_datetime, "$lte": end_datetime}, "sm_id": platform }) )

    total_comments = {}
    for post in posts_by_date:
        date = post['date']
        comments_count = post['total_comments']

        if date in total_comments:
            total_comments[date] += comments_count
        else:
            total_comments[date] = comments_count

    return total_comments


def highlighted_comments(db: MongoClient, platform: str, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    highlighted_comments = []
    comment_sentiment_threshold = 0.7

    comment_sentiments = list(db.CommentSentiment.find({ "date_calculated": {"$gte": start_datetime, "$lte": end_datetime}, "sm_id": platform }))

    comments_with_sentiment = []
    for comment_sentiment in comment_sentiments:

        total_sentiment = comment_sentiment['s_score'] * comment_sentiment_threshold
        s_score = comment_sentiment['s_score']
        
        if total_sentiment is not None:
            comment = db.Comment.find_one({"_id": comment_sentiment['comment_id']})
            
            if comment["comment_url"] is None:
                url = db.Post.find_one({"_id": comment["post_id"]})["post_url"]
            else:
                url = comment["comment_url"]
                
            comments_with_sentiment.append({
                "comment_id": str(comment_sentiment['comment_id']),
                "total_sentiment": total_sentiment,
                "description": comment.get("description", ""),
                "author": comment.get("author", ""),
                "date": comment["date"].strftime("%Y-%m-%d"),
                "comment_url": url,
                "s_score": s_score,
                "color": convert_s_score_to_color(s_score)
            })

    comments_with_sentiment.sort(key=lambda x: x['total_sentiment'], reverse=True)

    highlighted_comments.extend(comments_with_sentiment[:3])
    highlighted_comments.extend(comments_with_sentiment[-4:])

    return highlighted_comments


def average_sentiment_score(db: MongoClient, platform: str, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    
    comment_sentiments = list(db.CommentSentiment.find({
        "date_calculated": {"$gte": start_datetime, "$lte": end_datetime},
        "sm_id": platform
    }))
    subcomment_sentiments = list(db.SubCommentSentiment.find({
        "date_calculated": {"$gte": start_datetime, "$lte": end_datetime},
        "sm_id": platform
    }))

    comment_sentiment_scores = {}
    comment_counts = {}
    for sentiment in comment_sentiments:
        date = sentiment['date_calculated'].strftime("%Y-%m-%d")
        s_score = sentiment['s_score']
        
        if date in comment_sentiment_scores:
            comment_sentiment_scores[date] += s_score
            comment_counts[date] += 1
        else:
            comment_sentiment_scores[date] = s_score
            comment_counts[date] = 1

    for date in comment_sentiment_scores:
        comment_sentiment_scores[date] /= comment_counts[date]

    subcomment_sentiment_scores = {}
    subcomment_counts = {}
    for sentiment in subcomment_sentiments:
        date = sentiment['date_calculated'].strftime("%Y-%m-%d")
        s_score = sentiment['s_score']
        
        if date in subcomment_sentiment_scores:
            subcomment_sentiment_scores[date] += s_score
            subcomment_counts[date] += 1
        else:
            subcomment_sentiment_scores[date] = s_score
            subcomment_counts[date] = 1

    for date in subcomment_sentiment_scores:
        subcomment_sentiment_scores[date] /= subcomment_counts[date]

    return {
        "comments": comment_sentiment_scores,
        "subcomments": subcomment_sentiment_scores
    }

# ------------------ CRON TASKS ------------------