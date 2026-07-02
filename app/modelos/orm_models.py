from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class ClienteORM(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)

    facturas = relationship("FacturaORM", back_populates="cliente")


class FacturaORM(Base):
    __tablename__ = "factura"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    items = Column(String, nullable=True)

    cliente = relationship("ClienteORM", back_populates="facturas")
    transacciones = relationship("TransaccionORM", back_populates="factura", cascade="all, delete-orphan")


class TransaccionORM(Base):
    __tablename__ = "transaccion"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    vr_unitario = Column(Float, nullable=False)

    factura = relationship("FacturaORM", back_populates="transacciones")