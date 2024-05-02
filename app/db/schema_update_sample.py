from app.models.post_models import FacebookPost, CommentsOfPosts, SubComments
from bson import ObjectId

from pymongo import MongoClient
from datetime import datetime


def get_sub_comments(comment) -> dict:
    return SubComments( 
        id=str(comment['id']),
        sub_comment=str(comment['sub_comment']),
        created_time=str(comment['created_time'])
    )

def get_comments_of_post(comment) -> dict:
    return CommentsOfPosts( 
        id=str(comment['id']),
        comment=str(comment['comment']),
        created_time=str(comment['created_time']),
        likes=int(comment['likes']),
        sub_comments=[get_sub_comments(sub_comment) for sub_comment in comment.get('sub_comments', [])]
    )

def get_post(post) -> dict:
    return FacebookPost(
        id=str(post['id']),
        message=str(post['message']),
        created_time=str(post['created_time']),
        likes=int(post['likes']),
        comments=[get_comments_of_post(comment) for comment in post.get('comments', [])]
    )

def list_posts(posts) -> list:
    return [get_post(post) for post in posts]


def get_keyword_alerts(db: MongoClient) -> dict:
    keyword_alerts_cursor = db.KeywordAlerts.find({}, {'_id':0})
    keyword_alerts = list(keyword_alerts_cursor)
    
    keyword_alerts_with_keywords = []
    
    for alert in keyword_alerts:
        keyword_ids = alert.get('keyword_ids', [])
        object_ids = [ObjectId(id_str) for id_str in keyword_ids]
        
        keywordsAll = list(db.Keywords.find({"_id": {"$in": object_ids}}, { 'keyword': 1 }))
        keywords = [Keyword['keyword'] for Keyword in keywordsAll]
        
        alert['keywords'] = keywords
        alert.pop('keyword_ids')
        
        keyword_alerts_with_keywords.append(alert)
    
    return keyword_alerts_with_keywords

def get_keyword_trend_count(db: MongoClient, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    result = list( db.FilteredKeywordsByDate.find({ "date": {"$gte": start_datetime, "$lte": end_datetime} }) )

    keyword_trend_count = {}
    for keyword in result:
        keyword_name = db.Keywords.find_one({"_id": ObjectId(keyword['keyword_id']['$oid'])}, {"keyword": 1})['keyword']

        if keyword_name in keyword_trend_count:
            keyword_trend_count[keyword_name] += keyword['total_count']
        else:
            keyword_trend_count[keyword_name] = keyword['total_count']

    return keyword_trend_count


def get_highlighted_coments(db: MongoClient, start_date: str, end_date: str):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    highlighted_comments = []

    comment_sentiments = list(db.CommentSentiment.find({
        "data_calculated": {"$gte": start_datetime, "$lte": end_datetime}
    }))

    comment_ids = [comment["comment_id"]["$oid"] for comment in comment_sentiments]
    object_ids = [ObjectId(id_str) for id_str in comment_ids]

    comments = list(db.Comment.find({"_id": {"$in": object_ids}}))

    for comment in comments:
        sentiment = next((s for s in comment_sentiments if ObjectId(s["comment_id"]["$oid"]) == comment["_id"]), None)
        if sentiment:
            highlighted_comments.append({
                "description": comment.get("description", ""),
                "author": comment.get("author", ""),
                "s_score": sentiment["s_score"]
            })

    return highlighted_comments