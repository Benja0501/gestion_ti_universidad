# Sistema de Gestión de Equipos de TI – Universidad Pública

Aplicación web basada en microservicios para la **gestión de equipos de TI** en una universidad pública.  
Permite centralizar:

- Inventario de equipos de TI.
- Gestión de proveedores.
- Planificación y seguimiento de mantenimiento.
- Dashboard de reportes con exportación a PDF.
- Alertas inteligentes de equipos obsoletos y mantenimientos próximos.

La solución está construida con:

- **Frontend**: Streamlit.
- **Backend**: Python + FastAPI (microservicios).
- **Base de datos**: PostgreSQL.
- **Infraestructura**: Docker + Docker Compose.

---

## 1. Arquitectura general

La aplicación está compuesta por los siguientes servicios:

- `ti_frontend` – interfaz web en Streamlit.
- `api_gateway` – API Gateway en FastAPI.
- `equipos_service` – microservicio de gestión de equipos.
- `proveedores_service` – microservicio de proveedores.
- `mantenimiento_service` – microservicio de mantenimiento.
- `reportes_service` – microservicio de reportes y generación de PDF.
- `agent_service` – microservicio de alertas inteligentes.
- `ti_db` – PostgreSQL (base de datos principal).

### 1.1. Diagrama de arquitectura (lógico)

```mermaid
flowchart LR
    subgraph Frontend
        A[Streamlit\n(ti_frontend)]
    end

    subgraph Infraestructura
        G[API Gateway\nFastAPI]
        DB[(PostgreSQL\n ti_db)]
    end

    subgraph Microservicios
        E[equipos_service]
        P[proveedores_service]
        M[mantenimiento_service]
        R[reportes_service]
        AG[agent_service]
    end

    A <--> G

    G <--> E
    G <--> P
    G <--> M
    G <--> R
    G <--> AG

    E <--> DB
    P <--> DB
    M <--> DB

    R --> E
    R --> M
    AG --> E
    AG --> M
