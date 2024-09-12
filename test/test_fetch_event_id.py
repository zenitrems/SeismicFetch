import unittest
from src import fetch_event_id

class TestFetchId(unittest.TestCase):
    def setUp(self) -> None:
        self.fetch_id = fetch_event_id.fetch_by_id
        return super().setUp()
    
    def test_fetch_id(self):
        main_event = {'unid':'20170919_0000091', 'source': 'UNID', 'out': 'all'}
        self.fetch_id(main_event)