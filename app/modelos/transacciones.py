from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .clientes import ClienteDB as ClienteLeer

if TYPE_CHECKING:
    from .facturas import FacturaLeer


class TransaccionBase(SQLModel):
    cantidad: int
    vr_unitario: float


class TransaccionCrear(TransaccionBase):
    pass


class TransaccionUpdate(TransaccionBase):
    pass


class TransaccionDB(TransaccionBase):
    id: int
    factura_id: int


class TransaccionLeer(TransaccionBase):
    id: int
    factura_id: int
    factura: FacturaLeer | None = None


class Transaccion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    factura_id: int = Field(foreign_key="factura.id")
    cantidad: int
    vr_unitario: float

    factura: FacturaLeer = Relationship(back_populates="transacciones")
