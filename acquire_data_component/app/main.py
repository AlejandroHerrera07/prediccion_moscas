# app/main.py
from fastapi import FastAPI
from app.routes.api_routes import router
from app.middleware.core_middleware import setup_middleware
from app.model_data import database
from app.model_data import models  # noqa: F401

app = FastAPI(title="Acquire Data Component API")

# 1. Pasa por el Middleware
setup_middleware(app)

# 2. Llega a las rutas
app.include_router(router, prefix="/api")
