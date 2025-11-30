# agent_service/main.py
from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI(title="Agent Service", version="1.0.0")

EQUIPOS_SERVICE_URL = os.getenv("EQUIPOS_SERVICE_URL", "http://equipos_service:8001")
MANTENIMIENTO_SERVICE_URL = os.getenv("MANTENIMIENTO_SERVICE_URL", "http://mantenimiento_service:8003")


@app.get("/resumen-alertas")
async def resumen_alertas(dias: int = 7, anios: int = 5):
    """
    Devuelve:
      - mantenimientos próximos en los próximos 'dias'
      - equipos obsoletos (antigüedad >= 'anios')
    """
    async with httpx.AsyncClient() as client:
        # Mantenimientos próximos
        try:
            resp_mt = await client.get(
                f"{MANTENIMIENTO_SERVICE_URL}/mantenimientos/proximos",
                params={"dias": dias},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error conectando a mantenimiento_service: {e}")

        # Equipos obsoletos
        try:
            resp_eq = await client.get(
                f"{EQUIPOS_SERVICE_URL}/equipos/obsoletos",
                params={"anios": anios},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error conectando a equipos_service: {e}")

    if resp_mt.status_code != 200:
        raise HTTPException(status_code=resp_mt.status_code, detail="Error al obtener mantenimientos próximos")

    if resp_eq.status_code != 200:
        raise HTTPException(status_code=resp_eq.status_code, detail="Error al obtener equipos obsoletos")

    proximos_mantenimientos = resp_mt.json()
    equipos_obsoletos = resp_eq.json()

    return {
        "dias": dias,
        "anios": anios,
        "proximos_mantenimientos": proximos_mantenimientos,
        "equipos_obsoletos": equipos_obsoletos,
    }
