"""
Fetch USGS geojson feed
www.usgs.gov
"""
import time
import requests
from dotenv import load_dotenv
from helpers import UsgsUtils, logger
from telegram_parse import UsgsBotParse


load_dotenv()

usgs_utils = UsgsUtils()
bot_action = UsgsBotParse()

# USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson"
USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson"
# USGS_FEED = "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=2023-01-01%2000:00:00&endtime=2023-06-27%2023:59:59&minmagnitude=2.5&orderby=time-asc"

SLEEP_SECONDS = 60


def fetch_usgs():
    """Fetch USGS geojson feed"""
    try:
        response = requests.get(USGS_FEED, timeout=60)
        if response.status_code == 200:
            data = response.json()
            new_events = usgs_utils.process_data(data)
            if new_events:
                bot_action.parse_event(new_events)

    except requests.Timeout as request_timeout:
        logger.error(request_timeout)
    except requests.ConnectionError as request_conection_error:
        logger.error(request_conection_error)


def main():
    """Main Start"""
    while True:
        fetch_usgs()
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
