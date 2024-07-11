# app/db/platform_insights_data.py

import re
from collections import defaultdict
from pymongo import MongoClient
from datetime import datetime

from app.utils.common import convert_s_score_to_color


comment_sentiment_threshold = 0.8
sub_comment_sentiment_threshold = 0.3


def keyword_trend_count(db: MongoClient, platform: str, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    keyword_trend_count = { "products": [], "s_scores": [], "colors": [] }

    CustomProducts = list(db.CustomProducts.find())

    for CustomProduct in CustomProducts:
        productName = CustomProduct["product"]

        identified_products = list(db.IdentifiedProducts.find({
            "sm_id": platform,
            "identified_product": re.compile(CustomProduct["product"], re.IGNORECASE)
        }))
        total_product_sentiments = []

        for identified_product in identified_products:
            post_id = identified_product["post_id"]

            post = db.Post.find_one({"_id": post_id})
            if not post:
                continue

            comments = list(db.Comment.find({"post_id": post_id}))
            comment_ids = [comment["_id"] for comment in comments]

            comment_sentiments = list(db.CommentSentiment.find({"comment_id": {"$in": comment_ids}, "date_calculated": {"$gte": start_datetime, "$lte": end_datetime}}))

            sub_comments = list(db.SubComment.find({"comment_id": {"$in": comment_ids}}))
            sub_comment_ids = [sub_comment["_id"] for sub_comment in sub_comments]

            sub_comment_sentiments = list(db.SubCommentSentiment.find({"sub_comment_id": {"$in": sub_comment_ids}, "date_calculated": {"$gte": start_datetime, "$lte": end_datetime}}))

            sentiment_by_date = defaultdict(list)

            for comment in comments:
                comment_id = comment["_id"]
                comment_date = comment["date"].date()
                sentiment = next((cs["s_score"] for cs in comment_sentiments if cs["comment_id"] == comment_id), None)
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
            
            total_product_sentiments.append(s_score_arr[-1] if len(s_score_arr) > 0 else 0)

        if len(total_product_sentiments) != 0:
            total_sentiment_score = (sum(total_product_sentiments) / len(total_product_sentiments))
            
            keyword_trend_count["products"].append(productName.title())
            keyword_trend_count["s_scores"].append(round(total_sentiment_score * 10, 1))
            keyword_trend_count["colors"].append(convert_s_score_to_color(total_sentiment_score))


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