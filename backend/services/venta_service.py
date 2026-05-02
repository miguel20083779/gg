from models.venta import Venta
from typing import List

class VentaService:
    def __init__(self):
        self.ventas: List[Venta] = []

    def listar(self):
        return self.ventas

    def registrar(self, venta: Venta):
        self.ventas.append(venta)
        return venta
