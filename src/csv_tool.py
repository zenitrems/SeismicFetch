import csv
from datetime import datetime
import json
import time
import pytz

UTC_TIMEZONE = pytz.timezone("UTC")


def csv_edit():
    with open("catalogo.csv", "r", encoding="utf-8") as file_input, open(
        "catalogo_edit.csv", "w", encoding="utf-8"
    ) as file_output:
        reader = csv.reader(file_input)
        writer = csv.writer(file_output)

        writer.writerow(["timestamp_utc"])

        for row in reader:
            date_row = row[0]
            time_row = row[1]
            datetime_str = f"{date_row} {time_row}" + ".000000" + "+00:00"
            try:
                datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f%z")
                print(datetime_obj)
                writer.writerow([datetime_obj])
            except ValueError as value_error:
                print(str(value_error))


def csv_to_json():
    jsonArray = []

    with open("catalogo.csv", encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            jsonArray.append(row)

    with open("catalogo.json", "w", encoding="utf-8") as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


start = time.perf_counter()
# csv_to_json()
csv_edit()
finish = time.perf_counter()
print(f"{finish - start:0.4f}")
