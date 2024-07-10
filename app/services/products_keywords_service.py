# app/services/products_service.py

from pymongo import MongoClient
from app.services.llm_integration_service import get_gemini_chat, get_gemini_response
import re


# products identification
def identify_products(facebook_post_description: str, db: MongoClient):
    """
    Attempts to identify products in a Facebook post description using Gemini.

    Args:
        facebook_post_description (str): The text content of the Facebook post.

    Returns:
        str: A list of potential products found in the description. Otherwise -1
    """

    chat = get_gemini_chat()

    message = f"This is a Facebook post description: '{facebook_post_description}'.\n Give me a ',' separated list string of products mentioned in this post. Give the mainly identified Products. Not sub Products or partially mentioned Products. Also, product should be as one name. (eg: Chat GPT -> ChatGPT, Vertex AI -> VertexAI) And Do not provide anything else."

    response = get_gemini_response(chat, message)
    print(response)

    potential_products = []
    for word in response.split(','):
        if is_potentially_a_product(word.strip().lower(), db):
            potential_products.append(word.strip())

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
    


# keyword identification
def identify_keywords(facebook_post_description:str,db:MongoClient):

    chat = get_gemini_chat()

    message = f"This is a facebook Post Description:'{facebook_post_description}.\n Give me a ',' separated String list of Hashtags mentioned in this post. Give the mainly identified Hashtags. And Do not provide anything else."

    response = get_gemini_response(chat,message)

    keywords = []
    for word in response.split(','):
        keyword = word.strip().lower()
        if re.match(r'^#[a-z0-9]+$', keyword):
            keywords.append(keyword)
        else:
            pass

    return keywords