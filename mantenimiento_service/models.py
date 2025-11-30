# mantenimiento_service/models.py
from sqlalchemy import Column, Integer, String, Date, Numeric
from db import Base

class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, nullable=False)            # FK lógica a equipos.id
    tipo = Column(String(30), nullable=False)              # PREVENTIVO / CORRECTIVO
    descripcion = Column(String(255), nullable=True)
    fecha_programada = Column(Date, nullable=False)
    fecha_real = Column(Date, nullable=True)
    estado = Column(String(30), nullable=False, default="PROGRAMADO")
    costo = Column(Numeric(12, 2), nullable=True)
