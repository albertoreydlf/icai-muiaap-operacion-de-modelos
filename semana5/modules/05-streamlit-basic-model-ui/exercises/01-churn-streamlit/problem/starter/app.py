"""Starter: conecta una función de inferencia pura con Streamlit."""

from collections.abc import Callable
from typing import Any

from churn_demo.model import ChurnPrediction, predict

Predictor = Callable[..., ChurnPrediction]


def collect_profile(st: Any) -> tuple[bool, dict[str, object]]:
    """Renderiza cuatro widgets dentro de un único formulario."""
    # TODO 1 (alumno): usa st.form("churn_form"), los cuatro widgets con las
    # claves indicadas en el README y st.form_submit_button. El formulario evita
    # inferencias durante cada edición. Compruébalo con el primer test de app.
    with st.form("churn_form"):
        antiguedad = st.slider(
            "Antigüedad (Meses)", 0, 120, 12, key="tenure_months"
        )  # Se escribe: texto, mínimo, máximo, valor inicial.
        gasto_mensual = st.number_input(
            "Gasto mensual",
            min_value=0.0,
            max_value=300.0,
            value=60.0,
            key="monthly_spend_eur",
        )
        llamadas_a_soporte = st.slider(
            "Llamadas a soporte", 0, 20, 1, key="support_calls"
        )
        contrato_anual = st.checkbox(
            "Contrato anual", value=False, key="has_annual_contract"
        )

        enviado = st.form_submit_button("Calcular riesgo")

    return (
        enviado,
        {  # devuelvo dos cosas, si pulsó(enviado es true o false) y los 4 valores
            "tenure_months": antiguedad,
            "monthly_spend_eur": gasto_mensual,
            "support_calls": llamadas_a_soporte,
            "has_annual_contract": contrato_anual,
        },
    )


def render_prediction(st: Any, result: ChurnPrediction) -> None:
    """Muestra etiqueta, score orientativo y explicación."""
    # TODO 3 (alumno): presenta label, risk_score y explanation con componentes
    # Streamlit. No recalcules el score. Compruébalo con el test de presentación.
    if result["will_churn"]:
        st.warning(result["label"])  # amarillo si se da de baja
    else:
        st.success(result["label"])  # Verde si se queda
    st.metric(
        "Score orientativo (0 a 1)", f"{result['risk_score']:.2f}"
    )  # el score con 2 decimales
    st.write(result["explanation"])  # la explicación debajo


def run_app(st: Any, predictor: Predictor) -> None:
    """Conecta submit, llamada al predictor y actualización visible."""
    # TODO 2 (alumno): llama a collect_profile, ejecuta predictor(**values) solo
    # tras el submit y una única vez; convierte ValueError en un mensaje seguro.
    # Los tests de 0/1 llamadas y de error verifican este contrato.
    enviado, valores = collect_profile(st)
    if not enviado:  # si enviado esta en false
        st.info(
            "Hay que rellenar el formulario y pulsar el boton"
        )  # recuadro azul de aviso
        return
    try:
        resultado = predictor(**valores)
    except ValueError:
        # raise ValueError("los valores recibidos no son válidos") ESTO NO!!
        # ESTO ES LO QUE QUEREMOS EVITAR.EN CASO DE VALUEERROR,HAREMOS:
        st.error(
            "No se pudo calcular el riesgo. Revisa los datos e inténtalo de nuevo."
        )  # aviso rojo de streamlit
        return  # es necesario porque si no haria el render prediction
        # con un resultado que no existe
    render_prediction(st, resultado)


def main() -> None:
    """Configura la página real y delega el flujo comprobable en run_app."""
    import streamlit as st

    st.set_page_config(page_title="Churn sintético · S5", page_icon="📉")
    st.title("¿Qué cliente podría darse de baja?")
    st.caption("Caso docente sintético; el score no es una probabilidad calibrada.")
    run_app(st, predict)


if __name__ == "__main__":
    main()
