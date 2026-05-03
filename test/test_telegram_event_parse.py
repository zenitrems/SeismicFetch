import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.telegram import telegram_parser


RUN_TELEGRAM_INTEGRATION = os.getenv("RUN_TELEGRAM_INTEGRATION") == "1"


class TestSsnBotParse(unittest.TestCase):
    def setUp(self) -> None:
        self.ssn_parse = telegram_parser.SsnBotParse()
        self.test_data = [
            {
                "_id": {"$oid": "64e8672ea69b44c678f10285"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-108.7, 20.68, 65]},
                "properties": {
                    "mag": 5.5,
                    "place": "275 km al SURESTE de CABO SAN LUCAS, BCS",
                    "time": "2023-08-25T07:24:16.000Z",
                    "preliminary": True,
                    "auth": "SSN",
                    "magType": "m",
                    "type": "earthquake",
                },
            }
        ]

        return super().setUp()

    def test_parse_event(self):
        """Test SSN DataParse Function."""
        self.ssn_parse.template_event = MagicMock()

        self.ssn_parse.parse_event(self.test_data)
        self.ssn_parse.template_event.assert_called_with(
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

    @patch.object(telegram_parser.bot, "send_update", new_callable=AsyncMock)
    def test_template_event_snapshot(self, send_update):
        """Visual mockup for the SSN Telegram message."""
        expected_message = (
            "<b>SSN - Sismo m 5.5</b>\n\n"
            "<pre>Ubicacion   : 275 km al SURESTE de CABO SAN LUCAS, BCS\n"
            "Fecha UTC   : 25-08-2023, 07:24 UTC\n"
            "Profundidad : 65 km\n"
            "Coordenadas : 20.6800, -108.7000\n"
            "Estado      : PRELIMINAR</pre>"
        )

        self.ssn_parse.template_event(
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

        send_update.assert_awaited_once_with(expected_message, [20.68, -108.7])

    @patch.object(telegram_parser.bot, "send_update", new_callable=AsyncMock)
    def test_template_event_ignores_events_below_threshold(self, send_update):
        self.ssn_parse.template_event(
            {
                "time": "25-08-2023, 07:24 UTC",
                "mag": 4.9,
                "magType": "m",
                "place": "275 km al SURESTE de CABO SAN LUCAS, BCS",
                "depth": 65,
                "lat": 20.68,
                "lon": -108.7,
                "auth": "SSN",
                "preliminary": False,
            }
        )

        send_update.assert_not_called()


class TestUsgsBotParse(unittest.TestCase):
    def setUp(self) -> None:
        self.usgs_parse = telegram_parser.UsgsBotParse()
        self.test_data = [
            {
                "_id": {"$oid": "652bcd61c51490aa1c879e65"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [49.5001, 31.1027, 10]},
                "properties": {
                    "mag": 5.3,
                    "place": "A < B & C",
                    "time": "2023-10-15T11:15:37.551",
                    "updated": "2023-10-15T11:29:32.040",
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
        """Test USGS DataParse Function."""
        self.usgs_parse.template_event = MagicMock()
        self.usgs_parse.parse_event(self.test_data)
        self.usgs_parse.template_event.assert_called_with(
            {
                "time": "15-10-2023, 11:15 UTC",
                "mag": 5.3,
                "magType": "mww",
                "place": "A < B & C",
                "depth": 10,
                "lat": 31.1027,
                "lon": 49.5001,
                "status": "reviewed",
                "sig": 432,
                "tsunami": 0,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9",
            }
        )

    @patch.object(telegram_parser.bot, "send_update", new_callable=AsyncMock)
    def test_template_event_snapshot_with_escaped_text(self, send_update):
        """Visual mockup for the USGS Telegram message."""
        expected_message = (
            "<b>USGS - Sismo mww 5.3</b>\n\n"
            "<pre>Ubicacion   : A &lt; B &amp; C\n"
            "Fecha UTC   : 15-10-2023, 11:15 UTC\n"
            "Profundidad : 10 km\n"
            "Coordenadas : 31.1027, 49.5001\n"
            "Estado      : reviewed\n"
            "SIG         : 432\n"
            "Tsunami     : 0</pre>\n\n"
            "<a href='https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9'>USGS URL</a>"
        )

        self.usgs_parse.template_event(
            {
                "time": "15-10-2023, 11:15 UTC",
                "mag": 5.3,
                "magType": "mww",
                "place": "A < B & C",
                "depth": 10,
                "lat": 31.1027,
                "lon": 49.5001,
                "status": "reviewed",
                "sig": 432,
                "tsunami": 0,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000lfq9",
            }
        )

        send_update.assert_awaited_once_with(expected_message, [31.1027, 49.5001])


class TestEmscBotParse(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.emsc_parse = telegram_parser.EmscBotParse()
        return super().setUp()

    async def test_parse_event(self):
        data = [
            {
                "_id": {"$oid": "652bcb43c51490aa1c879e62"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [49.4634, 31.1201, -11]},
                "properties": {
                    "time": "2023-10-15T11:15:38.310Z",
                    "updated": "2023-10-15T11:35:14.788Z",
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

        self.emsc_parse.template_event = AsyncMock()
        await self.emsc_parse.parse_event(data)
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

    @patch.object(telegram_parser.bot, "send_update", new_callable=AsyncMock)
    async def test_template_event_snapshot(self, send_update):
        """Visual mockup for the EMSC Telegram message."""
        expected_message = (
            "<b>EMSC - Sismo mw 5.3</b>\n\n"
            "<pre>Ubicacion   : WESTERN IRAN\n"
            "Fecha UTC   : 15-10-2023, 11:15 UTC\n"
            "Profundidad : 11 km\n"
            "Coordenadas : 31.1201, 49.4634</pre>"
        )

        await self.emsc_parse.template_event(
            {
                "time": "2023-10-15T11:15:38.310Z",
                "mag": 5.3,
                "magType": "mw",
                "place": "WESTERN IRAN",
                "depth": 11,
                "lat": 31.1201,
                "lon": 49.4634,
                "auth": "EMSC",
            }
        )

        send_update.assert_awaited_once_with(expected_message, [31.1201, 49.4634])


@unittest.skipUnless(
    RUN_TELEGRAM_INTEGRATION,
    "Set RUN_TELEGRAM_INTEGRATION=1 to send this parsed test message to Telegram.",
)
class TestTelegramChannelIntegration(unittest.TestCase):
    def test_send_parsed_message_to_telegram_channel(self):
        """Send the parsed visual mockup to the configured Telegram channel."""
        ssn_parse = telegram_parser.SsnBotParse()

        ssn_parse.template_event(
            {
                "time": "2026-04-30T12:00:00.000Z",
                "mag": 5.5,
                "magType": "m",
                "place": "MENSAJE DE PRUEBA - A < B & C",
                "depth": 10,
                "lat": 19.4326,
                "lon": -99.1332,
                "auth": "SSN",
                "preliminary": True,
            }
        )


if __name__ == "__main__":
    unittest.main()
