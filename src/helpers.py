# pylint: disable=broad-exception-caught, line-too-long
"""
Feeder utilities
"""
import sys
from datetime import datetime
from loguru import logger
import pytz
from mongo_model import UsgsDbActions, EmscDbActions, SsnDbActions
from telegram_parse import SsnBotParse, UsgsBotParse, EmscBotParse

UTC_TIMEZONE = pytz.timezone("UTC")
AMERICA_MEXICO_TIMEZONE = pytz.timezone("America/Mexico_City")
logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    format="[{time:HH:mm:ss}] | <lvl>{level}</lvl> | {name}:{function} | <b><y>{message}{exception}</y></b>",
    level="DEBUG",
)

level_new = logger.level("NEW_EVENT", no=38, color="<r>")
level_update = logger.level("UPDATE", no=39, color="<y>")


class SsnUtils:
    """SSN Data Utils"""

    def __init__(self) -> None:
        self.db_action = SsnDbActions()
        self.bot_actions = SsnBotParse()
        self.new_events = []

    def process_data(self, data):
        """Arrange table rows"""
        json_data = []
        self.new_events = []  # cleanup new events
        for row in data[1:]:
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
        self.compare_ssn_data(json_data)
        return self.new_events

    def compare_ssn_data(self, data):
        """Compare existing times, whith new times"""
        # List Dates in existing data
        existing_data = self.db_action.get_event_list()
        existing_datetimes = set()
        for element in existing_data:
            time_date = datetime.strptime(
                element["fecha"] + " " + element["hora"], "%Y-%m-%d %H:%M:%S"
            )
            existing_datetimes.add(time_date)

        # Filter and save
        for element in data:
            new_datetime = datetime.strptime(
                element["fecha"] + " " + element["hora"], "%Y-%m-%d %H:%M:%S"
            )
            if new_datetime not in existing_datetimes:
                self.db_action.insert_ssn(element)
                logger.log(
                    "NEW_EVENT",
                    "\n{place} | M{mag} | Time: {time} | Network: {net}\n",
                    place=element["referencia"],
                    mag=element["magnitud"],
                    time=element["timestamp_utc"],
                    net="SSN",
                )
                self.new_events.append(element)

        return self.new_events


class UsgsUtils:
    """USGS Data Utils"""

    def __init__(self) -> None:
        self.db_action = UsgsDbActions()
        self.bot_actions = UsgsBotParse()
        self.new_events = []

    def process_data(self, data):
        """Process data for event"""
        self.new_events = []  # cleanup new events
        try:
            if data["features"]:
                for feature in data["features"]:
                    # unixtime to seconds
                    time_usgs = feature["properties"]["time"] / 1000
                    time_updated = feature["properties"]["updated"] / 1000

                    timestamp = datetime.fromtimestamp(time_usgs, tz=UTC_TIMEZONE)
                    updated = datetime.fromtimestamp(time_updated, tz=UTC_TIMEZONE)
                    local_timestamp = timestamp.astimezone(
                        tz=AMERICA_MEXICO_TIMEZONE
                    ).isoformat()
                    document = {
                        "type": feature["type"],
                        "properties": {
                            "mag": feature["properties"]["mag"],
                            "place": feature["properties"]["place"],
                            "time": timestamp,
                            "updated": updated,
                            "tz": feature["properties"][
                                "tz"
                            ],  # Timezone offset from UTC in minutes at the event epicenter.
                            "url": feature["properties"][
                                "url"
                            ],  # Link to USGS Event Page for event.
                            "detail": feature["properties"][
                                "detail"
                            ],  # Link to GeoJSON detail feed from a GeoJSON summary feed.
                            "felt": feature["properties"][
                                "felt"
                            ],  # The total number of felt reports submitted to the DYFI? system.
                            "cdi": feature["properties"][
                                "cdi"
                            ],  # The maximum reported intensity for the event. Computed by DYFI
                            "mmi": feature["properties"][
                                "mmi"
                            ],  # The maximum estimated instrumental intensity for the event.
                            "alert": feature["properties"][
                                "alert"
                            ],  # The alert level from the PAGER earthquake impact scale
                            "status": feature["properties"][
                                "status"
                            ],  # Status is either automatic or reviewed
                            "tsunami": feature["properties"][
                                "tsunami"
                            ],  # This flag is set to "1" for large events in oceanic regions and "0" otherwise.
                            "sig": feature["properties"][
                                "sig"
                            ],  # A number describing how significant the event is
                            "net": feature["properties"][
                                "net"
                            ],  # The ID of a data contributor.
                            "code": feature["properties"][
                                "code"
                            ],  # An identifying code assigned by
                            "ids": feature["properties"][
                                "ids"
                            ],  # A comma-separated list of event ids that are associated to an event.
                            "sources": feature["properties"][
                                "sources"
                            ],  # A comma-separated list of network contributors.
                            "types": feature["properties"][
                                "types"
                            ],  # Type of seismic event.
                            "nst": feature["properties"][
                                "nst"
                            ],  # Number of seismic stations which reported P- and S-arrival times for this earthquake.
                            "dmin": feature["properties"][
                                "dmin"
                            ],  # Horizontal distance from the epicenter to the nearest station (in degrees). 1 degree is approximately 111.2 kilometers
                            "rms": feature["properties"][
                                "rms"
                            ],  # The root-mean-square (RMS) travel time residual, in sec, using all weights. This parameter provides a measure of the fit of the observed arrival times to the predicted arrival times for this location
                            "gap": feature["properties"][
                                "gap"
                            ],  # The horizontal location error, in km, defined as the length of the largest projection of the three principal errors on a horizontal plane
                            "magType": feature["properties"][
                                "magType"
                            ],  # The method or algorithm used to calculate the preferred magnitude for the event.
                            "type": feature["properties"][
                                "type"
                            ],  # Type of seismic event.
                        },
                        "geometry": feature["geometry"],
                        "id": feature["id"],
                        "local_timestamp": local_timestamp,
                    }
                    self.compare_usgs_id(document)

        except Exception:
            logger.exception(Exception)

        return self.new_events

    def compare_usgs_id(self, data):
        """Compare ids and save new events"""
        new_id = data["id"]
        existing_id = self.db_action.find_usgs_id(new_id)
        if existing_id is True:
            logger.trace(
                "{id} Exists\n{place} | M{mag} | Time:{time} | Updated:{updated}| Network:{net}\n ",
                place=data["properties"]["place"],
                updated=data["properties"]["updated"],
                mag=data["properties"]["mag"],
                time=data["properties"]["time"],
                net=data["properties"]["sources"],
                id=data["id"],
            )
            return
        self.db_action.insert_usgs(data)
        logger.log(
            "NEW_EVENT",
            "\n{place} | M{mag} | Time: {time} | Id: {id} | Network: {net}\n",
            place=data["properties"]["place"],
            mag=data["properties"]["mag"],
            time=data["properties"]["time"],
            net=data["properties"]["sources"],
            id=data["id"],
        )
        self.new_events.append(data)


class EmscUtils:
    """EMSC Data Utils"""

    def __init__(self) -> None:
        self.db_action = EmscDbActions()
        self.bot_actions = EmscBotParse()
        self.new_events = []

    def process_data(self, data):
        """Process data for event"""
        self.new_events = []  # cleanup new events
        try:
            feature = data["data"]
            time = feature["properties"]["time"]
            lastupdate = feature["properties"]["lastupdate"]

            format_time = time[:-1]
            format_lastupdate = lastupdate[:-1]

            datetimeobj_time = datetime.strptime(format_time, "%Y-%m-%dT%H:%M:%S.%f")
            datetimeobj_lastupdate = datetime.strptime(
                format_lastupdate, "%Y-%m-%dT%H:%M:%S.%f"
            )

            utc_timezone = datetime.replace(datetimeobj_time, tzinfo=UTC_TIMEZONE)
            local_timestamp = utc_timezone.astimezone(
                tz=AMERICA_MEXICO_TIMEZONE
            ).isoformat()

            document = {
                "type": feature["type"],
                "properties": {
                    "time": datetimeobj_time,
                    "lastupdate": datetimeobj_lastupdate,
                    "place": feature["properties"]["flynn_region"],
                    "mag": feature["properties"]["mag"],
                    "magType": feature["properties"]["magtype"],
                    "evType": feature["properties"]["evtype"],
                    "auth": feature["properties"]["auth"],
                    "source_id": feature["properties"]["source_id"],
                    "source_catalog": feature["properties"]["source_catalog"],
                    "unid": feature["properties"]["unid"],
                },
                "geometry": feature["geometry"],
                "local_timestamp": local_timestamp,
                "id": feature["id"],
            }
            self.compare_emsc_id(document)

        except Exception:
            logger.exception(Exception)

        return self.new_events

    def compare_emsc_id(self, document):
        """Compare ids and save new events"""

        new_id = document["id"]
        existing_id = self.db_action.find_emsc_id(new_id)
        if existing_id is True:
            self.db_action.update_document(document)
            logger.log(
                "UPDATE",
                "\n{place} | M{mag} | Time:{time} | Updated: {update} | Id: {id} | Network:{net}\n",
                place=document["properties"]["place"],
                mag=document["properties"]["mag"],
                time=document["properties"]["time"],
                update=document["properties"]["lastupdate"],
                net=document["properties"]["auth"],
                id=document["id"],
            )
            return

        self.db_action.insert_emsc(document)
        logger.log(
            "NEW_EVENT",
            "\n{place} | M{mag} | Time: {time} | Id: {id} | Network: {net}\n",
            place=document["properties"]["place"],
            mag=document["properties"]["mag"],
            time=document["properties"]["time"],
            net=document["properties"]["auth"],
            id=document["id"],
        )
        self.new_events.append(document)
