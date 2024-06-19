from typing import List
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
from app.models.product_models import CustomProducts, IdentifiedProducts
from app.services.products_keywords_service import identify_products
from fastapi import HTTPException



def add_custom_products(db: MongoClient, custom_product: str) -> dict:
    product = CustomProducts(product=custom_product)
    result = db.CustomProducts.insert_one(product.dict())
    return {"id": str(result.inserted_id)}


def get_custom_products(db: MongoClient) -> List[str]:
    custom_products = db.CustomProducts.find({}, {"_id": 0, "product": 1})

    products = []
    for product in custom_products:
        products.append(product["product"])

    return products


def add_identified_products(db: MongoClient):
    try:
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

        return {"message": "Identified products added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_identified_products(db: MongoClient) -> List[dict]:
    identified_products = db.IdentifiedProducts.find({}, {"_id": 0, "identified_product": 1})

    products = []
    for product in identified_products:
        products.append(product["identified_product"])

    return products

    