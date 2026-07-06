from fastapi import FastAPI
from pydantic import Cliente,Facturas,Transaccion,BaseModel
from datetime import datetime

app = FastAPI()

# --- BASES DE DATOS TEMPORALES Y CONTADORES ---
lista_clientes = []
lista_facturas = []
lista_transacciones = []

id_cliente_inc = 1
id_factura_inc = 1
id_transaccion_inc = 1

# --- 1. INICIO ---
@app.get("/")
def inicio():
    return {"mensaje": "Sistema Integral ReCal Tech - FastAPI"}

# --- 2. APARTADO CLIENTES (GET, POST, PUT, DELETE) ---
@app.get("/clientes")
def listar_clientes():
    return {"Clientes": lista_clientes}

@app.post("/clientes")
def crear_cliente(datos: Cliente):
    global id_cliente_inc
    nuevo = datos.model_dump()
    nuevo["id"] = id_cliente_inc
    lista_clientes.append(nuevo)
    id_cliente_inc += 1
    return {"mensaje": "Cliente creado satisfactoriamente", "cliente": nuevo}

@app.put("/clientes/{id}")
def editar_cliente(id: int, datos: Cliente):
    for i, obj in enumerate(lista_clientes):
        if obj["id"] == id:
            actualizado = datos.model_dump()
            actualizado["id"] = id
            lista_clientes[i] = actualizado
            return {"mensaje": "Cliente actualizado", "Cliente": actualizado}
    return {"error": "No encontrado"}

@app.delete("/clientes/{id}")
def eliminar_cliente(id: int):
    for i, obj in enumerate(lista_clientes):
        if obj["id"] == id:
            eliminado = lista_clientes.pop(i)
            return {"mensaje": "Cliente eliminado", "datos_eliminados": eliminado}
    return {"error": "No encontrado"}

# --- 3. APARTADO FACTURAS (POST y GET) ---
@app.get("/facturas")
def listar_facturas():
    return {"Facturas": lista_facturas}

@app.post("/facturas")
def crear_factura(datos: Facturas):
    global id_factura_inc
    # Validación: ¿Existe el cliente?
    if not any(c["id"] == datos.cliente_id for c in lista_clientes):
        return {"error": "El cliente no existe"}

    nueva_f = datos.model_dump()
    nueva_f["id"] = id_factura_inc
    nueva_f["fecha"] = datetime.now().strftime("")
    lista_facturas.append(nueva_f)
    id_factura_inc += 1
    return {"mensaje": "Factura generada", "factura": nueva_f}

# --- 4. APARTADO TRANSACCIONES (POST y GET) ---
@app.get("/transacciones")
def listar_transacciones():
    return {"Transacciones": lista_transacciones}

@app.post("/transacciones")
def crear_transaccion(datos: Transaccion):
    global id_transaccion_inc
    # Validación: ¿Existe la factura?
    if not any(f["id"] == datos.factura_id for f in lista_facturas):
        return {"error": "La factura no existe"}

    nueva_t = datos.model_dump()
    nueva_t["id"] = id_transaccion_inc
    nueva_t["fecha_pago"] = datetime.now().strftime("")
    lista_transacciones.append(nueva_t)
    id_transaccion_inc += 1
    return {"mensaje": "Transacción registrada", "detalle": nueva_t
} 
    
# --- ELIMINAR FACTURA ---
@app.delete("/facturas/{factura_id}", )
def eliminar_factura(factura_id: int):
    global db_facturas
    
    # Buscamos si la factura existe
    factura_existente = next((f for f in db_facturas if f.id == factura_id), None)
    
    if not factura_existente:
        raise Transaccion(status_code=404, detail="La factura no existe")
    
    # Eliminamos la factura de la lista
    db_facturas = [f for f in db_facturas if f.id != factura_id]
    
    return {"message": f"Factura {factura_id} eliminada correctamente"}

# --- ELIMINAR TRANSACCIÓN ---
@app.delete("/transacciones/{transaccion_id}")
def eliminar_transaccion(transaccion_id: int):
    global db_transacciones
    
    # Buscamos si la transacción existe
    transaccion_existente = next((t for t in db_transacciones if t.id == transaccion_id), None)
    
    if not transaccion_existente:
        raise Transaccion(status_code=404, detail="La transacción no existe")
    
    # Eliminamos la transacción
    db_transacciones = [t for t in db_transacciones if t.id != transaccion_id]
    
    return {"message": f"Transacción {transaccion_id} eliminada con éxito"}
    