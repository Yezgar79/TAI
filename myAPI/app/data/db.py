from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
 # definimos   la url de la conexion con el contenedor 

DATABASE_URL = os.getenv(
  "DATABASE_URL", 
  "postgresql://admin:123456@postgres:5432/DB_miapi"

)
#2 creamos el motor de la CONEXION DE LA base de datos
engine = create_engine(DATABASE_URL)

#CREAMOs  el manejador de seciones 
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# instanciamos la base declarativa del modelo
Base = declarative_base()

#5 Funcion para manejo de seciones por peticiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


