"""
Mongo data Model
"""
from datetime import datetime, timedelta
import pytz
from pymongo.errors import PyMongoError
from get_mongo_db import mongodb
from helpers import logger

UTC_TIMEZONE = pytz.timezone("UTC")
AMERICA_MEXICO_TIMEZONE = pytz.timezone("America/Mexico_City")

db = mongodb()


class SsnDbActions:
    """SSN Database Actions"""
    def __init__(self) -> None:
        self.ssn_collection = db["sismicidad_ssn"]
        self.start_date = datetime.now() - timedelta(days=3)
        self.start_date_str = self.start_date.strftime("%Y-%m-%d")

    def insert_ssn(self, event):
        """Insert event to SSN DB"""
        try:
            self.ssn_collection.insert_one(event)

        except PyMongoError as mongo_error:
            logger.error(mongo_error)

    def get_event_list(self):
        """Get latest SSN event id's"""
        try:
            collection_list = list(
                self.ssn_collection.aggregate(
                    [{"$match": {"fecha": {"$gte": self.start_date_str}}}]
                )
            )
        except PyMongoError as mongo_error:
            logger.error(mongo_error)

        return collection_list


class UsgsDbActions:
    """USGS Database Actions"""

    def __init__(self) -> None:
        self.usgs_collection = db["sismicidad_usgs"]
        self.start_date = datetime.now(UTC_TIMEZONE) - timedelta(hours=24)

    def insert_usgs(self, event):
        """Insert event to USGS DB"""
        try:
            self.usgs_collection.insert_one(event)

        except PyMongoError as mongo_error:
            logger.exception(mongo_error)

    def find_usgs_id(self, document_id):
        """Get latest USGS event id's"""
        try:
            find_id = self.usgs_collection.find_one({"id": document_id})
        except PyMongoError as mongo_error:
            logger.exception(mongo_error)
        if find_id:
            return True
        return False


class EmscDbActions:
    """EMSC Database Actions"""

    def __init__(self) -> None:
        self.emsc_collection = db["sismicidad_emsc"]
        self.start_date = datetime.now(UTC_TIMEZONE) - timedelta(hours=24)

    def insert_emsc(self, event):
        """Insert event to EMSC DB"""
        try:
            self.emsc_collection.insert_one(event)

        except PyMongoError as mongo_error:
            logger.exception(mongo_error)

    def find_emsc_id(self, document_id):
        """Get latest EMSC event id's"""
        try:
            find_id = self.emsc_collection.find_one({"id": document_id})
        except PyMongoError as mongo_error:
            logger.exception(mongo_error)
        if find_id:
            return True
        return False

    def update_document(self, document):
        """Update a single document"""
        document_id = {"id": document["id"]}
        try:
            self.emsc_collection.update_one(document_id, {"$set": document})

        except PyMongoError as mongo_error:
            logger.exception(mongo_error)
