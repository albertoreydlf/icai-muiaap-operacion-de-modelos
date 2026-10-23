"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)
from model_packaging.preprocess import FEATURE_NAMES, PREPROCESSING_VERSION, preprocess_wine_request
import joblib

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)


class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(min_length=1)  # no puede venir vacío
    model_version: str = Field(min_length=1)
    preprocessing_version: str = Field(min_length=1)  # tampoco puede venir vacío
    feature_names: tuple[str, ...] = Field(min_length=1)  # tiene que haber al menos una feature
    output_labels: tuple[QualityBand, ...] = Field(min_length=1)  # y al menos una etiqueta
    estimator_type: str = Field(min_length=1)


@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """TODO: devuelve un manifiesto compatible con el contrato."""

    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,  # La forma del manifest, ya está definida arriba en el archivo
        model_version=model_version,  #El nombre del modelo, me lo pasan al llamar a la función
        preprocessing_version= PREPROCESSING_VERSION,  # la versión del preprocesado de la semana 3(lo he traido con un import)
        feature_names=FEATURE_NAMES,  #las 11 columnas en su orden
        output_labels=OUTPUT_LABELS,  #las tres etiquetas permitidas, también definidas arriba
        estimator_type=type(estimator).__name__,  #el nombre de la clase del modelo que me pasan
    )

    raise NotImplementedError("Implementa create_manifest().")


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """TODO: escribe manifest.json y model.joblib de forma segura."""
    #hecho con IA porque no sabia hacerlo
    bundle_path.mkdir(parents=True, exist_ok=True)  # crea la carpeta si no existe, como hice con el CSV

    with open(bundle_path / MANIFEST_FILENAME, "w", encoding="utf-8") as file:  # abro manifest.json para escribir
        file.write(manifest.model_dump_json(indent=2))  # escribo el manifest como texto JSON

    joblib.dump(estimator, bundle_path / MODEL_FILENAME)  # guardo el modelo en model.joblib

    return manifest

    raise NotImplementedError("Implementa save_model_bundle().")

def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """Lee el manifest y lo comprueba antes de cargar el modelo."""

    if not (bundle_path / "manifest.json").exists():  # miro si hay un manifest.json dentro de la carpeta
        raise FileNotFoundError("No encuentro manifest.json")

    with open(bundle_path / "manifest.json", encoding="utf-8") as f:  # abro el manifest.json
        manifest = ArtifactManifest.model_validate_json(f.read())  # Compruebo que tiene los seis campos y nada más

    if manifest.schema_version != ARTIFACT_SCHEMA_VERSION:
        raise ValueError("La forma del manifest no es la que espero")
    if manifest.preprocessing_version != PREPROCESSING_VERSION:  # el preprocesado tiene que ser el de mi código
        raise ValueError("La versión del preprocesado no coincide")
    if manifest.feature_names != FEATURE_NAMES:  # Las features tienen que estar en el mismo orden
        raise ValueError("Las features no coinciden o están en otro orden")
    if manifest.output_labels != OUTPUT_LABELS:
        raise ValueError("Las etiquetas de salida no son las permitidas")

    if not (bundle_path / "model.joblib").exists():  # miro si está el modelo
        raise FileNotFoundError("No encuentro model.joblib")

    estimator = joblib.load(bundle_path / "model.joblib")  # solo abro el modelo cuando todo lo anterior está bien

    if type(estimator).__name__ != manifest.estimator_type:  # el modelo tiene que ser del tipo que dice el manifest
        raise ValueError("El modelo no es del tipo que dice el manifest")

    return LoadedModelBundle(estimator=estimator, manifest=manifest)

    raise NotImplementedError("Implementa load_model_bundle().")


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    # Aquí hago cuatro cosas. Primero paso los datos del vino a una lista de 11 números.Después se los doy al modelo 
    # para que prediga y me diga con qué seguridad lo hace.
    # Luego miro que la etiqueta sea una de las permitidas en el manifest.Si todo está bien devuelvo la respuesta 
    # con las versiones del manifest.

    #Paso 1: Preparar los datos
    features = preprocess_wine_request(request)  # los datos del vino ya ordenados
    numeros = features.as_vector()  # los 11 números en una lista
    matriz = [numeros]  # el modelo espera una lista de filas, así que meto mi lista dentro de otra

    #Paso 2:Predecir
    respuestas = bundle.estimator.predict(matriz)  # el modelo da una respuesta por cada fila
    categoria = respuestas[0]  # solo tengo una fila, así que me quedo con su respuesta

    # Paso 3:Calcular la confianza
    todas_las_probabilidades = bundle.estimator.predict_proba(matriz)  # una lista de probabilidades por cada fila
    probabilidades = todas_las_probabilidades[0]  # me quedo con las de mi fila
    confianza = max(probabilidades)  # la confianza es la probabilidad más alta

    # Paso 4: Comprobar la etiqueta
    if categoria not in bundle.manifest.output_labels:  # Si la etiqueta no está permitida paro
        raise ValueError(f"Etiqueta no permitida: {categoria}")

    return WineQualityPrediction(
        quality_band=categoria,
        confidence=confianza,
        model_version=bundle.manifest.model_version,  # estos dos datos salen del manifest
        preprocessing_version=bundle.manifest.preprocessing_version,
    )

    raise NotImplementedError("Implementa infer_wine_quality().")
