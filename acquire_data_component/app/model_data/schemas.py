# app/model_data/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# ==========================================
# 1. ESQUEMAS PARA IOT (Raspberry Pi)
# ==========================================
class RegistroSensorCrear(BaseModel):
    """
    Valida los datos en tiempo real que envía la Raspberry Pi 
    desde el componente 'Capture_data'.
    """
    id_contenedor: str = Field(..., max_length=30)
    id_sensor: str = Field(..., max_length=30)
    fecha: datetime
    valor: float

# ==========================================
# 2. ESQUEMAS PARA EL MOTOR DE PREDICCIÓN
# ==========================================
class PrediccionEntrada(BaseModel):
    """
    Valida las 26 variables fisicoquímicas necesarias para 
    el módulo 'Calculate_values'.
    """
    Temperatura: float
    Relacion_C_N: float
    Humedad: float
    pH: float
    Cenizas: float
    Carbono_organico_total_oxidable: float
    Nitrogeno_total: float
    Fosforo_total: float
    Potasio_total: float
    Calcio_total: float
    Magnesio_total: float
    Densidad_g_cm3: float
    Lignina_db: float
    
    Mezcla_Humedad: float
    Mezcla_pH: float
    Mezcla_Cenizas: float
    Mezcla_C_Org: float
    Mezcla_N_Total: float
    Mezcla_C_N: float
    Mezcla_P_Total: float
    Mezcla_K_Total: float
    Mezcla_Ca_Total: float
    Mezcla_Mg_Total: float
    Mezcla_Densidad: float
    Mezcla_Lignina: float

class PrediccionSalida(BaseModel):
    """
    Estructura la respuesta que se le devolverá al 'Visualization_component'.
    """
    larva_proteina_predicha: float
    frass_n_total_predicho: float
    estado: str