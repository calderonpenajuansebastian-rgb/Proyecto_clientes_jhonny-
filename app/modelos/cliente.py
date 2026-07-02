# Archivo de compatibilidad para main.py
# Reexporta los modelos desde clientes.py
from .clientes import (
    ClienteBase,
    ClienteCreate,
    ClienteUpdate,
    ClienteDB,
    Cliente,
)

# Alias para compatibilidad con main.py
__all__ = ["ClienteCreate", "ClienteDB", "ClienteUpdate"]