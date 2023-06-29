"""
Mongo Client
"""
from pymongo import MongoClient, monitoring
from helpers import logger


class CustomCommandLogger(monitoring.CommandListener):
    """Custom"""

    def started(self, event):
        logger.trace(f"{event.command_name} Start")

    def succeeded(self, event):
        logger.trace(f"{event.command_name} Succeeded")

    def failed(self, event):
        logger.error(f"{event.command_name} Failed")


# Configura el logger personalizado
command_logger = CustomCommandLogger()


def mongodb():
    """Mongo init"""
    client = MongoClient("mongodb://localhost", event_listeners=[command_logger])
    return client["sismicidad"]


if __name__ == "__main__":
    dbname = mongodb()
