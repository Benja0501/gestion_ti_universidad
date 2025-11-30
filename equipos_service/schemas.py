# equipos_service/schemas.py
from datetime import date
from pydantic import BaseModel
from typing import Optional

class EquipoBase(BaseModel):
    nombre: str
    tipo: str
    ubicacion: Optional[str] = None
    fecha_compra: date
    estado: str = "OPERATIVO"
    proveedor_id: Optional[int] = None  # <--- NUEVO

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha_compra: Optional[date] = None
    estado: Optional[str] = None
    proveedor_id: Optional[int] = None  # <--- NUEVO

class EquipoRead(EquipoBase):
    id: int

    class Config:
        orm_mode = True
