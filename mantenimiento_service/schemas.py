# mantenimiento_service/schemas.py
from datetime import date
from pydantic import BaseModel
from typing import Optional

class MantenimientoBase(BaseModel):
    equipo_id: int
    tipo: str                # PREVENTIVO / CORRECTIVO
    descripcion: Optional[str] = None
    fecha_programada: date
    fecha_real: Optional[date] = None
    estado: str = "PROGRAMADO"
    costo: Optional[float] = None

class MantenimientoCreate(MantenimientoBase):
    pass

class MantenimientoUpdate(BaseModel):
    equipo_id: Optional[int] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_programada: Optional[date] = None
    fecha_real: Optional[date] = None
    estado: Optional[str] = None
    costo: Optional[float] = None

class MantenimientoRead(MantenimientoBase):
    id: int

    class Config:
        orm_mode = True
