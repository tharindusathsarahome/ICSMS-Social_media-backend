from app.models.post_models import FacebookPost, CommentsOfPosts, SubComments
from bson import ObjectId

from pymongo import MongoClient


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
    
    keyword_alerts_with_keywords = {0:[]}
    
    for alert in keyword_alerts:
        keyword_ids = alert.get('keyword_ids', [])
        object_ids = [ObjectId(id_str) for id_str in keyword_ids]
        
        keywordsAll = list(db.Keywords.find({"_id": {"$in": object_ids}}, { 'keyword': 1 }))
        keywords = [Keyword['keyword'] for Keyword in keywordsAll]
        
        alert['keywords'] = keywords
        alert.pop('keyword_ids')
        
        keyword_alerts_with_keywords[0].append(alert)
    
    return keyword_alerts_with_keywords

# {"insert": "Keywords", "documents": [{"sm_id": "SM01", "author": "Dummy Author 1", "keyword": "Dummy Keyword 1"}, {"sm_id": "SM01", "author": "Dummy Author 2", "keyword": "Dummy Keyword 2"}, {"sm_id": "SM01", "author": "Dummy Author 3", "keyword": "Dummy Keyword 3"}, {"sm_id": "SM01", "author": "Dummy Author 4", "keyword": "Dummy Keyword 4"}, {"sm_id": "SM01", "author": "Dummy Author 5", "keyword": "Dummy Keyword 5"}]}
# {"insert": "KeywordAlerts", "documents": [{"keyword_ids": ["661b851282246fcaaab579d4"], "author": "Dummy Author 1", "min_val": 20, "max_val": 50, "alert_type": "Email"}, {"keyword_ids": ["661b851282246fcaaab579d5", "661b851282246fcaaab579d4"], "author": "Dummy Author 2", "min_val": 10, "max_val": 30, "alert_type": "App"}, {"keyword_ids": ["661b851282246fcaaab579d6"], "author": "Dummy Author 3", "min_val": 40, "max_val": 60, "alert_type": "Email"}, {"keyword_ids": ["661b851282246fcaaab579d7"], "author": "Dummy Author 4", "min_val": 5, "max_val": 25, "alert_type": "App"}, {"keyword_ids": ["661b851282246fcaaab579d8", "661b851282246fcaaab579d6", "661b851282246fcaaab579d7"], "author": "Dummy Author 5", "min_val": 35, "max_val": 70, "alert_type": "Email"}]}
