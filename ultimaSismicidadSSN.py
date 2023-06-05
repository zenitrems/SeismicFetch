import os
import json
import requests
import asyncio
import re
from dotenv import load_dotenv
from termcolor import colored
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from get_mongo_db import mongodb
from pymongo.errors import PyMongoError
from telegram.error import TelegramError
from telegram_bot import MyBot
load_dotenv()
token = os.getenv('TELEGRAM_KEY')
bot = MyBot(token)


async def consultar_ssn():
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

                profundidad_split = cells[3].text.split(" ")[0]

                magnitud_text = cells[0].text.split(' ')[0]
                if re.match(r'^PRELIMINAR', magnitud_text):
                    magnitud = magnitud_text.split(' ')[1]
                    es_preliminar = True
                else:
                    magnitud = magnitud_text
                    es_preliminar = False

                row_data = {
                    'fecha': datetime_span_texts[0].strip(),
                    'hora': datetime_span_texts[1].strip(),
                    'magnitud': float(magnitud),
                    'latitud': float(epi_span_texts[1]),
                    'longitud': float(epi_span_texts[2]),
                    'profundidad': float(profundidad_split),
                    'referencia': epi_span_texts[0].strip(),
                    'preliminar': es_preliminar
                }
                raw_data.append(row_data)
            json_data = json.dumps(raw_data, indent=4)
            await guardar_nuevos(json_data)
        else:
            print(f"error", {response})
    except Exception as e:
        print("error", str(e))


async def guardar_nuevos(json_data):
    dbname = mongodb()
    collection_name = dbname["sismos"]

    try:
        data_collection = list(collection_name.find())
        datos_existentes = data_collection
    except PyMongoError as e:
        print(colored(f"\nError en mongodb: {e}",
              "red", attrs=["blink", "reverse"]))
        datos_existentes = []

    fecha_hora_mas_reciente = None

    if datos_existentes:
        fecha_hora_mas_reciente = datetime.strptime(
            datos_existentes[-1]['fecha'] + " " + datos_existentes[-1]['hora'], "%Y-%m-%d %H:%M:%S")
        print(
            colored(f"\nÚltimo evento: {fecha_hora_mas_reciente} Hora Centro", 'yellow'))

    # obtener fechas y horas existentes
    fecha_limite = datetime.now() - timedelta(days=3)
    fechas_horas_existentes = set()
    for dato in datos_existentes:
        fecha_hora = datetime.strptime(
            dato['fecha'] + " " + dato['hora'], "%Y-%m-%d %H:%M:%S")
        fechas_horas_existentes.add(fecha_hora)

    # Filtrar y guardar nuevos
    nuevos_datos = []
    json_data_list = json.loads(json_data)
    for dato in json_data_list:
        fecha_hora_dato = datetime.strptime(
            dato['fecha'] + " " + dato['hora'], "%Y-%m-%d %H:%M:%S")
        if fecha_hora_dato >= fecha_limite and fecha_hora_dato not in fechas_horas_existentes:
            nuevos_datos.append(dato)

    if nuevos_datos:
        nuevos_datos.reverse()
        for evento in nuevos_datos:
            print(colored("\nNuevo evento detectado:", "red"),
                  json.dumps(evento, indent=4))
            try:
                await bot.send_evento(evento)
            except TelegramError as botError:
                print(colored(f"Error TelegramBot: {botError}",
                      "red", attrs=["blink", "reverse"]))
            try:
                collection_name.insert_one(evento)
            except PyMongoError as mongoError:
                print(colored(f"Error Mongo: {mongoError}",
                      "red", attrs=["blink", "reverse"]))


async def main():
    while True:
        print(colored("\nActualizando...", "yellow"))
        await consultar_ssn()
        print(colored("\nCompleto, Esperando...\n", 'green'))
        await asyncio.sleep(150)

if __name__ == '__main__':
    asyncio.run(main())
