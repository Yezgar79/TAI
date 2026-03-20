from app.data.database import usuarios
from app.models.usuarios import crear_usuario
from app.security.auth import verificar_peticion


from typing import Optional
import asyncio 
from app.data.database import usuarios
from fastapi import APIRouter

routerV = APIRouter(
    tags=['Inicio']
)
#3. endpoints V
@routerV.get("/")
async def holaMundo():
    return {"message": "Hola Mundo FASTAPI"}



@routerV.get("/v1/promedio", tags=['calificaciones'])
async def promedio():
    await asyncio.sleep(5)#para que el codigo continue mientras espera lo demás
    return {
        "Calificación": "7.5",
        "estatus": "200"
        }



@routerV.get("/v1/usuario/{id}", tags=['parametros'])
async def consultaUno(id:int):
    await asyncio.sleep(3)
    return {
        "resultado": "usuario encontrado",
        "estatus": "200"
        }


@routerV.get("/v1/parametro0/", tags=['parameto opcional'])
async def consulta0p(id:Optional[int]=None):
    await asyncio.sleep(2)
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == str(id):
                return {"usuario encontrado":id, "datos": usuario}
        return{"mensaje": "usuario no encontrado"}
    else:
        return{"aviso": "no se dio ningun id"}