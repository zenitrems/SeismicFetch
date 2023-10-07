import unittest
from unittest.mock import MagicMock
from src import telegram_parse


class TestSsnBotParse(unittest.TestCase):
    def setUp(self):
        self.ssn_parse = telegram_parse.SsnBotParse()

    def test_parse_event(self):
        """Test DataParse Function"""
        data = [
            {
                "properties": {
                    "time": "2023-10-07T12:34:56",
                    "mag": 8.0,
                    "magType": "mb",
                    "place": "Test Place",
                    "auth": "Test Auth",
                    "preliminary": True,
                },
                "geometry": {"coordinates": [0.0, 0.0, 10.0]},
            }
        ]

        # Mock para el metodo template_event
        self.ssn_parse.template_event = MagicMock()

        self.ssn_parse.parse_event(data)
        self.ssn_parse.template_event.assert_called_with(
            {
                "time": "2023-10-07T12:34:56",
                "mag": 8.0,
                "magType": "mb",
                "place": "Test Place",
                "depth": 10.0,
                "lat": 0.0,
                "lon": 0.0,
                "auth": "Test Auth",
                "preliminar": True,
            }
        )

    def test_template_event(self):
        # Mock para la función asyncio.run(bot.send_evento)
        bot = MagicMock()
        bot.send_evento = MagicMock()
        # Llama a la función que deseas probar
        self.ssn_parse.template_event(
            {
                "time": "2023-10-07T12:34:56",
                "mag": 8.0,
                "magType": "mb",
                "place": "Test Place",
                "depth": 10.0,
                "lat": 0.0,
                "lon": 0.0,
                "auth": "Test Auth",
                "preliminar": True,
            }
        )
        # Verifica que asyncio.run(bot.send_evento) se haya llamado con el argumento correcto
        """ bot.send_evento.assert_called_with(
            f"<b> Test Auth| mb 8.0 | Depth: 10.0 Km </b>\n\n"
            f"<pre>Test Place</pre>\n\n"
            f"<i>2023-10-07T12:34:56</i>\n\n"
        ) """


if __name__ == "__main__":
    unittest.main()
