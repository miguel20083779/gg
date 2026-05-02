from fastapi import APIRouter, HTTPException
from models.producto import Producto
from services.inventario_service import InventarioService

router = APIRouter()
inventario_service = InventarioService()

@router.get("/productos", response_model=list[Producto])
def listar_productos():
    return inventario_service.listar()

@router.post("/productos", response_model=Producto)
def agregar_producto(producto: Producto):
    if not inventario_service.agregar(producto):
        raise HTTPException(status_code=400, detail="El producto ya existe")
    return producto

@router.get("/productos/{codigo}", response_model=Producto)
def obtener_producto(codigo: str):
    producto = inventario_service.obtener(codigo)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.put("/productos/{codigo}", response_model=Producto)
def actualizar_producto(codigo: str, producto: Producto):
    if not inventario_service.actualizar(codigo, producto):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.delete("/productos/{codigo}")
def eliminar_producto(codigo: str):
    if not inventario_service.eliminar(codigo):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"ok": True}
