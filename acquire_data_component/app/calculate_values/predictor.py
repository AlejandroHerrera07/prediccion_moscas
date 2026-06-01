from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.model_data.models import Ensayo, Mezcla, Residuos, ResiduosMezcla


INPUT_COLUMNS = [
    "Temperatura",
    "Relacion_C_N",
    "Humedad",
    "pH",
    "Cenizas",
    "Carbono_organico_total_oxidable",
    "Nitrogeno_total",
    "Fosforo_total",
    "Potasio_total",
    "Calcio_total",
    "Magnesio_total",
    "Densidad_g_cm3",
    "Lignina_db",
    "Mezcla_Humedad",
    "Mezcla_pH",
    "Mezcla_Cenizas",
    "Mezcla_C_Org",
    "Mezcla_N_Total",
    "Mezcla_C_N",
    "Mezcla_P_Total",
    "Mezcla_K_Total",
    "Mezcla_Ca_Total",
    "Mezcla_Mg_Total",
    "Mezcla_Densidad",
    "Mezcla_Lignina",
]

LARVA_TARGETS = ["Larva_Humedad", "Larva_N_Organico", "Larva_Extracto_Etereo", "Larva_Proteina"]
FRASS_TARGETS = [
    "Frass_Humedad",
    "Frass_pH",
    "Frass_Cenizas",
    "Frass_C_Organico",
    "Frass_N_Total",
    "Frass_C_N",
    "Frass_Fosforo",
    "Frass_Potasio",
    "Frass_Densidad",
]


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _natural_key(value: str) -> tuple[int, str]:
    match = re.search(r"(\d+)$", value or "")
    return (int(match.group(1)) if match else math.inf, value or "")


def _parse_relacion_cn(nombre_mezcla: str) -> float:
    match = re.search(r"C(?::N)?(?P<ratio>\d+(?:\.\d+)?)\:1", nombre_mezcla or "")
    if not match:
        raise ValueError(f"No se pudo extraer la relacion C:N desde la mezcla '{nombre_mezcla}'.")
    return float(match.group("ratio"))


def _weighted_average(componentes: list[tuple[Residuos, float]], field_name: str) -> float | None:
    if not componentes:
        return None

    total = 0.0
    total_peso = 0.0
    for residuo, porcentaje in componentes:
        valor = getattr(residuo, field_name)
        if valor is None:
            continue
        peso = float(porcentaje) / 100.0
        total += float(valor) * peso
        total_peso += peso

    if total_peso == 0:
        return None
    return total / total_peso


@dataclass
class AjusteLineal:
    feature_names: list[str]
    coeficientes: np.ndarray

    def predecir(self, frame: pd.DataFrame) -> np.ndarray:
        X = frame[self.feature_names].astype(float).to_numpy()
        X = np.column_stack([np.ones(len(X)), X])
        return X @ self.coeficientes


class MotorCalculo:
    def __init__(self) -> None:
        self._residuo_keys_base = [
            ("Humedad", "humedad"),
            ("pH", "ph"),
            ("Cenizas", "cenizas"),
            ("Carbono_organico_total_oxidable", "carbono_organico"),
            ("Nitrogeno_total", "nitrogeno_total"),
            ("Fosforo_total", "fosforo"),
            ("Potasio_total", "potasio"),
            ("Calcio_total", "calcio"),
            ("Magnesio_total", "magnesio"),
            ("Densidad_g_cm3", "densidad"),
            ("Lignina_db", "lignina"),
        ]
        self._residuo_keys_mezcla = [
            ("Mezcla_Humedad", "humedad"),
            ("Mezcla_pH", "ph"),
            ("Mezcla_Cenizas", "cenizas"),
            ("Mezcla_C_Org", "carbono_organico"),
            ("Mezcla_N_Total", "nitrogeno_total"),
            ("Mezcla_C_N", "carbono_nitrogeno"),
            ("Mezcla_P_Total", "fosforo"),
            ("Mezcla_K_Total", "potasio"),
            ("Mezcla_Ca_Total", "calcio"),
            ("Mezcla_Mg_Total", "magnesio"),
            ("Mezcla_Densidad", "densidad"),
            ("Mezcla_Lignina", "lignina"),
        ]

    def _cargar_tablas(
        self, db: Session
    ) -> tuple[list[Ensayo], dict[str, Mezcla], dict[str, Residuos], dict[str, list[tuple[Residuos, float]]]]:
        ensayos = db.query(Ensayo).all()
        mezclas = {mezcla.Id_Mezcla: mezcla for mezcla in db.query(Mezcla).all()}
        residuos = {residuo.id_residuo: residuo for residuo in db.query(Residuos).all()}

        componentes: dict[str, list[tuple[Residuos, float]]] = {}
        for fila in db.query(ResiduosMezcla).all():
            residuo = residuos.get(fila.id_residuo)
            if residuo is None:
                continue
            componentes.setdefault(fila.id_mezcla, []).append((residuo, float(fila.porcentaje)))

        for item in componentes.values():
            item.sort(key=lambda par: (-par[1], par[0].id_residuo))

        return ensayos, mezclas, residuos, componentes

    def _inferir_residuo_base(self, ensayos: list[Ensayo], residuos: dict[str, Residuos]) -> dict[str, Residuos | None]:
        """
        La base de datos no expone un FK directo entre ensayo y residuo base.
        Mientras el esquema no lo tenga, se reproduce el orden de carga del dataset.
        """

        residuos_ordenados = sorted(residuos.values(), key=lambda r: _natural_key(r.id_residuo))
        ensayos_ordenados = sorted(ensayos, key=lambda e: _natural_key(e.id_Ensayo))
        mapa: dict[str, Residuos | None] = {}
        for indice, ensayo in enumerate(ensayos_ordenados):
            mapa[ensayo.id_Ensayo] = residuos_ordenados[indice] if indice < len(residuos_ordenados) else None
        return mapa

    def _construir_frame(self, db: Session) -> pd.DataFrame:
        ensayos, mezclas, residuos, componentes = self._cargar_tablas(db)
        base_por_ensayo = self._inferir_residuo_base(ensayos, residuos)

        registros: list[dict[str, Any]] = []
        for ensayo in sorted(ensayos, key=lambda e: _natural_key(e.id_Ensayo)):
            mezcla = mezclas.get(ensayo.id_mezcla)
            if mezcla is None:
                raise ValueError(f"No existe la mezcla '{ensayo.id_mezcla}' para el ensayo '{ensayo.id_Ensayo}'.")

            componentes_mezcla = componentes.get(mezcla.Id_Mezcla, [])
            residuo_base = base_por_ensayo.get(ensayo.id_Ensayo)

            fila: dict[str, Any] = {
                "id_ensayo": ensayo.id_Ensayo,
                "id_mezcla": ensayo.id_mezcla,
                "residuo_base": residuo_base.nombre if residuo_base is not None else None,
                "Temperatura": _to_float(ensayo.temperatura),
                "Relacion_C_N": _parse_relacion_cn(mezcla.nombre),
                "Larva_Humedad": _to_float(ensayo.larva_humedad),
                "Larva_N_Organico": _to_float(ensayo.larva_n_organico),
                "Larva_Extracto_Etereo": _to_float(ensayo.larva_extracto_etereo),
                "Larva_Proteina": _to_float(ensayo.larva_proteina),
                "Frass_Humedad": _to_float(ensayo.frass_humedad),
                "Frass_pH": _to_float(ensayo.frass_ph),
                "Frass_Cenizas": _to_float(ensayo.frass_cenizas),
                "Frass_C_Organico": _to_float(ensayo.frass_c_organico),
                "Frass_N_Total": _to_float(ensayo.frass_n_total),
                "Frass_C_N": _to_float(ensayo.frass_c_n),
                "Frass_Fosforo": _to_float(ensayo.frass_fosforo),
                "Frass_Potasio": _to_float(ensayo.frass_potasio),
                "Frass_Densidad": _to_float(ensayo.frass_densidad),
                "Tasa_Bioconversion": _to_float(ensayo.tasa_bioconversion),
            }

            if residuo_base is not None:
                for salida, atributo in self._residuo_keys_base:
                    fila[salida] = _to_float(getattr(residuo_base, atributo))
            else:
                for salida, _ in self._residuo_keys_base:
                    fila[salida] = None

            for salida, atributo in self._residuo_keys_mezcla:
                fila[salida] = _weighted_average(componentes_mezcla, atributo)

            registros.append(fila)

        return pd.DataFrame(registros)

    def _ajustar_modelo(self, frame: pd.DataFrame, target: str) -> AjusteLineal:
        data = frame.dropna(subset=INPUT_COLUMNS + [target])
        if data.empty:
            raise ValueError(f"No hay datos suficientes para entrenar el modelo de '{target}'.")

        X = data[INPUT_COLUMNS].astype(float).to_numpy()
        X = np.column_stack([np.ones(len(X)), X])
        y = data[target].astype(float).to_numpy()
        coeficientes, *_ = np.linalg.lstsq(X, y, rcond=None)
        return AjusteLineal(feature_names=INPUT_COLUMNS, coeficientes=coeficientes)

    def _aplicar_modelos(self, frame: pd.DataFrame, modelos: dict[str, AjusteLineal]) -> pd.DataFrame:
        resultado = frame.copy()
        for target, modelo in modelos.items():
            resultado[f"{target}_predicho"] = modelo.predecir(frame)
        return resultado

    def _to_record(self, row: pd.Series) -> dict[str, Any]:
        return {
            "id_ensayo": row["id_ensayo"],
            "id_mezcla": row["id_mezcla"],
            "residuo_base": row.get("residuo_base"),
            "temperatura": _to_float(row["Temperatura"]),
            "relacion_c_n": _to_float(row["Relacion_C_N"]),
            "larvas_observadas": {
                "humedad": _to_float(row.get("Larva_Humedad")),
                "n_organico": _to_float(row.get("Larva_N_Organico")),
                "grasa": _to_float(row.get("Larva_Extracto_Etereo")),
                "proteina": _to_float(row.get("Larva_Proteina")),
            },
            "larvas_predichas": {
                "humedad": _to_float(row.get("Larva_Humedad_predicho")),
                "n_organico": _to_float(row.get("Larva_N_Organico_predicho")),
                "grasa": _to_float(row.get("Larva_Extracto_Etereo_predicho")),
                "proteina": _to_float(row.get("Larva_Proteina_predicho")),
            },
            "frass_observado": {
                "humedad": _to_float(row.get("Frass_Humedad")),
                "ph": _to_float(row.get("Frass_pH")),
                "cenizas": _to_float(row.get("Frass_Cenizas")),
                "c_organico": _to_float(row.get("Frass_C_Organico")),
                "n_total": _to_float(row.get("Frass_N_Total")),
                "c_n": _to_float(row.get("Frass_C_N")),
                "fosforo": _to_float(row.get("Frass_Fosforo")),
                "potasio": _to_float(row.get("Frass_Potasio")),
                "densidad": _to_float(row.get("Frass_Densidad")),
            },
            "frass_predicho": {
                "humedad": _to_float(row.get("Frass_Humedad_predicho")),
                "ph": _to_float(row.get("Frass_pH_predicho")),
                "cenizas": _to_float(row.get("Frass_Cenizas_predicho")),
                "c_organico": _to_float(row.get("Frass_C_Organico_predicho")),
                "n_total": _to_float(row.get("Frass_N_Total_predicho")),
                "c_n": _to_float(row.get("Frass_C_N_predicho")),
                "fosforo": _to_float(row.get("Frass_Fosforo_predicho")),
                "potasio": _to_float(row.get("Frass_Potasio_predicho")),
                "densidad": _to_float(row.get("Frass_Densidad_predicho")),
            },
            "tasa_bioconversion": _to_float(row.get("Tasa_Bioconversion")),
        }

    def calcular_predicciones(self, db: Session) -> dict[str, Any]:
        frame = self._construir_frame(db)
        if frame.empty:
            raise ValueError("No hay ensayos disponibles para calcular predicciones.")

        modelos_larvas = {target: self._ajustar_modelo(frame, target) for target in LARVA_TARGETS}
        modelos_frass = {target: self._ajustar_modelo(frame, target) for target in FRASS_TARGETS}
        resultado = self._aplicar_modelos(frame, {**modelos_larvas, **modelos_frass})

        tasa_series = resultado["Tasa_Bioconversion"]
        if tasa_series.notna().any():
            idx = tasa_series.astype(float).idxmax()
            temperatura_optima = _to_float(resultado.loc[idx, "Temperatura"])
            tasa_maxima = _to_float(tasa_series.loc[idx])
        else:
            temperatura_optima = None
            tasa_maxima = None

        registros = [self._to_record(row) for _, row in resultado.iterrows()]
        return {
            "total_ensayos": int(len(registros)),
            "temperatura_optima": temperatura_optima,
            "tasa_bioconversion_maxima": tasa_maxima,
            "resultados": registros,
        }

    def calcular_prediccion_ensayo(self, db: Session, id_ensayo: str) -> dict[str, Any]:
        lote = self.calcular_predicciones(db)
        for registro in lote["resultados"]:
            if registro["id_ensayo"] == id_ensayo:
                return registro
        raise ValueError(f"No se encontró el ensayo '{id_ensayo}'.")
