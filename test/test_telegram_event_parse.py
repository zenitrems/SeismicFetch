import unittest
from unittest.mock import MagicMock, patch
from src.telegram import telegram_parser


class TestSsnBotParse(unittest.TestCase):
    def setUp(self) -> None:
        self.ssn_parse = telegram_parser.SsnBotParse()
        return super().setUp()

    def test_parse_event(self):
        """Test DataParse Function"""
        data = [
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

        # Mock para el metodo template_event
        self.ssn_parse.template_event = MagicMock()

        self.ssn_parse.parse_event(data)
        self.ssn_parse.template_event.assert_called_with(
            {
                "time": "2023-08-25T07:24:16.000Z",
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

    def test_template_event(self):
        # Mock para la función asyncio.run(bot.send_evento)
        bot = MagicMock()
        bot.send_evento = MagicMock()
        # Llama a la función que deseas probar
        self.ssn_parse.template_event(
            {
                "time": "2023-08-25T07:24:16.000Z",
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
        # Verifica que asyncio.run(bot.send_evento) se haya llamado con el argumento correcto
        """ bot.send_evento.assert_called_with(
            f"<b> Test Auth| mb 8.0 | Depth: 10.0 Km </b>\n\n"
            f"<pre>Test Place</pre>\n\n"
            f"<i>2023-10-07T12:34:56</i>\n\n"
        ) """


class TestUsgsBotParse(unittest.TestCase):
    def setUp(self) -> None:
        self.usgs_parse = telegram_parser.UsgsBotParse()
        return super().setUp()

    def test_parse_event(self):
        """Test DataParse Function"""
        data = [
            {
                "_id": {"$oid": "652bcd61c51490aa1c879e65"},
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [49.5001, 31.1027, 10]},
                "properties": {
                    "mag": 5.3,
                    "place": "21 km SSW of Rāmhormoz, Iran",
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

        # Mock para el metodo template_event
        self.usgs_parse.template_event = MagicMock()
        self.usgs_parse.parse_event(data)
        self.usgs_parse.template_event.assert_called_with(
            {
                "time": "2023-10-15T11:15:37.551",
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

    def test_template_event(self):
        # Mock para la función asyncio.run(bot.send_evento)
        bot = MagicMock()
        bot.send_evento = MagicMock()
        # Llama a la función que deseas probar
        self.usgs_parse.template_event(
            {
                "time": "2023-10-15T11:15:37.551",
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


class TestEmscBotParse(unittest.TestCase):
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

        self.emsc_parse.template_event = MagicMock()
        await self.emsc_parse.parse_event(data)
        self.emsc_parse.template_event.assert_called_with(
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

    def test_template_event(self):
        bot = MagicMock()
        bot.send_evento = MagicMock()
        self.emsc_parse.template_event(
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


if __name__ == "__main__":
    unittest.main()
