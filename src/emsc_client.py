"""
EMSC Websocket Client
www.seismicportal.eu
"""

from __future__ import unicode_literals
import json
from tornado.websocket import websocket_connect, WebSocketError, WebSocketClosedError
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import to_asyncio_future
from tornado import gen
from src import helpers, telegram_parse


bot_action = telegram_parse.EmscBotParse()

ECHO_URI = "wss://www.seismicportal.eu/standing_order/websocket"
PING_INTERVAL = 15
RETRY_INTERVAL = 5


emsc_utils = helpers.EmscUtils()
logger = helpers.logger


def process_event(message):
    """Process New Events"""
    try:
        data = json.loads(message)
        new_events = emsc_utils.process_data(data)
        if new_events:
            to_asyncio_future(bot_action.parse_event(new_events))
    except json.JSONDecodeError:
        logger.exception(json.JSONDecodeError)


@gen.coroutine
def listen_events(web_socket):
    """Listen to events"""
    while True:
        try:
            msg = yield web_socket.read_message()
            if msg is None:
                logger.warning("No message received, attempting to reconnect...")
                raise WebSocketClosedError
            process_event(msg)

        except WebSocketClosedError:
            logger.info(
                "Disconnected. Reconnecting in {} seconds...".format(RETRY_INTERVAL)
            )
            yield gen.sleep(RETRY_INTERVAL)
            try:
                web_socket = yield websocket_connect(
                    ECHO_URI, ping_interval=PING_INTERVAL
                )
                logger.info("Reconected successfully")
            except WebSocketClosedError:
                logger.exception(WebSocketClosedError)


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

    listen_events(web_socket)


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    launch_client()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logger.info("Close Client")
        ioloop.stop()
