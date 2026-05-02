from pydantic import BaseModel

class Producto(BaseModel):
    codigo: str
    nombre: str
    precio: float
    cantidad: int
    umbral_minimo: int
