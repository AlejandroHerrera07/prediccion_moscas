from __future__ import annotations

from pathlib import Path
from pprint import pprint
import os

import pandas as pd
from dotenv import load_dotenv

from acquire_data_component.app.calculate_values.predictor import *
from acquire_data_component.app.model_data.database import *


OUTPUT_FILE = Path("predicciones_ensayos.xlsx")


def _flatten_registro(registro: dict) -> dict:
    return {
        "id_ensayo": registro["id_ensayo"],
        "id_mezcla": registro["id_mezcla"],
        "residuo_base": registro.get("residuo_base"),
        "temperatura": registro.get("temperatura"),
        "relacion_c_n": registro.get("relacion_c_n"),
        "larva_humedad_observada": registro["larvas_observadas"].get("humedad"),
        "larva_n_organico_observada": registro["larvas_observadas"].get("n_organico"),
        "larva_grasa_observada": registro["larvas_observadas"].get("grasa"),
        "larva_proteina_observada": registro["larvas_observadas"].get("proteina"),
        "larva_humedad_predicha": registro["larvas_predichas"].get("humedad"),
        "larva_n_organico_predicha": registro["larvas_predichas"].get("n_organico"),
        "larva_grasa_predicha": registro["larvas_predichas"].get("grasa"),
        "larva_proteina_predicha": registro["larvas_predichas"].get("proteina"),
        "frass_humedad_observada": registro["frass_observado"].get("humedad"),
        "frass_ph_observado": registro["frass_observado"].get("ph"),
        "frass_cenizas_observado": registro["frass_observado"].get("cenizas"),
        "frass_c_organico_observado": registro["frass_observado"].get("c_organico"),
        "frass_n_total_observado": registro["frass_observado"].get("n_total"),
        "frass_c_n_observado": registro["frass_observado"].get("c_n"),
        "frass_fosforo_observado": registro["frass_observado"].get("fosforo"),
        "frass_potasio_observado": registro["frass_observado"].get("potasio"),
        "frass_densidad_observada": registro["frass_observado"].get("densidad"),
        "frass_humedad_predicha": registro["frass_predicho"].get("humedad"),
        "frass_ph_predicho": registro["frass_predicho"].get("ph"),
        "frass_cenizas_predicho": registro["frass_predicho"].get("cenizas"),
        "frass_c_organico_predicho": registro["frass_predicho"].get("c_organico"),
        "frass_n_total_predicho": registro["frass_predicho"].get("n_total"),
        "frass_c_n_predicho": registro["frass_predicho"].get("c_n"),
        "frass_fosforo_predicho": registro["frass_predicho"].get("fosforo"),
        "frass_potasio_predicho": registro["frass_predicho"].get("potasio"),
        "frass_densidad_predicha": registro["frass_predicho"].get("densidad"),
        "tasa_bioconversion": registro.get("tasa_bioconversion"),
    }


def main() -> int:
    load_dotenv(Path(".env"))

    db = SessionLocal()
    try:
        resultado = MotorCalculo().calcular_predicciones(db)
    finally:
        db.close()

    filas = [_flatten_registro(registro) for registro in resultado["resultados"]]
    df = pd.DataFrame(filas)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="predicciones")
        pd.DataFrame(
            [
                {
                    "total_ensayos": resultado["total_ensayos"],
                    "temperatura_optima": resultado["temperatura_optima"],
                    "tasa_bioconversion_maxima": resultado["tasa_bioconversion_maxima"],
                }
            ]
        ).to_excel(writer, index=False, sheet_name="resumen")

    print(f"Archivo generado: {OUTPUT_FILE.resolve()}")
    print("Resumen:")
    pprint(
        {
            "total_ensayos": resultado["total_ensayos"],
            "temperatura_optima": resultado["temperatura_optima"],
            "tasa_bioconversion_maxima": resultado["tasa_bioconversion_maxima"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
