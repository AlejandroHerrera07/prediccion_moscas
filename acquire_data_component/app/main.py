# app/main.py
from fastapi import FastAPI
from .routes.api_routes import router
from .middleware.core_middleware import setup_middleware

openapi_tags = [
    {
        "name": "Prediccion",
        "description": "Endpoints para calcular predicciones de larvas y frass desde Supabase.",
    },
    {
        "name": "Residuos",
        "description": "Endpoints para listar y registrar residuos en Supabase.",
    },
]

app = FastAPI(
    title="Acquire Data Component API",
    description="API para consulta de predicciones y gestión básica de residuos sobre Supabase.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=openapi_tags,
)

# 1. Pasa por el Middleware
setup_middleware(app)

# 2. Llega a las rutas
app.include_router(router, prefix="/api")
