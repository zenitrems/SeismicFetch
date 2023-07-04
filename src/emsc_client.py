"""
EMSC Websocket Client
www.seismicportal.eu
"""
from __future__ import unicode_literals
import json
from tornado.websocket import websocket_connect, WebSocketError
from tornado.ioloop import IOLoop
from tornado import gen
from telegram_parse import EmscBotParse

from helpers import EmscUtils, logger
bot_action = EmscBotParse()

ECHO_URI = "wss://www.seismicportal.eu/standing_order/websocket"
PING_INTERVAL = 15


emsc_utils = EmscUtils()


def process_event(message):
    """Process Event"""
    try:
        data = json.loads(message)
        new_events = emsc_utils.process_data(data)
        if new_events:
            bot_action.parse_event(new_events)
    except json.JSONDecodeError:
        logger.exception(json.JSONDecodeError)


@gen.coroutine
def listen_events(web_socket):
    """Listen to events"""
    while True:
        msg = yield web_socket.read_message()
        if msg is None:
            logger.info("close")
            web_socket = None
            break
        process_event(msg)


@gen.coroutine
def launch_client():
    """Launch Web Socket Client"""
    try:
        logger.info(
            f"Open connection to EMSC Ping: {PING_INTERVAL}",
        )
        web_socket = yield websocket_connect(ECHO_URI, ping_interval=PING_INTERVAL)
    except WebSocketError:
        logger.exception(WebSocketError)
    else:
        listen_events(web_socket)


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    launch_client()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logger.info("Close Client")
        ioloop.stop()
