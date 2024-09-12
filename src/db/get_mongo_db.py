"""
Mongo Client
"""
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from src import helpers

load_dotenv()
logger = helpers.logger


# Singleton for MongoClient
mongo_client = None

def db_connect():
    """Mongo init - Singleton pattern"""
    global mongo_client
    if mongo_client is None:
        try:
            mongo_client = MongoClient(os.getenv("MONGO_URI"))
            logger.info("MongoDB client initialized")
        except PyMongoError as e:
            logger.exception(f"Failed to connect to MongoDB: {e}")
            raise
    return mongo_client["sismicidad"]


def test_connection():
    """Test MongoDB connection"""
    try:
        db = db_connect()
        db.list_collection_names()  # Test the connection by listing collections
        logger.info("MongoDB connection test successful")
    except PyMongoError as e:
        logger.exception(f"MongoDB connection test failed: {e}")
        raise


def db_close():
    """Close Mongo Client Connection (if necessary)"""
    global mongo_client
    if mongo_client:
        try:
            mongo_client.close()
            logger.info("MongoDB connection closed")
            mongo_client = None  # Reset the client after closing
        except PyMongoError as e:
            logger.exception(f"Error while closing MongoDB connection: {e}")
    else:
        logger.warning("MongoDB connection was already closed or not initialized")