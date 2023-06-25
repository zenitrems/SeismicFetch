"""
Usgs
"""
import os
import asyncio
import datetime
import time
import pytz
import requests
from termcolor import colored
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
from telegram.error import TelegramError
from get_mongo_db import mongodb
from telegram_bot import MyBot

load_dotenv()
mongo_db = mongodb()
collection_name = mongo_db["sismicidad_usgs"]

token = os.getenv("TELEGRAM_KEY")
bot = MyBot(token)
# USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson"
USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson"
#USGS_FEED = "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=2023-01-01%2000:00:00&endtime=2023-06-23%2023:59:59&minmagnitude=2.5&orderby=time-asc"


async def consulta_usgs():
    """Peticion de datos"""
    start = time.perf_counter()
    try:
        response = requests.get(USGS_FEED, timeout=60)
        if response.status_code == 200:
            finish = time.perf_counter()
            print(
                colored(
                    f"\nusgs consultado en {finish - start:0.4f} segundos", "yellow"
                )
            )
            data = response.json()
            await procesar_datos(data)
        else:
            print(
                colored(
                    f"Error consultando USGS\n {response.status_code}",
                    "red",
                    attrs=["reverse"],
                ),
            )
    except requests.Timeout as request_timeout:
        print(
            colored("Request Timeout: \n", "red", attrs=["reverse"]),
            str(request_timeout),
        )
    except requests.ConnectionError as request_conection_error:
        print(
            colored("Request Connection error: \n", "red", attrs=["reverse"]),
            str(request_conection_error),
        )


async def procesar_datos(data):
    """Procesa datos"""
    document_data = []
    utc_timezone = pytz.timezone("UTC")
    mexico_timezone = pytz.timezone("America/Mexico_City")

    for feature in data["features"]:
        feature_properties = feature["properties"]
        feature_geo = feature["geometry"]
        feature_id = feature["id"]

        # Miliseconds to seconds
        time_usgs = feature_properties["time"] / 1000
        time_updated = feature_properties["time"] / 1000

        timestamp = datetime.datetime.fromtimestamp(time_usgs, tz=utc_timezone)
        updated = datetime.datetime.fromtimestamp(time_updated, tz=utc_timezone)
        timestamp_local = (
            timestamp.replace(tzinfo=utc_timezone)
            .astimezone(tz=mexico_timezone)
            .isoformat()
        )
        # https://earthquake.usgs.gov/data/comcat/data-eventterms.php
        properties = {
            "mag": feature_properties["mag"],
            "place": feature_properties["place"],
            "time": timestamp,
            "updated": updated,
            "tz": feature_properties[
                "tz"
            ],  # Timezone offset from UTC in minutes at the event epicenter.
            "url": feature_properties["url"],  # Link to USGS Event Page for event.
            "detail": feature_properties[
                "detail"
            ],  # Link to GeoJSON detail feed from a GeoJSON summary feed.
            "felt": feature_properties[
                "felt"
            ],  # The total number of felt reports submitted to the DYFI? system.
            "cdi": feature_properties[
                "cdi"
            ],  # The maximum reported intensity for the event. Computed by DYFI
            "mmi": feature_properties[
                "mmi"
            ],  # The maximum estimated instrumental intensity for the event.
            "alert": feature_properties[
                "alert"
            ],  # The alert level from the PAGER earthquake impact scale
            "status": feature_properties[
                "status"
            ],  # Status is either automatic or reviewed
            "tsunami": feature_properties[
                "tsunami"
            ],  # This flag is set to "1" for large events in oceanic regions and "0" otherwise.
            "sig": feature_properties[
                "sig"
            ],  # A number describing how significant the event is
            "net": feature_properties["net"],  # The ID of a data contributor.
            "code": feature_properties["code"],  # An identifying code assigned by
            "ids": feature_properties[
                "ids"
            ],  # A comma-separated list of event ids that are associated to an event.
            "sources": feature_properties[
                "sources"
            ],  # A comma-separated list of network contributors.
            "types": feature_properties["types"],  # Type of seismic event.
            "nst": feature_properties[
                "nst"
            ],  # Number of seismic stations which reported P- and S-arrival times for this earthquake.
            "dmin": feature_properties[
                "dmin"
            ],  # Horizontal distance from the epicenter to the nearest station (in degrees). 1 degree is approximately 111.2 kilometers
            "rms": feature_properties[
                "rms"
            ],  # The root-mean-square (RMS) travel time residual, in sec, using all weights. This parameter provides a measure of the fit of the observed arrival times to the predicted arrival times for this location
            "gap": feature_properties[
                "gap"
            ],  # The horizontal location error, in km, defined as the length of the largest projection of the three principal errors on a horizontal plane
            "magType": feature_properties[
                "magType"
            ],  # The method or algorithm used to calculate the preferred magnitude for the event.
            "type": feature_properties["type"],  # Type of seismic event.
        }
        geometry = {"coordinates": feature_geo["coordinates"]}
        document = {
            "properties": properties,
            "geometry": geometry,
            "timestamp_local": timestamp_local,
            "usgs_id": feature_id,
        }
        document_data.append(document)

    await comparar_datos(document_data)


async def comparar_datos(document_data):
    """Compara los datos nuevos con los existentes"""
    try:
        data_collection = list(collection_name.find())
    except PyMongoError as mongo_error:
        print("mongo error", str(mongo_error))

    if data_collection:
        nuevos_datos = []
        id_dato_existente = [dato["usgs_id"] for dato in data_collection]
        for dato in document_data:
            id_dato_nuevo = dato["usgs_id"]
            if id_dato_nuevo in id_dato_existente:
                print(f"El dato con ID {id_dato_nuevo} ya existe")
                return

            print(f"El dato con ID {id_dato_nuevo} Es Nuevo")
            nuevos_datos.append(dato)
        await almacena_datos(nuevos_datos)


async def almacena_datos(nuevos_datos):
    """almacena datos en mongo"""
    try:
        for dato in nuevos_datos:
            print(
                colored(f"Nuevo evento detectado\n {dato}", "red"),
            )
            collection_name.insert_one(dato)

            dato_property = dato["properties"]
            evento_template = (
                f"<b>Sismo detectado USGS:</b>\n\n"
                f"<b>{dato_property['place']}</b>\n"
                f"<b>Timestamp:</b> {dato['timestamp_local']}\n"
                f"<b>Magnitud:</b> {dato_property['mag']}\n"
                f"<b>Profundidad</b> {dato['geometry']['coordinates'][2]}"
            )
            if dato_property["mag"] >= 4.0:
                try:
                    await bot.send_evento(evento_template)
                except TelegramError as bot_error:
                    print(
                        colored(
                            "Error TelegramBot:\n", "red", attrs=["blink", "reverse"]
                        ),
                        str(bot_error),
                    )
    except PyMongoError as mongo_error:
        print("mongo error", str(mongo_error))


async def main():
    """Main function"""
    while True:
        print(colored("\nActualizando...", "green"))
        await consulta_usgs()
        print(colored("\nEsperando...\n", "green"))
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
