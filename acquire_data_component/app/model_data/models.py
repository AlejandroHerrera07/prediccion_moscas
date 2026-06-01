from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Numeric, String

from .database import Base


class Contenedor(Base):
    __tablename__ = "Contenedor"

    id_contenedor = Column(String(30), primary_key=True, nullable=False)
    nombre = Column(String(30), nullable=False)
    descripcion = Column(String(255), nullable=False)


class Mezcla(Base):
    __tablename__ = "Mezcla"

    Id_Mezcla = Column(String(30), primary_key=True, nullable=False)
    nombre = Column(String(30), nullable=False)
    fecha_creacion = Column(Date, nullable=False)


class Residuos(Base):
    __tablename__ = "Residuos"

    id_residuo = Column(String(30), primary_key=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    humedad = Column(Numeric(5, 2), nullable=False)
    ph = Column(Numeric(5, 2), nullable=False)
    cenizas = Column(Numeric(5, 2), nullable=False)
    carbono_organico = Column(Numeric(5, 2), nullable=False)
    nitrogeno_total = Column(Numeric(5, 2), nullable=False)
    carbono_nitrogeno = Column(Numeric(5, 2), nullable=False)
    fosforo = Column(Numeric(5, 2), nullable=False)
    potasio = Column(Numeric(5, 2), nullable=False)
    calcio = Column(Numeric(5, 2), nullable=False)
    magnesio = Column(Numeric(5, 2), nullable=False)
    densidad = Column(Numeric(6, 4), nullable=False)
    lignina = Column(Numeric(5, 2), nullable=False)


class ResiduosMezcla(Base):
    __tablename__ = "Residuos_Mezcla"

    id_mezcla = Column(String(30), ForeignKey("Mezcla.Id_Mezcla"), primary_key=True, nullable=False)
    id_residuo = Column(String(30), ForeignKey("Residuos.id_residuo"), primary_key=True, nullable=False)
    porcentaje = Column(Numeric(5, 2), nullable=False)


class Ensayo(Base):
    __tablename__ = "Ensayo"

    id_Ensayo = Column(String(30), primary_key=True, nullable=False)
    id_mezcla = Column(String(30), ForeignKey("Mezcla.Id_Mezcla"), nullable=False)
    temperatura = Column(Numeric(5, 2), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)
    tasa_supervivencia = Column(Numeric(5, 2), nullable=True)
    tasa_bioconversion = Column(Numeric(5, 2), nullable=True)
    tasa_conversion_proteina = Column(Numeric(5, 2), nullable=True)
    tasa_bioconversion_grasa = Column(Numeric(5, 2), nullable=True)
    tasa_reduccion_residuos = Column(Numeric(5, 2), nullable=True)
    larva_humedad = Column(Numeric(5, 2), nullable=True)
    larva_n_organico = Column(Numeric(5, 2), nullable=True)
    larva_extracto_etereo = Column(Numeric(5, 2), nullable=True)
    larva_proteina = Column(Numeric(5, 2), nullable=True)
    frass_humedad = Column(Numeric(5, 2), nullable=True)
    frass_ph = Column(Numeric(5, 2), nullable=True)
    frass_cenizas = Column(Numeric(5, 2), nullable=True)
    frass_c_organico = Column(Numeric(5, 2), nullable=True)
    frass_n_total = Column(Numeric(5, 2), nullable=True)
    frass_c_n = Column(Numeric(5, 2), nullable=True)
    frass_fosforo = Column(Numeric(5, 2), nullable=True)
    frass_potasio = Column(Numeric(5, 2), nullable=True)
    frass_densidad = Column(Numeric(6, 4), nullable=True)


class RegistrosSensores(Base):
    __tablename__ = "Registros_sensores"

    id_contenedor = Column(String(30), ForeignKey("Contenedor.id_contenedor"), primary_key=True, nullable=False)
    id_sensor = Column(String(30), primary_key=True, nullable=False)
    fecha = Column(DateTime, primary_key=True, nullable=False)
    valor = Column(Numeric(5, 2), nullable=False)


class Sensor(Base):
    __tablename__ = "Sensor"

    id_sensor = Column(String(30), primary_key=True, nullable=False)
    id_contenedor = Column(String(30), ForeignKey("Contenedor.id_contenedor"), primary_key=True, nullable=False)
    tipo = Column(String(30), nullable=False)


Index("ix_nombre", Contenedor.nombre)
Index("IX_fecha", Ensayo.fecha_inicio)
Index("Ix_Date", Mezcla.fecha_creacion)
Index("IXFK_Registros_sensores_Sensor", RegistrosSensores.id_contenedor, RegistrosSensores.id_sensor)
Index("IX_Nombre", Residuos.nombre)
Index("IX_id_contenedor", Sensor.id_contenedor)
Index("IXFK_Sensor_Contenedor", Sensor.id_contenedor)
