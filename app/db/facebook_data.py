# app/db/facebook_data.py

from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from facebook import GraphAPI
from typing import List, Dict


from app.models.post_models import Post, Comment, SubComment
from app.utils.common import convert_s_score_to_color
from app.services.sentiment_analysis_service import analyze_sentiment


# ------------------ CRON TASKS ------------------

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

    print("Data fetched and stored successfully.")




# ------------------ CRON TASKS ------------------

def analyze_and_update_comments(db: MongoClient):
    unread_comments = db.Comment.find({"s_score": {"$exists": False}})

    for comment in unread_comments:
        description = comment['description']
        score = analyze_sentiment(description)
        db.Comment.update_one({"fb_comment_id": comment['comment_id']}, {"$set": {"s_score": score}})
        sentiment_comment_collection = db.sentimentcomments
        sentiment_comment_collection.insert_one({"fb_comment_id": comment['comment_id'], "s_score": score})
    
    print("Sentiment analysis for comments completed.")


def analyze_and_update_subcomments(db: MongoClient):
    unread_subcomments = db.SubComment.find({"s_score": {"$exists": False}})

    for subcomment in unread_subcomments:
        description = subcomment['description']
        score = analyze_sentiment(description)
        db.SubComment.update_one({"comment_id": subcomment['comment_id']}, {"$set": {"s_score": score}})
        sentiment_subcomment_collection = db.sentimentsubcomment
        sentiment_subcomment_collection.insert_one({"comment_id": subcomment['comment_id'], "s_score": score})

    print("Sentiment analysis for subcomments completed.")