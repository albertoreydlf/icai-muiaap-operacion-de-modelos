from fastapi import APIRouter

from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada
from app.services.modelo import predecir

router = APIRouter()


# TODO: POST /predict (entrada PrestamoEntrada, salida PrediccionSalida)

@router.post("/predict", response_model = PrediccionSalida) #creamos el endpoint y es post pq el cliente envia datos(el prestamo)
def predict(entrada : PrestamoEntrada):
    return predecir(entrada) # llamo al modelo y devuelvo el resultado

