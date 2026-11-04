"""Starter de la primera interfaz Streamlit para Wine Quality."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from model_ui.contracts import PredictionPayload
from model_ui.errors import ArtifactUnavailableError, InputContractError
from model_ui.gateway import InferenceGateway, PackagedBundleGateway
from model_ui.ui_schema import FIELD_SPECS


def build_gateway() -> InferenceGateway:
    """Carga obligatoriamente el bundle de S4 configurado."""

    bundle_value = os.getenv("MODEL_UI_BUNDLE")
    if not bundle_value:
        raise ArtifactUnavailableError("MODEL_UI_BUNDLE no está configurado.")
    try:
        return PackagedBundleGateway.from_bundle_path(Path(bundle_value))
    except Exception as error:  # noqa: BLE001
        raise ArtifactUnavailableError("No se pudo cargar el bundle de S4.") from error


def render_bundle_error(st: Any) -> None:
    """Presenta una recuperación segura sin revelar detalles internos."""

    st.error("No se pudo cargar el bundle de S4.")
    st.info("Configura MODEL_UI_BUNDLE y vuelve a ejecutar la aplicación.")


def render_inference_error(st: Any) -> None:
    """Presenta un fallo de validación o inferencia sin detalles sensibles."""

    st.error("No se pudo ejecutar la inferencia.")
    st.info("Revisa los datos y la compatibilidad del bundle de S4.")


def collect_values(st: Any) -> tuple[bool, dict[str, float]]:
    """TODO: renderiza ``FIELD_SPECS`` dentro de un único ``st.form``.

    Cada ``number_input`` debe recibir label, rango, default, step y una key
    estable. Devuelve ``(submitted, values)`` sin llamar al gateway.
    """
    # cada campo tiene la forma:
    #  FieldSpec(
    #       name="fixed_acidity",
    #       label="Acidez fija",
    #       min_value=0.0,
    #       max_value=20.0,
    #       default=7.4,
    #       step=0.1,
    #   ),
    # FieldSpec(
    #        name="volatile_acidity",
    #        label="Acidez volátil",
    #        min_value=0.0,
    #        max_value=2.0,
    #        default=0.7,
    #        step=0.01,
    #    ),...

    valores = {}
    with st.form("wine_quality_form"):
        for campo in FIELD_SPECS:  # una vuelta por cada campo
            valores[campo.name] = st.number_input(  # Casilla y guardo su valor
                campo.label,  # Texto que se ve encima
                min_value=campo.min_value,  # el minimo
                max_value=campo.max_value,  # el maximo
                value=campo.default,  # lo que sale al abrir la app
                step=campo.step,  # Cuánto sube con el + y el -
                key=f"input_{campo.name}",  # nombre interno de cada casilla,la clave
                # por la q se reconce
            )
        enviado = st.form_submit_button("Ejecutar inferencia")  # True si lo pulsan
    return enviado, valores  # devuelvo si pulsó y los 11 valores


def render_prediction(st: Any, prediction: PredictionPayload) -> None:
    """TODO: presenta los cuatro campos de ``PredictionPayload``."""
    # prediction tiene esta forma,es un objeto al que accedemos con prediction.loqsea
    # class PredictionPayload(BaseModel):
    # """Respuesta validada que llega desde el gateway."""
    #
    # model_config = ConfigDict(extra="forbid")
    #
    # quality_band: QualityBand
    # confidence: FiniteFloat = Field(ge=0, le=1)
    # model_version: str = Field(min_length=1)
    # preprocessing_version: str = Field(min_length=1)
    st.info("Resultado del modelo")  # un aviso azul de título
    st.caption(f"quality_band: {prediction.quality_band}")  # la calidad
    st.caption(
        f"confidence: {prediction.confidence:.2f}"
    )  # La confianza con 2 decimales
    st.caption(f"model_version: {prediction.model_version}")  # versión del modelo
    st.caption(
        f"preprocessing_version: {prediction.preprocessing_version}"
    )  # Y del preproceso
    # st.write es lo mismo que el st.caption pero sale la letra mas grande.


def run_app(st: Any, gateway: InferenceGateway) -> None:
    """Conecta submit, gateway y salida sin añadir estado avanzado."""

    submitted, values = collect_values(st)
    if not submitted:
        st.info("Completa el formulario y pulsa «Ejecutar inferencia».")
        return

    try:
        prediction = gateway.predict(values)
    except ArtifactUnavailableError:
        render_bundle_error(st)
        return
    except InputContractError:
        render_inference_error(st)
        return
    except ValueError:
        render_inference_error(st)
        return

    render_prediction(st, prediction)


def run_configured_app(
    st: Any,
    gateway_factory: Callable[[], InferenceGateway] = build_gateway,
) -> None:
    """Carga la configuración y contiene cualquier fallo del bundle."""

    try:
        gateway = gateway_factory()
    except ArtifactUnavailableError:
        render_bundle_error(st)
        return
    run_app(st, gateway)


def main() -> None:
    """Ejecuta la pantalla básica; S6 añadirá estado explícito."""

    try:
        import streamlit as st
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Instala Streamlit con `uv run --with streamlit streamlit run app.py`."
        ) from error

    st.set_page_config(page_title="Wine Quality · S5", page_icon="🍷")
    st.title("Primera interfaz de inferencia")
    st.caption("S5: formulario, gateway y resultado; el estado avanzado llega en S6.")

    run_configured_app(st)


if __name__ == "__main__":
    main()
