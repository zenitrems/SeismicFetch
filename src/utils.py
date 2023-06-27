# pylint: disable=broad-exception-caught
"""
Feeder utilities
"""

import sys
import logging
from datetime import datetime, timedelta
import pytz
from mongo_model import MongoModel

UTC_TIMEZONE = pytz.timezone("UTC")
AMERICA_MEXICO_TIMEZONE = pytz.timezone("America/Mexico_City")

start_date = datetime.now(UTC_TIMEZONE) - timedelta(hours=24)

db_action = MongoModel()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class EmscUtils:
    """EMSC Data Utils"""

    def __init__(self) -> None:
        pass

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
            self.save_data(document)

        except Exception:
            print(str(Exception))

    def compare_id(
        self,
    ):
        """Compare existent id's"""
        db_action.get_usgs_ids()

    def save_data(self, data):
        """MongoDB save"""
        self.compare_id()
        db_action.insert_emsc(data)


class UsgsUtils:
    """USGS Data Utils"""

    def __init__(self) -> None:
        pass

    def process_data(self, data):
        """Process data for event"""
        try:
            document_data = []
            for feature in data["features"]:
                # timehash to seconds
                time_usgs = feature["properties"]["time"] / 1000
                time_updated = feature["properties"]["updated"] / 1000

                timestamp = datetime.fromtimestamp(time_usgs, tz=UTC_TIMEZONE)
                updated = datetime.fromtimestamp(time_updated, tz=UTC_TIMEZONE)
                local_timestamp = (
                    timestamp.replace(tzinfo=UTC_TIMEZONE)
                    .astimezone(tz=AMERICA_MEXICO_TIMEZONE)
                    .isoformat()
                )
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
                        "type": feature["properties"]["type"],  # Type of seismic event.
                    },
                    "geometry": feature["geometry"],
                    "id": feature["id"],
                    "local_timestamp": local_timestamp,
                }
                document_data.append(document)

            self.compare_id(document_data)

        except Exception:
            print(str(Exception))

    def compare_id(self, data):
        """Compare new id whith exitent id to avoid duplicates"""
        id_collection = db_action.get_usgs_ids()
        new_events = []
        existent_id = [dato["usgs_id"] for dato in id_collection]
        for element in data:
            new_id = element["id"]
            if new_id in existent_id:
                print(f"El dato con ID {new_id} ya existe")
                return
            print(f"El dato con ID {new_id} Es Nuevo")
            new_events.append(element)

        print(new_events)

    # def save_event(self, new_events):
