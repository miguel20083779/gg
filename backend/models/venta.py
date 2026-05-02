from pydantic import BaseModel
from typing import List
from .producto import Producto

class Venta(BaseModel):
    id: int
    productos: List[Producto]
    total: float
    metodo_pago: str
    fecha: str
