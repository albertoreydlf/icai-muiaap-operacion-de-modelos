import os
import requests
from dotenv import load_dotenv
#no podemos poner la api key en este codigo porque no se debe de ver
#lo que hacemos es crar la variable API_KEY en el .env que esta oculto y leer con la siguiente funcion
load_dotenv()  # lee el .env
API_KEY = os.getenv("API_KEY")  # saco la clave del .env

url_inventario = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

IDEMA = "3194U"
url = (
    "https://opendata.aemet.es/opendata/api/valores/"
    "climatologicos/diarios/datos/"
    "fechaini/2019-10-01T00:00:00UTC/"
    "fechafin/2019-10-30T23:59:59UTC/"
    f"estacion/{IDEMA}"
)

respuesta = requests.get(
    url_inventario,
    params={"api_key" : API_KEY}
    )
#con esto hacemos la llamada al inventario de todas las estaciones,para obtener el IDEMA 
#(arriba ya esrta puesto pq esto lo escribo despues de haberlo obtenido)
#eso nos devuelve
#{
#    "descripcion": "exito",
#    "estado": 200,
#    "datos": "https://opendata.aemet.es/opendata/sh/17f045ce",
#    "metadatos": "https://opendata.aemet.es/opendata/sh/0556af7a"
#}

response = respuesta.json()
#con esto obtenenos la respuesta en formato json

url_datos = requests.get(response["datos"])
response_datos = url_datos.json()
#print(response_datos) la comento pq ya la vi en postman y es gigante no quiero eso en terminal
#ahora con esto lo que hacemos es acceder a la url dentro de datos del json de arriba
#esa url nos devuelve todas las estaciones(son muchisimas),que tienen la pinta:
#[ {
#  "latitud" : "394924N",
#  "provincia" : "ILLES BALEARS",
#  "altitud" : "490",
#  "indicativo" : "B013X",
#  "nombre" : "ESCORCA, LLUC",
#  "indsinop" : "08304",
#  "longitud" : "025309E"
#}, {
#  "latitud" : "394744N",
#  "provincia" : "BALEARES",
#  "altitud" : "5",
#  "indicativo" : "B051A",
#  "nombre" : "SÓLLER, PUERTO",
#  "indsinop" : "08316",
#  "longitud" : "024129E"
#},
#Dentro de todas,buscamos(usando la lupa de postman)el campo "indicativo"
#que corresponda a la estacion de Madrid,Ciudad Universitaria.Cogemos ese indicativo
#y lo ponemos arriba en la variabke que guardamos como IDEMA.Con esto ya podemos 
#rellenar los 3 params que nos pedia la peticion inicial(fechaIni,FechaFin e idema)

#Peticiones para obtener la climatología diaria de Madrid, Ciudad Universitariaen oct 2019
respuesta_clima = requests.get(url, params={"api_key": API_KEY})  # 1ª llamada a la api de aemet,url
#esta definido arriba y tiene los 3 parametros q se piden
print(respuesta_clima.status_code)  # tiene que salir 200 q significa que va bien,si no hay un problema

enlace_clima = respuesta_clima.json()  # diccionario con descripcion, estado, datos, metadatos
datos_clima = requests.get(enlace_clima["datos"]).json()  # 2ª llamada: al enlace, sin clave

print(len(datos_clima))  # número de dias para comprobar,si no sale 30(oct) pues estara mal
print(datos_clima[0])  # primer día para ver como es



