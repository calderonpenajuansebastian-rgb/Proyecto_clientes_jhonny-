from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload
from ..modelos.transacciones import Transaccion, TransaccionCrear, TransaccionEditar, TransaccionLeer
from ..modelos.facturas import Factura
from ..conexion_bd import Sesion_dependencia

rutas_transacciones = APIRouter()


# Endpoint para obtener todas las transacciones
@rutas_transacciones.get("/transacciones", response_model=list[TransaccionLeer])
async def listar_transacciones(sesion: Sesion_dependencia):
    consulta = select(Transaccion).options(selectinload(Transaccion.factura))
    transacciones = sesion.exec(consulta).all()
    return transacciones


# Endpoint para obtener una transacción por id
@rutas_transacciones.get("/transacciones/{transaccion_id}", response_model=TransaccionLeer)
async def obtener_transaccion(transaccion_id: int, sesion: Sesion_dependencia):
    transaccion = sesion.get(Transaccion, transaccion_id)
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La transacción con id {transaccion_id} no existe."
        )
    return transaccion


# Endpoint para crear una transacción en una factura
@rutas_transacciones.post("/facturas/{factura_id}/transacciones", response_model=TransaccionLeer)
async def crear_transaccion(factura_id: int, datos_transaccion: TransaccionCrear, sesion: Sesion_dependencia):
    # Buscar la factura
    factura = sesion.get(Factura, factura_id)
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La Factura con id {factura_id}, no existe."
        )
    
    # Crear la transacción
    transaccion_dict = datos_transaccion.model_dump()
    transaccion_dict["factura_id"] = factura_id
    transaccion_val = Transaccion.model_validate(transaccion_dict)
    
    sesion.add(transaccion_val)
    sesion.commit()
    sesion.refresh(transaccion_val)
    
    # Recargar con relaciones para que la respuesta traiga la factura
    consulta = (
        select(Transaccion)
        .where(Transaccion.id == transaccion_val.id)
        .options(selectinload(Transaccion.factura))
    )
    transaccion_completa = sesion.exec(consulta).first()
    
    return transaccion_completa



@rutas_transacciones.patch("/transacciones/{transaccion_id}", response_model=TransaccionLeer)
async def editar_transaccion(
    transaccion_id: int,
    datos_transaccion: TransaccionEditar,
    sesion: Sesion_dependencia
):
    transaccion = sesion.get(Transaccion, transaccion_id)
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La transacción con id {transaccion_id} no existe."
        )
    
    datos_actualizados = datos_transaccion.model_dump(exclude_unset=True)
    transaccion.sqlmodel_update(datos_actualizados)
    
    sesion.add(transaccion)
    sesion.commit()
    sesion.refresh(transaccion)
    
    # Recargar con relaciones
    consulta = (
        select(Transaccion)
        .where(Transaccion.id == transaccion_id)
        .options(selectinload(Transaccion.factura))
    )
    transaccion_completa = sesion.exec(consulta).first()
    
    return transaccion_completa


@rutas_transacciones.delete("/transacciones/{transaccion_id}", response_model=TransaccionLeer)
async def eliminar_transaccion(transaccion_id: int, sesion: Sesion_dependencia):
    transaccion = sesion.get(Transaccion, transaccion_id)
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La transacción con id {transaccion_id} no existe."
        )
    
    sesion.delete(transaccion)
    sesion.commit()
    
    return transaccion
