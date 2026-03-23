# 1. IMPORTACIONES

from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from pydantic import BaseModel, Field

# CAMBIO: Se elimino HTTP Basic y se agrega OAuth2 + JWT
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt


# 2. CONFIGURACIÓN JWT

# CAMBIO: Configuracin de seguridad para tokens
SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CAMBIO: Esquema OAuth2 (extrae el token automáticamente)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



# 3. INICIALIZACIÓN DE LA APP

app = FastAPI(
    title='Mi API con JWT', 
    description="Jesús González García", 
    version='2.0.0'
)
  


# 4. BASE DE DATOS

usuarios = [
    {"id": 1, "nombre": "Jesús", "edad": 20},
    {"id": 2, "nombre": "María", "edad": 25},
    {"id": 3, "nombre": "Carlos", "edad": 30},
]



# 5. MODELO DE VALIDACIÓN

class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50)
    edad: int = Field(..., ge=1, le=123)



# 6. FUNCIÓN PARA CREAR TOKEN

# CAMBIO: Genera JWT con expiración (máx 30 min)
def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# 7.LOGIN (GENERACIÓN DE TOKEN)

# CAMBIO: Endpoint obligatorio para OAuth2
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    # Usuario simulado
    if form_data.username != "jesusgonzalez" or form_data.password != "123456":
        raise HTTPException(
            status_code=400,
            detail="Credenciales incorrectas"
        )
    
    # Generación del token
    token = crear_token({"sub": form_data.username})
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }



# 8. VALIDACIN DE TOKEN

# CAMBIO: Reemplaza verificar_peticion (HTTP Basic
def validar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")



# 9. ENDPOINTS DE INICIO

@app.get("/", tags=['Inicio'])
async def holamundo():
    return {"mensaje": "Hola mundo FASTAPI"}


@app.get("/bienvenidos", tags=['Inicio'])
async def bienvenidos():
    return {"mensaje": "Bienvenidos"}


@app.get("/v1/promedio", tags=['calificaciones'])
async def promedio():
    await asyncio.sleep(2)
    return {
        "Calificación": "7.5",
        "estatus": "200"
    }


@app.get("/v1/usuario/{id}", tags=['parametros'])
async def consultaUno(id: int):
    await asyncio.sleep(2)
    return {
        "resultado": "usuario encontrado",
        "estatus": "200"
    }


@app.get("/v1/parametro0/", tags=['parametro opcional'])
async def consulta0p(id: Optional[int] = None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"usuario encontrado": id, "datos": usuario}
        return {"mensaje": "usuario no encontrado"}
    else:
        return {"aviso": "no se dio ningun id"}



# 10. CONSULTAS

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



# 11. POST

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
        "mensaje": "Usuario agregado correctamente",
        "Usuario": usuario
    }


# DELETE (PROTEGIDO)

# CAMBIO: Ahora requiere token JWT
@app.delete("/v1/usuario/{id}", tags=['CRUD HTTP'])
async def eliminar_usuario(id: int, username: str = Depends(validar_token)):

    usuario = next((u for u in usuarios if u["id"] == id), None)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuarios.remove(usuario)
    return {"mensaje": f"Usuario eliminado por {username}"}



# 13. PUT (PROTEGIDO)

# CAMBIO: Ahora requiere token JWT
@app.put("/v1/usuario/{id}", tags=['CRUD HTTP'])
async def actualiza_usuario(id: int, usuario: dict, username: str = Depends(validar_token)):

    for usr in usuarios:
        if usr["id"] == id:
            usr["nombre"] = usuario.get("nombre", usr["nombre"])
            usr["edad"] = usuario.get("edad", usr["edad"])
            return {
                "mensaje": f"Usuario actualizado por {username}",
                "status": "200",
                "usuario": usr
            }

    raise HTTPException(
        status_code=404,
        detail="El usuario no existe"
    )

