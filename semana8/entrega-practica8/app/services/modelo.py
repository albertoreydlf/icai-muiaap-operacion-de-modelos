import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada
#añadimos prestamoEntrada pq no estaba puesto y hace falta en el 3 todo

# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

# TODO: cargar el modelo joblib una sola vez, al importar el modulo
modelo = joblib.load(MODEL_PATH)
# TODO: funcion decidir(probabilidad) -> "aprobar", "revisar" o "rechazar" (umbrales en el enunciado)
def decidir(probabilidad : float) -> str:
    decisiones = ["aprobar", "revisar", "rechazar"]
    if probabilidad < 0.2:
        return decisiones[0]
    
    elif probabilidad < 0.5:
        return decisiones[1]
    
    else:
        return decisiones[2]
        

# TODO: funcion predecir(entrada) -> PrediccionSalida, usando VARIABLES para ordenar los valores
def predecir(entrada : PrestamoEntrada) -> PrediccionSalida : 
    valores = []
    for variable in VARIABLES:
        valor = getattr(entrada, variable)
        valores.append(valor)

    probabilidad = modelo.predict_proba([valores])[0][1]  # probabilidad de impago
    decision = decidir(probabilidad)  # con el numero saco el texto
    return PrediccionSalida(probabilidad_impago=probabilidad, decision=decision)

#recordatorio de pq usamos predict_proba([valores][0][1]):
#Mi bucle deja esto(nums de ejemplo):  valores = [30, 2500, 12000, 36, 5, 0]
#Es una fila. predict_proba no acepta una fila suelta: espera una lista de filas. Por eso le paso [valores]:
#[[30, 2500, 12000, 36, 5, 0]]      , una lista con una fila dentro
#Si fueran dos solicitantes, serían dos filas:
#[[30, 2500, 12000, 36, 5, 0],
# [45, 1800, 20000, 60, 10, 2]]

# pq usamos [0][1]??

#predict_proba devuelve una fila por cada solicitante, y en cada fila dos números: la probabilidad de no impago y la de impago. 
# Para mi fila podría devolver,por ej:  [[0.92, 0.08]]
#[0] coge la primera fila: [0.92, 0.08]
#[0][1] coge, dentro de esa fila, el segundo número: 0.08
#luego ese numero se lo metemeos a la funcion decicir y obtenemos la prediccion segun lo q he definido dentro de esa funcion