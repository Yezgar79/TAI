from fastapi import FastAPI, status, HTTPException, Depends
from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from datetime import date

# --- Base de datos simulada ---
# Nota: He convertido las fechas a objetos 'date' para que coincidan con el modelo
reservas = [
    {"id": 1, "nombre": "Jesús García", "fecha_entrada": date(2026, 6, 1), "fecha_salida": date(2026, 6, 3), "tipo_habitacion": "doble", "confirmada": False},
    {"id": 2, "nombre": "María López", "fecha_entrada": date(2026, 6, 2), "fecha_salida": date(2026, 6, 4), "tipo_habitacion": "suite", "confirmada": True},
    {"id": 3, "nombre": "Carlos Pérez", "fecha_entrada": date(2026, 6, 3), "fecha_salida": date(2026, 6, 5), "tipo_habitacion": "sencilla", "confirmada": False},
]

# --- Modelo Pydantic (V2) ---
class Reserva(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de reserva")
    nombre: str = Field(..., min_length=5, max_length=50)
    fecha_entrada: date
    fecha_salida: date
    tipo_habitacion: str = Field(..., pattern="^(sencilla|doble|suite)$")

    @field_validator("fecha_entrada")
    @classmethod
    def validar_fecha_entrada(cls, v: date):
        if v < date.today():
            raise ValueError("La fecha de entrada no puede ser menor a la fecha actual")
        return v

    @model_validator(mode='after')
    def validar_estancia(self) -> 'Reserva':
        if self.fecha_salida <= self.fecha_entrada:
            raise ValueError("La fecha de salida debe ser mayor que la fecha de entrada")
        
        dias = (self.fecha_salida - self.fecha_entrada).days
        if dias > 7:
            raise ValueError("La estancia no puede ser mayor a 7 días")
        return self

# --- Seguridad ---
security = HTTPBasic()

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    userAuth = secrets.compare_digest(credenciales.username, "hotel")
    passAuth = secrets.compare_digest(credenciales.password, "r2026")

    if not (userAuth and passAuth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no autorizadas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credenciales.username

# --- App ---
app = FastAPI(
    title="API Hotel",
    description="Jesús González García",
    version="1.0.0"
)

@app.get("/", tags=["Inicio"])
async def holamundo():
    return {"mensaje": "Hola mundo FASTAPI"}

@app.get("/v1/reserva/", tags=["Reservas"])
async def listar_reservas():
    return {"status": "200", "reservas": reservas}

@app.post("/v1/reserva/", tags=["Reservas"], status_code=201)
async def crear_reserva(reserva: Reserva, username: str = Depends(verificar_peticion)):
    if any(r["id"] == reserva.id for r in reservas):
        raise HTTPException(status_code=400, detail="El ID ya existe")

    nueva_reserva = reserva.model_dump()
    nueva_reserva["confirmada"] = False
    reservas.append(nueva_reserva)
    return {"status": "201", "reserva": nueva_reserva}

@app.get("/v1/reserva/{reserva_id}", tags=["Reservas"])
async def consultar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            return {"status": "200", "reserva": r}
    raise HTTPException(status_code=404, detail="Reserva no encontrada")

@app.put("/v1/reserva/{reserva_id}/confirmar", tags=["Reservas"])
async def confirmar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            r["confirmada"] = True
            return {"status": "200", "reserva": r}
    raise HTTPException(status_code=404, detail="Reserva no encontrada")

@app.delete("/v1/reserva/{reserva_id}", tags=["Reservas"])
async def cancelar_reserva(reserva_id: int, username: str = Depends(verificar_peticion)):
    for r in reservas:
        if r["id"] == reserva_id:
            reservas.remove(r)
            return {"status": "200", "mensaje": "Reserva cancelada"}
    raise HTTPException(status_code=404, detail="Reserva no encontrada")