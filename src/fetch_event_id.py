"""
EMSC Web Services
"""

import requests
import json

url = "http://www.seismicportal.eu/fdsnws/event/1/query\
?start=2017-09-01&end=2017-11-01&format=json&minmag={minmag}".format(
    minmag=6.5
)


def get_url(url):
    res = requests.get(url, timeout=15)
    return {"status": res.status_code, "content": res.text}


event = get_url(url)
print(event['content'])



