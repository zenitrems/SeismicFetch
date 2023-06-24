"""
MONGO QUERY
"""

from pymongo.errors import PyMongoError
from get_mongo_db import mongodb

mongo = mongodb()
usgs_collection = mongo["sismicidad_usgs"]
ssn_collection = mongo["sismicidad_ssn"]


def update_last_week_data():
    """Update view"""
    try:
        pipeline = [{"$sort": {"properties.time": -1}}]

        match_mag = [{"$match": {"magnitud": {"$gte": 7}}}]

        results = ssn_collection.aggregate(match_mag)

        for event in results:
            print(event)
    except PyMongoError as mongo_error:
        print("mongo error", str(mongo_error))
    finally:
        mongo.client.close()


update_last_week_data()
