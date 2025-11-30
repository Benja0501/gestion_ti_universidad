# mantenimiento_service/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from db import Base, engine, get_db
from models import Mantenimiento
from schemas import MantenimientoCreate, MantenimientoUpdate, MantenimientoRead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mantenimiento Service", version="1.0.0")


@app.get("/mantenimientos", response_model=list[MantenimientoRead])
def listar_mantenimientos(db: Session = Depends(get_db)):
    return db.query(Mantenimiento).order_by(Mantenimiento.fecha_programada).all()


@app.get("/mantenimientos/proximos", response_model=list[MantenimientoRead])
def mantenimientos_proximos(dias: int = 7, db: Session = Depends(get_db)):
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    return (
        db.query(Mantenimiento)
        .filter(Mantenimiento.fecha_programada >= hoy)
        .filter(Mantenimiento.fecha_programada <= limite)
        .order_by(Mantenimiento.fecha_programada)
        .all()
    )


@app.get("/mantenimientos/{mant_id}", response_model=MantenimientoRead)
def obtener_mantenimiento(mant_id: int, db: Session = Depends(get_db)):
    mant = db.query(Mantenimiento).filter(Mantenimiento.id == mant_id).first()
    if not mant:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    return mant


@app.post("/mantenimientos", response_model=MantenimientoRead, status_code=201)
def crear_mantenimiento(data: MantenimientoCreate, db: Session = Depends(get_db)):
    mant = Mantenimiento(**data.dict())
    db.add(mant)
    db.commit()
    db.refresh(mant)
    return mant


@app.put("/mantenimientos/{mant_id}", response_model=MantenimientoRead)
def actualizar_mantenimiento(
    mant_id: int, data: MantenimientoUpdate, db: Session = Depends(get_db)
):
    mant = db.query(Mantenimiento).filter(Mantenimiento.id == mant_id).first()
    if not mant:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(mant, k, v)

    db.commit()
    db.refresh(mant)
    return mant


@app.delete("/mantenimientos/{mant_id}", response_model=MantenimientoRead)
def eliminar_mantenimiento(mant_id: int, db: Session = Depends(get_db)):
    mant = db.query(Mantenimiento).filter(Mantenimiento.id == mant_id).first()
    if not mant:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    db.delete(mant)
    db.commit()
    return mant
