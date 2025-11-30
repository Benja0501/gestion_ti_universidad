# reportes_service/main.py
from io import BytesIO
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from fastapi import FastAPI, HTTPException
import httpx
import os
from collections import Counter

app = FastAPI(title="Reportes Service", version="1.0.0")

EQUIPOS_SERVICE_URL = os.getenv("EQUIPOS_SERVICE_URL", "http://equipos_service:8001")
MANTENIMIENTO_SERVICE_URL = os.getenv("MANTENIMIENTO_SERVICE_URL", "http://mantenimiento_service:8003")


@app.get("/equipos-resumen")
async def equipos_resumen():
    """
    Llama a /equipos de equipos_service y arma un resumen:
    - total de equipos
    - conteo por estado
    - conteo por tipo
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{EQUIPOS_SERVICE_URL}/equipos")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error conectando a Equipos: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Error en equipos_service")

    equipos = resp.json()
    total = len(equipos)
    estados = Counter([e.get("estado", "DESCONOCIDO") for e in equipos])
    tipos = Counter([e.get("tipo", "DESCONOCIDO") for e in equipos])

    return {
        "total_equipos": total,
        "por_estado": estados,
        "por_tipo": tipos,
    }


@app.get("/mantenimiento-resumen")
async def mantenimiento_resumen():
    """
    Llama a /mantenimientos de mantenimiento_service y arma un resumen:
    - total de mantenimientos
    - conteo por tipo
    - conteo por estado
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{MANTENIMIENTO_SERVICE_URL}/mantenimientos")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error conectando a Mantenimiento: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Error en mantenimiento_service")

    mant = resp.json()
    total = len(mant)
    tipos = Counter([m.get("tipo", "DESCONOCIDO") for m in mant])
    estados = Counter([m.get("estado", "DESCONOCIDO") for m in mant])

    return {
        "total_mantenimientos": total,
        "por_tipo": tipos,
        "por_estado": estados,
    }
@app.get("/reporte-pdf")
async def reporte_pdf():
    """
    Genera un PDF con el resumen de equipos y mantenimiento.
    """
    # Reutilizamos las funciones ya definidas en este servicio
    equipos = await equipos_resumen()
    mantenimiento = await mantenimiento_resumen()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Reporte de Gestión de Equipos de TI")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Universidad Pública - Sistema de Gestión de Equipos TI")
    y -= 30

    # Sección Equipos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. Resumen de equipos")
    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(60, y, f"Total de equipos: {equipos.get('total_equipos', 0)}")
    y -= 20

    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "Equipos por estado:")
    y -= 15
    c.setFont("Helvetica", 11)
    for estado, cantidad in equipos.get("por_estado", {}).items():
        c.drawString(80, y, f"- {estado}: {cantidad}")
        y -= 15

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "Equipos por tipo:")
    y -= 15
    c.setFont("Helvetica", 11)
    for tipo, cantidad in equipos.get("por_tipo", {}).items():
        c.drawString(80, y, f"- {tipo}: {cantidad}")
        y -= 15

    # Salto de página si estamos muy abajo
    if y < 120:
        c.showPage()
        y = height - 50

    # Sección Mantenimiento
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. Resumen de mantenimiento")
    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(
        60, y, f"Total de mantenimientos: {mantenimiento.get('total_mantenimientos', 0)}"
    )
    y -= 20

    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "Mantenimientos por tipo:")
    y -= 15
    c.setFont("Helvetica", 11)
    for tipo, cantidad in mantenimiento.get("por_tipo", {}).items():
        c.drawString(80, y, f"- {tipo}: {cantidad}")
        y -= 15

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "Mantenimientos por estado:")
    y -= 15
    c.setFont("Helvetica", 11)
    for estado, cantidad in mantenimiento.get("por_estado", {}).items():
        c.drawString(80, y, f"- {estado}: {cantidad}")
        y -= 15

    c.showPage()
    c.save()

    buffer.seek(0)

    headers = {
        "Content-Disposition": 'attachment; filename="reporte_ti.pdf"'
    }

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers=headers,
    )
