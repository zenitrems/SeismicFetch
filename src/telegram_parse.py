"""
Telegram Bot Parse events
"""
import asyncio
from dotenv import load_dotenv
from telegram_bot import MyBot

load_dotenv()
bot = MyBot()
MAG_THRESHOLD = float(4.3)


class SsnBotParse:
    """Telegram chanel Events"""

    def __init__(self):
        pass

    def parse_event(self, data):
        """Parse event text"""
        for element in data:
            event = {
                "time": element["properties"]["time"],
                "mag": element["properties"]["mag"],
                "magType": element["properties"]["magType"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": element["properties"]["auth"],
            }
            self.template_event(event)

    def template_event(self, event):
        """Send Event to Chanel"""
        if event["mag"] >= MAG_THRESHOLD:
            template = (
                f"<b>{event['auth']} | {event['magType']} {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
                f"<pre>{event['place']}</pre>\n\n"
                f"<i>{event['time']}</i>\n\n"
            )
            asyncio.run(bot.send_evento(template))


class UsgsBotParse:
    """Telegram chanel Events"""

    def __init__(self):
        pass

    def parse_event(self, data):
        """Parse event text"""
        for element in data:
            event = {
                "time": element["properties"]["time"],
                "mag": element["properties"]["mag"],
                "magType": element["properties"]["magType"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": "USGS",
            }
            self.template_event(event)

    def template_event(self, event):
        """Send Event to Chanel"""
        if event["mag"] >= MAG_THRESHOLD:
            template = (
                f"<b>{event['auth']} | {event['magType']} {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
                f"<pre>{event['place']}</pre>\n\n"
                f"<i>{event['time']}</i>\n\n"
            )

            asyncio.run(bot.send_evento(template))


class EmscBotParse:
    """Telegram chanel Events"""

    def __init__(self):
        pass

    async def parse_event(self, data):
        """Parse event text"""
        for element in data:
            event = {
                "time": element["properties"]["time"],
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
        if event["mag"] >= MAG_THRESHOLD:
            template = (
                f"<b>{event['auth']} | {event['magType']} {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
                f"<pre>{event['place']}</pre>\n\n"
                f"<i>{event['time']}</i>\n\n"
            )

            await bot.send_evento(template)
