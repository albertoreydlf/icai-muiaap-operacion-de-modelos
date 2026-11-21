from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# TODO: clase PrestamoEntrada (BaseModel) con las 6 variables del modelo, con sus rangos (ver enunciado).
#       Debe rechazar campos que no existan.
class PrestamoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edad: int = Field(ge=18, le=75)
    ingresos_mensuales: float = Field(gt=0)
    importe_prestamo: float = Field(gt=0)
    plazo_meses: int = Field(ge=6, le=84)
    antiguedad_laboral_anios: int = Field(ge=0, le=50)
    impagos_previos: int = Field(ge=0, le=20)

    # TODO: field_validator (con classmethod) para antiguedad_laboral_anios: no puede ser incoherente con la edad.
    @field_validator("antiguedad_laboral_anios")
    @classmethod
    def valid_age(cls, valor, info):
        # cls: la clase.
        # valor: el valor de la antigüedad que se está comprobando.
        # info.data es un diccionario con los campos ya validados (los que están escritos antes en la clase).
        # Aquí saco la edad. Uso .get porque si la edad falló (por ejemplo, un 5), no estará en el diccionario y .get devuelve None en vez de dar error
        edad = info.data.get("edad")
        if edad is not None and valor > edad - 16:
            raise ValueError("la antiguedad no puede ser mayor que edad - 16")
        return valor


# TODO: clase PrediccionSalida con probabilidad_impago (entre 0 y 1) y decision (aprobar, revisar o rechazar).
class PrediccionSalida(BaseModel):
    probabilidad_impago: float = Field(ge=0, le=1)  # una probabilidad va de 0 a 1
    decision: Literal["aprobar", "revisar", "rechazar"]
