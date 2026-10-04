from pydantic import BaseModel,Field, field_validator
import pandas as pd
import scikit-learn

class WineInputSchema(BaseModel):
    sample_id: int = Field(..., description="Unique identifier for the wine sample")
    fixed_acidity: float = Field(..., description="Fixed acidity of the wine sample")
    volatile_acidity: float = Field(..., ge=0,le=20,example=0.5, description="Volatile acidity of the wine sample")
    citric_acid: float = Field(..., description="Citric acid of the wine sample")
    residual_sugar: float = Field(..., description="Residual sugar of the wine sample")
    chlorides: float = Field(..., description="Chlorides of the wine sample")
    free_sulfur_dioxide: float = Field(..., description="Free sulfur dioxide of the wine sample")
    total_sulfur_dioxide: float = Field(..., description="Total sulfur dioxide of the wine sample")
    density: float = Field(..., description="Density of the wine sample")
    pH: float = Field(..., description="pH of the wine sample")
    sulphates: float = Field(..., description="Sulphates of the wine sample")
    alcohol: float = Field(..., description="Alcohol content of the wine sample")


if __name__ == "__main__":
    mi_contrato = WineInputSchema(
        sample_id=1,
        fixed_acidity=7.4,
        volatile_acidity=0.7,
        citric_acid=0.0,
        residual_sugar=1.9,
        chlorides=0.076,
        free_sulfur_dioxide=11.0,
        total_sulfur_dioxide=34.0,
        density=0.9978,
        pH=3.51,
        sulphates=0.56,
        alcohol=9.4
    )

    df = pd.read_csv("wine_data.csv")
    for row in df.iterrows():
        valid_row = WineInputSchema(**row[1].to_dict())
        model.transform(valid_row.dict())
        model.predict(valid_row.dict)

#corregir esto

