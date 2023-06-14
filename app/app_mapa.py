"""
Sismos Get 
"""
import os
import json
import concurrent.futures
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import folium
from folium import plugins
from pymongo.errors import PyMongoError
from flask import Flask, render_template
from get_mongo_db import mongodb


load_dotenv()
app = Flask(__name__)
DATABASE = mongodb()

mexico_bounds = [[14.5, -120.9], [32.7, -85]]
mexico_center = [19.4, -99.1]
SSN_REF = '<a href=\"http://www.ssn.unam.mx/\">Servicio Sismógico Nacional</a>'
UNAM_REF = '<a href=\"https://www.unam.mx/\">UNAM</a>'
NORDPIL_REF = '<a href=\"https://nordpil.com/\">Nordpil</a>'
MAP_ATRIBUTION = f"{SSN_REF} | {UNAM_REF} | USGS | {NORDPIL_REF}"
MAP_TILE = os.getenv('MAP_TILE')

MAPBOX_LAYER = folium.TileLayer(
    tiles=MAP_TILE,
    attr=MAP_ATRIBUTION,
    name="Mapbox",
    min_zoom=3,
    control=False
)


def style_function(features):
    """style function for GeoJson"""
    return {
        'color': 'red',  # Color de la línea
        'weight': 1,     # Grosor de la línea
        'fillColor': 'yellow',  # Color de relleno
        'fillOpacity': 0.5  # Opacidad del relleno
    }


with open('boundaries.json', 'r', encoding='utf-8', ) as file:
    geojson_data = json.load(file)
tectonic_boundaries = folium.GeoJson(
    data=geojson_data,
    name='Tectonic Plates Boundaries',
    style_function=style_function
)


def get_marker_color(magnitud):
    """asigna color por magnitud"""
    color = '#fff'
    if magnitud < 3.0:
        color = '#62ab5d'
    elif magnitud < 4.0:
        color = '#ffc304'
    elif magnitud < 5.0:
        color = '#f79b3f'
    elif magnitud < 6.0:
        color = '#ea5354'
    elif magnitud < 7.0:
        color = '#a85164'
    elif magnitud < 8.0:
        color = '#ff3fff'
    else:
        color = '#9f3f9f'
    return color


def get_nested_value(data, keys):
    """Get nested Value"""
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list):
            value = [item.get(key) if isinstance(item, dict)
                     else None for item in value]
        else:
            value = None
        if value is None:
            break
    return value


def draw_points(ssn_list, usgs_list):
    """Marker Maker for points"""
    mapa = folium.Map(
        tiles=MAPBOX_LAYER,
        location=mexico_center,
        zoom_start=4,
        zoom_control=False,
        control_scale=True,
    )

    grupos = [
        {
            'name': 'SSN',
            'data': ssn_list,
            'header_mapping': {
                'lat': ['lat'],
                'lon': ['lon'],
                'ref': ['ref'],
                'mag': ['mag'],
                'depth': ['depth'],
                'time': ['time'],
                'local_time': ['local_time']
            }
        },
        {
            'name': 'USGS',
            'data': usgs_list,
            'header_mapping': {
                'lat': ['lat'],
                'lon': ['lon'],
                'depth': ['depth'],
                'ref': ['ref'],
                'mag': ['mag'],
                'time': ['time'],
                'local_time': ['local_time']
            }
        }
    ]
    ultimo_evento_ssn = None
    ultimo_evento_usgs = None

    for evento in ssn_list:
        if ultimo_evento_ssn is None or evento['time'] > ultimo_evento_ssn:
            ultimo_evento_ssn = evento['time']
    for evento in usgs_list:
        if ultimo_evento_usgs is None or evento['time'] > ultimo_evento_usgs:
            ultimo_evento_usgs = evento['time']

    for grupo in grupos:
        group_name, group_data, header_mapping = grupo.values()
        marker_group = folium.FeatureGroup(name=group_name)
        for point in group_data:

            sismo_marker = folium.Marker(
                location=[get_nested_value(point, header_mapping['lat']), get_nested_value(
                    point, header_mapping['lon'])],
                icon=plugins.BeautifyIcon(
                    icon_shape='doughnut',
                    border_width=1,
                    background_color=get_marker_color(
                        get_nested_value(point, header_mapping['mag']))
                )
            )

            if group_name == 'SSN' and get_nested_value(point, header_mapping['time']) == ultimo_evento_ssn:
                # Aplicar estilo especial al marcador del último sismo de SSN
                sismo_marker.add_child(folium.Popup(
                    'Último sismo SSN', max_width=100, show=True))

            elif group_name == 'USGS' and get_nested_value(point, header_mapping['time']) == ultimo_evento_usgs:
                # Aplicar estilo especial al marcador del último sismo de USGS
                sismo_marker.add_child(folium.Popup(
                    'Último sismo USGS', max_width=100))

            tooltip_content = f"""
            <div style="font-size: 12px;">
               <strong>{get_nested_value(point, header_mapping['ref'])}</strong></br>
               <strong style="color:{get_marker_color(get_nested_value(point, header_mapping['mag']))}">M {get_nested_value(point, header_mapping['mag'])}</strong></br>
               <span>Profundidad: {get_nested_value(point, header_mapping['depth'])} Km</span><br>
               <span>{get_nested_value(point, header_mapping['time'])} UTC</span></br>
               <span>{get_nested_value(point, header_mapping['local_time'])} UTC-6</span>
            </div>
           """
            sismo_marker.add_child(folium.Tooltip(text=tooltip_content))
            sismo_marker.add_to(marker_group)

        marker_group.add_to(mapa)

    listener_script = """
    <script>
        window.addEventListener('message', function (event) {
          if (event.data.type === 'center') {
            var lat = event.data.lat;
            var lon = event.data.lon;
            parent.postMessage({ type: 'center', lat: lat, lon: lon }, '*');
            console.log(lat, lon)
            var mapElement = document.querySelector('.folium-map');
            if (mapElement) {
              var mapObject = mapElement._leaflet_map;
              document.addEventListener('DOMContentLoaded', function() {
                var bounds = L.latLngBounds([[lat, lon], [lat, lon]]);
                mapObject.fitBounds(bounds);
              });
            }
          }
        });
    </script>
    """

    mapa.get_root().html.add_child(folium.Element(listener_script))
    tectonic_boundaries.add_to(mapa)
    folium.LayerControl(position="bottomright").add_to(mapa)
    # Guardar el mapa en un archivo HTML
    mapa.save('static/mapa.html')


def data_format(ssn_list, usgs_list, ssn_data_simplify, usgs_data_simplify):
    """Format Data"""
    for item in ssn_list:
        timestamp_local_str = f"{item['fecha']} {item['hora']}"
        timestamp_local_format = timestamp_local_str
        timestamp_local = datetime.strptime(
            timestamp_local_format, "%Y-%m-%d %H:%M:%S")
        document = {
            'lat': item['latitud'],
            'lon': item['longitud'],
            'depth': item['profundidad'],
            'ref': item['referencia'],
            'mag': item['magnitud'],
            'time': item['timestamp_utc'],
            'local_time': timestamp_local
        }
        ssn_data_simplify.append(document)

    for item in usgs_list:
        time = item['properties']['time']
        time_str = datetime.strftime(time, "%Y-%m-%d %H:%M:%S")
        local_time = datetime.strptime(
            item['timestamp_local'], "%Y-%m-%dT%H:%M:%S.%f%z")
        local_time_str = datetime.strftime(local_time, "%Y-%m-%d %H:%M:%S")
        document = {
            'lat': item['geometry']['coordinates'][1],
            'lon': item['geometry']['coordinates'][0],
            'depth': item['geometry']['coordinates'][2],
            'ref': item['properties']['place'],
            'mag': item['properties']['mag'],
            'time': time_str,
            'local_time': local_time_str
        }
        usgs_data_simplify.append(document)
    return ssn_data_simplify, usgs_data_simplify


@app.route('/')
def index(start_date=None):
    """App Index"""
    utc_timezone = pytz.timezone('UTC')

    # Establecer fecha actual si no se encontro solicitud de fecha
    if start_date is None:
        start_date = datetime.now(utc_timezone) - timedelta(hours=24)

    # Mongo
    try:
        ssn_collection = DATABASE["sismicidad_ssn"]
        usgs_collection = DATABASE["sismicidad_usgs"]

        ssn_list = list(ssn_collection.find(

            {
                "timestamp_utc": {
                    '$gte': start_date
                }
            }

        ))
        usgs_list = list(usgs_collection.find(
            {
                'properties.time': {
                    '$gte': start_date
                }
            }
        ))
    except PyMongoError as mongo_error:
        print("error mongo", str(mongo_error))

    ssn_data_simplify = []
    usgs_data_simplify = []
    data_format(ssn_list, usgs_list, ssn_data_simplify, usgs_data_simplify)
    draw_points(ssn_data_simplify, usgs_data_simplify)
    return render_template('index.html', eventos=ssn_data_simplify)


# Search Start date
@app.route('/date/<start_date>')
def index_with_date(start_date):
    """Index for date"""
    fecha_completa_str = start_date + ' 00:00:00.000000+00:00'
    start_date = datetime.strptime(
        fecha_completa_str, '%Y-%m-%d %H:%M:%S.%f%z')
    return index(start_date)


@app.route('/historico')
def historico():
    """Major Earthquakes"""
    collection_name = DATABASE["magAggregate"]
    try:
        ssn_list = list(collection_name.find())
    except PyMongoError as mongo_error:
        print("mongoError", str(mongo_error))

    usgs_list = []
    ssn_data_simplify = []
    usgs_data_simplify = []
    data_format(ssn_list, usgs_list, ssn_data_simplify, usgs_data_simplify)

    draw_points(ssn_data_simplify, usgs_data_simplify)

    return render_template('index.html', eventos=ssn_data_simplify)

# HeatMap Route


@app.route('/heatmap')
def heatmap():
    """Draw Heatmap"""
    mapa = folium.Map(
        tiles=MAPBOX_LAYER,
        location=mexico_center,
        zoom_start=4,
        zoom_control=False,
        control_scale=True,
    )
    try:
        collection_name = DATABASE["magAggregate"]
        data_collection = list(collection_name.find())
    except PyMongoError as mongo_error:
        print("mongoError", str(mongo_error))

    heatmap_data = []

    if data_collection:
        def proccess_point(point):
            lat = point['latitud']
            lon = point['longitud']
            return [lat, lon]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            heatmap_data = list(executor.map(proccess_point, data_collection))

        heat = plugins.HeatMap(
            data=heatmap_data,
            name='EventoHeatmap',
            min_opacity=0.1,
            radius=20,
            blur=18,
            gradient={0.1: 'blue', 0.3: 'lime',
                      0.5: 'yellow', 0.8:  'orange', 1: 'red'},
        )
        heat.add_to(mapa)
    tectonic_boundaries.add_to(mapa)
    mapa.save('static/mapa.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
