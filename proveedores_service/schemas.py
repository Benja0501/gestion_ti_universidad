# proveedores_service/schemas.py
from pydantic import BaseModel
from typing import Optional

class ProveedorBase(BaseModel):
    nombre: str
    ruc: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None   # <--- str en vez de EmailStr
    estado: str = "ACTIVO"

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    ruc: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None   # <--- también str
    estado: Optional[str] = None

class ProveedorRead(ProveedorBase):
    id: int

    class Config:
        orm_mode = True
