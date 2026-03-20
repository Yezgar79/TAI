from fastapi import FastAPI
from app.routers import usuarios,varios

app = FastAPI(
    title='Mi PRIMER API', 
    description="Jesús González García", 
    version='1.0.0'
)

app.include_router(usuarios.routerU)
app.include_router(varios.routerV)












