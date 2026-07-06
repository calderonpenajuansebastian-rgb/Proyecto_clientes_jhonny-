from typing import TYPE_CHECKING
from pydantic import computed_field
from sqlmodel import SQLModel, Field, Relationship
from .clientes import ClienteDB as ClienteLeer

if TYPE_CHECKING:
    from .facturas import FacturaLeer


class TransaccionBase(SQLModel):
    cantidad: int
    vr_unitario: float
    metodo_pago: str | None = None


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

    @computed_field
    @property
    def vr_total(self) -> float:
        return abs(self.cantidad * self.vr_unitario)


class Transaccion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    factura_id: int = Field(foreign_key="factura.id")
    cantidad: int
    vr_unitario: float
    metodo_pago: str | None = Field(default=None)

    factura: FacturaLeer = Relationship(back_populates="transacciones")
