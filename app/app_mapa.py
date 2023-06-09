"""
Sismos Get 
"""

import os
import concurrent.futures
from datetime import datetime
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
MAP_ATRIBUTION = f"{SSN_REF}|{UNAM_REF}"


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


def draw_points(points_data):
    """Marker Maker for points"""
    mapa = folium.Map(
        location=mexico_center,
        tiles=os.getenv('MAP_TILE'),
        attr=MAP_ATRIBUTION,
        min_zoom=5,
        zoom_control=False,
        control_scale=True,
        max_bounds=True
    )
    ultimo_sismo = points_data[-1]
    lat_ultimo_sismo = ultimo_sismo['latitud']
    lon_ultimo_sismo = ultimo_sismo['longitud']

    # Agregar marcador de ultimo sismo
    magnitud_ultimo_sismo = ultimo_sismo['magnitud']
    color_magnitud = get_marker_color(magnitud_ultimo_sismo)
    # Template popup ultimo sismo
    popup_ultimo_sismo = f"""
       <p>ultimo sismo</p>
       <h4>{ultimo_sismo['referencia']}</h4>
       <strong style="color:{color_magnitud}">M </strong><strong style="color:{color_magnitud}">{magnitud_ultimo_sismo}</strong><br>
       <span>Profundidad: </span>{ultimo_sismo['profundidad']}<span> Kilometros</span></br>
       <strong>{ultimo_sismo['fecha']}, {ultimo_sismo['hora']}</strong>
       """
    marker_ultimo_sismo = folium.Marker(
        location=[lat_ultimo_sismo, lon_ultimo_sismo],
        icon=plugins.BeautifyIcon(
            icon_shape='circle',
            border_width=1,
            background_color=get_marker_color(magnitud_ultimo_sismo),
            inner_icon_style='font-size:8px; padding: 4px; text-align:center;',
            number=magnitud_ultimo_sismo
        )
    )
    for point in points_data:
        lat = point['latitud']
        lon = point['longitud']
        referencia = point['referencia']
        magnitud = point['magnitud']
        color_magnitud = get_marker_color(magnitud)
        profundidad = point['profundidad']
        fecha = point['fecha']
        hora = point['hora']
        # Template popup epicentro

        popup_content = f"""
            <h4>{referencia}</h4>
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
        sismo_marker.add_to(mapa)

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
    marker_ultimo_sismo.add_child(folium.Tooltip(text=popup_ultimo_sismo))
    marker_ultimo_sismo.add_to(mapa)

    # Guardar el mapa en un archivo HTML
    mapa.fit_bounds(mexico_bounds)
    mapa.get_root().html.add_child(folium.Element(listener_script))
    mapa.save('static/mapa.html')


@app.route('/')
def index(start_date=None):
    """App Index"""

    # Establecer fecha actual si no se encontro solicitud de fecha
    if start_date is None:
        start_date = datetime.now()

    start_date_str = start_date.strftime("%Y-%m-%d")

    # Mongo
    try:
        collection_name = dbname["sismos"]
        data_collection = list(collection_name.find(
            {"fecha": start_date_str}))

    except PyMongoError as mongo_error:
        print("error mongo", str(mongo_error))

    if data_collection:
        draw_points(data_collection)
    return render_template('index.html', eventos=data_collection)


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

    if data_collection:
        draw_points(data_collection)
    return render_template('index.html', eventos=data_collection)

# Heat Map Route


@app.route('/heatmap')
def heatmap():
    """Draw Heatmap"""
    mapa = folium.Map(
        tiles=os.getenv('MAP_TILE'),
        attr=MAP_ATRIBUTION,
        zoom_start=8,
        min_zoom=4,
        zoom_control=False,
        control_scale=True,
        max_bounds=True
    )
    mapa.fit_bounds(mexico_bounds)
    try:
        collection_name = dbname["magAggregate"]
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
            min_opacity=0.05,
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
