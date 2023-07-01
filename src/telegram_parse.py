"""
Telegram Bot Parse events
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from helpers import logger
from telegram_bot import MyBot

load_dotenv()
bot = MyBot(os.getenv("TELEGRAM_KEY"))

logger.info("Telegram")


class SsnBotParse:
    """Telegram chanel Events"""

    def __init__(self) -> None:
        pass

    async def parse_event(self, data):
        """Parse event text"""
        local_timestamp = datetime.strptime(
            data["fecha"] + " " + data["hora"], "%Y-%m-%d %H:%M:%S"
        )
        event = {
            "utc_timestamp": data["timestamp_utc"],
            "local_timestamp": local_timestamp,
            "mag": data["magnitud"],
            "place": data["referencia"],
            "depth": data["profundidad"],
            "lat": data["latitud"],
            "lon": data["longitud"],
            "net": "SSN",
        }
        await message_template(event)


class UsgsBotParse:
    """Telegram chanel Events"""

    def __init__(self) -> None:
        pass

    async def parse_event(self, data):
        """Parse event text"""
        event = {
            "utc_timestamp": data["properties"]["time"],
            "local_timestamp": data["local_timestamp"],
            "mag": data["properties"]["mag"],
            "place": data["properties"]["place"],
            "depth": data["geometry"]["coordinates"][2],
            "lat": data["geometry"]["coordinates"][1],
            "lon": data["geometry"]["coordinates"][0],
            "net": "USGS",
        }
        await message_template(event)


class EmscBotParse:
    """Telegram chanel Events"""

    def __init__(self) -> None:
        pass

    async def parse_event(self, data):
        """Parse event text"""
        event = {
            "utc_timestamp": data["properties"]["time"],
            "local_timestamp": data["local_timestamp"],
            "mag": data["properties"]["mag"],
            "place": data["properties"]["place"],
            "depth": data["geometry"]["coordinates"][2],
            "lat": data["geometry"]["coordinates"][1],
            "lon": data["geometry"]["coordinates"][0],
            "net": "EMSC",
        }
        await message_template(event)


async def message_template(event):
    """Send Event to Chanel"""
    if event["mag"] >= 4:
        template = (
            f"<b>{event['net']}:</b>\n\n"
            f"<b>{event['place']}:</b>\n\n"
            f"<b>{event['local_timestamp']}</b>\n\n"
            f"<b>{event['utc_timestamp']}</b>\n"
            f"<b>{event['mag']}</b>\n"
            f"<b>Profundidad:</b> {event['depth']}\n"
        )
        await bot.send_evento(template)
