from pymongo import MongoClient

def mongodb():
    CONECTION_STRING = "mongodb://localhost"
    client = MongoClient(CONECTION_STRING)
    return client['sismicidad_SSN']

if __name__ == "__main__":
    dbname = mongodb()
    