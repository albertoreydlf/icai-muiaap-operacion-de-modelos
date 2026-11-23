from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)

# TODO S9.3a: mueve aquí `prefix="/v1/predictions"` y `tags=["predictions"]`.
# TODO S9.3c: declara a nivel de router `responses=` para 400, 422 y 503 con
# `{"model": ErrorResponse, "description": ...}`. Así el 422 deja de
# documentarse como `HTTPValidationError`, que ya no es lo que devolvemos.
router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        400: {"model": ErrorResponse, "description": "El cuerpo no es JSON válido."},
        422: {"model": ErrorResponse, "description": "El cuerpo incumple el contrato."},
        503: {"model": ErrorResponse, "description": "Modelo no disponible."},
    },
)

# Tres cuerpos para probar en swagger (uno bien y dos mal)
EJEMPLOS = {
    "valid": {
        "summary": "Cuerpo válido",
        "value": {"features": VALID_FEATURES_EXAMPLE},
    },
    "alcohol_fuera_de_rango": {
        "summary": "Alcohol por encima del máximo (422)",
        "value": {"features": {**VALID_FEATURES_EXAMPLE, "alcohol": 25.0}},
    },
    "alcohol_texto": {
        "summary": "Alcohol como texto (422)",
        "value": {"features": {**VALID_FEATURES_EXAMPLE, "alcohol": "mucho"}},
    },
}


@router.post(
    "",
    summary="Predecir la calidad de un vino tinto",
    response_description="Banda de calidad con su confianza.",
)
def create_prediction(
    payload: Annotated[PredictionRequest, Body(openapi_examples=EJEMPLOS)],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:
    """Predice la banda de calidad de un vino a partir de sus once variables.

    Envía las once variables fisicoquímicas dentro de `features`, cada una dentro
    de su rango (los límites valen). La confianza va entre 0 y 1 con dos
    decimales. Si el JSON está mal formado devuelve 400, si un campo incumple el
    contrato devuelve 422 y si el modelo no está listo devuelve 503.
    """
    # TODO S9.3e: añade summary, response_description y un docstring útil para
    # quien consume la API (campos, rangos, decimales de confidence).
    # TODO S9.3f: ofrece en Swagger al menos tres ejemplos de cuerpo (uno válido
    # y dos inválidos). Investiga `Annotated[PredictionRequest, Body(...)]` con
    # `openapi_examples=`; usa VALID_FEATURES_EXAMPLE como base.
    output = predictor.predict(payload.features)
    # TODO S9.1e: este dict expone `raw_score` y la confianza sin redondear.
    # Declara `-> PredictionResponse` y construye el modelo; para pasar de la
    # dataclass ModelOutput a Prediction investiga `from_attributes=True`.
    return PredictionResponse(
        # Solo salen los 4 campos públicos y raw_score se queda fuera
        prediction=Prediction.model_validate(output, from_attributes=True),
        request_id=request_id,
        served_at=datetime.now(UTC),  # la hora de ahora en utc
    )
