from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from ..model_data.database import get_supabase_client


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


def _row_value(row: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    return default


def _weighted_average(componentes: list[tuple[dict[str, Any], float]], field_name: str) -> float | None:
    if not componentes:
        return None

    total = 0.0
    total_peso = 0.0
    for residuo, porcentaje in componentes:
        valor = _row_value(residuo, field_name)
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
        self, client: Any
    ) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[tuple[dict[str, Any], float]]]]:
        ensayos = client.table("Ensayo").select("*").execute().data or []
        mezclas_raw = client.table("Mezcla").select("*").execute().data or []
        residuos_raw = client.table("Residuos").select("*").execute().data or []
        residuos_mezcla_raw = client.table("Residuos_Mezcla").select("*").execute().data or []

        mezclas = {str(_row_value(mezcla, "Id_Mezcla", "id_mezcla")): mezcla for mezcla in mezclas_raw}
        residuos = {str(_row_value(residuo, "id_residuo")): residuo for residuo in residuos_raw}

        componentes: dict[str, list[tuple[dict[str, Any], float]]] = {}
        for fila in residuos_mezcla_raw:
            id_mezcla = str(_row_value(fila, "id_mezcla"))
            id_residuo = str(_row_value(fila, "id_residuo"))
            residuo = residuos.get(id_residuo)
            if residuo is None:
                continue
            componentes.setdefault(id_mezcla, []).append((residuo, float(_row_value(fila, "porcentaje", default=0.0))))

        for item in componentes.values():
            item.sort(key=lambda par: (-par[1], str(_row_value(par[0], "id_residuo"))))

        return ensayos, mezclas, residuos, componentes

    def _inferir_residuo_base(self, ensayos: list[dict[str, Any]], residuos: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any] | None]:
        """
        La base de datos no expone un FK directo entre ensayo y residuo base.
        Mientras el esquema no lo tenga, se reproduce el orden de carga del dataset.
        """

        residuos_ordenados = sorted(residuos.values(), key=lambda r: _natural_key(str(_row_value(r, "id_residuo"))))
        ensayos_ordenados = sorted(ensayos, key=lambda e: _natural_key(str(_row_value(e, "id_Ensayo", "id_ensayo"))))
        mapa: dict[str, dict[str, Any] | None] = {}
        for indice, ensayo in enumerate(ensayos_ordenados):
            ensayo_id = str(_row_value(ensayo, "id_Ensayo", "id_ensayo"))
            mapa[ensayo_id] = residuos_ordenados[indice] if indice < len(residuos_ordenados) else None
        return mapa

    def _construir_frame(self, client: Any) -> pd.DataFrame:
        ensayos, mezclas, residuos, componentes = self._cargar_tablas(client)
        base_por_ensayo = self._inferir_residuo_base(ensayos, residuos)

        registros: list[dict[str, Any]] = []
        for ensayo in sorted(ensayos, key=lambda e: _natural_key(str(_row_value(e, "id_Ensayo", "id_ensayo")))):
            ensayo_id = str(_row_value(ensayo, "id_Ensayo", "id_ensayo"))
            id_mezcla = str(_row_value(ensayo, "id_mezcla"))
            mezcla = mezclas.get(id_mezcla)
            if mezcla is None:
                raise ValueError(f"No existe la mezcla '{id_mezcla}' para el ensayo '{ensayo_id}'.")

            mezcla_id = str(_row_value(mezcla, "Id_Mezcla", "id_mezcla"))
            componentes_mezcla = componentes.get(mezcla_id, [])
            residuo_base = base_por_ensayo.get(ensayo_id)

            fila: dict[str, Any] = {
                "id_ensayo": ensayo_id,
                "id_mezcla": id_mezcla,
                "residuo_base": _row_value(residuo_base, "nombre") if residuo_base is not None else None,
                "Temperatura": _to_float(_row_value(ensayo, "temperatura")),
                "Relacion_C_N": _parse_relacion_cn(str(_row_value(mezcla, "nombre", default=""))),
                "Larva_Humedad": _to_float(_row_value(ensayo, "larva_humedad")),
                "Larva_N_Organico": _to_float(_row_value(ensayo, "larva_n_organico")),
                "Larva_Extracto_Etereo": _to_float(_row_value(ensayo, "larva_extracto_etereo")),
                "Larva_Proteina": _to_float(_row_value(ensayo, "larva_proteina")),
                "Frass_Humedad": _to_float(_row_value(ensayo, "frass_humedad")),
                "Frass_pH": _to_float(_row_value(ensayo, "frass_ph")),
                "Frass_Cenizas": _to_float(_row_value(ensayo, "frass_cenizas")),
                "Frass_C_Organico": _to_float(_row_value(ensayo, "frass_c_organico")),
                "Frass_N_Total": _to_float(_row_value(ensayo, "frass_n_total")),
                "Frass_C_N": _to_float(_row_value(ensayo, "frass_c_n")),
                "Frass_Fosforo": _to_float(_row_value(ensayo, "frass_fosforo")),
                "Frass_Potasio": _to_float(_row_value(ensayo, "frass_potasio")),
                "Frass_Densidad": _to_float(_row_value(ensayo, "frass_densidad")),
                "Tasa_Bioconversion": _to_float(_row_value(ensayo, "tasa_bioconversion")),
            }

            if residuo_base is not None:
                for salida, atributo in self._residuo_keys_base:
                    fila[salida] = _to_float(_row_value(residuo_base, atributo))
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

    def calcular_predicciones(self, client: Any | None = None) -> dict[str, Any]:
        if client is None:
            client = get_supabase_client()

        frame = self._construir_frame(client)
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

    def calcular_prediccion_ensayo(self, client: Any | None = None, id_ensayo: str = "") -> dict[str, Any]:
        lote = self.calcular_predicciones(client)
        for registro in lote["resultados"]:
            if registro["id_ensayo"] == id_ensayo:
                return registro
        raise ValueError(f"No se encontró el ensayo '{id_ensayo}'.")
