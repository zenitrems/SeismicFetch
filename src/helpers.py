# pylint: disable=broad-exception-caught
"""
Feeder utilities
"""
import sys
from datetime import datetime
from loguru import logger
import pytz
from mongo_model import UsgsDbActions, EmscDbActions, SsnDbActions

UTC_TIMEZONE = pytz.timezone("UTC")
AMERICA_MEXICO_TIMEZONE = pytz.timezone("America/Mexico_City")
logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    format="[{time:HH:mm:ss}] | <lvl>{level}</lvl> | {name}:{function} | <y>{message}{exception}</y>",
    level="DEBUG",
)
level_new = logger.level("NEW_EVENT", no=38, color="<r>")
level_update = logger.level("UPDATE", no=39, color="<y>")


class UsgsUtils:
    """USGS Data Utils"""

    def __init__(self) -> None:
        self.db_action = UsgsDbActions()

    def process_data(self, data):
        """Process data for event"""
        try:
            if data["features"]:
                document_data = []
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
                    document_data.append(document)

                self.compare_usgs_id(document_data)
        except Exception:
            logger.exception(Exception)

    def compare_usgs_id(self, data):
        """Compare ids and save new events"""
        for element in data:
            new_id = element["id"]
            existing_id = self.db_action.find_usgs_id(new_id)
            if existing_id is True:
                logger.trace(
                    "\nId:{id} Exists Updated:{updated} \n{place} | M{mag} | Time:{time} | Network:{net} | Id:{id}\n",
                    place=element["properties"]["place"],
                    updated=element["properties"]["updated"],
                    mag=element["properties"]["mag"],
                    time=element["properties"]["time"],
                    net=element["properties"]["sources"],
                    id=element["id"],
                )
                return
            self.db_action.insert_usgs(element)
            logger.log(
                "NEW_EVENT",
                "\n{place} | M{mag} | Time: {time} | Network: {net} | Id: {id}\n",
                place=element["properties"]["place"],
                mag=element["properties"]["mag"],
                time=element["properties"]["time"],
                net=element["properties"]["sources"],
                id=element["id"],
            )


class EmscUtils:
    """EMSC Data Utils"""

    def __init__(self) -> None:
        self.db_action = EmscDbActions()

    def process_data(self, data):
        """Process data for event"""
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

    def compare_emsc_id(self, document):
        """Compare ids and save new events"""

        new_id = document["id"]
        existing_id = self.db_action.find_emsc_id(new_id)
        if existing_id is True:
            self.db_action.update_document(document)
            logger.log(
                "UPDATE",
                "\n{id} Updated: {update} | {place} | M{mag} | Time:{time} | Network:{net}\n",
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
            "\n{place} | M{mag} | Time: {time} | Network: {net} | Id: {id}\n",
            place=document["properties"]["place"],
            mag=document["properties"]["mag"],
            time=document["properties"]["time"],
            net=document["properties"]["auth"],
            id=document["id"],
        )


class SsnUtils:
    """SSN Data Utils"""

    def __init__(self) -> None:
        self.db_action = SsnDbActions()

    def compare_ssn_data(self, data):
        """Compara los datos nuevos con los existentes"""
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
