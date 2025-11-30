# equipos_service/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from db import Base, engine, get_db
from models import Equipo
from schemas import EquipoCreate, EquipoUpdate, EquipoRead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Equipos Service", version="1.0.0")


@app.get("/equipos", response_model=list[EquipoRead])
def listar_equipos(db: Session = Depends(get_db)):
    return db.query(Equipo).order_by(Equipo.id).all()


# ⚠️ Primero declaramos obsoletos
@app.get("/equipos/obsoletos", response_model=list[EquipoRead])
def equipos_obsoletos(anios: int = 5, db: Session = Depends(get_db)):
    hoy = date.today()
    limite = hoy.replace(year=hoy.year - anios)
    equipos = (
        db.query(Equipo)
        .filter(Equipo.fecha_compra <= limite)
        .filter(Equipo.estado != "BAJA")
        .all()
    )
    return equipos


# Luego la ruta dinámica
@app.get("/equipos/{equipo_id}", response_model=EquipoRead)
def obtener_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipo


@app.post("/equipos", response_model=EquipoRead, status_code=201)
def crear_equipo(data: EquipoCreate, db: Session = Depends(get_db)):
    equipo = Equipo(**data.dict())
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


@app.put("/equipos/{equipo_id}", response_model=EquipoRead)
def actualizar_equipo(equipo_id: int, data: EquipoUpdate, db: Session = Depends(get_db)):
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(equipo, k, v)
    db.commit()
    db.refresh(equipo)
    return equipo


@app.delete("/equipos/{equipo_id}", response_model=EquipoRead)
def eliminar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    db.delete(equipo)
    db.commit()
    return equipo
