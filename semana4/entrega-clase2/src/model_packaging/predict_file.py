"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    infer_wine_quality,
    load_model_bundle,
)
from model_packaging.contracts import WineQualityRequest


# columnas del csv de salida, en este orden
COLUMNAS_SALIDA = [
    "sample_id",
    "quality_band",
    "confidence",
    "model_version",
    "preprocessing_version",
]

def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """TODO: valida todas las filas y escribe el CSV solo al final."""
#Paso 1: Cargar el bundle
    bundle = load_model_bundle(bundle_path)  # ya comprueba el manifest al cargarlo

    #Paso 2: Leer el CSV y predecir cada fila, sin escribir nada todavía
    resultados = []  # aquí voy guardando las filas ya predichas
    with open(input_path, newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            sample_id = fila.pop("sample_id", "")  # lo saco porque no es una medida del vino(con pop se guarda en sample_id ademas de quitarlo)
            try:
                peticion = WineQualityRequest(**fila)  # compruebo que la fila cumple el contrato de entrada
                prediccion = infer_wine_quality(bundle, peticion)  # predigo y compruebo la salida
            except ValueError as error:  # Si falla algo digo qué fila ha sido
                raise ValueError(f"Fila inválida (línea {lector.line_num}): {error}") from error
            fila_de_salida = prediccion.model_dump()  # la predicción pasada a diccionario
            fila_de_salida["sample_id"] = sample_id  # le añado el sample_id
            resultados.append(fila_de_salida)

    if not resultados:
        raise ValueError("El CSV no tiene filas")

    # Paso 3:Escribir el CSV solo si todas las filas han ido bien
    output_path.parent.mkdir(parents=True, exist_ok=True)  # crea la carpeta de salida si no existe
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_SALIDA)
        escritor.writeheader()
        for resultado in resultados:
            escritor.writerow(resultado)

    return len(resultados)  # cuántas filas he predicho
    raise NotImplementedError("Implementa predict_file().")


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )
