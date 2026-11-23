"""Punto de entrada de la API: `fastapi dev` usa `wine_api.main:app`."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wine_api.errors import install_error_handlers
from wine_api.predictor import Predictor, build_predictor
from wine_api.request_id import request_id_middleware
from wine_api.routers import health, predictions

# TODO S9.3g: completa los metadatos que lee el consumidor en /docs:
# `version` (¿mayor, menor o parche tras S9.1c?), `summary`, una `description`
# en Markdown que explique `request_id` y el sobre de error, y `openapi_tags`
# con una descripción por tag. Comprobación: tests/test_s9_3_openapi.py
API_VERSION = "1.1.0"  # Añadir served_at no rompe nada así que sube la menor

RESUMEN_API = "Predice la banda de calidad de un vino tinto."

DESCRIPCION_API = """
API de ejemplo para predecir la calidad de un vino tinto a partir de sus
variables fisicoquímicas.

**request_id.** Cada respuesta lleva un `request_id` en el cuerpo y en la
cabecera `X-Request-Id`. Se usa para localizar una petición en los logs.

**Errores.** Todos los errores tienen la misma forma:
`{"error": {"code", "message", "fields"}, "request_id"}`. Programa contra
`code`, que es estable, y no contra `message`. `fields` solo aparece en los
errores de validación.
"""

ETIQUETAS_API = [
    {"name": "health", "description": "Estado del servicio y del modelo."},
    {"name": "predictions", "description": "Predicción de la calidad del vino."},
]


def create_app(predictor: Predictor | None = None) -> FastAPI:
    """Crea la aplicación; los tests inyectan su propio predictor."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.predictor = predictor or build_predictor(
            os.environ.get("WINE_API_MODE", "ready")
        )
        yield

    app = FastAPI(
        title="Wine Quality API",
        version=API_VERSION,
        summary=RESUMEN_API,
        description=DESCRIPCION_API,
        openapi_tags=ETIQUETAS_API,
        lifespan=lifespan,
    )
    app.middleware("http")(request_id_middleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(predictions.router)
    return app


app = create_app()
