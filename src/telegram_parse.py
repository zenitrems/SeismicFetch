"""
Telegram Bot Parse events
"""
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from telegram_bot import MyBot

load_dotenv()
bot = MyBot()


class SsnBotParse:
    """Telegram chanel Events"""

    def __init__(self) -> None:
        pass

    def parse_event(self, data):
        """Parse event text"""
        for element in data:
            local_timestamp = datetime.strptime(
                element["fecha"] + " " + element["hora"], "%Y-%m-%d %H:%M:%S"
            )
            event = {
                "utc_timestamp": element["timestamp_utc"],
                "local_timestamp": local_timestamp,
                "mag": element["magnitud"],
                "place": element["referencia"],
                "depth": element["profundidad"],
                "lat": element["latitud"],
                "lon": element["longitud"],
                "net": "SSN",
            }
            message_template(event)


class UsgsBotParse:
    """Telegram chanel Events"""

    def __init__(self) -> None:
        pass

    def parse_event(self, data):
        """Parse event text"""
        for element in data:
            event = {
                "utc_timestamp": element["properties"]["time"],
                "local_timestamp": element["local_timestamp"],
                "mag": element["properties"]["mag"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "net": "USGS",
            }
            message_template(event)


class EmscBotParse:
    """Telegram chanel Events"""

    def __init__(self) -> None:
        pass

    def parse_event(self, data):
        """Parse event text"""
        for element in data:
            event = {
                "utc_timestamp": element["properties"]["time"],
                "local_timestamp": element["local_timestamp"],
                "mag": element["properties"]["mag"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "net": "EMSC",
            }
            # telegramBot.main(event)


def message_template(event):
    """Send Event to Chanel"""
    seismic_url = f"https://seismic.duckdns.org/#6/{event['lat']}/{event['lon']}"
    if event["mag"] >= 4.3:
        template = (
            f"<b>{event['net']} | Mag: {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
            f"<pre>{event['place']}</pre>\n\n"
            f"<i>{event['local_timestamp']}</i>\n"
            f"<i>{event['utc_timestamp']}</i>\n\n"
            f"<a href='{seismic_url}'>Seismic Map</a>"
        )

        asyncio.run(bot.send_evento(template))
