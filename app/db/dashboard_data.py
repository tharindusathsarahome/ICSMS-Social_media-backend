from pymongo import MongoClient
from datetime import datetime
from fastapi import HTTPException

def get_facebook_analysis_data(db:MongoClient,start_date:str,end_date:str):
    start_datetime = datetime.strptime(start_date,"%Y-%m-%d")
    end_datetime = datetime.strptime(end_date,"%Y-%m-%d")

    posts_by_date = list(db.Post.find({"date":{"$gte":start_datetime,"$lte":end_datetime}}))

    total_results = {}


    total_reactions={}
    for post in posts_by_date:
        date = post['date']
        total_likes = post['total_likes']

        if date in total_reactions:
            total_reactions[date] = total_reactions[date]+total_likes
        else:
            total_reactions[date] = total_likes

    total_results['1'] = total_reactions


    total_comments = {}
    for post in posts_by_date:
        date = post['date']
        comments_count = post['total_comments']

        if date in total_comments:
            total_comments[date] += comments_count
        else:
            total_comments[date] = comments_count

    total_results['2'] = total_comments

    return total_results


def get_products_trend_data(db:MongoClient,start_date:str,end_date:str):
    start_datetime = datetime.strptime(start_date,"%Y-%m-%d")
    end_datetime = datetime.strptime(end_date,"%Y-%m-%d")

    pipeline = [
        {
            "$match": {
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }
        },
        {
            "$group": {
                "_id": "$identified_product",  
                "count": {"$sum": 1}  
            }
        },
        {
            "$sort": {"count": -1}  
        },
        {
            "$project": {
                "_id": 0,  
                "identified_product": "$_id",  # Rename _id to product
                "count": 1  # Include the count field
            }
        }
    ]
    
    result = list(db.IdentifiedProducts.aggregate(pipeline))
    
    return result


def get_keyword_trend_data(db:MongoClient,start_date:str,end_date:str):
    start_datetime = datetime.strptime(start_date,"%Y-%m-%d")
    end_datetime = datetime.strptime(end_date,"%Y-%m-%d")

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
                "identified_keyword": "$_id",  # Rename _id to product
                "count": 1  # Include the count field
            }
        }
    ]
    
    result = list(db.IdentifiedKeywords.aggregate(pipeline))
    print(result)
    
    return result


#overall sentiment_dashboard
def get_setiment_percentage(db:MongoClient):
    negative, neutral, positive = 0, 0, 0
    comment_sentiment_threshold = 0.7
    sub_comment_sentiment_threshold = 0.4

    cursor_Comments = db.commentSentiments.find({}, {"s_score": 1})
    
    for doc in cursor_Comments:
        sentiment_result = doc['s_score'] * comment_sentiment_threshold
        if sentiment_result <= -0.3:
            negative += 1
        elif sentiment_result < 0.3:
            neutral += 1
        else:
            positive += 1

    cursor_sub_comments = db.subcommentSentiments.find({}, {"s_score": 1})

    for doc in cursor_sub_comments:
        sentiment_result = doc['s_score'] * sub_comment_sentiment_threshold
        if sentiment_result <= -0.3:
            negative += 1
        elif sentiment_result < 0.3:
            neutral += 1
        else:
            positive += 1

    total_count = negative+neutral+positive

    negative_percent = (negative/total_count)*100
    neutral_percent = (neutral/total_count)*100
    positive_percent = (positive/ total_count)*100

    chart_data ={
        "labels":['Negative','Neutral', 'Positive'],
        "percentage":[negative_percent,neutral_percent,positive_percent]
    }
    
    return chart_data
