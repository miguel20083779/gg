from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.productos import router as productos_router
from routes.ventas import router as ventas_router
from routes.caja import router as caja_router

app = FastAPI()

# Permitir acceso desde cualquier origen (para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(productos_router)
app.include_router(ventas_router)
app.include_router(caja_router)
