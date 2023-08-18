"""
Mongo Client
"""
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from helpers import logger

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["sismicidad"]


def db_connect():
    """Mongo init"""
    try:
        db.list_collections()
        return db

    except PyMongoError as mongo_error:
        logger.error("DB CONNECTION FAILED")
        logger.exception(mongo_error)
        return None


def db_close():
    """Mongo Client Close"""
    logger.info("Mongo Client Close")
    client.close()
