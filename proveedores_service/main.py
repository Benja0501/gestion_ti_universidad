# proveedores_service/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models import Proveedor
from schemas import ProveedorCreate, ProveedorUpdate, ProveedorRead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Proveedores Service", version="1.0.0")


@app.get("/proveedores", response_model=list[ProveedorRead])
def listar_proveedores(db: Session = Depends(get_db)):
    return db.query(Proveedor).order_by(Proveedor.id).all()


@app.get("/proveedores/{proveedor_id}", response_model=ProveedorRead)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return prov


@app.post("/proveedores", response_model=ProveedorRead, status_code=201)
def crear_proveedor(data: ProveedorCreate, db: Session = Depends(get_db)):
    prov = Proveedor(**data.dict())
    db.add(prov)
    db.commit()
    db.refresh(prov)
    return prov


@app.put("/proveedores/{proveedor_id}", response_model=ProveedorRead)
def actualizar_proveedor(
    proveedor_id: int, data: ProveedorUpdate, db: Session = Depends(get_db)
):
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(prov, k, v)

    db.commit()
    db.refresh(prov)
    return prov


@app.delete("/proveedores/{proveedor_id}", response_model=ProveedorRead)
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    db.delete(prov)
    db.commit()
    return prov
