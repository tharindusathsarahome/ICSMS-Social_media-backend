# app/db/connection.py

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from app.core.config import MONGODB_URI, MONGODB_DB

def connect_to_mongo():
    """
    Create MongoDB database client.
    """

    global client
    client = MongoClient(MONGODB_URI)
    # client = MongoClient(MONGODB_URI, tls=True, tlsCertificateKeyFile='app\db\X509-cert-5527943773821302944.pem', server_api=ServerApi('1'))


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
