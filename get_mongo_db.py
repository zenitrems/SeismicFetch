"""
Mongo Client
"""
from pymongo import MongoClient, monitoring


class CustomCommandLogger(monitoring.CommandListener):
    """Custom"""

    def started(self, event):
        print("Comando MongoDB iniciado: %s" % (event.command_name))

    def succeeded(self, event):
        print("Comando MongoDB exitoso: %s" % (event.command_name))

    def failed(self, event):
        print("Comando MongoDB fallido: %s" % (event.command_name))


# Configura el logger personalizado
command_logger = CustomCommandLogger()


def mongodb():
    """Mongo init"""
    client = MongoClient("mongodb://localhost",
                         event_listeners=[command_logger])
    return client['sismicidad_SSN']


if __name__ == "__main__":
    dbname = mongodb()
