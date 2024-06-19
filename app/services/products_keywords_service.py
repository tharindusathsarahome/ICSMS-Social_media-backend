# app/services/products_service.py

from datetime import datetime
from pymongo import MongoClient
from app.models.product_models import CustomProducts, IdentifiedProducts
from app.models.post_models import Post
from app.services.llm_integration_service import get_gemini_chat, get_gemini_response




def identify_products(facebook_post_description: str, db: MongoClient):
    """
    Attempts to identify products in a Facebook post description using Gemini.

    Args:
        facebook_post_description (str): The text content of the Facebook post.

    Returns:
        str: A list of potential products found in the description. Otherwise -1
    """

    chat = get_gemini_chat()

    message = f"This is a Facebook post description: '{facebook_post_description}'.\n Give me a ',' separated list string of products mentioned in this post. Give the mainly identified Products. Not sub Products or partially mentioned Products. And Do not provide anything else."

    response = get_gemini_response(chat, message)

    potential_products = []
    for word in response.split(','):
        if is_potentially_a_product(word, db):
            potential_products.append(word)

    if potential_products:
        return potential_products
    else:
        return -1


def is_potentially_a_product( product_name: str, db: MongoClient ):
    product = db.CustomProducts.find_one({"product": product_name})
    
    if product:
        return True
    else:
        return False
