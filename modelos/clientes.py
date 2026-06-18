from pydantic import BaseModel
#Crear el modelo clientes (id, nombre, email, descripcion)
class ClienteBase(BaseModel):
    nombre: str
    email: str
    descripcion: str

class ClienteCrear(ClienteBase):
     pass


class  Cliente(ClienteBase):
      id: int | None = None