from __future__ import unicode_literals
import logging
import json
import sys

from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
from tornado import gen


ECHO_URI = "wss://www.seismicportal.eu/standing_order/websocket"
PING_INTERVAL = 15


# You can modify this function to run custom process on the message
def myprocessing(message):
    try:
        data = json.loads(message)
        info = data["data"]["properties"]
        print(data)
        info["action"] = data["action"]
        logging.info(
            ">>>> {action:7} event from {auth:7}, unid:{unid}, T0:{time}, Mag:{mag}, Region: {flynn_region}".format(
                **info
            )
        )
    except Exception:
        logging.exception("Unable to parse json message")


@gen.coroutine
def listen(ws):
    while True:
        msg = yield ws.read_message()
        if msg is None:
            logging.info("close")
            self.ws = None
            break
        myprocessing(msg)


@gen.coroutine
def launch_client():
    try:
        logging.info("Open WebSocket connection to %s", ECHO_URI)
        ws = yield websocket_connect(ECHO_URI, ping_interval=PING_INTERVAL)
    except Exception:
        logging.exception("connection error")
    else:
        logging.info("Waiting for messages...")
        listen(ws)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    ioloop = IOLoop.instance()
    launch_client()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logging.info("Close WebSocket")
        ioloop.stop()
