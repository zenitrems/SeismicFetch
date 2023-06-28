from __future__ import unicode_literals
import json
from loguru import logger
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
from tornado import gen

from utils import EmscUtils


ECHO_URI = "wss://www.seismicportal.eu/standing_order/websocket"
PING_INTERVAL = 15


emsc_utils = EmscUtils()


def myprocessing(message):
    """Process message"""
    try:
        data = json.loads(message)
        emsc_utils.process_data(data)
    except Exception:
        logger.exception("Unable to parse json message")


@gen.coroutine
def listen(ws):
    """Listen to Messages"""
    while True:
        msg = yield ws.read_message()
        if msg is None:
            logger.info("close")
            ws = None
            break
        myprocessing(msg)


@gen.coroutine
def launch_client():
    """Launch WebSocket Client"""
    try:
        logger.info(f"Open WebSocket connection to {ECHO_URI}", )
        ws = yield websocket_connect(ECHO_URI, ping_interval=PING_INTERVAL)
    except Exception:
        logger.exception("connection error")
    else:
        logger.info("Waiting for messages...")
        listen(ws)


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    launch_client()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logger.info("Close WebSocket")
        ioloop.stop()
