# app/middleware/core_middleware.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_middleware(app: FastAPI):
    # Configuración para permitir que el Visualization_component (frontend) se conecte
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # En producción cambiar por la URL de tu frontend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )