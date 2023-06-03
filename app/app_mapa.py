import folium
import folium.plugins as plugins
import concurrent.futures
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta
from flask import Flask, render_template
from get_mongo_db import mongodb


app = Flask(__name__)


dbname = mongodb()
collection_name = dbname["sismos"]


@app.route('/')
def index(start_date=None):

    def get_marker_color(magnitud):
        if magnitud < 3.0:
            return '#62ab5d'
        elif magnitud < 4.0:
            return '#ffe13f'
        elif magnitud < 5.0:
            return '#f79b3f'
        elif magnitud < 6.0:
            return '#ea5354'
        elif magnitud < 7.0:
            return '#a85164'
        elif magnitud < 8.0:
            return '#ff3fff'
        else:
            return '#9f3f9f'

    # Establecer fecha actual si no se encontro solicitud de fecha
    if start_date is None:
        start_date = datetime.now() - timedelta()
    start_date_str = start_date.strftime("%Y-%m-%d")
    data_collection = None
    # Mongo
    try:
        data_collection = list(collection_name.find(
            {"fecha": {"$gte": "2023-06-03"}})) 
        print(data_collection)
        if data_collection is None:
            return 
    except PyMongoError as e:
        print("error mongo", str(e))

    ultimo_sismo = data_collection[-1]
    lat_ultimo_sismo = float(ultimo_sismo['latitud'])
    lon_ultimo_sismo = float(ultimo_sismo['longitud'])
    
    # folium map
    mapa = folium.Map(
        location=[lat_ultimo_sismo, lon_ultimo_sismo],
        tiles="https://api.mapbox.com/styles/v1/zenlab/clie0gyeu007e01qg570s0wop/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiemVubGFiIiwiYSI6ImNsODUxbDZyeTBsaWgzc28wNjZsYW93MGMifQ.7BiAwxa2_grM12ZYaC2_6g",
        attr='<a href=\"http://www.ssn.unam.mx/\">Servicio Sismógico Nacional</a>|<a href=\"https://www.unam.mx/\">UNAM</a>',
        zoom_start=8,
        min_zoom=4,
        zoom_control=False,
        control_scale=True
    )

    if data_collection:
        # Agregar un marcador al mapa para cada epicentro
        for registro in data_collection:
            lat = float(registro['latitud'])
            lon = float(registro['longitud'])
            magnitud = float(registro['magnitud'])
            color_magnitud = get_marker_color(magnitud)

            # Template popup epicentro
            popup_content = f"""
            <div style="font-size:12px;">
                <strong>Magnitud: </strong><strong style="color:{color_magnitud}">{magnitud}</strong><br>
                <strong>Fecha y Hora: </strong>{registro['fecha']}, {registro['hora']}<br>
                <strong>Epicentro: </strong>{registro['referencia']}<br>
                <strong>Profundidad: </strong>{registro['profundidad']}
            </div>
            """
            sismo_marker = folium.Marker(
                location=[lat, lon],
                icon=plugins.BeautifyIcon(
                    icon_shape='circle',
                    border_width=1,
                    background_color=color_magnitud,
                    inner_icon_style='font-size:8px;padding:4px;',
                    number=magnitud
                )
            )
            sismo_marker.add_child(folium.Popup(
                html=popup_content, max_width=200))
            sismo_marker.add_to(mapa)

        # Agregar marcador de ultimo sismo
        magnitud_ultimo_sismo = float(ultimo_sismo['magnitud'])

        # Template popup ultimo sismo
        popup_ultimo_sismo = f"""
        <div style="font-size:12px">
            <strong style="color:red;font-size:13px;">Ultimo Sismo</strong><br>
            <strong>Epicentro: </strong>{ultimo_sismo['referencia']}<br>
            <strong>Magnitud: </strong><strong style="color:{color_magnitud}">{magnitud_ultimo_sismo}</strong><br>
            <strong>Fecha y Hora: </strong>{ultimo_sismo['fecha']}, {ultimo_sismo['hora']}<br>
            <strong>Profundidad: </strong>{ultimo_sismo['profundidad']}
        </div>
        """
        marker_ultimo_sismo = folium.Marker(
            location=[lat_ultimo_sismo, lon_ultimo_sismo],
            icon=plugins.BeautifyIcon(
                icon_shape='circle',
                border_width=2,
                border_color='red',
                background_color=get_marker_color(magnitud_ultimo_sismo),
                inner_icon_style='font-size:8px;padding:4px ;',
                number=magnitud_ultimo_sismo
            )
        )
        marker_ultimo_sismo.add_child(folium.Popup(
            html=popup_ultimo_sismo, max_width=200, show=True))

        marker_ultimo_sismo.add_to(mapa)

    mapa.get_root().html.add_child(folium.Element(
        '<style>.map-iframe { pointer-events: none; }</style>'))
    # Guardar el mapa en un archivo HTML
    mapa.save('static/mapa.html')
    return render_template('index.html')

# Search Start date


@app.route('/date/<start_date>')
def index_with_date(start_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    return index(start_date)


@app.route('/heatmap')
def heatmap():

    mapa = folium.Map(
        tiles="https://api.mapbox.com/styles/v1/zenlab/clie0gyeu007e01qg570s0wop/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiemVubGFiIiwiYSI6ImNsODUxbDZyeTBsaWgzc28wNjZsYW93MGMifQ.7BiAwxa2_grM12ZYaC2_6g",
        attr='<a href=\"http://www.ssn.unam.mx/\">Servicio Sismógico Nacional</a>|<a href=\"https://www.unam.mx/\">UNAM</a>',
        control_scale=True,
        max_bounds=True,
        zoom_control=False
    )

    try:
        data_collection = list(collection_name.find())
    except PyMongoError as e:
        print("mongoError", str(e))

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
            min_opacity=0.09,
            radius=20,
            blur=15,
            gradient={0.1: 'blue', 0.5: 'lime', 1: 'red'},
        )
    heat.add_to(mapa)

    mexico_bounds = [[14.5, -120.9], [32.7, -85]]
    mapa.fit_bounds(mexico_bounds)
    mapa.save('static/mapa.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
