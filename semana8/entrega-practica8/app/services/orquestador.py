import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


# TODO: definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada
def definir_tool() -> dict:
    return {
        "type": "function",  # el tipo de tool que entiende el LLM
        "function": {
            "name": NOMBRE_TOOL,  # el nombre con el que el LLM la llama,esta definido arriba
            "description": "Calcula la probabilidad de impago de un prestamo y da una decision.",  # explicacion de para que sirve
            "parameters": PrestamoEntrada.model_json_schema(),  # los datos que pide, sacados de la clase
        },
    }

# Una tool es una funcion mia que el LLM puede pedir que ejecute
# El LLM solo escribe texto y no puede usar el modelo
# Asi que le doy una ficha con el nombre de la tool y los datos que necesita
# Esos datos salen de PrestamoEntrada y no los escribo a mano
# Con esta funcion solo creo la ficha, no calcula nada
# TODO: ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)
def ejecutar_tool(nombre, argumentos_json) -> dict:
    if nombre != NOMBRE_TOOL:  # si pide una tool que no existe
        return {"ok": False, "error": "tool desconocida: " + str(nombre)} #dict con ok false
    datos = leer_argumentos(argumentos_json)  # paso el texto JSON a diccionario(funcion de arriba)
    try:
        entrada = PrestamoEntrada(**datos)  # Validamos los datos con el contrato,** es para desempaquetar el dict
    except ValidationError as error:  # si algun dato esta mal o sobra alguno
        return {"ok": False, "error": str(error)}  # devuelvo el fallo en vez de romper
    salida = predecir(entrada)  # los datos son buenos asi que uso el modelo
    return {
        "ok": True,  # todo ha ido bien
        "probabilidad_impago": salida.probabilidad_impago,
        "decision": salida.decision,
    }

# Esta funcion es la que se ejecuta cuando el LLM pide usar la tool(mi funcion)
# Recibe el nombre de la tool y los datos en texto JSON
# Comprueba que todo este bien y si lo esta calcula el riesgo con el modelo
# Nunca da error, siempre devuelve un diccionario con ok True o ok False pq nos lo piden
# Asi el LLM puede ver que paso y corregirse o pedirle el dato al usuario
# 
# # TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)

# Esta funcion es la que lleva la conversacion con el LLM
# Le mando el historial y si el LLM pide una tool la ejecuto
# y le devuelvo el resultado para que escriba la respuesta final
# Lo repito como mucho MAX_VUELTAS veces para no quedarme en un bucle infinito
def responder(mensajes, llm) -> ChatSalida:
    historial = [{"role": "system", "content": SISTEMA}]  # el primer mensaje es el system
    for mensaje in mensajes:  # despues meto los mensajes del usuario
        historial.append({"role": mensaje.role, "content": mensaje.content})
    herramientas = [definir_tool()]  # la ficha de la tool
    herramienta_usada = None  # de momento no se ha usado ninguna

    for vuelta in range(MAX_VUELTAS):  # como mucho MAX_VUELTAS veces
        respuesta = llm.completar(historial, herramientas)  # le pregunto al LLM con una funcion q esta en llm.py
        llamadas = respuesta.get("tool_calls")  # miro si pide alguna tool
        if not llamadas:  # si no pide tool ya ha contestado con texto
            return ChatSalida(respuesta=respuesta["content"], herramienta=herramienta_usada)
        historial.append(respuesta)  # guardo lo que pidio el LLM
        for llamada in llamadas:
            nombre = llamada["function"]["name"]  # que tool pide
            argumentos = llamada["function"]["arguments"]  # con que datos (en texto)
            resultado = ejecutar_tool(nombre, argumentos)  # la ejecuto
            herramienta_usada = HerramientaUsada(
                nombre=nombre,
                argumentos=leer_argumentos(argumentos),
                resultado=resultado,
            )  # me lo guardo para devolverlo al final
            historial.append(
                {"role": "tool", "tool_call_id": llamada["id"], "content": json.dumps(resultado)}
            )  # le devuelvo el resultado al LLM

    return ChatSalida(  # si llego aqui el LLM no ha contestado en MAX_VUELTAS
        respuesta="No he podido completar la solicitud. Prueba a darme de nuevo los datos.",
        herramienta=herramienta_usada,
    )