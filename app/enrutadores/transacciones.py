from fastapi import APIRouter, HTTPException, status
from ..modelos.transacciones import Transaccion, TransaccionCrear, TransaccionEditar
from ..modelos.facturas import Factura
from ..listas import lista_transacciones, lista_facturas

rutas_transacciones = APIRouter()

#lista_transacciones: list[Transaccion] = []
#lista_facturas: list[Factura] = []

#transacciones

@rutas_transacciones.get("/transacciones", response_model=list[Transaccion])
async def listar_transacciones():
    return lista_transacciones

@rutas_transacciones.get("/transacciones/{id_transaccion}", response_model=Transaccion)
async def listar_transaccion(id_transaccion: int):
    pass



@rutas_transacciones.post("/transacciones/{factura_id}", response_model=Transaccion)
async def crear_transaccion(factura_id: int, datos_transaccion: Transaccion):
    # buscar la factura
    factura_encontrada = None
    for factura in lista_facturas:
        if factura.id == factura_id:
            factura_encontrada = factura
            
    # mensaje si no existe el factura
    if not factura_encontrada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La Factura con id {factura_id}, no existe."
        )
        
    # validar datos de la transaccion
    transaccion_val = Transaccion.model_validate(datos_transaccion.model_dump())
    transaccion_val.factura_id = factura_id 
    factura_encontrada.transacciones.append(transaccion_val)
    # id de la transaccion
    transaccion_val.id = len(lista_transacciones) + 1
    lista_transacciones.append(transaccion_val)
    return transaccion_val



@rutas_transacciones.patch("/transacciones/{id_transaccion}", response_model=Transaccion)
async def editar_transaccion(
    id_transaccion: int,
    datos_transaccion: Transaccion
):

    for i, transaccion in enumerate(lista_transacciones):
        if transaccion.id == id_transaccion:
            transaccion_val = Transaccion.model_validate(
            datos_transaccion.model_dump()
            )

            transaccion_val.id = id_transaccion
            transaccion_val.factura_id = transaccion.factura_id
            lista_transacciones[i] = transaccion_val

            return transaccion_val

    raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"La transacción con id {id_transaccion} no existe."
    )


@rutas_transacciones.delete("/transacciones/{id_transaccion}", response_model=Transaccion)
async def eliminar_transaccion(id_transaccion: int):

    for i, transaccion in enumerate(lista_transacciones):
        if transaccion.id == id_transaccion:
           transaccion_eliminada = lista_transacciones.pop(i)
        return transaccion_eliminada

    raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"La transacción con id {id_transaccion} no existe."
    )