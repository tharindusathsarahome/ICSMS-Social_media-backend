# app/db/database.py

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from app.core.config import MONGODB_URI, MONGODB_DB

def connect_to_mongo():
    """
    Create MongoDB database client.
    """

    global client
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

def get_database():
    """
    Get the MongoDB database client.
    """

    global client
    return client[MONGODB_DB]

def close_mongo_connection():
    """
    Close the MongoDB connection.
    """

    global client
    client.close()
