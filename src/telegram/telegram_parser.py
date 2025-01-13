"""
Parse each event in the array to separate events above the magnitude threshold, 
and creates an HTML template to send to the telegram channel with specific data for each agency. 
"""

import asyncio
from datetime import datetime
from dotenv import load_dotenv
from src.telegram import telegram_bot

load_dotenv()
bot = telegram_bot.MyBot()
MAG_THRESHOLD = float(5.0)


class SsnBotParse:
    """Parse Class For SSN Events"""

    def __init__(self):
        pass

    def parse_event(self, data):
        """For each event Create a template"""
        for element in data:

            datetime_obj = datetime.strptime(
                element["properties"]["time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            legible_datetime = (
                datetime.strftime(datetime_obj, "%d-%m-%Y, %H:%M") + " UTC"
            )
            # print(legible_datetime,"\n")

            event = {
                "time": legible_datetime,
                "mag": element["properties"]["mag"],
                "magType": element["properties"]["magType"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": element["properties"]["auth"],
                "preliminary": element["properties"]["preliminary"],
            }
            self.template_event(event)

    def template_event(self, event):
        """Send Event to Chanel"""
        event_location = [event["lat"], event["lon"]]
        if event["mag"] >= MAG_THRESHOLD:
            if event["preliminary"] == True:
                template = (
                    f"<b>{event['auth']} | {event['magType']} {event['mag']} (PRELIMINAR) | Depth: {event['depth']} Km </b>\n\n"
                    f"<pre>{event['place']}</pre>\n\n"
                    f"<i>{event['time']}</i>\n\n"
                )
            else:
                template = (
                    f"<b>{event['auth']} | {event['magType']} {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
                    f"<pre>{event['place']}</pre>\n\n"
                    f"<i>{event['time']}</i>\n\n"
                )

            asyncio.run(bot.send_update(template, event_location))


class UsgsBotParse:
    """Parse Class For USGS Events"""

    def __init__(self):
        pass

    def parse_event(self, data):
        """For each event Create a template"""
        for element in data:

            datetime_obj = datetime.strptime(
                element["properties"]["time"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            legible_datetime = (
                datetime.strftime(datetime_obj, "%d-%m-%Y, %H:%M") + " UTC"
            )

            event = {
                "time": legible_datetime,
                "mag": element["properties"]["mag"],
                "magType": element["properties"]["magType"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "status": element["properties"]["status"],
                "sig": element["properties"]["sig"],
                "tsunami": element["properties"]["tsunami"],
                "url": element["properties"]["url"],
            }
            self.template_event(event)

    def template_event(self, event):
        """Send Event to Chanel"""
        event_location = [event["lat"], event["lon"]]
        if event["mag"] >= MAG_THRESHOLD:
            template = (
                f"<b>USGS | {event['magType']} {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
                f"<pre>{event['place']}</pre>\n\n"
                f"<i>{event['time']}</i>\n\n"
                f"<pre>Status: {event['status']}, SIG: {event['sig']}</pre>\n\n"
                f"<a href='{event['url']}'>USGS URL</a>"
            )

            asyncio.run(bot.send_update(template, event_location))


class EmscBotParse:
    """Parse Class For EMSC Events"""

    def __init__(self):
        pass

    async def parse_event(self, data):
        """For each event Create a template"""
        for element in data:
            datetime_obj = datetime.strptime(
                element["properties"]["time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            legible_datetime = (
                datetime.strftime(datetime_obj, "%d-%m-%Y, %H:%M") + " UTC"
            )
            event = {
                "time": legible_datetime,
                "mag": element["properties"]["mag"],
                "magType": element["properties"]["magType"],
                "place": element["properties"]["place"],
                "depth": abs(element["geometry"]["coordinates"][2]),
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": element["properties"]["auth"],
            }
            print(event)
            await self.template_event(event)

    async def template_event(self, event):
        """Send Event to Chanel"""
        event_location = [event["lat"], event["lon"]]
        if event["mag"] >= MAG_THRESHOLD:
            template = (
                f"<b>{event['auth']} | {event['magType']} {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
                f"<pre>{event['place']}</pre>\n\n"
                f"<i>{event['time']}</i>\n\n"
            )

            await bot.send_update(template, event_location)
