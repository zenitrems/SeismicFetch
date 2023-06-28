"""
Mongo data Model
"""
from datetime import datetime, timedelta
import pytz
from pymongo.errors import PyMongoError
from get_mongo_db import mongodb

UTC_TIMEZONE = pytz.timezone("UTC")
AMERICA_MEXICO_TIMEZONE = pytz.timezone("America/Mexico_City")

db = mongodb()


class UsgsDbActions:
    """USGS Database Actions"""

    def __init__(self) -> None:
        self.usgs_collection = db["sismicidad_usgs"]
        self.start_date = datetime.now(UTC_TIMEZONE) - timedelta(hours=24)

    def insert_usgs(self, event):
        """Insert event to USGS DB"""
        try:
            self.usgs_collection.insert_many(event)

        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))

    def get_usgs_ids(self):
        """Get latest USGS event id's"""
        try:
            usgs_id_list = list(
                self.usgs_collection.aggregate(
                    [
                        {"$match": {"properties.time": {"$gt": self.start_date}}},
                        {"$project": {"id": 1}},
                    ]
                )
            )
        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))

        return usgs_id_list


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
            print("MongoDB error", str(mongo_error))

    def find_emsc_id(self, document_id):
        """Get latest EMSC event id's"""
        try:
            find_id = self.emsc_collection.find_one({"id": document_id})
        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))
        if find_id:
            return True
        return False

    def update_document(self, document):
        """Update a single document"""
        document_id = {"id": document["id"]}
        try:
            self.emsc_collection.update_one(document_id, {"$set": document})

        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))
