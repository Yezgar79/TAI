#1. importaciones
from fastapi import FastAPI

#2. inicializacion APP
app = FastAPI()

#3. Endpoints
@app.get("/")
async def holamundo():
    return {"mensaje":"hola mundo FASTAPI"}

@app.get("/bienvenidos")
async def bienvenidos():
    return {"mensaje":"Bienvenidos"}