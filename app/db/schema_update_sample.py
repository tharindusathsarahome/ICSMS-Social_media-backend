# from app.models.post_models import FacebookPost, CommentsOfPosts, SubComments
from bson import ObjectId

from pymongo import MongoClient
from datetime import datetime
from facebook import GraphAPI

from app.models.post_models import Post, Comment, SubComment
from app.utils.common import convert_s_score_to_color

def get_keyword_alerts(db: MongoClient) -> dict:
    keyword_alerts_cursor = db.KeywordAlert.find({}, {'_id':0})
    keyword_alerts = list(keyword_alerts_cursor)
    
    keyword_alerts_with_keywords = []
    
    for alert in keyword_alerts:
        keyword_ids = alert.get("keyword_ids", [])
        object_ids = [ObjectId(id_str) for id_str in keyword_ids]
        
        keywordsAll = list(db.Keyword.find({"_id": {"$in": object_ids}}, { 'keyword': 1 }))
        keywords = [Keyword['keyword'] for Keyword in keywordsAll]
        
        alert['keywords'] = keywords
        alert.pop('keyword_ids')
        
        keyword_alerts_with_keywords.append(alert)
    
    return keyword_alerts_with_keywords



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


# sentiment shift
def get_sentiment_shift(db: MongoClient) -> list:
    sentiment_shift_cursor = db.SentimentShifts.find({}, {"_id": 0, "author": 0})
    sentiment_shift = list(sentiment_shift_cursor)
    for shift in sentiment_shift:
        social_media = db.SocialMedia.find_one(
            {"sm_id": shift["sm_id"]}, {"_id": 0, "name": 1}
        )
        shift["platform"] = social_media["name"]
        shift.pop("sm_id")

    return sentiment_shift
