from typing import List
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
from app.schemas.product_keyword_schemas import CustomProducts, IdentifiedProducts, IdentifiedKeywords
from app.services.products_keywords_service import identify_products,identify_keywords
from fastapi import HTTPException



def add_custom_products(db: MongoClient, custom_product: str) -> dict:
    product = CustomProducts(product=custom_product.lower())
    result = db.CustomProducts.insert_one(product.dict())
    return {"id": str(result.inserted_id)}


def get_custom_products(db: MongoClient) -> List[str]:
    custom_products = db.CustomProducts.find({}, {"_id": 0, "product": 1})

    products = []
    for product in custom_products:
        products.append(product["product"])

    return products


def get_identified_products(db: MongoClient) -> List[dict]:
    identified_products = db.IdentifiedProducts.find({}, {"_id": 0, "identified_product": 1})

    products = []
    for product in identified_products:
        products.append(product["identified_product"])

    return products


def get_identified_keywords(db: MongoClient) -> List[dict]:
    identified_keywords = db.IdentifiedKeywords.find({}, {"_id": 0, "identified_keyword": 1})

    keywords = []
    for keyword in identified_keywords:
        keywords.append(keyword["identified_keyword"])

    return keywords


def get_identified_products_by_date(db: MongoClient, start_date: datetime, end_date: datetime) -> List[dict]:
    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$lookup": {
                "from": "Keyword",
                "localField": "Keywords_keyword_id",
                "foreignField": "keyword_id",
                "as": "keywordDetails"
            }
        },
        {
            "$unwind": "$keywordDetails"
        },
        {
            "$project": {
                "_id": 0,
                "keyword_id": "$Keywords_keyword_id",
                "date": "$date",
                "total_count": "$total_count",
                "keyword": "$keywordDetails.keyword",
                "author": "$keywordDetails.author"
            }
        }
    ]
    filtered_keywords = list(db.IdentifiedProducts.aggregate(pipeline))
    return filtered_keywords


# ------------------ CRON TASKS ------------------


def add_identified_products(db: MongoClient):
    posts = db.Post.find()

    for post in posts:
        identified_product = db.IdentifiedProducts.find_one({"post_id": post["_id"]})
        if identified_product:
            continue

        description = post.get("description")
        if description:
            identified_product_names = identify_products(description, db)
            if identified_product_names == -1:
                continue

            for product_name in identified_product_names:
                identified_product = IdentifiedProducts(
                    sm_id=post["sm_id"],
                    post_id=post["_id"],
                    identified_product=product_name,
                    date=datetime.now()
                )
                db.IdentifiedProducts.insert_one(identified_product.dict())

    return "Identified products added successfully."


def add_identified_keywords(db:MongoClient):
    posts = db.Post.find()

    for post in posts:
        identified_keyword = db.IdentifiedKeywords.find_one({"post_id":post["_id"]})
        if identified_keyword:
            continue

        description = post.get("description")
        if description:
            identified_keyword_tags = identify_keywords(description,db)
            if identified_keyword_tags == -1:
                continue

            for keyword_tag in identified_keyword_tags:
                identified_keyword = IdentifiedKeywords(
                    sm_id=post["sm_id"],
                    post_id=post["_id"],
                    identified_keyword=keyword_tag,
                    date=datetime.now()
                )
                db.IdentifiedKeywords.insert_one(identified_keyword.dict())
                
    return "Identified keyword added successfully."