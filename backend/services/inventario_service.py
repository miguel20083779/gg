from models.producto import Producto
from typing import Dict

class InventarioService:
    def __init__(self):
        self.productos: Dict[str, Producto] = {}

    def listar(self):
        return list(self.productos.values())

    def agregar(self, producto: Producto):
        if producto.codigo in self.productos:
            return False
        self.productos[producto.codigo] = producto
        return True

    def obtener(self, codigo: str):
        return self.productos.get(codigo)

    def actualizar(self, codigo: str, producto: Producto):
        if codigo not in self.productos:
            return False
        self.productos[codigo] = producto
        return True

    def eliminar(self, codigo: str):
        if codigo not in self.productos:
            return False
        del self.productos[codigo]
        return True
