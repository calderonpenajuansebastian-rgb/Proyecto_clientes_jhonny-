
from pydantic import BaseModel


class Clientebase (BaseModel):
    nombre: str
    edad: int
    descripcion: str | None=None
    
    
class Clientecrear (Clientebase):
    pass

class Cliente(Clientebase):
    id: int | None = None
    


class Facturas(BaseModel):
    id: int
    fecha: str
    cliente: str
    valortotal: float


class Transaccion(BaseModel):
    id: int
    descripcion: str
    factura: int

# Entregado
