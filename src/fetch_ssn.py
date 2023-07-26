"""
Fetch SSN latest Earthquakes
www.ssn.unam.mx
"""
import sys
import time
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from helpers import SsnUtils, logger
from telegram_parse import SsnBotParse

ssn_utils = SsnUtils()
bot_action = SsnBotParse()

load_dotenv()
SLEEP_SECONDS = 60


def fetch_ssn():
    """Fetch SSN URL"""
    try:
        response = requests.get(
            "http://www.ssn.unam.mx/sismicidad/ultimos-utc/", timeout=60
        )
        if response.status_code == 200:
            parse_ssn(response)
    except requests.Timeout as request_timeout:
        logger.error(request_timeout)
    except requests.ConnectionError as request_conection_error:
        logger.error(request_conection_error)


def parse_ssn(response):
    """Parse data from SSN table"""
    soup = BeautifulSoup(response.text, "html.parser")
    footer = soup.find("footer")
    ssn_ultimo = footer.find("p", "update-time")
    ssn_ultimo_start_index = ssn_ultimo.text.find("a las ") + len("a las ")
    ssn_ultimo_finish_index = ssn_ultimo.text.find(" (")
    ssn_ultimo_extract_date = ssn_ultimo.text[
        ssn_ultimo_start_index:ssn_ultimo_finish_index
    ]
    ssn_ultima_actualizacion = ssn_ultimo_extract_date.replace("  ", " ")
    logger.trace(f"\nSSN Latest Update: {ssn_ultima_actualizacion} UTC-6\n")
    table = soup.find("table")
    rows = table.find_all("tr")
    new_events = ssn_utils.process_data(rows)
    if new_events:
        bot_action.parse_event(new_events)


def main():
    """Main function"""
    while True:
        fetch_ssn()
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
    sys.exit(0)
