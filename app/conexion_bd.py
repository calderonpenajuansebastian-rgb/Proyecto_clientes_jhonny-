from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated
from fastapi import Depends

nombre_bd = "bd_clientes.sqlite3"
url_bd = f"sqlite:///{nombre_bd}"

motor_bd = create_engine(url_bd)

@asynccontextmanager
async def crear_tablas(app: FastAPI):
    SQLModel.metadata.create_all(motor_bd)
    yield

def obtener_sesion():
    with Session(motor_bd) as mi_sesion:
        yield mi_sesion

Sesion_dependencia = Annotated[Session, Depends(obtener_sesion)]