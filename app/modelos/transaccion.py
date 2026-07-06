# Archivo de compatibilidad para main.py
# Reexporta los modelos desde transacciones.py
from .transacciones import (
    TransaccionBase,
    TransaccionCrear as TransaccionCreate,
    TransaccionUpdate,
    TransaccionDB,
    TransaccionLeer,
    Transaccion,
)

# Alias para compatibilidad con main.py
__all__ = ["TransaccionCreate", "TransaccionDB", "TransaccionUpdate"]

# Entregado
