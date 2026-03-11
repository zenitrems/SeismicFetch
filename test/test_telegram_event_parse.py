import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.telegram import telegram_parser


class TestSsnBotParse(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = MagicMock()
        self.bot.send_update = AsyncMock()
        self.ssn_parse = telegram_parser.SsnBotParse(bot_action=self.bot)
        self.test_data = [
            {
                "_id": {"$oid": "64e8672ea69b44c678f10285"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-108.7, 20.68, 65]},
                "properties": {
                    "mag": 5.5,
                    "place": "275 km al SURESTE de CABO SAN LUCAS, BCS",
                    "time": datetime(2023, 8, 25, 7, 24, 16),
                    "preliminary": True,
                    "auth": "SSN",
                    "magType": "m",
                    "type": "earthquake",
                },
            }
        ]
        return super().setUp()

    def test_parse_event(self):
        self.ssn_parse.template_event = MagicMock()

        self.ssn_parse.parse_event(self.test_data)

        self.ssn_parse.template_event.assert_called_once_with(
            {
                "time": "25-08-2023, 07:24 UTC",
                "mag": 5.5,
                "magType": "m",
                "place": "275 km al SURESTE de CABO SAN LUCAS, BCS",
                "depth": 65,
                "lat": 20.68,
                "lon": -108.7,
                "auth": "SSN",
                "preliminary": True,
            }
        )

    def test_template_event_sends_message_when_above_threshold(self):
        event = {
            "time": "25-08-2023, 07:24 UTC",
            "mag": 5.5,
            "magType": "m",
            "place": "275 km al SURESTE de CABO SAN LUCAS, BCS",
            "depth": 65,
            "lat": 20.68,
            "lon": -108.7,
            "auth": "SSN",
            "preliminary": True,
        }

        with patch(
            "src.telegram.telegram_parser.asyncio.run",
            side_effect=lambda coro: coro.close(),
        ) as asyncio_run:
            self.ssn_parse.template_event(event)

        asyncio_run.assert_called_once()
        self.bot.send_update.assert_called_once_with(
            "<b>SSN | m 5.5 (PRELIMINAR) | Depth: 65 Km </b>\n\n"
            "<pre>275 km al SURESTE de CABO SAN LUCAS, BCS</pre>\n\n"
            "<i>25-08-2023, 07:24 UTC</i>\n\n",
            [20.68, -108.7],
        )

    def test_template_event_skips_below_threshold(self):
        event = {
            "time": "25-08-2023, 07:24 UTC",
            "mag": 4.9,
            "magType": "m",
            "place": "CABO SAN LUCAS, BCS",
            "depth": 65,
            "lat": 20.68,
            "lon": -108.7,
            "auth": "SSN",
            "preliminary": False,
        }

        with patch("src.telegram.telegram_parser.asyncio.run") as asyncio_run:
            self.ssn_parse.template_event(event)

        asyncio_run.assert_not_called()


class TestUsgsBotParse(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = MagicMock()
        self.bot.send_update = AsyncMock()
        self.usgs_parse = telegram_parser.UsgsBotParse(bot_action=self.bot)
        self.test_data = [
            {
                "_id": {"$oid": "652bcd61c51490aa1c879e65"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [49.5001, 31.1027, 10]},
                "properties": {
                    "mag": 5.3,
                    "place": "21 km SSW of Rāmhormoz, Iran",
                    "time": datetime(2023, 10, 15, 11, 15, 37, 551000),
                    "updated": datetime(2023, 10, 15, 11, 29, 32, 40000),
                    "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9",
                    "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/us6000lfq9.geojson",
                    "status": "reviewed",
                    "tsunami": 0,
                    "sig": 432,
                    "net": "us",
                    "code": "6000lfq9",
                    "ids": ",us6000lfq9,",
                    "sources": ",us,",
                    "types": ",moment-tensor,origin,phase-data,",
                    "nst": 103,
                    "dmin": 5.383,
                    "rms": 0.8,
                    "gap": 48,
                    "magType": "mww",
                    "type": "earthquake",
                },
                "id": "us6000lfq9",
            }
        ]
        return super().setUp()

    def test_parse_event(self):
        self.usgs_parse.template_event = MagicMock()

        self.usgs_parse.parse_event(self.test_data)

        self.usgs_parse.template_event.assert_called_once_with(
            {
                "time": "15-10-2023, 11:15 UTC",
                "mag": 5.3,
                "magType": "mww",
                "place": "21 km SSW of Rāmhormoz, Iran",
                "depth": 10,
                "lat": 31.1027,
                "lon": 49.5001,
                "status": "reviewed",
                "sig": 432,
                "tsunami": 0,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9",
            }
        )

    def test_template_event_sends_message_when_above_threshold(self):
        event = {
            "time": "15-10-2023, 11:15 UTC",
            "mag": 5.3,
            "magType": "mww",
            "place": "21 km SSW of Rāmhormoz, Iran",
            "depth": 10,
            "lat": 31.1027,
            "lon": 49.5001,
            "status": "reviewed",
            "sig": 432,
            "tsunami": 0,
            "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9",
        }

        with patch(
            "src.telegram.telegram_parser.asyncio.run",
            side_effect=lambda coro: coro.close(),
        ) as asyncio_run:
            self.usgs_parse.template_event(event)

        asyncio_run.assert_called_once()
        self.bot.send_update.assert_called_once_with(
            "<b>USGS | mww 5.3 | Depth: 10 Km </b>\n\n"
            "<pre>21 km SSW of Rāmhormoz, Iran</pre>\n\n"
            "<i>15-10-2023, 11:15 UTC</i>\n\n"
            "<pre>Status: reviewed, SIG: 432</pre>\n\n"
            "<a href='https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9'>USGS URL</a>",
            [31.1027, 49.5001],
        )


class TestEmscBotParse(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.bot = MagicMock()
        self.bot.send_update = AsyncMock()
        self.emsc_parse = telegram_parser.EmscBotParse(bot_action=self.bot)
        self.data = [
            {
                "_id": {"$oid": "652bcb43c51490aa1c879e62"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [49.4634, 31.1201, -11]},
                "properties": {
                    "time": datetime(2023, 10, 15, 11, 15, 38, 310000),
                    "updated": datetime(2023, 10, 15, 11, 35, 14, 788000),
                    "place": "WESTERN IRAN",
                    "mag": 5.3,
                    "magType": "mw",
                    "evType": "ke",
                    "auth": "EMSC",
                    "source_id": "1566312",
                    "source_catalog": "EMSC-RTS",
                    "unid": "20231015_0000088",
                },
                "id": "20231015_0000088",
            }
        ]
        return super().setUp()

    async def test_parse_event(self):
        self.emsc_parse.template_event = AsyncMock()

        await self.emsc_parse.parse_event(self.data)

        self.emsc_parse.template_event.assert_awaited_once_with(
            {
                "time": "15-10-2023, 11:15 UTC",
                "mag": 5.3,
                "magType": "mw",
                "place": "WESTERN IRAN",
                "depth": 11,
                "lat": 31.1201,
                "lon": 49.4634,
                "auth": "EMSC",
            }
        )

    async def test_template_event_sends_message_when_above_threshold(self):
        event = {
            "time": "15-10-2023, 11:15 UTC",
            "mag": 5.3,
            "magType": "mw",
            "place": "WESTERN IRAN",
            "depth": 11,
            "lat": 31.1201,
            "lon": 49.4634,
            "auth": "EMSC",
        }

        await self.emsc_parse.template_event(event)

        self.bot.send_update.assert_awaited_once_with(
            "<b>EMSC | mw 5.3 | Depth: 11 Km </b>\n\n"
            "<pre>WESTERN IRAN</pre>\n\n"
            "<i>15-10-2023, 11:15 UTC</i>\n\n",
            [31.1201, 49.4634],
        )


if __name__ == "__main__":
    unittest.main()
