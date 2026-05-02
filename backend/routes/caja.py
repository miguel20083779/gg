from fastapi import APIRouter
from models.caja import Caja
from services.caja_service import CajaService

router = APIRouter()
caja_service = CajaService()

@router.post("/caja/abrir", response_model=Caja)
def abrir_caja(caja: Caja):
    return caja_service.abrir(caja)

@router.post("/caja/cerrar")
def cerrar_caja():
    return caja_service.cerrar()

@router.get("/caja", response_model=Caja)
def obtener_caja():
    return caja_service.obtener()
