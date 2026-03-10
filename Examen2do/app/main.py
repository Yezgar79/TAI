# 1. Importaciones
from fastapi import FastAPI, status, HTTPException, Depends
from typing import List
from pydantic import BaseModel, Field, validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from datetime import date, datetime


# Base de datos simulada

reservas = [
    {"id": 1, "nombre": "Jesús García", "fecha_entrada": "2026-06-01", "fecha_salida": "2026-06-03", "tipo_habitacion": "doble", "confirmada": False},
    {"id": 2, "nombre": "María López", "fecha_entrada": "2026-06-02", "fecha_salida": "2026-06-04", "tipo_habitacion": "suite", "confirmada": True},
    {"id": 3, "nombre": "Carlos Pérez", "fecha_entrada": "2026-06-03", "fecha_salida": "2026-06-05", "tipo_habitacion": "sencilla", "confirmada": False},
]


# Modelo Pydantic

class Reserva(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de reserva")
    nombre: str = Field(..., min_length=5, max_length=50)
    fecha_entrada: date
    fecha_salida: date
    tipo_habitacion: str = Field(..., regex="^(sencilla|doble|suite)$")

    @validator("fecha_entrada")
    def validar_fecha_entrada(cls, v):
        if v < date.today():
            raise ValueError("La fecha de entrada no puede ser menor a la fecha actual")
        return v

    @validator("fecha_salida")
    def validar_estancia(cls, v, values):
        if "fecha_entrada" in values:
            entrada = values["fecha_entrada"]

            if v <= entrada:
                raise ValueError("La fecha de salida debe ser mayor que la fecha de entrada")

            dias = (v - entrada).days
            if dias > 7:
                raise ValueError("La estancia no puede ser mayor a 7 días")

        return v



# Seguridad HTTP Basic

security = HTTPBasic()

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):

    userAuth = secrets.compare_digest(credenciales.username, "hotel")
    passAuth = secrets.compare_digest(credenciales.password, "r2026")

    if not (userAuth and passAuth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no autorizadas",
        )

    return credenciales.username



# Inicialización APP

app = FastAPI(
    title="API Hotel",
    description="Jesús González García",
    version="1.0.0"
)


# Endpoints de Inicio

@app.get("/", tags=["Inicio"])
async def holamundo():
    return {"mensaje": "Hola mundo FASTAPI"}

@app.get("/bienvenidos", tags=["Inicio"])
async def bienvenidos():
    return {"mensaje": "Bienvenidos al sistema de reservas del hotel"}



# Crear reserva (PROTEGIDO)

@app.post("/v1/reserva/", tags=["Reservas"])
async def crear_reserva(reserva: Reserva, username: str = Depends(verificar_peticion)):

    # verificar ID duplicado
    for r in reservas:
        if r["id"] == reserva.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")

    nueva_reserva = reserva.dict()
    nueva_reserva["confirmada"] = False

    reservas.append(nueva_reserva)

    return {"status": "201", "reserva": nueva_reserva}



# Listar reservas

@app.get("/v1/reserva/", tags=["Reservas"])
async def listar_reservas():
    return {"status": "200", "reservas": reservas}



# Consultar reserva por ID

@app.get("/v1/reserva/{reserva_id}", tags=["Reservas"])
async def consultar_reserva(reserva_id: int):

    for reserva in reservas:
        if reserva["id"] == reserva_id:
            return {"status": "200", "reserva": reserva}

    raise HTTPException(status_code=404, detail="Reserva no encontrada")



# Confirmar reserva

@app.put("/v1/reserva/{reserva_id}/confirmar", tags=["Reservas"])
async def confirmar_reserva(reserva_id: int):

    for reserva in reservas:
        if reserva["id"] == reserva_id:
            reserva["confirmada"] = True
            return {"status": "200", "reserva": reserva}

    raise HTTPException(status_code=404, detail="Reserva no encontrada")


# Cancelar reserva (PROTEGIDO)

@app.delete("/v1/reserva/{reserva_id}", tags=["Reservas"])
async def cancelar_reserva(reserva_id: int, username: str = Depends(verificar_peticion)):

    for reserva in reservas:
        if reserva["id"] == reserva_id:
            reservas.remove(reserva)
            return {"status": "200", "mensaje": "Reserva cancelada"}

    raise HTTPException(status_code=404, detail="Reserva no encontrada")

