import csv
import json
import time
from bson import ObjectId


def csv_to_json():
    jsonArray = []

    with open("catalogo.csv", encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            row["_id"] = str(ObjectId())
            jsonArray.append(row)

    with open('catalogo.json', 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


start = time.perf_counter()
csv_to_json()
finish = time.perf_counter()
print(f"{finish - start:0.4f}")
