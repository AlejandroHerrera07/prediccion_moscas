from fastapi import APIRouter, Depends, HTTPException

from ..calculate_values.predictor import MotorCalculo
from ..model_data.database import get_supabase_client
from ..model_data.schemas import (
    PrediccionEnsayoSalida,
    PrediccionLoteSalida,
    ResiduoCrear,
    ResiduoSalida,
)

router = APIRouter()
calculador = MotorCalculo()


@router.get(
    "/prediccion",
    response_model=PrediccionLoteSalida,
    tags=["Prediccion"],
    summary="Obtener predicción de todos los ensayos",
    description="Calcula las predicciones de larvas y frass para todos los ensayos disponibles en Supabase.",
)
def obtener_prediccion(client=Depends(get_supabase_client)):
    try:
        return calculador.calcular_predicciones(client)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/prediccion/{id_ensayo}",
    response_model=PrediccionEnsayoSalida,
    tags=["Prediccion"],
    summary="Obtener predicción de un ensayo",
    description="Calcula la predicción para un ensayo específico por su identificador.",
)
def obtener_prediccion_ensayo(id_ensayo: str, client=Depends(get_supabase_client)):
    try:
        return calculador.calcular_prediccion_ensayo(client, id_ensayo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/residuos",
    response_model=list[ResiduoSalida],
    tags=["Residuos"],
    summary="Listar residuos",
    description="Devuelve todos los residuos almacenados en Supabase.",
)
def obtener_residuos(client=Depends(get_supabase_client)):
    try:
        return client.table("Residuos").select("*").execute().data
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/residuos",
    response_model=ResiduoSalida,
    status_code=201,
    tags=["Residuos"],
    summary="Crear residuo",
    description="Inserta un nuevo residuo en Supabase validando el esquema de Database.sql.",
)
def crear_residuo(residuo: ResiduoCrear, client=Depends(get_supabase_client)):
    try:
        resultado = client.insert("Residuos", residuo.model_dump())
        if not resultado:
            raise RuntimeError("Supabase no devolvió el residuo insertado.")
        return resultado[0]
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
