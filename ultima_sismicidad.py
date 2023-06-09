"""
Ultima Sismicidad SSN
Author: Fernando Martínez
github.com/zenitrems
2023
"""

import os
import sys
import json
import asyncio
import re
import time
from datetime import datetime, timedelta
from termcolor import colored
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from pymongo.errors import PyMongoError
from telegram.error import TelegramError
from get_mongo_db import mongodb
from telegram_bot import MyBot

load_dotenv()

token = os.getenv('TELEGRAM_KEY')
bot = MyBot(token)
dbname = mongodb()
collection_name = dbname["sismos"]


async def consultar_ssn():
    """Peticion de datos"""
    start = time.perf_counter()
    try:
        response = requests.get(
            "http://www.ssn.unam.mx/sismicidad/ultimos/", timeout=60)
        if response.status_code == 200:
            finish = time.perf_counter()
            print(colored(f"\nssn.unam.mx consultado en {finish - start:0.4f} segundos",
                          "yellow"))
            await buscar_datos(response)
        else:
            print(colored(
                f"Error consultando SSN\n {response.status_code}", "red", attrs=["reverse"], ),)
    except requests.Timeout as request_error:
        print(colored("Request Timeout: \n",
                      "red", attrs=["reverse"]), str(request_error))


async def buscar_datos(response):
    """Busca la ultima Actualizacion y la tabla de sismos """
    soup = BeautifulSoup(response.text, 'html.parser')
    footer = soup.find('footer')
    ssn_ultimo = footer.find("p", "update-time")
    ssn_ultimo_start_index = ssn_ultimo.text.find(
        "a las ") + len("a las ")
    ssn_ultimo_finish_index = ssn_ultimo.text.find(" (")
    ssn_ultimo_extract_date = ssn_ultimo.text[ssn_ultimo_start_index:ssn_ultimo_finish_index]
    ssn_ultima_actualizacion = ssn_ultimo_extract_date.replace(
        "  ", " ")
    print(colored(
        f"\nÚltima actualización SSN {ssn_ultima_actualizacion} Hora Centro", "yellow"))
    table = soup.find('table')
    rows = table.find_all('tr')
    await acomodar_datos(rows)


async def acomodar_datos(rows):
    """Acomoda las filas obtenidas de la tabla"""
    json_data = []
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
            is_preliminar = True
        else:
            magnitud = magnitud_text
            is_preliminar = False
        document = {
            'preliminar': is_preliminar,
            'fecha': datetime_span_texts[0].strip(),
            'hora': datetime_span_texts[1].strip(),
            'magnitud': float(magnitud),
            'latitud': float(epi_span_texts[1]),
            'longitud': float(epi_span_texts[2]),
            'profundidad': float(profundidad_split),
            'referencia': epi_span_texts[0].strip()
        }
        json_data.append(document)
    datos_nuevos = json.dumps(json_data, indent=4)
    await buscar_existentes(datos_nuevos)


async def buscar_existentes(datos_nuevos):
    """busca datos existentes"""
    try:
        datos_existentes = []
        oneday = datetime.now() - timedelta(days=5)
        oneday_str = oneday.strftime("%Y-%m-%d")
        data_collection = list(collection_name.find(
            {"fecha": {"$gte": oneday_str}}))
        datos_existentes = data_collection

        fecha_hora_mas_reciente = None

        if datos_existentes:
            fecha_existente = datos_existentes[-1]['fecha']
            hora_existente = datos_existentes[-1]['hora']
            fecha_hora_mas_reciente = datetime.strptime(
                fecha_existente + " " + hora_existente, "%Y-%m-%d %H:%M:%S")
            print(
                colored(f"\nÚltimo evento: {fecha_hora_mas_reciente} Hora Centro", 'yellow'))
            await comparar_datos(datos_existentes, datos_nuevos)

    except PyMongoError as mongo_error:
        print(colored("mongo error: \n",
                      "red", attrs=["reverse"]), str(mongo_error))
        try:
            await bot.send_error("Error en mongo script terminado")
        except TelegramError as bot_error:
            print(colored("Error TelegramBot:\n",
                          "red", attrs=["blink", "reverse"]), str(bot_error))
        sys.exit()


async def comparar_datos(datos_existentes, datos_nuevos):
    """Compara los datos nuevos con los existentes"""
    # obtener fechas y horas existentes
    fecha_limite = datetime.now() - timedelta(days=3)
    fechas_horas_existentes = set()
    for dato in datos_existentes:
        fecha_hora = datetime.strptime(
            dato['fecha'] + " " + dato['hora'], "%Y-%m-%d %H:%M:%S")
        fechas_horas_existentes.add(fecha_hora)
    # Filtrar y guardar nuevos
    nuevos_datos = []
    json_data_list = json.loads(datos_nuevos)
    for dato in json_data_list:
        fecha_hora_dato = datetime.strptime(
            dato['fecha'] + " " + dato['hora'], "%Y-%m-%d %H:%M:%S")
        if fecha_hora_dato >= fecha_limite and fecha_hora_dato not in fechas_horas_existentes:
            nuevos_datos.append(dato)
    if nuevos_datos:
        nuevos_datos.reverse()
        await guardar_nuevos(nuevos_datos)
    else:
        print(colored("\nSin nuevos eventos", "yellow"))


async def guardar_nuevos(nuevos_datos):
    """Guarda nuevos en mongo"""
    try:
        for evento in nuevos_datos:
            collection_name.insert_one(evento)
            print(colored(f"Nuevo evento detectado\n {evento}", "red"),)
            if evento['magnitud'] >= 4.0:
                try:
                    await bot.send_evento(evento)
                except TelegramError as bot_error:
                    print(colored("Error TelegramBot:\n",
                                  "red", attrs=["blink", "reverse"]), str(bot_error))

    except PyMongoError as mongo_error:
        print(colored("mongo error: \n", "red",
              attrs=["reverse"]), str(mongo_error))
        try:
            await bot.send_error("Error en mongo script terminado")
        except TelegramError as bot_error:
            print(colored("Error TelegramBot:\n", "red",
                  attrs=["blink", "reverse"]), str(bot_error))
        sys.exit()


async def main():
    """Main function"""
    while True:
        print(colored("\nActualizando...", "green"))
        await consultar_ssn()
        print(colored("\nEsperando...\n", 'green'))
        await asyncio.sleep(300)

if __name__ == '__main__':
    asyncio.run(main())
