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
    keyword_trend_count = {}

    pipeline = [
        {
            "$match": {
                "date": {"$gte": start_datetime, "$lte": end_datetime}
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
    comment_sentiment_threshold = 0.7
    sub_comment_sentiment_threshold = 0.3

    comment_sentiments = list(db.commentSentiments.find({ "date_calculated": {"$gte": start_datetime, "$lte": end_datetime} }))

    comments_with_sentiment = []
    for sentiment in comment_sentiments:
        comment_id = sentiment['comment_id']
        comment_sentiment = db.commentSentiments.find_one({"comment_id": comment_id})
        if not comment_sentiment:
            return None

        # sub_comment_sentiments = list(db.subcommentSentiments.find({"comment_id": comment_id}))

        total_sentiment = comment_sentiment['s_score'] * comment_sentiment_threshold
        # for sub_comment_sentiment in sub_comment_sentiments:
        #     total_sentiment += sub_comment_sentiment['s_score'] * sub_comment_sentiment_threshold

        s_score = comment_sentiment['s_score']
        
        if total_sentiment is not None:
            comment = db.Comment.find_one({"_id": sentiment['comment_id']})
            comments_with_sentiment.append({
                "comment_id": str(sentiment['comment_id']),
                "total_sentiment": total_sentiment,
                "description": comment.get("description", ""),
                "author": comment.get("author", ""),
                "date": comment["date"].strftime("%Y-%m-%d"),
                "comment_url": comment["comment_url"],
                "s_score": s_score,
                "color": convert_s_score_to_color(s_score)
            })

    comments_with_sentiment.sort(key=lambda x: x['total_sentiment'], reverse=True)

    highlighted_comments.extend(comments_with_sentiment[:5])
    highlighted_comments.extend(comments_with_sentiment[-5:])


    total_results['3'] = highlighted_comments


    ############## 4: Get average sentiment score of comments and reacts ##############

    comment_sentiments = list( db.commentSentiments.find({ "date_calculated": {"$gte": start_datetime, "$lte": end_datetime} }) )
    subcomment_sentiments = list( db.subcommentSentiments.find({ "date_calculated": {"$gte": start_datetime, "$lte": end_datetime} }) )

    comment_sentiment_scores = {}
    for sentiment in comment_sentiments:
        date = sentiment['date_calculated'].strftime("%Y-%m-%d")
        s_score = sentiment['s_score']

        if date in comment_sentiment_scores:
            comment_sentiment_scores[date] += s_score
        else:
            comment_sentiment_scores[date] = s_score

    subcomment_sentiment_scores = {}
    for sentiment in subcomment_sentiments:
        date = sentiment['date_calculated'].strftime("%Y-%m-%d")
        s_score = sentiment['s_score']

        if date in subcomment_sentiment_scores:
            subcomment_sentiment_scores[date] += s_score
        else:
            subcomment_sentiment_scores[date] = s_score

    total_results['4'] = {
        "comments": comment_sentiment_scores,
        "subcomments": subcomment_sentiment_scores
    }

    return total_results




# ------------------ CRON TASKS ------------------