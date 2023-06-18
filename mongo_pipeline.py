"""
MONGO QUERY
"""
from datetime import datetime, timedelta
from pymongo.errors import PyMongoError
from get_mongo_db import mongodb

mongo = mongodb()
mongo_db = mongo['sismicidad_ssn']


def update_last_week_data():
    """Update view"""
    try:
        last_week_date = datetime.now() - timedelta(days=7)
        last_week_str = last_week_date.strftime('%Y-%m-%d')
        print(last_week_str)

        # Filtrar y almacenar los datos de la última semana en la colección "last_week_data"
        pipeline = [
            {
                '$match': {
                    'magnitud': {
                        '$gte': 7
                    }
                }
            }, {
                '$out': 'magAggregate'
            }
        ]
        mongo_db['sismos'].aggregate(pipeline)

        print('Actualización de datos de la última semana completada')
    except PyMongoError as mongo_error:
        print('mongo error', str(mongo_error))
    finally:
        mongo.client.close()


update_last_week_data()
