"""
Mongo Client
"""
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from helpers import logger


def mongodb():
    """Mongo init"""
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
    except PyMongoError as mongo_error:
        logger.error("DB CONNECTION FAILED")
        logger.exception(mongo_error)
    return client["sismicidad"]
