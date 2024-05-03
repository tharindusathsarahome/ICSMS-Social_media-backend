from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["icsms_backend"]




start_datetime = datetime.strptime("2021-01-01", "%Y-%m-%d")
end_datetime = datetime.strptime("2021-01-20", "%Y-%m-%d")

result = list( db.FilteredKeywordsByDate.find({ "date": {"$gte": start_datetime, "$lte": end_datetime} }) )

# get total count of each keyword according to date. add total_count for each keyword
keyword_trend_count = {}
for keyword in result:
    # get keyword name from Keywords collection according to keyword_id
    keyword_name = db.Keywords.find_one({"_id": ObjectId(keyword['keyword_id']['$oid'])}, {"keyword": 1})['keyword']

    if keyword_name in keyword_trend_count:
        keyword_trend_count[keyword_name] += keyword['total_count']
    else:
        keyword_trend_count[keyword_name] = keyword['total_count']

# make 2 lists for keys and values of keyword_trend_count
keys = list(keyword_trend_count.keys())
values = list(keyword_trend_count.values())


print({"keys": keys, "values": values})