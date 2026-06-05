# app/main.py
from fastapi import FastAPI
from .routes.api_routes import router
from .middleware.core_middleware import setup_middleware

app = FastAPI(title="Acquire Data Component API")

# 1. Pasa por el Middleware
setup_middleware(app)

# 2. Llega a las rutas
app.include_router(router, prefix="/api")
