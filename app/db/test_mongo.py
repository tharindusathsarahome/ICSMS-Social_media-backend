from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["icsms_backend"]




start_datetime = datetime.strptime("2021-01-20", "%Y-%m-%d")
end_datetime = datetime.strptime("2021-01-30", "%Y-%m-%d")


highlighted_comments = []

# Query CommentSentiment collection
comment_sentiments = list(db.CommentSentiment.find({
    "data_calculated": {"$gte": start_datetime, "$lte": end_datetime}
}))

# Extract comment_ids
comment_ids = [comment["comment_id"]["$oid"] for comment in comment_sentiments]
object_ids = [ObjectId(id_str) for id_str in comment_ids]

# Query Comment collection with filtered comment_ids
comments = list(db.Comment.find({"_id": {"$in": object_ids}}))



# Merge CommentSentiment and Comment data
for comment in comments:
    sentiment = next((s for s in comment_sentiments if ObjectId(s["comment_id"]["$oid"]) == comment["_id"]), None)
    if sentiment:
        highlighted_comments.append({
            "description": comment.get("description", ""),
            "author": comment.get("author", ""),
            "s_score": sentiment["s_score"]
        })

print(highlighted_comments)