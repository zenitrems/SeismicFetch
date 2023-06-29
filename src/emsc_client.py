"""
EMSC Websocket Client
wss://www.seismicportal.eu/standing_order/websocket
"""
from __future__ import unicode_literals
import json
from tornado.websocket import websocket_connect, WebSocketError
from tornado.ioloop import IOLoop
from tornado import gen

from helpers import EmscUtils, logger


ECHO_URI = "wss://www.seismicportal.eu/standing_order/websocket"
PING_INTERVAL = 15


emsc_utils = EmscUtils()

class WebSocketClient:
    """Tornado Websocket client"""

    def __init__(self) -> None:
        pass

    def process_event(self, message):
        """Process Event"""
        try:
            data = json.loads(message)
            emsc_utils.process_data(data)
        except json.JSONDecodeError:
            logger.exception(json.JSONDecodeError)


    @gen.coroutine
    def listen_events(self, web_socket):
        """Listen to events"""
        while True:
            msg = yield web_socket.read_message()
            if msg is None:
                logger.info("close")
                web_socket = None
                break
            self.process_event(msg)


    @gen.coroutine
    def launch_client(self):
        """Launch Web Socket Client"""
        try:
            logger.info(
                f"Open connection to: {ECHO_URI} ping:{PING_INTERVAL}",
            )
            web_socket = yield websocket_connect(ECHO_URI, ping_interval=PING_INTERVAL)
        except WebSocketError:
            logger.exception(WebSocketError)
        else:
            logger.info("listening to events")
            self.listen_events(web_socket)


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    client = WebSocketClient()
    client.launch_client()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logger.info("Close WebSocket")
        ioloop.stop()
