#!/usr/bin/env python3
"""
Fernando Martinez 
@zenitrems 

SeismicFetch init
"""
import threading
import sys
import signal

from tornado.ioloop import IOLoop
from src import helpers, get_mongo_db, fetch_ssn, fetch_usgs, emsc_client

logger = helpers.logger


class ScriptStart:
    """Start Main Process"""

    def __init__(self) -> None:
        self.main()

    def ssn_fetch(self):
        """Fetch USGS Feed"""
        logger.info("Fetching SSN")
        fetch_ssn.main()

    def usgs_fetch(self):
        """Fetch USGS Feed"""
        logger.info("Fetching USGS")
        fetch_usgs.main()

    def emsc_socket(self):
        """Start EMSC Client"""
        ioloop = IOLoop.instance()
        emsc_client.launch_client()
        ioloop.start()

    def main(self):
        """Main Function"""
        thread_0 = threading.Thread(target=self.ssn_fetch)
        thread_1 = threading.Thread(target=self.usgs_fetch)
        thread_2 = threading.Thread(target=self.emsc_socket)

        thread_0.start()
        thread_1.start()
        thread_2.start()

        thread_0.join()
        thread_1.join()
        thread_2.join()


def stop_handler(signal, frame):
    """Stop Program"""
    logger.info("stopping")
    get_mongo_db.db_close()
    IOLoop.current().stop()
    sys.exit(0)


signal.signal(signal.SIGINT, stop_handler)

if __name__ == "__main__":
    ScriptStart()
