# equipos_service/models.py
from sqlalchemy import Column, Integer, String, Date
from db import Base

class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    ubicacion = Column(String(100), nullable=True)
    fecha_compra = Column(Date, nullable=False)
    estado = Column(String(30), nullable=False, default="OPERATIVO")
    proveedor_id = Column(Integer, nullable=True)  # <--- NUEVO
