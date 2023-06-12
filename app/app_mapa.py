"""
Sismos Get 
"""
import pytz
import os
import concurrent.futures
from datetime import datetime, timedelta
from dotenv import load_dotenv
import folium
from folium import plugins
from pymongo.errors import PyMongoError
from flask import Flask, render_template
from get_mongo_db import mongodb


load_dotenv()
app = Flask(__name__)
dbname = mongodb()

mexico_bounds = [[14.5, -120.9], [32.7, -85]]
mexico_center = [19.4, -99.1]
SSN_REF = '<a href=\"http://www.ssn.unam.mx/\">Servicio Sismógico Nacional</a>'
UNAM_REF = '<a href=\"https://www.unam.mx/\">UNAM</a>'
MAP_ATRIBUTION = f"{SSN_REF} | {UNAM_REF} | USGS"


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
        location=mexico_center,
        tiles=os.getenv('MAP_TILE'),
        attr=MAP_ATRIBUTION,
        zoom_start=4,
        min_zoom=3,
        zoom_control=False,
        control_scale=True,
    )

    grupos = [
        {
            'name': 'SSN',
            'data': ssn_list,
            'header_mapping': {
                'lat': ['latitud'],
                'lon': ['longitud'],
                'ref': ['referencia'],
                'mag': ['magnitud'],
                'depth': ['profundidad'],
                'date': ['fecha'],
                'time': ['hora']
            }
        },

        {
            'name': 'USGS',
            'data': usgs_list,
            'header_mapping': {
                'lat': ['lat'],
                'lon': ['lon'],
                'depth': ['depht'],
                'ref': ['ref'],
                'mag': ['mag'],
                'date': ['time'],
                'time': ['time']
            }
        }
    ]
    for grupo in grupos:
        group_name = grupo['name']
        group_data = grupo['data']
        header_mapping = grupo['header_mapping']
        marker_group = folium.FeatureGroup(name=group_name)
        for point in group_data:

            lat = get_nested_value(point, header_mapping['lat'])
            lon = get_nested_value(point, header_mapping['lon'])
            magnitud = get_nested_value(point, header_mapping['mag'])
            referencia = get_nested_value(point, header_mapping['ref'])
            color_magnitud = get_marker_color(magnitud)
            profundidad = get_nested_value(point, header_mapping['depth'])
            fecha = get_nested_value(point, header_mapping['date'])
            hora = get_nested_value(point, header_mapping['time'])
            popup_content = f"""
               <h5>{referencia}</h5>
               <strong style="color:{color_magnitud}">M </strong><strong style="color:{color_magnitud}">{magnitud}</strong></br>
               <span>Profundidad: </span>{profundidad}<span> Km</span><br>
               <strong>{fecha}, {hora}</strong>
           """
            sismo_marker = folium.Marker(
                location=[lat, lon],
                icon=plugins.BeautifyIcon(
                    icon_shape='doughnut',
                    border_width=1,
                    background_color=color_magnitud,
                )
            )
            sismo_marker.add_child(folium.Tooltip(text=popup_content))
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

    folium.LayerControl(position="bottomright").add_to(mapa)
    mapa.get_root().html.add_child(folium.Element(listener_script))
    # Guardar el mapa en un archivo HTML
    mapa.save('static/mapa.html')


@app.route('/')
def index(start_date=None):
    """App Index"""
    utc_timezone = pytz.timezone('UTC')

    # Establecer fecha actual si no se encontro solicitud de fecha
    if start_date is None:
        start_date = datetime.now()

    start_date_utc = datetime.now(utc_timezone) - timedelta(days=1)
    start_date_str = start_date.strftime("%Y-%m-%d")

    # Mongo
    try:
        ssn_collection = dbname["sismos"]
        usgs_collection = dbname["sismos_usgs"]

        ssn_list = list(ssn_collection.find(
            {"fecha": start_date_str}
        ))
        usgs_list = list(usgs_collection.find(
            {
                'properties.time': {
                    '$gte': start_date_utc
                }
            }
        ))

        usgs_data_simplify = []
        for item in usgs_list:
            document = {
                'lat': item['geometry']['coordinates'][1],
                'lon': item['geometry']['coordinates'][0],
                'depht': item['geometry']['coordinates'][2],
                'ref': item['properties']['place'],
                'mag': item['properties']['mag'],
                'time': item['properties']['time']
            }
            usgs_data_simplify.append(document)

        draw_points(ssn_list, usgs_data_simplify)
        return render_template('index.html', eventos=ssn_list)
    except PyMongoError as mongo_error:
        print("error mongo", str(mongo_error))


# Search Start date
@app.route('/date/<start_date>')
def index_with_date(start_date):
    """Index for date"""
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    return index(start_date)


@app.route('/historico')
def historico():
    """Major Earthquakes"""
    try:
        collection_name = dbname["magAggregate"]
        data_collection = list(collection_name.find())
    except PyMongoError as mongo_error:
        print("mongoError", str(mongo_error))

    usgs_list = []
    draw_points(data_collection, usgs_list)

    return render_template('index.html', eventos=data_collection)

# Heat Map Route


@app.route('/heatmap')
def heatmap():
    """Draw Heatmap"""
    mapa = folium.Map(
        location=mexico_center,
        tiles=os.getenv('MAP_TILE'),
        attr=MAP_ATRIBUTION,
        min_zoom=4,
        zoom_control=False,
        control_scale=True,
        max_bounds=True
    )
    mapa.fit_bounds(mexico_bounds)
    try:
        collection_name = dbname["sismos"]
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

        mapa.save('static/mapa.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
