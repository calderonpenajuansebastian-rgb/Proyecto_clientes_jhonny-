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
    title="Sistema Integral ReCal Tech",
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
    return {"clientes": [ClienteDB.model_validate(c) for c in clientes]}


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
    return {
        "facturas": [
            {**FacturaDB.from_orm_factura(f).model_dump(), "valor_total": FacturaDB.from_orm_factura(f).valor_total()}
            for f in facturas
        ]
    }


@app.get("/facturas/{factura_id}", tags=["Facturas"])
def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = obtener_factura_orm(db, factura_id)
    factura_db = FacturaDB.from_orm_factura(factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()
    return {"factura": data}


@app.post("/facturas", tags=["Facturas"])
def crear_factura(datos: FacturaCreate, db: Session = Depends(get_db)):
    obtener_cliente_orm(db, datos.cliente)

    nueva_factura = FacturaORM(cliente_id=datos.cliente)
    db.add(nueva_factura)
    db.commit()
    db.refresh(nueva_factura)

    factura_db = FacturaDB.from_orm_factura(nueva_factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()
    return {"mensaje": "Factura creada", "factura": data}


@app.put("/facturas/{factura_id}", tags=["Facturas"])
def editar_factura(factura_id: int, datos: FacturaUpdate, db: Session = Depends(get_db)):
    obtener_cliente_orm(db, datos.cliente)
    factura = obtener_factura_orm(db, factura_id)
    factura.cliente_id = datos.cliente
    db.commit()
    db.refresh(factura)

    factura_db = FacturaDB.from_orm_factura(factura)
    data = factura_db.model_dump()
    data["valor_total"] = factura_db.valor_total()
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
    return {"transacciones": [TransaccionDB.model_validate(t) for t in transacciones]}


@app.get("/transacciones/{transaccion_id}", tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = obtener_transaccion_orm(db, transaccion_id)
    return {"transaccion": TransaccionDB.model_validate(transaccion)}


@app.post("/facturas/{factura_id}/transacciones", tags=["Transacciones"])
def crear_transaccion(factura_id: int, datos: TransaccionCreate, db: Session = Depends(get_db)):
    obtener_factura_orm(db, factura_id)

    nueva_transaccion = TransaccionORM(**datos.model_dump(), factura_id=factura_id)
    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)
    return {"mensaje": "Transaccion creada", "transaccion": TransaccionDB.model_validate(nueva_transaccion)}


@app.put("/facturas/{factura_id}/transacciones/{transaccion_id}", tags=["Transacciones"])
def editar_transaccion(factura_id: int, transaccion_id: int, datos: TransaccionUpdate, db: Session = Depends(get_db)):
    obtener_factura_orm(db, factura_id)
    transaccion = obtener_transaccion_orm(db, transaccion_id)

    for campo, valor in datos.model_dump().items():
        setattr(transaccion, campo, valor)
    transaccion.factura_id = factura_id
    db.commit()
    db.refresh(transaccion)
    return {
        "mensaje": "Transaccion actualizada",
        "transaccion": TransaccionDB.model_validate(transaccion),
    }


@app.delete("/transacciones/{transaccion_id}", tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = obtener_transaccion_orm(db, transaccion_id)
    eliminada = TransaccionDB.model_validate(transaccion)
    db.delete(transaccion)
    db.commit()
    return {
        "mensaje": "Transaccion eliminada",
        "transaccion": eliminada,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
