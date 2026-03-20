from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.data.database import usuarios
from app.models.usuarios import crear_usuario
from app.security.auth import verificar_peticion

routerU = APIRouter(
    prefix="/v1/usuarios",
    tags=['CRUD HTTP']
)
#get
@routerU.get("/")
async def consultaT():
    return{
        "status":"200",
        "total":len(usuarios),
        "data": usuarios
    }

#post
@routerU.post("/", status_code=status.HTTP_201_CREATED)
async def crea_usuario(usuario:crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="el usuario ya existe broo"
            )
    usuarios.append(usuario)
    return{
        "mensaje": "usuario creado exitosamente",
        "usuario": usuario
    }
            

#put
@routerU.put("/{id}", status_code=status.HTTP_200_OK)
async def actualiza_usuario(id:int, usuario:dict):
    for urs in usuarios:
        if urs["id"]==str(id):
            urs["nombre"]=usuario.get("nombre", urs["nombre"])
            urs["edad"]=usuario.get("edad", urs["edad"])
            return{
                "mensaje": "usuario actualizado exitosamente",
                "status":"200",
                "usuario": urs
            }
    raise HTTPException(
        status_code=400,
        detail="el usuario no existe broo"
    )

#delete
@routerU.delete("/{id}", status_code=status.HTTP_200_OK)
async def elimina_usuario(id:int, userAuth: str = Depends(verificar_peticion)):
    for urs in usuarios:
        if urs["id"] == str(id):
            usuarios.remove(urs)

            return{
                "mensaje": f"usuario eliminado pro {userAuth}",
            }
    raise HTTPException(
        status_code=400,
        detail="el usuario no existe broo"
    )