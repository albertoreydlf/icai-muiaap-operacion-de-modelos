**02 M1 - Serialización - Con serialization_demo.py compara /v1/scores/leaky y /v1/scores/public; anota los campos que solo
aparecen en la primera, explica por qué /v1/scores/filtered tampoco los devuelve aunque la función retorna un dict y mira en
/docs si PublicScore incluye is_reliable.**

a)
En /v1/scores/leaky salen los campos :
{
  "band": "acceptable",
  "confidence": 0.8312377,
  "raw_score": 6.137,
  "threshold_config": "/srv/models/thresholds.yaml"
}

Y en /v1/scores/public salen:
{
  "band": "acceptable",
  "confidence": 0.83,
  "served_at": "2026-10-30T19:30:59.719523Z",
  "note": null,
  "is_reliable": true
}

Por lo que los campos que aparecen solo en el primero son raw_score y threshold_config
b)

/v1/scores/filtered tampoco los devuelve aunque la función devuelve un dict:Esta no devuelve los campos porque dentro de su decorador(Va justo encima de una función y significa “esta función responde a peticiones GET en esta dirección”) hay un response_model =PublicScore, por lo que la respuesta siempre va a ser como declaramos en publicSCore.Pego ambas cosas abajo para que se vea de lo que hablo.raw_score y threshold_config no están declarados en PublicScore, así que response_model los quita de la respuesta aunque la función los devuelva en el dict
Todo esto lo he sacado de serialization_demo.py, que está en /examples

@app.get("/v1/scores/filtered", response_model=PublicScore)

class PublicScore(BaseModel):
    """Lo que promete la API."""

    band: Band
    confidence: float = Field(ge=0, le=1)
    served_at: datetime
    note: str | None = None

    @field_serializer("confidence")
    def _two_decimals(self, value: float) -> float:
        return round(value, 2)

    @field_serializer("served_at")
    def _utc_z(self, value: datetime) -> str:
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")

    @computed_field
    @property
    def is_reliable(self) -> bool:
        return self.confidence >= 0.8

c)

PublicScore si inclute is_reliable en /docs

**03 M2 - Errores - Con errors_demo.py envía a POST /v1/scores los tres cuerpos del enunciado y llama a GET /v1/nada y GET
/v1/boom; tabula status, error.code y error.fields. Comenta el decorador de handle_validation, observa la respuesta por defecto y
restáuralo**


a)
Mando las 3 peticiones al POST /v1/scores y luego llamo a GET /v1/nada y a GET /v1/boom. Lo apunto en esta tabla:

| Petición | status | error.code | error.fields |
|---|---|---|---|
| POST con {"age": 30, "income": 1000} | 200 | no tiene | no tiene (devuelve {"score": 0.01}) |
| POST con {"age": "treinta", "income": 1000} | 422 | validation_error | campo age y mensaje "Input should be a valid integer, unable to parse string as an integer" |
| POST con {"age": 30} | 422 | validation_error | campo income y mensaje "Field required" |
| GET /v1/nada | 404 | not_found | no tiene |
| GET /v1/boom | 500 | internal_error | no tiene |

La primera petición está bien hecha y por eso da 200 y no hay error. Las otras 4 son errores y todas tienen la clave error en la raíz.
En /v1/boom el mensaje es solo "Unexpected error". El texto con TU_SECRETO no sale en la respuesta porque el handler lo manda al log con logger.exception 

b)
Primero lo que es cada cosa de errors_demo.py:
- Un handler es una función que se ejecuta cuando salta un tipo de error concreto y decide qué respuesta se manda.
- @app.exception_handler(RequestValidationError) es el decorador (va justo encima de la función) y significa "cuando falle la validación del cuerpo usa esta función"
- handle_validation es la función de debajo. Con esta función convertimos los errores de pydantic en nuestro formato con code, message y fields

Si comento el decorador FastAPI usa su respuesta por defecto. En el segundo caso (age = "treinta") saldría esto:
{"detail": [{"type": "int_parsing", "loc": ["body", "age"], "msg": "Input should be a valid integer, unable to parse string as an integer", "input": "treinta"}]}
Lo que cambia es que la clave es detail y no error, que no hay code y que además repite en input lo que escribió el usuario. Después hay que volver a poner el decorador para que quede como estaba.

c)
Comprobación del enunciado. Las respuestas de error tienen la clave error en la raíz y ninguna lleva el texto TU_SECRETO.

**04 M3 - OpenAPI - Con openapi_demo.py localiza en /openapi.json dónde acaban summary, el docstring y responses de create_score, ejecuta el ejemplo minor desde Swagger y añade un tercer ejemplo no_income sin el campo income.**

a)
En /openapi.json hay que ir a paths, luego /v1/scores y luego post. Dentro salen:
- summary que es el "Calcular el score de riesgo" que ponemos en el decorador del endpoint.
- description que es el docstring de la función create_score.
- responses que tiene el 200 (con el response_description "Score y versión del modelo.") y el 422 y el 503. Estos dos últimos los ponemos una sola vez en el APIRouter con responses= y valen para todo el router.

b)
El ejemplo minor es {"age": 16, "income": 1} y da 422 porque age tiene ge=18 (tiene que ser mayor o igual que 18). Esta demo no tiene handler propio así que la respuesta es la de por defecto de FastAPI con detail. Algo que me llama la atención es que /docs dice que el 422 es de tipo ErrorResponse y la respuesta real no lo es. Esto es justo lo que se arregla luego en la 9.2.

c)
Lo que he usado para los ejemplos es openapi_examples. Es un parámetro de Body y sirve para que en /docs salga un desplegable con varios cuerpos de ejemplo. Es un diccionario donde cada ejemplo tiene un nombre y dentro un summary (el texto que se ve) y un value (el cuerpo que se manda).

Añado un tercer ejemplo en openapi_demo.py:
"no_income": {
    "summary": "Sin income: 422",
    "value": {"age": 42},
},
Sale en el desplegable con los otros dos y al ejecutarlo da 422 con "Field required" en income.
Como el test test_openapi_documents_errors_and_examples compara los ejemplos con {"valid", "minor"} lo he cambiado a {"valid", "minor", "no_income"}. Así pytest sigue en verde.

**05 M4 - Tests - Localiza el test que usa dependency_overrides, quita temporalmente raise_server_exceptions=False del fixture errors_client y explica qué cambia y escribe un test nuevo para income: 0.**

a)
Lo que es cada cosa que sale en los tests:
- TestClient es un cliente de FastAPI para probar la API sin arrancarla. Se le hacen get y post como si fuera un navegador.
- Un fixture (errors_client) es una función de pytest que prepara algo que luego usan los tests.
- dependency_overrides es un diccionario de la app que sirve para cambiar una dependencia solo mientras dura el test.

El test que lo usa es test_dependency_override_simulates_unavailable_model. Cambia get_model por una función que devuelve un Model con ready = False. Así se simula que el modelo no está listo sin tocar el código de la API y la respuesta es 503 con model_unavailable. El fixture limpia los overrides al acabar (dependency_overrides.clear()) para que no afecten a otros tests.

b)
raise_server_exceptions=False es una opción del TestClient. Si la quito el cliente vuelve a lanzar dentro del test los errores que explotan en el servidor. Entonces test_unexpected_error_hides_secrets ya no recibe el 500 y falla con el RuntimeError original (el que lleva el TU_SECRETO). Con la opción puesta el test ve lo mismo que vería un cliente de verdad que es un 500 normal con nuestro formato de error. Después se vuelve a dejar como estaba.

c)
Con esta función vamos a comprobar que si mandamos income = 0 la API contesta 422 y dice que el fallo está en income.

def test_income_cero_se_rechaza(errors_client: TestClient) -> None:
    response = errors_client.post("/v1/scores", json={"age": 30, "income": 0})

    assert response.status_code == 422
    assert response.json()["error"]["fields"][0]["field"] == "income"

Da 422 porque income tiene gt=0 (mayor que 0) y 0 no lo cumple. Con este test nuevo la suite queda en verde con 10 tests.
