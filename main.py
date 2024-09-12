#!/usr/bin/env python3.11
"""
Fernando Martinez @zenitrems 

SeismicFetch Main
"""
import threading
import sys
import signal
import time
from tornado.ioloop import IOLoop
from src import helpers, fetch_ssn, fetch_usgs, emsc_client
from src.db import get_mongo_db

logger = helpers.logger


class ScriptStart:
    """Start Main Process"""

    def __init__(self) -> None:
        self.shutdown_event = threading.Event()  # Event for graceful shutdown
        self.threads = []  # Keep track of threads
        self.main()

    def ssn_fetch(self):
        """Fetch SSN Feed"""
        try:
            logger.info("Fetching SSN")
            while not self.shutdown_event.is_set():
                fetch_ssn.main()
                time.sleep(60)  # Add a delay between fetches to avoid rapid polling
        except Exception as e:
            logger.error(f"Error in SSN Fetch: {e}")

    def usgs_fetch(self):
        """Fetch USGS Feed"""
        try:
            logger.info("Fetching USGS")
            while not self.shutdown_event.is_set():
                fetch_usgs.main()
                time.sleep(60)  # Add a delay between fetches to avoid rapid polling
        except Exception as e:
            logger.error(f"Error in USGS Fetch: {e}")

    def emsc_socket(self):
        """Start EMSC Client"""
        try:
            ioloop = IOLoop.instance()
            emsc_client.launch_client()
            ioloop.start()
        except Exception as e:
            logger.error(f"Error in EMSC Client: {e}")

    def main(self):
        """Main Function"""
        # Launch threads
        self.threads = [
            threading.Thread(target=self.ssn_fetch, daemon=True),
            threading.Thread(target=self.usgs_fetch, daemon=True),
            threading.Thread(target=self.emsc_socket, daemon=True),
        ]

        for thread in self.threads:
            thread.start()

        try:
            while any(thread.is_alive() for thread in self.threads):
                for thread in self.threads:
                    thread.join(timeout=1)  # Use timeout to allow interruption
        except (KeyboardInterrupt, SystemExit):
            logger.info("KeyboardInterrupt received. Shutting down...")
            self.stop()  # Gracefully stop all services

    def stop(self):
        """Stop the main process"""
        logger.info("Stopping fetch processes...")
        self.shutdown_event.set()  # Signal threads to stop
        IOLoop.current().stop()  # Stop the Tornado IOLoop


def handle_shutdown(signum, frame, script):
    """Handle shutdown signals"""
    logger.info(
        f"Received shutdown signal ({signal.strsignal(signum)}). Cleaning up..."
    )
    script.stop()  # Gracefully stop all services
    get_mongo_db.db_close()  # Close MongoDB connection
    sys.exit(0)


if __name__ == "__main__":
    seismic_script = ScriptStart()
    signal.signal(signal.SIGINT, lambda s, f: handle_shutdown(s, f, seismic_script))
    signal.signal(signal.SIGTERM, lambda s, f: handle_shutdown(s, f, seismic_script))
