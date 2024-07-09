# app/db/facebook_data.py

from pymongo import MongoClient
from datetime import datetime
from facebook import GraphAPI


from app.schemas.post_schemas import Post, Comment, SubComment, CommentSentiment, SubCommentSentiment
from app.services.sentiment_analysis_service import analyze_sentiment



# ------------------ CRON TASKS ------------------

def fetch_and_store_facebook_data(db: MongoClient, graph: GraphAPI):
    posts = graph.get_object('me/posts', fields='id,message,created_time,from,likes.summary(true),comments.summary(true),full_picture,shares,permalink_url,is_popular')

    commentsFetched = 0
    subCommentsFetched = 0

    for post in posts['data']:
        if 'message' and 'full_picture' not in post:
            continue

        post_model = Post(
            sm_post_id=post['id'],
            sm_id='SM01',
            description=post.get('message', None),
            img_url=post.get('full_picture', None),
            author = post['from']['name'] if 'from' in post else None,
            total_likes=post['likes']['summary']['total_count'],
            total_comments=post['comments']['summary']['total_count'],
            total_shares=post['shares']['count'] if 'shares' in post else 0,
            date=datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
            post_url=post['permalink_url']
        )

        if db.Post.find_one({"sm_post_id": post['id']}) is None:
            db.Post.insert_one(post_model.model_dump())
        db_post_id = db.Post.find_one({"sm_post_id": post['id']})['_id']

        comments = graph.get_object(f"{post['id']}/comments", fields='id,message,created_time,from,likes.summary(true),comments.summary(true),permalink_url')

        for comment in comments['data']:
            if 'message' not in comment:
                continue

            comment_model = Comment(
                sm_comment_id=comment['id'],
                post_id=db_post_id,
                description=comment['message'],
                author = comment['from']['name'] if 'from' in comment else None,
                total_likes=comment['likes']['summary']['total_count'],
                date=datetime.strptime(comment['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                comment_url=comment.get('permalink_url', None)
            )

            if db.Comment.find_one({"sm_comment_id": comment['id']}) is None:
                db.Comment.insert_one(comment_model.model_dump())
                commentsFetched += 1
            db_comment_id = db.Comment.find_one({"sm_comment_id": comment['id']})['_id']

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
                    subCommentsFetched += 1

    return f"Data fetched and stored successfully. Comments: {commentsFetched}, Subcomments: {subCommentsFetched}"


def fetch_and_store_instagram_data(db: MongoClient, graph: GraphAPI):
    accounts = graph.get_object('me/accounts', fields='connected_instagram_account')

    commentsFetched = 0
    subCommentsFetched = 0

    for account in accounts['data']:
        if 'connected_instagram_account' not in account:
            continue

        i_acc_id = account['connected_instagram_account']['id']
        posts = graph.get_object(f"{i_acc_id}/media")

        for post in posts['data']:
            post_x_id = post['id']
            post_details = graph.get_object(post_x_id, fields='id,caption,ig_id,media_url,permalink,thumbnail_url,timestamp,username')

            post_insights = graph.get_object(f"{post_x_id}/insights", metric='likes,comments,shares')

            post_model = Post(
                sm_post_id=post_details['id'],
                sm_id='SM02',
                description=post_details.get('caption', None),
                img_url=post_details.get('media_url', None),
                author=post_details.get('username', None),
                total_likes=post_insights['data'][0]['values'][0]['value'],
                total_comments=post_insights['data'][1]['values'][0]['value'],
                total_shares=post_insights['data'][2]['values'][0]['value'],
                date=datetime.strptime(post_details['timestamp'], '%Y-%m-%dT%H:%M:%S%z'),
                post_url=post_details['permalink']
            )

            if db.Post.find_one({"sm_post_id": post_details['id']}) is None:
                db.Post.insert_one(post_model.model_dump())
            db_post_id = db.Post.find_one({"sm_post_id": post_details['id']})['_id']

            comments = graph.get_object(f"{post_x_id}/comments", fields='id,from,like_count,text,timestamp,username,replies')

            for comment in comments['data']:
                comment_model = Comment(
                    sm_comment_id=comment['id'],
                    post_id=db_post_id,
                    description=comment['text'],
                    author=comment.get('username', None),
                    total_likes=comment['like_count'],
                    date=datetime.strptime(comment['timestamp'], '%Y-%m-%dT%H:%M:%S%z'),
                    comment_url=comment.get('permalink', None)
                )

                if db.Comment.find_one({"sm_comment_id": comment['id']}) is None:
                    db.Comment.insert_one(comment_model.model_dump())
                    commentsFetched += 1
                db_comment_id = db.Comment.find_one({"sm_comment_id": comment['id']})['_id']

                if 'replies' in comment:
                    for sub_comment in comment['replies']['data']:
                        sub_comment_model = SubComment(
                            comment_id=db_comment_id,
                            description=sub_comment['text'],
                            author=sub_comment.get('username', None),
                            date=datetime.strptime(sub_comment['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
                        )

                        if db.SubComment.find_one({"comment_id": db_comment_id, "description": sub_comment['text']}) is None:
                            db.SubComment.insert_one(sub_comment_model.model_dump())
                            subCommentsFetched += 1

    return f"Data fetched and stored successfully. Comments: {commentsFetched}, Subcomments: {subCommentsFetched}"


def analyze_and_update_comments(db: MongoClient):
    all_comments = db.Comment.find()

    anylyzed_comments = 0

    for comment in all_comments:
        if db.CommentSentiment.find_one({"comment_id": comment['_id']}) is not None:
            continue

        post = db.Post.find_one({"_id": comment['post_id']})
        if post is None:
            continue

        sm_id = post['sm_id']
        
        s_score = analyze_sentiment(comment['description'])
        comment_sentiment = CommentSentiment(
            comment_id=comment['_id'],
            s_score=s_score,
            sm_id=sm_id,
            date_calculated=datetime.now()
        )

        db.CommentSentiment.insert_one(comment_sentiment.model_dump())
        anylyzed_comments += 1
    
    return f"Sentiment analysis for comments completed. Analyzed: {anylyzed_comments}"


def analyze_and_update_subcomments(db: MongoClient):
    all_subcomments = db.SubComment.find()

    anylyzed_subcomments = 0

    for subcomment in all_subcomments:
        if db.SubCommentSentiment.find_one({"sub_comment_id": subcomment['_id']}) is not None:
            continue

        comment = db.Comment.find_one({"_id": subcomment['comment_id']})
        if comment is None:
            continue

        post = db.Post.find_one({"_id": comment['post_id']})
        if post is None:
            continue

        sm_id = post['sm_id']

        s_score = analyze_sentiment(subcomment['description'])
        subcomment_sentiment = SubCommentSentiment(
            sub_comment_id=subcomment['_id'],
            s_score=s_score,
            sm_id=sm_id,
            date_calculated=datetime.now()
        )

        db.SubCommentSentiment.insert_one(subcomment_sentiment.model_dump())
        anylyzed_subcomments += 1
    
    return f"Sentiment analysis for subcomments completed. Analyzed: {anylyzed_subcomments}"
