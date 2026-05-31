# app/model_data/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Para tu fase inicial local (ej. PostgreSQL local o SQLite)
# Cuando pases a la nube, solo cambias esta URL por la de tu proveedor
SQLALCHEMY_DATABASE_URL = "postgresql://usuario:contraseña@localhost:5432/biodegradacion_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyectar la sesión de la BD en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()