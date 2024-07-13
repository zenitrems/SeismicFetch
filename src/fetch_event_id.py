"""
EMSC Web Services
"""

import requests
import json
from src import helpers

logger = helpers.logger

def fetch_by_id(main_event, source, out):
    try:
        url = "http://www.seismicportal.eu/eventid/api/convert?source_id={id}&source_catalog={source}&out_catalog={out}&format=json".format(id=main_event['unid'], source='UNID', out='all')
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        json_response = res.json()
        json_str = json.dumps(json_response, indent=4)
        logger.info(json_str)

    except requests.Timeout as request_timeout:
        logger.error(request_timeout)
    except requests.ConnectionError as request_conection_error:
        logger.error(request_conection_error)
        
    
    return 


def event_data(response):
    json_events = json.dumps(response, indent=4)
    logger.info(json_events)