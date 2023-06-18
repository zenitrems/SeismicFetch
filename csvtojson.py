import csv
from datetime import datetime
import pytz
import json
import time

UTC_TIMEZONE = pytz.timezone('UTC')


def csv_edit():
    with open('catalogo.csv', 'r', encoding='utf-8') as file_input, open('catalogo_edit.csv', 'w', encoding='utf-8') as file_output:
        reader = csv.reader(file_input)
        writer = csv.writer(file_output)

        writer.writerow(['timestamp_utc'])

        for row in reader:
            fecha = row[0]
            hora = row[1]
            fecha_hora_str = f"{fecha} {hora}"
            try:
                fecha_hora = datetime.strptime(
                    fecha_hora_str, '%Y-%m-%d %H:%M:%S')
                writer.writerow([fecha_hora])
                print(fecha_hora)
            except ValueError as value_error:
                print(str(value_error))


def csv_to_json():
    jsonArray = []

    with open("catalogo.csv", encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            jsonArray.append(row)

    with open('catalogo.json', 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


start = time.perf_counter()
# csv_to_json()
csv_edit()
finish = time.perf_counter()
print(f"{finish - start:0.4f}")
