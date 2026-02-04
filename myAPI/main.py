from fastapi import FastAPI
from typing import Optional
import asyncio

# 2. Inicialización APP
app = FastAPI(title='Mi PRIMER API', 
              description="Jesús González García ", 
              version='1.0.0')

#BD ficticia por el momento
usuarios = [
    {"id": "1", "nombre": "Jesús", "edad": "20"},
    {"id": "2", "nombre": "María", "edad": "25"},
    {"id": "3", "nombre": "Carlos", "edad": "30"},
]
# 3. Endpoints
@app.get("/", tags=['Inicio'])
async def holamundo():
    return {"mensaje": "Hola mundo FASTAPI"}

@app.get("/bienvenidos", tags=['Inicio'])
async def bienvenidos():
    return {"mensaje": "Bienvenidos"}

@app.get("/v1/promedio", tags=['Calificaciones'])
async def promedio():
    await asyncio.sleep(3)  # Peticion a otra api, consultaa otra base de datos, imula llamada externa
    return {
        "calificacion": "7.5",
        "estatus": "200"
    }

@app.get("/v1/usuario/{id}", tags=['Parametros'])
async def consultaUno(id: int):
    await asyncio.sleep(3)  # Peticion a otra api, consultaa otra base de datos, imula llamada externa
    return {"Resultado": "usuario encontrado",
            "Estatus": "200",
            }

@app.get("/v1/usuario-op/", tags=['Parametros Opcional'])
async def consultaUno(id: Optional[int] = None):
    await asyncio.sleep(2)  # Peticion a otra api, consultaa otra base de datos, imula llamada externa
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"usuario encontrado":id,"Datos": usuario}
            return{"Mensaje":"usuario no encontrado"}
        else:
            return {"Aviso":"No se proporciono id"}
    