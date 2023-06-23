from get_mongo_db import mongodb

database = mongodb()
collection = database["sismicidad_ssn"]

collection.update_many({"profundidad": "en revision"}, {"$set": {"profundidad": 0.0}})

# en revision
# no calculable
