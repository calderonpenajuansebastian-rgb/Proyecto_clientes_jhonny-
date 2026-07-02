from pydantic import BaseModel, computed_field

from .transacciones import Transaccion
from .clientes import Cliente
from datetime import datetime




# Crear el modelo transacciones(id, fecha, vr_total, cliente)
class FacturaBase(BaseModel):
    fecha: str = datetime.now()
    cliente: Cliente  # esta es la relacion con el cliente(objeto)
    transacciones: list[Transaccion] = []
    
    @computed_field
    @property
    def vr_total(self) -> float:
        # calcular(cantidad * vr_unitario)
        # consultar el id actual de factura
        factura_id_actual = getattr(self, "id", None)
        total_factura = 0.0
        if not factura_id_actual or not self.transacciones:
            return total_factura
        # recorrer la lista de transacciones, segun el factura_id
        for transaccion in self.transacciones:
            if transaccion.factura_id == factura_id_actual:
                total_factura += transaccion.vr_unitario * transaccion.cantidad
                
        return total_factura

class FacturaCrear(FacturaBase):
    pass

class FacturaEditar(FacturaBase):
    pass

class Factura(FacturaBase):
    id: int | None = None