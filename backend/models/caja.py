from pydantic import BaseModel

class Caja(BaseModel):
    saldo_inicial: float
    saldo_final: float
    fecha_apertura: str
    fecha_cierre: str
