"""S9.4 — Tests que escribe el alumnado.

Cada test empieza en rojo con `pytest.fail`. Sustituye esa línea por el test
real; la entrega se considera completa cuando toda la suite está en verde.
"""

import pytest
from fastapi.testclient import TestClient

from wine_api.dependencies import get_predictor  # noqa: F401 - pista S9.4a
from wine_api.export_openapi import DEFAULT_PATH, render_openapi
from wine_api.predictor import UnavailablePredictor  # noqa: F401 - pista S9.4a


def test_prediction_returns_503_when_model_is_unavailable(
    client: TestClient, valid_payload: dict
) -> None:
    # TODO S9.4a: sin tocar el código de la API, haz que `get_predictor`
    # devuelva un UnavailablePredictor con `app.dependency_overrides` (llega
    # desde `client.app`). Comprueba status 503 y `error.code`. Limpia el
    # override al terminar para no contaminar otros tests.
    # Cambio el predictor solo para este test
    client.app.dependency_overrides[get_predictor] = lambda: UnavailablePredictor()

    response = client.post("/v1/predictions", json=valid_payload)

    client.app.dependency_overrides.clear()  # lo limpio al acabar
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "model_unavailable"


# Cada caso es un campo con un valor malo
@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("alcohol", 4.9),  # justo por debajo del mínimo
        ("alcohol", 20.1),  # Justo por encima del máximo
        ("ph", None),  # nulo
        ("density", "denso"),  # Un texto
        ("chlorides", -0.1),  # negativo
    ],
)
def test_out_of_contract_values_are_rejected(
    client: TestClient, valid_payload: dict, campo: str, valor: object
) -> None:
    # TODO S9.4b: convierte este test en `@pytest.mark.parametrize` con al
    # menos cinco casos (justo por debajo y por encima de un rango, None, un
    # texto...). Para cada uno comprueba 422 y que `fields` señala exactamente
    # `features.<campo>`.
    valid_payload["features"][campo] = valor

    response = client.post("/v1/predictions", json=valid_payload)

    assert response.status_code == 422
    campos = []
    for fallo in response.json()["error"]["fields"]:
        campos.append(fallo["field"])
    assert campos == [f"features.{campo}"]  # solo tiene que salir el campo malo


def test_range_limits_are_inclusive(client: TestClient, valid_payload: dict) -> None:
    # TODO S9.4c: los límites del contrato son inclusivos. Demuéstralo con los
    # dos extremos de `alcohol` (5 y 20): ambos deben devolver 200.
    for limite in (5, 20):  # el mínimo y el máximo de alcohol
        valid_payload["features"]["alcohol"] = limite

        response = client.post("/v1/predictions", json=valid_payload)

        assert response.status_code == 200


def test_openapi_matches_versioned_contract() -> None:
    # TODO S9.4d: genera `contracts/openapi.json` con
    # `uv run python -m wine_api.export_openapi` y versiónalo en Git. Después
    # compara el JSON de `render_openapi()` con el archivo: si alguien cambia el
    # contrato sin querer, este test lo detecta en la revisión.
    # Si cambia la api y no el archivo el test falla
    assert render_openapi() == DEFAULT_PATH.read_text(encoding="utf-8")
