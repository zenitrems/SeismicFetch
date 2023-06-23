"""
Ultima Sismicidad SSN
"""

import os
import sys
import asyncio
import time
from datetime import datetime, timedelta
import pytz
from termcolor import colored
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from pymongo.errors import PyMongoError
from telegram.error import TelegramError
from get_mongo_db import mongodb
from telegram_bot import MyBot

load_dotenv()

token = os.getenv("TELEGRAM_KEY")
bot = MyBot(token)
dbname = mongodb()
collection_name = dbname["sismicidad_ssn"]


async def consultar_ssn():
    """Peticion de datos"""
    start = time.perf_counter()
    try:
        response = requests.get(
            "http://www.ssn.unam.mx/sismicidad/ultimos/", timeout=60
        )
        if response.status_code == 200:
            finish = time.perf_counter()
            print(
                colored(
                    f"\nssn.unam.mx consultado en {finish - start:0.4f} segundos",
                    "yellow",
                )
            )
            await buscar_datos(response)
        else:
            print(
                colored(
                    f"Error consultando SSN\n {response.status_code}",
                    "red",
                    attrs=["reverse"],
                ),
            )
    except requests.Timeout as request_timeout:
        print(
            colored("Request Timeout: \n", "red", attrs=["reverse"]),
            str(request_timeout),
        )
    except requests.ConnectionError as request_conection_error:
        print(
            colored("Request Timeout: \n", "red", attrs=["reverse"]),
            str(request_conection_error),
        )


async def buscar_datos(response):
    """Busca la ultima Actualizacion y la tabla de sismos"""
    soup = BeautifulSoup(response.text, "html.parser")
    footer = soup.find("footer")
    ssn_ultimo = footer.find("p", "update-time")
    ssn_ultimo_start_index = ssn_ultimo.text.find("a las ") + len("a las ")
    ssn_ultimo_finish_index = ssn_ultimo.text.find(" (")
    ssn_ultimo_extract_date = ssn_ultimo.text[
        ssn_ultimo_start_index:ssn_ultimo_finish_index
    ]
    ssn_ultima_actualizacion = ssn_ultimo_extract_date.replace("  ", " ")
    print(
        colored(
            f"\nÚltima actualización SSN {ssn_ultima_actualizacion} Hora Centro",
            "yellow",
        )
    )
    table = soup.find("table")
    rows = table.find_all("tr")
    await acomodar_datos(rows)


async def acomodar_datos(rows):
    """Acomoda las filas obtenidas de la tabla"""
    json_data = []
    for row in rows[1:]:
        cells = row.find_all("td")
        epi_span_tags = cells[2].find_all("span")
        epi_span_texts = [span.text for span in epi_span_tags]
        datetime_span_tags = cells[1].find_all("span")
        datetime_span_texts = [span.text for span in datetime_span_tags]
        magnitud_text = cells[0].text

        fecha_hora_str = (
            f"{datetime_span_texts[0].strip()} {datetime_span_texts[1].strip()}"
        )
        fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
        utc_timestamp = fecha_hora.replace(
            tzinfo=pytz.timezone("America/Mexico_city")
        ).astimezone(pytz.timezone("UTC"))

        magnitud_parts = magnitud_text.split(" ")
        is_preliminar = (
            magnitud_parts[1] if magnitud_parts[0] == "PRELIMINAR" else False
        )
        magnitud = (
            float(magnitud_parts[1]) if is_preliminar else float(magnitud_parts[0])
        )

        document = {
            "preliminar": is_preliminar,
            "fecha": datetime_span_texts[0].strip(),
            "hora": datetime_span_texts[1].strip(),
            "timestamp_utc": utc_timestamp,
            "magnitud": magnitud,
            "latitud": float(epi_span_texts[1]),
            "longitud": float(epi_span_texts[2]),
            "profundidad": float(cells[3].text.split(" ")[0]),
            "referencia": epi_span_texts[0].strip(),
        }
        json_data.append(document)

    await buscar_existentes(json_data)


async def buscar_existentes(datos_nuevos):
    """busca datos existentes"""
    try:
        datos_existentes = []
        oneday = datetime.now() - timedelta(days=3)
        oneday_str = oneday.strftime("%Y-%m-%d")
        datos_existentes = list(collection_name.find({"fecha": {"$gte": oneday_str}}))

        fecha_hora_mas_reciente = None

        if datos_existentes:
            fecha_existente = datos_existentes[-1]["fecha"]
            hora_existente = datos_existentes[-1]["hora"]
            fecha_hora_mas_reciente = datetime.strptime(
                fecha_existente + " " + hora_existente, "%Y-%m-%d %H:%M:%S"
            )
            print(
                colored(
                    f"\nÚltimo evento: {fecha_hora_mas_reciente} Hora Centro", "yellow"
                )
            )
            await comparar_datos(datos_existentes, datos_nuevos)

    except PyMongoError as mongo_error:
        print(colored("mongo error: \n", "red", attrs=["reverse"]), str(mongo_error))
        try:
            await bot.send_error("Error en mongo script terminado")
        except TelegramError as bot_error:
            print(
                colored("Error TelegramBot:\n", "red", attrs=["blink", "reverse"]),
                str(bot_error),
            )
        sys.exit()


async def comparar_datos(datos_existentes, datos_nuevos):
    """Compara los datos nuevos con los existentes"""
    # obtener fechas y horas existentes
    fecha_limite = datetime.now() - timedelta(days=3)
    fechas_horas_existentes = set()
    for dato in datos_existentes:
        fecha_hora = datetime.strptime(
            dato["fecha"] + " " + dato["hora"], "%Y-%m-%d %H:%M:%S"
        )
        fechas_horas_existentes.add(fecha_hora)
    # Filtrar y guardar nuevos
    nuevos_datos = []

    for dato in datos_nuevos:
        fecha_hora_dato = datetime.strptime(
            dato["fecha"] + " " + dato["hora"], "%Y-%m-%d %H:%M:%S"
        )
        if (
            fecha_hora_dato >= fecha_limite
            and fecha_hora_dato not in fechas_horas_existentes
        ):
            nuevos_datos.append(dato)
    if nuevos_datos:
        nuevos_datos.reverse()
        await guardar_nuevos(nuevos_datos)

    print(colored("\nSin nuevos eventos", "yellow"))


async def guardar_nuevos(nuevos_datos):
    """Guarda nuevos en mongo"""
    try:
        for evento in nuevos_datos:
            print(
                colored(f"Nuevo evento detectado\n {evento}", "red"),
            )
            collection_name.insert_one(evento)
            evento_template = (
                f"<b>Sismo detectado SSN:</b>\n\n"
                f"<b>{evento['referencia']}</b>\n\n"
                f"<b>Timestamp:</b> {evento['fecha']}, {evento['hora']}\n"
                f"<b>Magnitud:</b> {evento['magnitud']}\n"
                f"<b>Profundidad:</b> {evento['profundidad']}\n"
            )

            if evento["magnitud"] >= 4.0:
                try:
                    await bot.send_evento(evento_template)
                except TelegramError as bot_error:
                    print(
                        colored(
                            "Error TelegramBot:\n", "red", attrs=["blink", "reverse"]
                        ),
                        str(bot_error),
                    )

    except PyMongoError as mongo_error:
        print(colored("mongo error: \n", "red", attrs=["reverse"]), str(mongo_error))
        try:
            await bot.send_error("Error en mongo. Script terminado")
        except TelegramError as bot_error:
            print(
                colored("Error TelegramBot:\n", "red", attrs=["blink", "reverse"]),
                str(bot_error),
            )
        sys.exit()


async def main():
    """Main function"""
    while True:
        print(colored("\nActualizando...", "green"))
        await consultar_ssn()
        print(colored("\nEsperando...\n", "green"))
        await asyncio.sleep(180)


if __name__ == "__main__":
    asyncio.run(main())
