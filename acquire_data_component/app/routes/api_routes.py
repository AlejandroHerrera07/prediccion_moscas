from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..calculate_values.predictor import MotorCalculo
from ..model_data.database import get_db
from ..model_data.schemas import PrediccionEnsayoSalida, PrediccionLoteSalida

router = APIRouter()
calculador = MotorCalculo()


@router.get("/prediccion", response_model=PrediccionLoteSalida)
def obtener_prediccion(db: Session = Depends(get_db)):
    try:
        return calculador.calcular_predicciones(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/prediccion/{id_ensayo}", response_model=PrediccionEnsayoSalida)
def obtener_prediccion_ensayo(id_ensayo: str, db: Session = Depends(get_db)):
    try:
        return calculador.calcular_prediccion_ensayo(db, id_ensayo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
