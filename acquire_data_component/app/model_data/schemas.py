from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RegistroSensorCrear(BaseModel):
    id_contenedor: str = Field(..., max_length=30)
    id_sensor: str = Field(..., max_length=30)
    fecha: datetime
    valor: float


class ResiduoBase(BaseModel):
    nombre: str = Field(..., max_length=100, examples=["Residuos de alimentos vegetales frescos"])
    humedad: float = Field(..., examples=[83.6])
    ph: float = Field(..., examples=[4.5])
    cenizas: float = Field(..., examples=[90.94])
    carbono_organico: float = Field(..., examples=[76.08])
    nitrogeno_total: float = Field(..., examples=[0.34])
    carbono_nitrogeno: float = Field(..., examples=[117.82])
    fosforo: float = Field(..., examples=[0.85])
    potasio: float = Field(..., examples=[0.4])
    calcio: float = Field(..., examples=[0.3])
    magnesio: float = Field(..., examples=[0.1])
    densidad: float = Field(..., examples=[0.4])
    lignina: float = Field(..., examples=[0.45])


class ResiduoCrear(ResiduoBase):
    id_residuo: str = Field(..., max_length=30, examples=["RES-015"])


class ResiduoSalida(ResiduoCrear):
    pass


class LarvaMetrics(BaseModel):
    humedad: float | None = Field(None, examples=[65.6])
    n_organico: float | None = Field(None, examples=[27.9])
    grasa: float | None = Field(None, examples=[8.37])
    proteina: float | None = Field(None, examples=[52.3])


class FrassMetrics(BaseModel):
    humedad: float | None = Field(None, examples=[51.6])
    ph: float | None = Field(None, examples=[6.48])
    cenizas: float | None = Field(None, examples=[7.32])
    c_organico: float | None = Field(None, examples=[15.5])
    n_total: float | None = Field(None, examples=[1.82])
    c_n: float | None = Field(None, examples=[8.5])
    fosforo: float | None = Field(None, examples=[1.3])
    potasio: float | None = Field(None, examples=[0.45])
    densidad: float | None = Field(None, examples=[1.8798])


class PrediccionRegistro(BaseModel):
    id_ensayo: str = Field(..., examples=["ENS-002"])
    id_mezcla: str = Field(..., examples=["MEZ-002"])
    residuo_base: str | None = Field(None, examples=["Residuos de alimentos vegetales frescos"])
    temperatura: float = Field(..., examples=[27.0])
    relacion_c_n: float = Field(..., examples=[12.0])
    larvas_observadas: LarvaMetrics
    larvas_predichas: LarvaMetrics
    frass_observado: FrassMetrics
    frass_predicho: FrassMetrics
    tasa_bioconversion: float | None = None


class PrediccionLoteSalida(BaseModel):
    total_ensayos: int = Field(..., examples=[11])
    temperatura_optima: float | None = Field(None, examples=[27.0])
    tasa_bioconversion_maxima: float | None = Field(None, examples=[25.21])
    resultados: list[PrediccionRegistro]


class PrediccionEnsayoSalida(PrediccionRegistro):
    pass
