from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from app.modelos.cliente import ClienteCreate, ClienteDB, ClienteUpdate
from app.modelos.factura import FacturaCreate, FacturaDB, FacturaUpdate
from app.modelos.orm_models import ClienteORM, FacturaORM, TransaccionORM
from app.modelos.transaccion import TransaccionCreate, TransaccionDB, TransaccionUpdate

# Crea las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Metadatos de las etiquetas (tags) para agrupar los endpoints en Swagger (/docs)
# Esto hace que en la documentación aparezcan secciones desplegables:
# General, Clientes, Facturas y Transacciones.
tags_metadata = [
    {
        "name": "General",
        "description": "Endpoints generales del sistema.",
    },
    {
        "name": "Clientes",
        "description": "Operaciones para crear, listar, actualizar y eliminar clientes.",
    },
    {
        "name": "Facturas",
        "description": "Operaciones para crear, listar, actualizar y eliminar facturas.",
    },
    {
        "name": "Transacciones",
        "description": "Operaciones para crear, listar, actualizar y eliminar transacciones asociadas a una factura.",
    },
]

app = FastAPI(
    title="fastAPI",
    description="API para la gestión de clientes, facturas y transacciones.",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


def obtener_cliente_orm(db: Session, cliente_id: int) -> ClienteORM:
    cliente = db.query(ClienteORM).filter(ClienteORM.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


def obtener_factura_orm(db: Session, factura_id: int) -> FacturaORM:
    factura = db.query(FacturaORM).filter(FacturaORM.id == factura_id).first()
    if factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


def obtener_transaccion_orm(db: Session, transaccion_id: int) -> TransaccionORM:
    transaccion = (
        db.query(TransaccionORM).filter(TransaccionORM.id == transaccion_id).first()
    )
    if transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    return transaccion


@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "Sistema Integral ReCal Tech - FastAPI"}


@app.get("/clientes", tags=["Clientes"])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(ClienteORM).all()
    resultado = []
    for cliente in clientes:
        cliente_dict = ClienteDB.model_validate(cliente).model_dump()
        # Obtener las facturas del cliente
        facturas = db.query(FacturaORM).filter(FacturaORM.cliente_id == cliente.id).all()
        items_comprados = []
        for factura in facturas:
            # Obtener las transacciones de cada factura
            transacciones = db.query(TransaccionORM).filter(TransaccionORM.factura_id == factura.id).all()
            for transaccion in transacciones:
                items_comprados.append({
                    "transaccion_id": transaccion.id,
                    "cantidad": transaccion.cantidad,
                    "vr_unitario": transaccion.vr_unitario,
                    "factura_id": factura.id,
                    "fecha_factura": factura.fecha
                })
        cliente_dict["items_comprados"] = items_comprados
        resultado.append(cliente_dict)
    return {"clientes": resultado}


@app.post("/clientes", tags=["Clientes"])
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    nuevo = ClienteORM(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Cliente creado satisfactoriamente", "cliente": ClienteDB.model_validate(nuevo)}


@app.put("/clientes/{id}", tags=["Clientes"])
def editar_cliente(id: int, datos: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = obtener_cliente_orm(db, id)
    for campo, valor in datos.model_dump().items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return {"mensaje": "Cliente actualizado", "cliente": ClienteDB.model_validate(cliente)}


@app.delete("/clientes/{id}", tags=["Clientes"])
def eliminar_cliente(id: int, db: Session = Depends(get_db)):
    cliente = obtener_cliente_orm(db, id)
    eliminado = ClienteDB.model_validate(cliente)
    db.delete(cliente)
    db.commit()
    return {"mensaje": "Cliente eliminado", "datos_eliminados": eliminado}


@app.get("/facturas", tags=["Facturas"])
def listar_facturas(db: Session = Depends(get_db)):
    facturas = db.query(FacturaORM).all()
    resultado = []
    for f in facturas:
        factura_dict = FacturaDB.from_orm_factura(f).model_dump()
        factura_dict["valor_total"] = FacturaDB.from_orm_factura(f).valor_total()
        # Agregar información del cliente
        cliente = db.query(ClienteORM).filter(ClienteORM.id == f.cliente_id).first()
        if cliente:
            factura_dict["cliente"] = {
                "id": cliente.id,
                "nombre": cliente.nombre,
                "email": cliente.email,
                "descripcion": cliente.descripcion
            }
        # Agregar transacciones con vr_total
        transacciones = db.query(TransaccionORM).filter(TransaccionORM.factura_id == f.id).all()
        factura_dict["transacciones"] = []
        for t in transacciones:
            transaccion_dict = TransaccionDB.model_validate(t).model_dump()
            transaccion_dict["vr_total"] = abs(t.cantidad * t.vr_unitario)
            factura_dict["transacciones"].append(transaccion_dict)
        resultado.append(factura_dict)
    return {"facturas": resultado}


@app.get("/facturas/{factura_id}", tags=["Facturas"])
def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = obtener_factura_orm(db, factura_id)
    factura_db = FacturaDB.from_orm_factura(factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()
    # Agregar información del cliente
    cliente = db.query(ClienteORM).filter(ClienteORM.id == factura.cliente_id).first()
    if cliente:
        data["cliente"] = {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "email": cliente.email,
            "descripcion": cliente.descripcion
        }
    # Agregar transacciones con vr_total
    transacciones = db.query(TransaccionORM).filter(TransaccionORM.factura_id == factura.id).all()
    data["transacciones"] = []
    for t in transacciones:
        transaccion_dict = TransaccionDB.model_validate(t).model_dump()
        transaccion_dict["vr_total"] = abs(t.cantidad * t.vr_unitario)
        data["transacciones"].append(transaccion_dict)
    return {"factura": data}


@app.post("/facturas", tags=["Facturas"])
def crear_factura(datos: FacturaCreate, db: Session = Depends(get_db)):
    cliente = obtener_cliente_orm(db, datos.cliente)

    nueva_factura = FacturaORM(cliente_id=datos.cliente, items=datos.items)
    db.add(nueva_factura)
    db.commit()
    db.refresh(nueva_factura)

    factura_db = FacturaDB.from_orm_factura(nueva_factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()
    # Agregar información del cliente
    data["cliente"] = {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "email": cliente.email,
        "descripcion": cliente.descripcion
    }
    # Agregar transacciones (vacío al crear)
    data["transacciones"] = []
    return {"mensaje": "Factura creada", "factura": data}


@app.put("/facturas/{factura_id}", tags=["Facturas"])
def editar_factura(factura_id: int, datos: FacturaUpdate, db: Session = Depends(get_db)):
    cliente = obtener_cliente_orm(db, datos.cliente)
    factura = obtener_factura_orm(db, factura_id)
    factura.cliente_id = datos.cliente
    factura.items = datos.items
    db.commit()
    db.refresh(factura)

    factura_db = FacturaDB.from_orm_factura(factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()
    # Agregar información del cliente
    data["cliente"] = {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "email": cliente.email,
        "descripcion": cliente.descripcion
    }
    # Agregar transacciones con vr_total
    transacciones = db.query(TransaccionORM).filter(TransaccionORM.factura_id == factura.id).all()
    data["transacciones"] = []
    for t in transacciones:
        transaccion_dict = TransaccionDB.model_validate(t).model_dump()
        transaccion_dict["vr_total"] = abs(t.cantidad * t.vr_unitario)
        data["transacciones"].append(transaccion_dict)
    return {"mensaje": "Factura actualizada", "factura": data}


@app.delete("/facturas/{factura_id}", tags=["Facturas"])
def eliminar_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = obtener_factura_orm(db, factura_id)
    factura_db = FacturaDB.from_orm_factura(factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()

    db.delete(factura)
    db.commit()
    return {"mensaje": "Factura eliminada", "factura": data}


@app.get("/transacciones", tags=["Transacciones"])
def listar_transacciones(db: Session = Depends(get_db)):
    transacciones = db.query(TransaccionORM).all()
    resultado = []
    for t in transacciones:
        transaccion_dict = TransaccionDB.model_validate(t).model_dump()
        transaccion_dict["vr_total"] = abs(t.cantidad * t.vr_unitario)
        resultado.append(transaccion_dict)
    return {"transacciones": resultado}


@app.get("/transacciones/{transaccion_id}", tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = obtener_transaccion_orm(db, transaccion_id)
    transaccion_dict = TransaccionDB.model_validate(transaccion).model_dump()
    transaccion_dict["vr_total"] = abs(transaccion.cantidad * transaccion.vr_unitario)
    return {"transaccion": transaccion_dict}


@app.post("/facturas/{factura_id}/transacciones", tags=["Transacciones"])
def crear_transaccion(factura_id: int, datos: TransaccionCreate, db: Session = Depends(get_db)):
    obtener_factura_orm(db, factura_id)

    nueva_transaccion = TransaccionORM(**datos.model_dump(), factura_id=factura_id)
    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)
    transaccion_dict = TransaccionDB.model_validate(nueva_transaccion).model_dump()
    transaccion_dict["vr_total"] = abs(nueva_transaccion.cantidad * nueva_transaccion.vr_unitario)
    return {"mensaje": "Transaccion creada", "transaccion": transaccion_dict}


@app.put("/transacciones/{transaccion_id}", tags=["Transacciones"])
def editar_transaccion(transaccion_id: int, datos: TransaccionUpdate, db: Session = Depends(get_db)):
    transaccion = obtener_transaccion_orm(db, transaccion_id)

    for campo, valor in datos.model_dump().items():
        setattr(transaccion, campo, valor)
    db.commit()
    db.refresh(transaccion)
    transaccion_dict = TransaccionDB.model_validate(transaccion).model_dump()
    transaccion_dict["vr_total"] = abs(transaccion.cantidad * transaccion.vr_unitario)
    return {
        "mensaje": "Transaccion actualizada",
        "transaccion": transaccion_dict,
    }


@app.delete("/transacciones/{transaccion_id}", tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = obtener_transaccion_orm(db, transaccion_id)
    eliminada = TransaccionDB.model_validate(transaccion).model_dump()
    eliminada["vr_total"] = abs(transaccion.cantidad * transaccion.vr_unitario)
    db.delete(transaccion)
    db.commit()
    return {
        "mensaje": "Transaccion eliminada",
        "transaccion": eliminada,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Entregado
