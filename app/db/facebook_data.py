# app/db/facebook_data.py

from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from facebook import GraphAPI

from app.models.post_models import Post, Comment, SubComment
from app.utils.common import convert_s_score_to_color


def fetch_and_store_facebook_data(db: MongoClient, graph: GraphAPI):
    posts = graph.get_object('me/posts', fields='id,message,created_time,from,likes.summary(true),comments.summary(true),full_picture,shares,permalink_url,is_popular')

    for post in posts['data']:
        if 'message' and 'full_picture' not in post:
            continue

        post_model = Post(
            fb_post_id=post['id'],
            description=post.get('message', None),
            img_url=post.get('full_picture', None),
            author = post['from']['name'] if 'from' in post else None,
            total_likes=post['likes']['summary']['total_count'],
            total_comments=post['comments']['summary']['total_count'],
            total_shares=post.get('shares', 0),
            date=datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
            is_popular=post['is_popular'],
            post_url=post['permalink_url']
        )

        # https://developers.facebook.com/docs/graph-api/reference/post/
        # me/tagged?fields=id,from,message,target,permalink_url,created_time

        if db.Post.find_one({"fb_post_id": post['id']}) is None:
            db.Post.insert_one(post_model.model_dump())
        db_post_id = db.Post.find_one({"fb_post_id": post['id']})['_id']

        comments = graph.get_object(f"{post['id']}/comments", fields='id,message,created_time,from,likes.summary(true),comments.summary(true),permalink_url')

        for comment in comments['data']:
            if 'message' not in comment:
                continue

            comment_model = Comment(
                fb_comment_id=comment['id'],
                post_id=db_post_id,
                description=comment['message'],
                author = comment['from']['name'] if 'from' in comment else None,
                total_likes=comment['likes']['summary']['total_count'],
                date=datetime.strptime(comment['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                comment_url=comment['permalink_url']
            )

            if db.Comment.find_one({"fb_comment_id": comment['id']}) is None:
                db.Comment.insert_one(comment_model.model_dump())
            db_comment_id = db.Comment.find_one({"fb_comment_id": comment['id']})['_id']

            for sub_comment in comment['comments']['data']:
                if 'message' not in sub_comment:
                    continue

                sub_comment_model = SubComment(
                    comment_id=db_comment_id,
                    description=sub_comment['message'],
                    author = sub_comment['from']['name'] if 'from' in sub_comment else None,
                    date=datetime.strptime(sub_comment['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                )
                
                if db.SubComment.find_one({"comment_id": db_comment_id, "description": sub_comment['message']}) is None:
                    db.SubComment.insert_one(sub_comment_model.model_dump())


# {"insert": "Keywords", "documents": [{"sm_id": "SM01", "author": "Dummy Author 1", "keyword": "Dummy Keyword 1"}, {"sm_id": "SM01", "author": "Dummy Author 2", "keyword": "Dummy Keyword 2"}, {"sm_id": "SM01", "author": "Dummy Author 3", "keyword": "Dummy Keyword 3"}, {"sm_id": "SM01", "author": "Dummy Author 4", "keyword": "Dummy Keyword 4"}, {"sm_id": "SM01", "author": "Dummy Author 5", "keyword": "Dummy Keyword 5"}]}
# {"insert": "KeywordAlerts", "documents": [{"keyword_ids": ["661b851282246fcaaab579d4"], "author": "Dummy Author 1", "min_val": 20, "max_val": 50, "alert_type": "Email"}, {"keyword_ids": ["661b851282246fcaaab579d5", "661b851282246fcaaab579d4"], "author": "Dummy Author 2", "min_val": 10, "max_val": 30, "alert_type": "App"}, {"keyword_ids": ["661b851282246fcaaab579d6"], "author": "Dummy Author 3", "min_val": 40, "max_val": 60, "alert_type": "Email"}, {"keyword_ids": ["661b851282246fcaaab579d7"], "author": "Dummy Author 4", "min_val": 5, "max_val": 25, "alert_type": "App"}, {"keyword_ids": ["661b851282246fcaaab579d8", "661b851282246fcaaab579d6", "661b851282246fcaaab579d7"], "author": "Dummy Author 5", "min_val": 35, "max_val": 70, "alert_type": "Email"}]}
