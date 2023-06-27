"""
Mongo data Model
"""
from pymongo.errors import PyMongoError
from get_mongo_db import mongodb


db = mongodb()


class MongoModel:
    """Model Class"""

    def __init__(self) -> None:
        self.emsc_collection = db["sismicidad_emsc"]
        self.usgs_collection = db["sismicidad_usgs"]

    def insert_emsc(self, event):
        """Insert event to EMSC DB"""
        try:
            self.emsc_collection.insert_one(event)

        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))

    def get_emsc_ids(self):
        """Compare recent EMSC id's"""
        try:
            id_collection = list(self.emsc_collection.find())
        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))

        return id_collection

    def insert_usgs(self, event):
        """Insert event to USGS DB"""
        try:
            self.usgs_collection.insert_one(event)

        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))

    def get_usgs_ids(self):
        """Compare recent USGS id's"""
        try:
            id_collection = list(self.usgs_collection.find())
        except PyMongoError as mongo_error:
            print("MongoDB error", str(mongo_error))

        return id_collection
