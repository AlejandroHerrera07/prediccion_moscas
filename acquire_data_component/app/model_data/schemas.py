from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RegistroSensorCrear(BaseModel):
    id_contenedor: str = Field(..., max_length=30)
    id_sensor: str = Field(..., max_length=30)
    fecha: datetime
    valor: float


class LarvaMetrics(BaseModel):
    humedad: float | None = None
    n_organico: float | None = None
    grasa: float | None = None
    proteina: float | None = None


class FrassMetrics(BaseModel):
    humedad: float | None = None
    ph: float | None = None
    cenizas: float | None = None
    c_organico: float | None = None
    n_total: float | None = None
    c_n: float | None = None
    fosforo: float | None = None
    potasio: float | None = None
    densidad: float | None = None


class PrediccionRegistro(BaseModel):
    id_ensayo: str
    id_mezcla: str
    residuo_base: str | None = None
    temperatura: float
    relacion_c_n: float
    larvas_observadas: LarvaMetrics
    larvas_predichas: LarvaMetrics
    frass_observado: FrassMetrics
    frass_predicho: FrassMetrics
    tasa_bioconversion: float | None = None


class PrediccionLoteSalida(BaseModel):
    total_ensayos: int
    temperatura_optima: float | None = None
    tasa_bioconversion_maxima: float | None = None
    resultados: list[PrediccionRegistro]


class PrediccionEnsayoSalida(PrediccionRegistro):
    pass
