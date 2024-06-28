# app/db/facebook_data.py

from pymongo import MongoClient
from datetime import datetime
from facebook import GraphAPI


from app.models.post_models import Post, Comment, SubComment, CommentSentiment, SubCommentSentiment
from app.services.sentiment_analysis_service import analyze_sentiment


# ------------------ CRON TASKS ------------------

def fetch_and_store_facebook_data(db: MongoClient, graph: GraphAPI):
    posts = graph.get_object('me/posts', fields='id,message,created_time,from,likes.summary(true),comments.summary(true),full_picture,shares,permalink_url,is_popular')

    for post in posts['data']:
        if 'message' and 'full_picture' not in post:
            continue

        post_model = Post(
            fb_post_id=post['id'],
            sm_id='SM01',
            description=post.get('message', None),
            img_url=post.get('full_picture', None),
            author = post['from']['name'] if 'from' in post else None,
            total_likes=post['likes']['summary']['total_count'],
            total_comments=post['comments']['summary']['total_count'],
            total_shares=post['shares']['count'] if 'shares' in post else 0,
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

    return "Data fetched and stored successfully."


def analyze_and_update_comments(db: MongoClient):
    all_comments = db.Comment.find()

    for comment in all_comments:
        if db.commentSentiments.find_one({"comment_id": comment['_id']}) is not None:
            continue
        
        s_score = analyze_sentiment(comment['description'])
        comment_sentiment = CommentSentiment(
            comment_id=comment['_id'],
            s_score=s_score,
            date_calculated=datetime.now()
        )

        db.commentSentiments.insert_one(comment_sentiment.model_dump())
    
    return "Sentiment analysis for comments completed."


def analyze_and_update_subcomments(db: MongoClient):
    all_subcomments = db.SubComment.find()

    for subcomment in all_subcomments:
        if db.subcommentSentiments.find_one({"sub_comment_id": subcomment['_id']}) is not None:
            continue

        s_score = analyze_sentiment(subcomment['description'])
        subcomment_sentiment = SubCommentSentiment(
            sub_comment_id=subcomment['_id'],
            s_score=s_score,
            date_calculated=datetime.now()
        )

        db.subcommentSentiments.insert_one(subcomment_sentiment.model_dump())
    
    return "Sentiment analysis for subcomments completed."