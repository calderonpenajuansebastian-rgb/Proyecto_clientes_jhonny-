from typing import TYPE_CHECKING
from pydantic import computed_field
from sqlmodel import SQLModel, Field, Relationship
from .clientes import Cliente as ClienteModelo, ClienteDB as ClienteLeer
from datetime import datetime

if TYPE_CHECKING:
    from .transacciones import Transaccion, TransaccionLeer


class FacturaBase(SQLModel):
    fecha: datetime = Field(default_factory=datetime.now)

    @computed_field
    @property
    def vr_total(self) -> float:
        total_factura = 0.0
        transacciones_factura = getattr(self, "transacciones", None)

        if not transacciones_factura:
            return 0.0

        for transaccion in transacciones_factura:
            total_factura += transaccion.vr_unitario * transaccion.cantidad

        return total_factura


class FacturaCreate(FacturaBase):
    cliente: int
    items: str | None = None


class FacturaUpdate(SQLModel):
    cliente: int
    items: str | None = None
    fecha: datetime | None = None


class FacturaDB(FacturaBase):
    id: int
    cliente_id: int
    items: str | None = None

    @classmethod
    def from_orm_factura(cls, factura_orm):
        """Método para crear FacturaDB desde Factura ORM"""
        return cls(
            id=factura_orm.id,
            cliente_id=factura_orm.cliente_id,
            fecha=factura_orm.fecha,
            items=factura_orm.items,
        )

    def valor_total(self):
        """Calcular el valor total de la factura"""
        total = 0.0
        if hasattr(self, 'transacciones') and self.transacciones:
            for transaccion in self.transacciones:
                total += transaccion.vr_unitario * transaccion.cantidad
        return total


class FacturaLeer(FacturaBase):
    id: int
    cliente_id: int
    cliente: ClienteLeer
    transacciones: list[TransaccionLeer] = []


class Factura(FacturaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id")
    items: str | None = Field(default=None)

    transacciones: list["Transaccion"] = Relationship(
        back_populates="factura",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    cliente: ClienteModelo = Relationship()

# Entregado
