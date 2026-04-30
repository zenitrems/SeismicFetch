"""
Parse each event in the array to separate events above the magnitude threshold, 
and creates an HTML template to send to the telegram channel with specific data for each agency. 
"""

import asyncio
from html import escape
from datetime import datetime
from dotenv import load_dotenv
from src.telegram import telegram_bot

load_dotenv()
bot = telegram_bot.MyBot()
MAG_THRESHOLD = float(5.0)


def format_event_time(value):
    """Return a readable UTC timestamp from datetime or ISO strings."""
    if isinstance(value, datetime):
        date_value = value
    elif isinstance(value, str):
        iso_value = value.replace("Z", "+00:00")
        try:
            date_value = datetime.fromisoformat(iso_value)
        except ValueError:
            return value if value.endswith("UTC") else f"{value} UTC"
    else:
        return f"{value} UTC"

    return f"{date_value.strftime('%d-%m-%Y, %H:%M')} UTC"


def format_coordinates(lat, lon):
    """Format coordinates for compact Telegram display."""
    return f"{lat:.4f}, {lon:.4f}"


def format_event_message(event, agency=None):
    """Create the compact HTML message shown in Telegram."""
    event_agency = escape(str(agency or event.get("auth", "USGS")))
    mag_type = escape(str(event["magType"]))
    mag = escape(str(event["mag"]))
    status = event.get("status")

    if event.get("preliminary") is True:
        status = "PRELIMINAR"

    body_lines = [
        f"Ubicacion   : {escape(str(event['place']))}",
        f"Fecha UTC   : {escape(format_event_time(event['time']))}",
        f"Profundidad : {escape(str(event['depth']))} km",
        f"Coordenadas : {format_coordinates(event['lat'], event['lon'])}",
    ]

    if status is not None:
        body_lines.append(f"Estado      : {escape(str(status))}")

    if "sig" in event:
        body_lines.append(f"SIG         : {escape(str(event['sig']))}")

    if "tsunami" in event:
        body_lines.append(f"Tsunami     : {escape(str(event['tsunami']))}")

    message = (
        f"<b>{event_agency} - Sismo {mag_type} {mag}</b>\n\n"
        f"<pre>{chr(10).join(body_lines)}</pre>"
    )

    if event.get("url"):
        url = escape(str(event["url"]), quote=True)
        message += f"\n\n<a href='{url}'>USGS URL</a>"

    return message


class SsnBotParse:
    """Parse Class For SSN Events"""

    def __init__(self):
        pass

    def parse_event(self, data):
        """For each event Create a template"""
        for element in data:

            event = {
                "time": format_event_time(element["properties"]["time"]),
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
            template = format_event_message(event)
            asyncio.run(bot.send_update(template, event_location))


class UsgsBotParse:
    """Parse Class For USGS Events"""

    def __init__(self):
        pass

    def parse_event(self, data):
        """For each event Create a template"""
        for element in data:

            event = {
                "time": format_event_time(element["properties"]["time"]),
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
            template = format_event_message(event, agency="USGS")
            asyncio.run(bot.send_update(template, event_location))


class EmscBotParse:
    """Parse Class For EMSC Events"""

    def __init__(self):
        pass

    async def parse_event(self, data):
        """For each event Create a template"""
        for element in data:
            event = {
                "time": format_event_time(element["properties"]["time"]),
                "mag": element["properties"]["mag"],
                "magType": element["properties"]["magType"],
                "place": element["properties"]["place"],
                "depth": abs(element["geometry"]["coordinates"][2]),
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": element["properties"]["auth"],
            }
            await self.template_event(event)

    async def template_event(self, event):
        """Send Event to Chanel"""
        event_location = [event["lat"], event["lon"]]
        if event["mag"] >= MAG_THRESHOLD:
            template = format_event_message(event)
            await bot.send_update(template, event_location)
