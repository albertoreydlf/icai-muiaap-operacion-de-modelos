"""TODO: contratos de entrada y salida de la inferencia."""
from pydantic import BaseModel, ConfigDict, Field

class WineQualityRequest(BaseModel):

    model_config = ConfigDict(extra="forbid")

    sample_id: str | None = Field(min_length=1, default=None) #comprobamos que sample_id es simpre un str o nada (sin identificador) y le damos sus valores minimos

    fixed_acidity: float = Field(ge=0, le=20)



# Implementa WineQualityRequest y WineQualityPrediction con Pydantic.
# Revisa los campos de assets/inference_samples.csv y prohíbe columnas extra.
