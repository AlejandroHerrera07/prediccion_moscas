from fastapi import APIRouter, Depends, HTTPException

from ..calculate_values.predictor import MotorCalculo
from ..model_data.database import get_supabase_client
from ..model_data.schemas import PrediccionEnsayoSalida, PrediccionLoteSalida

router = APIRouter()
calculador = MotorCalculo()


@router.get("/prediccion", response_model=PrediccionLoteSalida)
def obtener_prediccion(client=Depends(get_supabase_client)):
    try:
        return calculador.calcular_predicciones(client)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/prediccion/{id_ensayo}", response_model=PrediccionEnsayoSalida)
def obtener_prediccion_ensayo(id_ensayo: str, client=Depends(get_supabase_client)):
    try:
        return calculador.calcular_prediccion_ensayo(client, id_ensayo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
