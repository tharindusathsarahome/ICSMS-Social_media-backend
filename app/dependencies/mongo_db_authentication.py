# app/dependencies/mongo_db_authentication.py

from pymongo import MongoClient
from app.core.config import MONGODB_URI, MONGODB_DB

client = None


def connect_to_mongo():
    """
    Create MongoDB database client.
    """
    global client
    client = MongoClient(MONGODB_URI)
    print("Connected to MongoDB")

def get_database():
    """
    Get the MongoDB database client.
    """
    global client
    if client is None:
        connect_to_mongo()
    return client[MONGODB_DB]

def close_mongo_connection():
    """
    Close the MongoDB connection.
    """
    global client
    if client:
        client.close()
