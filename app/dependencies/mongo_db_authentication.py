# app/dependencies/mongo_db_authentication.py

from pymongo import MongoClient
from app.core.config import MONGODB_URI, MONGODB_DB

client = None


def connect_to_mongo():
    """
    Establishes a connection to the MongoDB database using the specified URI.

    Returns:
        None: The function connects to MongoDB but does not return any value.
    """
    global client
    client = MongoClient(MONGODB_URI)
    print("Connected to MongoDB")

def get_database():
    """
    Retrieves the MongoDB database client instance.

    Returns:
        MongoClient: The MongoDB database client instance.

    Raises:
        Exception: If the connection to the MongoDB client has not been established.
    """
    global client
    if client is None:
        connect_to_mongo()
    return client[MONGODB_DB]

def close_mongo_connection():
    """
    Closes the connection to the MongoDB database.

    Returns:
        None: The function closes the MongoDB connection but does not return any value.
    """
    global client
    if client:
        client.close()
