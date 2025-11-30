# proveedores_service/models.py
from sqlalchemy import Column, Integer, String
from db import Base

class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ruc = Column(String(20), nullable=True, unique=True)
    contacto = Column(String(100), nullable=True)
    telefono = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    estado = Column(String(20), nullable=False, default="ACTIVO")
