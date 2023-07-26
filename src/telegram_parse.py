"""
Telegram Bot Parse events
"""
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
            event = {
                "time": element["properties"]["time"],
                "mag": element["properties"]["mag"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": element["properties"]["auth"],
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
                "time": element["properties"]["time"],
                "mag": element["properties"]["mag"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": "USGS",
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
                "time": element["properties"]["time"],
                "mag": element["properties"]["mag"],
                "place": element["properties"]["place"],
                "depth": element["geometry"]["coordinates"][2],
                "lat": element["geometry"]["coordinates"][1],
                "lon": element["geometry"]["coordinates"][0],
                "auth": element["properties"]["auth"],
            }
            # telegramBot.main(event)


def message_template(event):
    """Send Event to Chanel"""
    seismic_url = f"https://seismic.duckdns.org/#6/{event['lat']}/{event['lon']}"
    if event["mag"] >= 4.3:
        template = (
            f"<b>{event['auth']} | Mag: {event['mag']} | Depth: {event['depth']} Km </b>\n\n"
            f"<pre>{event['place']}</pre>\n\n"
            f"<i>{event['time']}</i>\n\n"
            f"<a href='{seismic_url}'>Seismic Map</a>"
        )

        asyncio.run(bot.send_evento(template))
