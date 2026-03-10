# 1. Importaciones
from fastapi import FastAPI, status, HTTPException,Depends
import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


# 2. Inicialización de la APP
app = FastAPI(
    title='Mi PRIMER API', 
    description="Jesús González García", 
    version='1.0.0'
)

# 3. Base de datos
usuarios = [
    {"id": 1, "nombre": "Jesús", "edad": 20},
    {"id": 2, "nombre": "María", "edad": 25},
    {"id": 3, "nombre": "Carlos", "edad": 30},
]



# 4. Modelo de Validación Pydantic 
class crear_usuario(BaseModel):
    
    id: int = Field(..., gt=0, description="Identificador de usuario")
   
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
    
    edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123")


#seguridad http basic

security = HTTPBasic()
def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    userAuth = secrets.compare_digest(credenciales.username, "jesusgonzalez")
    passAuth = secrets.compare_digest(credenciales.password, "123456")
    
    if not (userAuth and passAuth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales noa autorizadas",
        )
    return credenciales.username


# 5. Endpoints de Inicio
@app.get("/", tags=['Inicio'])
async def holamundo():
    return {"mensaje": "Hola mundo FASTAPI"}

@app.get("/bienvenidos", tags=['Inicio'])
async def bienvenidos():
    return {"mensaje": "Bienvenidos"}

# 6. Endpoints de Consultas
@app.get("/v1/usuario/", tags=['CRUD HTTP'])
async def consulta_todos_los_usuarios():
    return {
        "status": "200",
        "total": len(usuarios),
        "data": usuarios
    }

@app.get("/v1/usuario/{id}", tags=['Parametros'])
async def consulta_por_id_ruta(id: int):
    for usuario in usuarios:
        if usuario["id"] == id:
            return {"Resultado": "usuario encontrado", "Datos": usuario}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# 7. Endpoint POST con Validación Pydantic 
@app.post("/v1/usuario/", tags=['CRUD HTTP'], status_code=status.HTTP_201_CREATED)
async def crear_nuevo_usuario(usuario: crear_usuario):
    
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400, 
                detail="El id ya existe"
            )
    
   
    usuarios.append(usuario.model_dump())
    return {
        "mensaje": "Usuario Agregado correctamente",
        "Usuario": usuario
    }

# 8. Endpoint DELETE

@app.delete("/v1/usuario/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, username: str = Depends(verificar_peticion)):
    
    usuario = next((u for u in usuarios if u["id"] == id), None)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    usuarios.remove(usuario)
    return {"mensaje": f"Usuario eliminado por {username}"}


