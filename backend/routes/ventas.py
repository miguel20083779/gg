from fastapi import APIRouter
from models.venta import Venta
from services.venta_service import VentaService

router = APIRouter()
venta_service = VentaService()

@router.get("/ventas", response_model=list[Venta])
def listar_ventas():
    return venta_service.listar()

@router.post("/ventas", response_model=Venta)
def registrar_venta(venta: Venta):
    return venta_service.registrar(venta)
