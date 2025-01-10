import unittest
from src import fetch_event_id
from src.helpers import logger
import logging

logging.basicConfig(level=logging.INFO)


class TestFetchId(unittest.TestCase):
    def setUp(self) -> None:
        self.fetch_id = fetch_event_id.fetch_by_id
        return super().setUp()

    def test_fetch_id(self):
        main_event = {"unid": "20170919_0000091", "source": "UNID", "out": "all"}
        response = self.fetch_id(main_event)
        logger.info(f"Response from fetch_by_id: {response}")
        # Add assertions for validation

        self.assertIsNotNone(response)
        self.assertIn("eventid", response)  # Example assertion
