# Archivo de compatibilidad para main.py
# Reexporta los modelos desde facturas.py
from .facturas import (
    FacturaBase,
    FacturaCreate,
    FacturaUpdate,
    FacturaDB,
    FacturaLeer,
    Factura,
)

# Alias para compatibilidad con main.py
__all__ = ["FacturaCreate", "FacturaDB", "FacturaUpdate"]
# Entregado
