# api_gateway/main.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import os

app = FastAPI(title="API Gateway TI", version="1.0.0")

EQUIPOS_SERVICE_URL = os.getenv("EQUIPOS_SERVICE_URL", "http://equipos_service:8001")
PROVEEDORES_SERVICE_URL = os.getenv("PROVEEDORES_SERVICE_URL", "http://proveedores_service:8002")
MANTENIMIENTO_SERVICE_URL = os.getenv("MANTENIMIENTO_SERVICE_URL", "http://mantenimiento_service:8003")
REPORTES_SERVICE_URL = os.getenv("REPORTES_SERVICE_URL", "http://reportes_service:8004")
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent_service:8005")


async def proxy(request: Request, base_url: str, path: str):
    url = f"{base_url}/{path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        body = await request.body()
        resp = await client.request(
            method,
            url,
            headers=headers,
            content=body,
            params=request.query_params,
        )

    # Usamos Response de fastapi.responses
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers={
            k: v
            for k, v in resp.headers.items()
            if k.lower() not in ["content-encoding", "transfer-encoding", "connection"]
        },
        media_type=resp.headers.get("content-type"),
    )


@app.api_route("/equipos/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def equipos_proxy(path: str, request: Request):
    # /equipos/equipos -> equipos_service: /equipos
    return await proxy(request, EQUIPOS_SERVICE_URL, path)

@app.api_route("/proveedores/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proveedores_proxy(path: str, request: Request):
    # /proveedores/proveedores -> proveedores_service: /proveedores
    return await proxy(request, PROVEEDORES_SERVICE_URL, path)

@app.api_route("/mantenimiento/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def mantenimiento_proxy(path: str, request: Request):
    # /mantenimiento/mantenimientos -> mantenimiento_service: /mantenimientos
    return await proxy(request, MANTENIMIENTO_SERVICE_URL, path)
@app.api_route("/reportes/{path:path}", methods=["GET"])
async def reportes_proxy(path: str, request: Request):
    # /reportes/equipos-resumen -> reportes_service: /equipos-resumen
    return await proxy(request, REPORTES_SERVICE_URL, path)
@app.api_route("/agente/{path:path}", methods=["GET"])
async def agente_proxy(path: str, request: Request):
    # /agente/resumen-alertas -> agent_service: /resumen-alertas
    return await proxy(request, AGENT_SERVICE_URL, path)
