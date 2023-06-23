"""
Mongo Client
"""
from pymongo import MongoClient, monitoring


class CustomCommandLogger(monitoring.CommandListener):
    """Custom"""

    def started(self, event):
        print(f"Comando MongoDB iniciado: {event.command_name}")

    def succeeded(self, event):
        print(f"Comando MongoDB exitoso: {event.command_name}")

    def failed(self, event):
        print(f"Comando MongoDB fallido: {event.command_name}")


# Configura el logger personalizado
command_logger = CustomCommandLogger()


def mongodb():
    """Mongo init"""
    client = MongoClient("mongodb://localhost", event_listeners=[command_logger])
    return client["sismicidad"]


if __name__ == "__main__":
    dbname = mongodb()
