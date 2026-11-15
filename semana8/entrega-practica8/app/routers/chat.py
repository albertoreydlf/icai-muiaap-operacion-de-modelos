from fastapi import APIRouter, Depends

from app.schemas.chat import ChatEntrada, ChatSalida
from app.services.llm import get_llm
from app.services.orquestador import responder

router = APIRouter()


# TODO: POST /chat (entrada ChatEntrada, salida ChatSalida). Recibe el LLM con Depends(get_llm)
@router.post("/chat", response_model=ChatSalida)  # recibe la conversacion y responde con esta forma
def chat(entrada: ChatEntrada, llm=Depends(get_llm)):  # FastAPI valida el JSON y me da el LLM(funcion de llm.py)
    return responder(entrada.mensajes, llm)  # el orquestador lleva la conversacion