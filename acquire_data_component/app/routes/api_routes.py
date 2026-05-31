# app/routes/api_routes.py
from fastapi import APIRouter
from app.model_data.schemas import PrediccionEntrada, PrediccionSalida
from app.calculate_values.predictor import MotorCalculo

router = APIRouter()
calculador = MotorCalculo()

# Usamos PrediccionSalida para formatear la respuesta
@router.post("/prediccion", response_model=PrediccionSalida)
def obtener_prediccion(datos_entrada: PrediccionEntrada): # Usamos PrediccionEntrada para validar lo que entra
    
    # Si FastAPI deja pasar el código hasta aquí, significa que los datos_entrada
    # son 100% correctos y no falta ninguna variable.
    
    # Convertimos el esquema validado a un diccionario para la matemática
    resultado = calculador.calcular_predicciones(datos_entrada.model_dump())
    
    return resultado