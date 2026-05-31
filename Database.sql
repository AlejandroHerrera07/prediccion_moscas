DROP TABLE IF EXISTS "Contenedor" CASCADE
;

DROP TABLE IF EXISTS "Ensayo" CASCADE
;

DROP TABLE IF EXISTS "Mezcla" CASCADE
;

DROP TABLE IF EXISTS "Registros_sensores" CASCADE
;

DROP TABLE IF EXISTS "Residuos" CASCADE
;

DROP TABLE IF EXISTS "Residuos_Mezcla" CASCADE
;

DROP TABLE IF EXISTS "Sensor" CASCADE
;

CREATE TABLE "Contenedor"
(
    id_contenedor varchar(30) NOT NULL,
    nombre varchar(30) NOT NULL,
    descripcion varchar(255) NOT NULL -- AJUSTE: Ampliado de 30 a 255 caracteres
)
;

CREATE TABLE "Ensayo"
(
    "id_Ensayo" varchar(30) NOT NULL,
    id_mezcla varchar(30) NOT NULL,
    temperatura numeric(5,2) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NULL,
    tasa_supervivencia numeric(5,2) NULL,
    tasa_bioconversion numeric(5,2) NULL, 
    tasa_conversion_proteina numeric(5,2) NULL,
    tasa_bioconversion_grasa numeric(5,2) NULL,
    tasa_reduccion_residuos numeric(5,2) NULL,
    larva_humedad numeric(5,2) NULL,
    larva_n_organico numeric(5,2) NULL,
    larva_extracto_etereo numeric(5,2) NULL,
    larva_proteina numeric(5,2) NULL,
    frass_humedad numeric(5,2) NULL,
    frass_ph numeric(5,2) NULL,
    frass_cenizas numeric(5,2) NULL,
    frass_c_organico numeric(5,2) NULL,
    frass_n_total numeric(5,2) NULL,
    frass_c_n numeric(5,2) NULL,
    frass_fosforo numeric(5,2) NULL,
    frass_potasio numeric(5,2) NULL,
    frass_densidad numeric(6,4) NULL
)
;

CREATE TABLE "Mezcla"
(
    "Id_Mezcla" varchar(30) NOT NULL,
    nombre varchar(30) NOT NULL,
    fecha_creacion date NOT NULL
)
;

CREATE TABLE "Registros_sensores"
(
    id_contenedor varchar(30) NOT NULL,
    id_sensor varchar(30) NOT NULL,
    fecha timestamp without time zone NOT NULL,
    valor numeric(5,2) NOT NULL
)
;

CREATE TABLE "Residuos"
(
    id_residuo varchar(30) NOT NULL,
    nombre varchar(100) NOT NULL,
    humedad numeric(5,2) NOT NULL,
    ph numeric(5,2) NOT NULL,
    cenizas numeric(5,2) NOT NULL,
    carbono_organico numeric(5,2) NOT NULL,
    nitrogeno_total numeric(5,2) NOT NULL,
    carbono_nitrogeno numeric(5,2) NOT NULL,
    fosforo numeric(5,2) NOT NULL,
    potasio numeric(5,2) NOT NULL,
    calcio numeric(5,2) NOT NULL,
    magnesio numeric(5,2) NOT NULL,
    densidad numeric(6,4) NOT NULL,
    lignina numeric(5,2) NOT NULL
)
;

CREATE TABLE "Residuos_Mezcla"
(
    id_mezcla varchar(30) NOT NULL,
    id_residuo varchar(30) NOT NULL,
    porcentaje numeric(5,2) NOT NULL
)
;

CREATE TABLE "Sensor"
(
    id_sensor varchar(30) NOT NULL,
    id_contenedor varchar(30) NOT NULL,
    tipo varchar(30) NOT NULL
)
;


ALTER TABLE "Contenedor" ADD CONSTRAINT "PK_contenedor"
    PRIMARY KEY (id_contenedor)
;

ALTER TABLE "Ensayo" ADD CONSTRAINT "PK_Ensayo"
    PRIMARY KEY ("id_Ensayo")
;

ALTER TABLE "Mezcla" ADD CONSTRAINT "PK_Mezcla"
    PRIMARY KEY ("Id_Mezcla")
;

ALTER TABLE "Registros_sensores" ADD CONSTRAINT "PK_Registros_sensores"
    PRIMARY KEY (id_contenedor,id_sensor,fecha)
;

ALTER TABLE "Residuos" ADD CONSTRAINT "PK_Residuos"
    PRIMARY KEY (id_residuo)
;

ALTER TABLE "Residuos_Mezcla" ADD CONSTRAINT "PK_mezcla_residuo"
    PRIMARY KEY (id_mezcla,id_residuo)
;

ALTER TABLE "Sensor" ADD CONSTRAINT "PK_Sensor"
    PRIMARY KEY (id_contenedor,id_sensor)
;

CREATE INDEX ix_nombre ON "Contenedor" (nombre ASC)
;

CREATE INDEX "IX_fecha" ON "Ensayo" (fecha_inicio ASC)
;

CREATE INDEX "Ix_Date" ON "Mezcla" (fecha_creacion ASC)
;

CREATE INDEX "IXFK_Registros_sensores_Sensor" ON "Registros_sensores" (id_contenedor ASC,id_sensor ASC)
;

CREATE INDEX "IX_Nombre" ON "Residuos" (nombre ASC)
;

CREATE INDEX "IX_id_contenedor" ON "Sensor" (id_contenedor ASC)
;

CREATE INDEX "IXFK_Sensor_Contenedor" ON "Sensor" (id_contenedor ASC)
;

ALTER TABLE "Ensayo" ADD CONSTRAINT "FK_Ensayo_Mezcla"
    FOREIGN KEY (id_mezcla) REFERENCES "Mezcla" ("Id_Mezcla") ON DELETE No Action ON UPDATE No Action
;

ALTER TABLE "Registros_sensores" ADD CONSTRAINT "FK_Registros_sensores_Sensor"
    FOREIGN KEY (id_contenedor,id_sensor) REFERENCES "Sensor" (id_contenedor,id_sensor) ON DELETE No Action ON UPDATE No Action
;

ALTER TABLE "Residuos_Mezcla" ADD CONSTRAINT "FK_Residuos_Mezcla_Mezcla"
    FOREIGN KEY (id_mezcla) REFERENCES "Mezcla" ("Id_Mezcla") ON DELETE No Action ON UPDATE No Action
;

ALTER TABLE "Residuos_Mezcla" ADD CONSTRAINT "FK_Residuos_Mezcla_Residuos"
    FOREIGN KEY (id_residuo) REFERENCES "Residuos" (id_residuo) ON DELETE No Action ON UPDATE No Action
;

ALTER TABLE "Sensor" ADD CONSTRAINT "FK_Sensor_Contenedor"
    FOREIGN KEY (id_contenedor) REFERENCES "Contenedor" (id_contenedor) ON DELETE No Action ON UPDATE No Action
;

