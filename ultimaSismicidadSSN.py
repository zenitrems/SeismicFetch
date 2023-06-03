import time
import json
import requests
from termcolor import colored
from datetime import datetime
from bs4 import BeautifulSoup
from bson import ObjectId
from get_mongo_db import mongodb
from pymongo.errors import PyMongoError
from telegram_bot import MyBot


def consultar_ssn():
    try:
        response = requests.get("http://www.ssn.unam.mx/sismicidad/ultimos/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            raw_data = []
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                epi_span_tags = cells[2].find_all('span')
                epi_span_texts = [span.text for span in epi_span_tags]
                datetime_span_tags = cells[1].find_all('span')
                datetime_span_texts = [
                    span.text for span in datetime_span_tags]
                row_data = {
                    'fecha': datetime_span_texts[0].strip(),
                    'hora': datetime_span_texts[1].strip(),
                    'magnitud': cells[0].text,
                    'latitud': epi_span_texts[1].strip(),
                    'longitud': epi_span_texts[2].strip(),
                    'profundidad': cells[3].text.strip(),
                    'referencia': epi_span_texts[0].strip()
                }
                raw_data.append(row_data)
            json_data = json.dumps(raw_data, indent=4)
            guardar_nuevos(json_data)
        else:
            print(f"error", {response})
    except Exception as e:
        print("error", str(e))


def guardar_nuevos(json_data):
    dbname = mongodb()
    collection_name = dbname["sismos"]

    try:
        data_collection = list(collection_name.find())
        datos_existentes = data_collection
    except PyMongoError:
        print(colored(f"\nError en mongodb: {e}",
              "red", attrs=["blink", "reverse"]))
        datos_existentes = []

    # Obtener Fecha de mas reciente
    fecha_hora_mas_reciente = None
    if datos_existentes:
        fecha_hora_mas_reciente = datetime.strptime(
            datos_existentes[-1]['fecha'] + " " + datos_existentes[-1]['hora'], "%Y-%m-%d %H:%M:%S")
        print(
            colored(f"\nÚltimo evento: {fecha_hora_mas_reciente} Hora Centro", 'yellow'))

    # Filtrar y guardar nuevos
    nuevos_datos = []
    json_data_list = json.loads(json_data)
    for dato in json_data_list:
        fecha_hora_dato = datetime.strptime(
            dato['fecha'] + " " + dato['hora'], "%Y-%m-%d %H:%M:%S")
        if fecha_hora_mas_reciente is None or fecha_hora_dato > fecha_hora_mas_reciente:
            dato['_id'] = str(ObjectId())
            nuevos_datos.append(dato)

    if nuevos_datos:
        nuevos_datos.reverse()
        for evento in nuevos_datos:
            print(colored("\nNuevo evento detectado:", "red"),
            json.dumps(evento, indent=4))
            try:
                collection_name.insert_one(evento)
            except PyMongoError as e:
                print(colored(f"Error Mongo: {e}",
                      "red", attrs=["blink", "reverse"]))

    # Escribir Datos
    nuevos_datos.extend(datos_existentes)
    with open('ultima_sismicidad.json', 'w') as f:
        json.dump(nuevos_datos, f, indent=4)


while True:
    print(colored("\nActualizando...", "yellow"))
    consultar_ssn()
    print(colored("\nCompleto, Esperando...\n", 'green'))
    time.sleep(150)
