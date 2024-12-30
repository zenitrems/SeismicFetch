"""
EMSC Web Services
"""

import requests
import json
from src import helpers

logger = helpers.logger



def fetch_by_id(main_event):
    """
    Fetch event data by ID using EMSC Web Services.

    Args:
        main_event (dict): A dictionary containing keys 'unid', 'source', and 'out'.

    Returns:
        str: A JSON string of the response or an error message.
    """
    json_str = {}
    try:
        url = "http://www.seismicportal.eu/eventid/api/convert?source_id={id}&source_catalog={source}&out_catalog={out}&format=json".format(
            id=main_event["unid"], source=main_event["source"], out=main_event["out"]
        )

        # Make Request
        res = requests.get(url, timeout=15)

        # HTTP error if status is not 200
        res.raise_for_status()

        # Search for JSON response
        json_response = res.json()

        # Dump response in JSON
        json_str = json.dumps(json_response, indent=4)

        return json_str

    except requests.Timeout as request_timeout:
        logger.error(f"Request timed out: {request_timeout}")
        return json.dumps({"error": "Timeout occurred"}, indent=4)

    except requests.ConnectionError as request_connection_error:
        logger.error(f"Connection error: {request_connection_error}")
        return json.dumps({"error": "Connection error occurred"}, indent=4)

    except requests.RequestException as generic_error:
        logger.error(f"Request failed: {generic_error}")
        return json.dumps({"error": "Request failed"}, indent=4)
