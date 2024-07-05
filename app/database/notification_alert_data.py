from pymongo import MongoClient
from collections import defaultdict
from typing import List, Dict


comment_sentiment_threshold = 0.7
sub_comment_sentiment_threshold = 0.4


def check_product_alerts(db: MongoClient) -> List[Dict]:
    alerts_within_range = []

    product_alerts = list(db.ProductAlert.find({}))

    for product_alert in product_alerts:
        identified_product = db.IdentifiedProducts.find_one({"_id": product_alert['product_id']})
        if not identified_product:
            continue

        sm_id = identified_product["sm_id"]
        post_id = identified_product["post_id"]
        identified_product_name = identified_product["identified_product"]

        post = db.Post.find_one({"_id": post_id})
        if not post:
            continue

        comments = list(db.Comment.find({"post_id": post_id}))
        comment_ids = [comment["_id"] for comment in comments]

        comment_sentiments = list(db.CommentSentiment.find({"comment_id": {"$in": comment_ids}}))

        sub_comments = list(db.SubComment.find({"comment_id": {"$in": comment_ids}}))
        sub_comment_ids = [sub_comment["_id"] for sub_comment in sub_comments]

        sub_comment_sentiments = list(db.SubCommentSentiment.find({"sub_comment_id": {"$in": sub_comment_ids}}))

        sentiment_by_date = defaultdict(list)

        for comment in comments:
            comment_id = comment["_id"]
            comment_date = comment["date"].date()
            sentiment = next((cs["s_score"] for cs in comment_sentiments if cs["comment_id"] == comment_id), 0)
            sentiment_by_date[comment_date].append(sentiment)

        for sub_comment in sub_comments:
            sub_comment_id = sub_comment["_id"]
            sub_comment_date = sub_comment["date"].date()
            sentiment = next((scs["s_score"] for scs in sub_comment_sentiments if scs["sub_comment_id"] == sub_comment_id), 0)
            sentiment_by_date[sub_comment_date].append(sentiment)

        avg_sentiment_by_date = {}
        for date, sentiments in sentiment_by_date.items():
            avg_sentiment_by_date[date] = sum(sentiments) / len(sentiments)

        sorted_dates = sorted(avg_sentiment_by_date.keys())
        s_score_arr = [avg_sentiment_by_date[date] for date in sorted_dates]

        total_sentiment_score = s_score_arr[-1]*10 if s_score_arr else 0

        alert_type = product_alert["alert_type"]
        min_val = product_alert["min_val"]
        max_val = product_alert["max_val"]

        if total_sentiment_score < min_val or max_val < total_sentiment_score:
            alert_info = {
                "identified_product_name": identified_product_name,
                "post_id": post_id,
                "alert_type": alert_type,
                "total_sentiment_score": round(total_sentiment_score,2),
                "alert_range": (min_val, max_val)
            }
            alerts_within_range.append(alert_info)

    return alerts_within_range


def check_sentiment_shifts(db: MongoClient) -> List[Dict]:
    results_within_range = []

    sentiment_shifts = list(db.SentimentShift.find({}))

    sentiment_by_sm_id = defaultdict(list)

    comment_sentiments = list(db.CommentSentiment.find({}))

    for sentiment in comment_sentiments:
        sm_id = sentiment["sm_id"]
        s_score = sentiment["s_score"] * comment_sentiment_threshold
        sentiment_by_sm_id[sm_id].append(s_score)

    sub_comment_sentiments = list(db.SubCommentSentiment.find({}))

    for sentiment in sub_comment_sentiments:
        sm_id = sentiment["sm_id"]
        s_score = sentiment["s_score"] * sub_comment_sentiment_threshold
        sentiment_by_sm_id[sm_id].append(s_score)

    total_sentiment_by_sm_id = {}
    for sm_id, sentiments in sentiment_by_sm_id.items():
        total_sentiment_by_sm_id[sm_id] = sum(sentiments) / len(sentiments)

    for sentiment_shift in sentiment_shifts:
        sm_id = sentiment_shift["sm_id"]
        alert_type = sentiment_shift["alert_type"]
        min_val = sentiment_shift["min_val"]
        max_val = sentiment_shift["max_val"]

        if sm_id in total_sentiment_by_sm_id:
            total_sentiment = total_sentiment_by_sm_id[sm_id]*10

            if total_sentiment < min_val or max_val < total_sentiment:
                alert_info = {
                    "platform": "Facebook" if sm_id == "SM01" else "Instagram",
                    "alert_type": alert_type,
                    "total_sentiment": round(total_sentiment,2),
                    "alert_range": (min_val, max_val)
                }
                results_within_range.append(alert_info)

    return results_within_range




if __name__ == "__main__":
    client = MongoClient("mongodb+srv://team-byte_bridges:backenddb@cluster0.pocr4yq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["icsms-social_media"]
    print(check_product_alerts(db))