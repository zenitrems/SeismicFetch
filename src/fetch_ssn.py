"""
Fetch SSN latest Earthquakes
www.ssn.unam.mx
"""
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from helpers import SsnUtils, logger

ssn_utils = SsnUtils()

load_dotenv()


def fetch_ssn():
    """Fetch SSN URL"""
    try:
        response = requests.get(
            "http://www.ssn.unam.mx/sismicidad/ultimos/", timeout=60
        )
        if response.status_code == 200:
            parse_ssn(response)
    except requests.Timeout as request_timeout:
        logger.exception(request_timeout)
    except requests.ConnectionError as request_conection_error:
        logger.exception(request_conection_error)


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
    logger.trace(f"SSN Latest Update: {ssn_ultima_actualizacion} UTC-6")
    table = soup.find("table")
    rows = table.find_all("tr")
    process_data(rows)


def process_data(rows):
    """Arrange table rows"""
    json_data = []
    for row in rows[1:]:
        cells = row.find_all("td")
        epi_span_tags = cells[2].find_all("span")
        epi_span_texts = [span.text for span in epi_span_tags]
        datetime_span_tags = cells[1].find_all("span")
        datetime_span_texts = [span.text for span in datetime_span_tags]
        magnitud_text = cells[0].text

        fecha_hora_str = (
            f"{datetime_span_texts[0].strip()} {datetime_span_texts[1].strip()}"
        )
        fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
        fecha_hora_timezone = datetime.replace(
            fecha_hora, tzinfo=pytz.timezone("America/Mexico_City")
        )

        utc_timestamp = fecha_hora_timezone.astimezone(pytz.timezone("UTC"))

        magnitud_parts = magnitud_text.split(" ")
        is_preliminar = True if magnitud_parts[0] == "PRELIMINAR" else False
        magnitud = (
            float(magnitud_parts[1]) if is_preliminar else float(magnitud_parts[0])
        )

        document = {
            "preliminar": is_preliminar,
            "fecha": datetime_span_texts[0].strip(),
            "hora": datetime_span_texts[1].strip(),
            "timestamp_utc": utc_timestamp,
            "magnitud": magnitud,
            "latitud": float(epi_span_texts[1]),
            "longitud": float(epi_span_texts[2]),
            "profundidad": float(cells[3].text.split(" ")[0]),
            "referencia": epi_span_texts[0].strip(),
        }
        json_data.append(document)
    json_data.reverse()
    ssn_utils.compare_ssn_data(json_data)


def main():
    """Main function"""
    while True:
        fetch_ssn()
        time.sleep(180)
