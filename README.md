# Sismos Get

Sismos Get obtiene, procesa y almacena datos proporcionados por el Servicio Sismológico Nacional (SSN México) y United States Geological Survey (USGS Estados Unidos).

El SSN publica en su portal http://www.ssn.unam.mx/ los sismos mayores a M 4.0 con un retraso aproximado de 15 a 20 minutos, mientras que los sismos de menor magnitud a M 4.0 se publican en 2 reportes: el primero a las 08:00 horas y el segundo a las 21:00 horas (Tiempo Centro de México).

USGS proporciona un feed en geojson https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php, que se actualiza cada minuto.

## Todo:

- pruebas unitarias
- mejor manejo de errores
- crear sistema de logging
- validacion de datos
- continuar con seedlinkclient
- mongo pipelines para magnitud y otros

## Bugs conocidos:
