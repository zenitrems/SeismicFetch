import datetime
from get_mongo_db import mongodb

database = mongodb()
collection = database["sismicidad_ssn"]

""" collection.update_many({"profundidad": "en revision"}, {"$set": {"profundidad": 0.0}}) """

filtro = {
    'timestamp_utc': {
        '$gt': datetime.datetime(2023, 6, 22, 0, 28, 12)
    }
}
collection.delete_many(filtro)
# en revision
# no calculable
