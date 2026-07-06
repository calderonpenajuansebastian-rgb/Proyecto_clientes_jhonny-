from fastapi import APIRouter, HTTPException, status
from ..modelos.clientes import Cliente, ClienteCrear, ClienteEditar
from ..conexion_bd import Sesion_dependencia
from sqlmodel import select

rutas_clientes = APIRouter()


# LISTAR TODOS
@rutas_clientes.get("/clientes", response_model=list[Cliente])
async def listar_clientes(sesion: Sesion_dependencia):
    clientes = sesion.exec(select(Cliente)).all()
    return clientes


# LISTAR UNO
@rutas_clientes.get("/clientes/{cliente_id}", response_model=Cliente)
async def obtener_cliente(cliente_id: int, sesion: Sesion_dependencia):
    cliente_bd = sesion.get(Cliente, cliente_id)

    if not cliente_bd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con id {cliente_id} no existe"
        )

    return cliente_bd


# CREAR
@rutas_clientes.post("/clientes", response_model=Cliente)
async def crear_cliente(datos_cliente: ClienteCrear, sesion: Sesion_dependencia):

    cliente_val = Cliente.model_validate(datos_cliente.model_dump())

    sesion.add(cliente_val)
    sesion.commit()
    sesion.refresh(cliente_val)

    return cliente_val


# EDITAR
@rutas_clientes.patch("/clientes/{cliente_id}", response_model=Cliente)
async def editar_cliente(cliente_id: int, datos_cliente: ClienteEditar, sesion: Sesion_dependencia):

    cliente_bd = sesion.get(Cliente, cliente_id)

    if not cliente_bd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con id {cliente_id} no existe"
        )

    cliente_dict = datos_cliente.model_dump(exclude_unset=True)
    cliente_bd.sqlmodel_update(cliente_dict)

    sesion.add(cliente_bd)
    sesion.commit()
    sesion.refresh(cliente_bd)

    return cliente_bd


# ELIMINAR
@rutas_clientes.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cliente(cliente_id: int, sesion: Sesion_dependencia):

    cliente_bd = sesion.get(Cliente, cliente_id)

    if not cliente_bd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con id {cliente_id} no existe"
        )

    sesion.delete(cliente_bd)
    sesion.commit()
# Entregado
