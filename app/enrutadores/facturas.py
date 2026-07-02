from fastapi import APIRouter, HTTPException, status
from ..modelos.facturas import Factura, FacturaCrear, FacturaEditar
from ..modelos.clientes import Cliente
from ..listas import lista_clientes, lista_facturas

rutas_facturas = APIRouter()

#lista_facturas: list[Factura] = []
#lista_clientes: list[Cliente] = []

#factura

@rutas_facturas.get("/facturas", response_model=list[Factura])
async def listar_facturas():
    return lista_facturas

@rutas_facturas.get("/facturas/{factura_id}", response_model=Factura)
async def listar_factura(factura_id: int):
    # recorrer la lista facturas
    for i, obj_factura in enumerate(lista_facturas):
        if obj_factura.id == factura_id:
            return obj_factura
            
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail=f"La factura con id {factura_id}, no existe."
    )

@rutas_facturas.post("/facturas/{cliente_id}", response_model=Factura)
async def crear_factura(cliente_id: int, datos_factura: FacturaCrear):
    # buscar el cliente
    cliente_encontrado = None
    for cliente in lista_clientes:
        if cliente.id == cliente_id:
            cliente_encontrado = cliente
            
    # mensaje si no existe el cliente
    if not cliente_encontrado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El cliente con id {cliente_id}, no existe.",
        )
        
    # validar datos de la factura
    factura_val = Factura.model_validate(datos_factura.model_dump())
    factura_val.cliente = cliente_encontrado
    # id de la factura
    factura_val.id = len(lista_facturas) + 1
    lista_facturas.append(factura_val)
    return factura_val


@rutas_facturas.patch("/facturas/{id_factura}", response_model=Factura)
async def editar_factura(id_factura: int, datos_factura: Factura):
    pass


@rutas_facturas.delete("/facturas/{id_factura}", response_model=Factura)
async def eliminar_factura(id_factura):
    pass
