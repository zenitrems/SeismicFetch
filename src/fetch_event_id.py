"""
EMSC Web Services
"""

import requests
import json
from src import helpers

logger = helpers.logger

def fetch_by_id(main_event):
    try:
        url = "http://www.seismicportal.eu/eventid/api/convert?source_id={id}&source_catalog={source}&out_catalog={out}&format=json".format(id=main_event['unid'], source=main_event['source'], out=main_event['out'])

        #Make Request 
        res = requests.get(url, timeout=15)

        #HTTP error if status is not 200
        res.raise_for_status()

        #Search for JSON response
        json_response = res.json()

        json_str = json.dumps(json_response, indent=4)

    except requests.Timeout as request_timeout:
        logger.error(request_timeout)
    except requests.ConnectionError as request_conection_error:
        logger.error(request_conection_error)

    return event_data(json_str)


def event_data(response):
    logger.info(response)