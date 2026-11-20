"""API de visitas del prototipo de observabilidad."""

import logging
import time
from contextlib import asynccontextmanager
from datetime import date, datetime, time as time_type
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db

# Logging en texto plano: fácil de recolectar y etiquetar con Loki/promtail.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("api.visitas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas al arrancar la aplicación."""
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos lista: tablas verificadas/creadas")
    yield


app = FastAPI(
    title="POC Observabilidad - Visitas",
    description="API mínima de registro de visitas para el prototipo de observabilidad.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Registra una línea por petición con método, ruta, estado y latencia."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "method=%s path=%s status=500 duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 500:
        log = logger.error
    elif response.status_code >= 400:
        log = logger.warning
    else:
        log = logger.info
    log(
        "method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


class VisitaCreate(BaseModel):
    """Datos necesarios para registrar una visita."""

    nombre: str = Field(min_length=1, max_length=150)
    correo: str = Field(min_length=1, max_length=255)
    fecha: date
    hora: time_type
    motivo: str = Field(min_length=1)


class VisitaOut(VisitaCreate):
    """Representación de una visita almacenada."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


DbSession = Annotated[Session, Depends(get_db)]


@app.get("/health", tags=["infra"])
def comprobar_salud() -> dict:
    """Comprueba que la API está viva."""
    return {"status": "ok"}


@app.post(
    "/api/visitas",
    status_code=status.HTTP_201_CREATED,
    tags=["visitas"],
)
def crear_visita(payload: VisitaCreate, db: DbSession) -> VisitaOut:
    """Registra una nueva visita."""
    visita = models.Visita(**payload.model_dump())
    db.add(visita)
    db.commit()
    db.refresh(visita)
    logger.info("visita_creada id=%s correo=%s", visita.id, visita.correo)
    return visita


@app.get("/api/visitas", tags=["visitas"])
def listar_visitas(db: DbSession) -> list[VisitaOut]:
    """Devuelve todas las visitas registradas."""
    visitas = db.scalars(select(models.Visita).order_by(models.Visita.id)).all()
    logger.info("visitas_listadas total=%s", len(visitas))
    return visitas


@app.get("/api/visitas/{visita_id}", tags=["visitas"])
def obtener_visita(visita_id: int, db: DbSession) -> VisitaOut:
    """Devuelve una visita por su identificador."""
    visita = db.get(models.Visita, visita_id)
    if visita is None:
        logger.warning("visita_no_encontrada id=%s", visita_id)
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    logger.info("visita_consultada id=%s", visita_id)
    return visita


@app.get("/api/simulate/slow", tags=["simulación"])
def simular_respuesta_lenta() -> dict:
    """Simula una respuesta exitosa con 3 segundos de latencia."""
    trace.get_current_span().set_attribute("simulation.delay_seconds", 3)
    logger.info("simulacion_lenta_inicio delay_seconds=3")
    time.sleep(3)
    logger.info("simulacion_lenta_fin delay_seconds=3")
    return {
        "status": "ok",
        "message": "Respuesta lenta simulada correctamente",
        "delay_seconds": 3,
    }


@app.get("/api/simulate/slow-db", tags=["simulación"])
def simular_db_lenta(db: DbSession) -> dict:
    """Simula una consulta lenta en la base de datos (2 segundos)."""
    trace.get_current_span().set_attribute("simulation.delay_seconds", 2)
    logger.info("simulacion_db_inicio delay_seconds=2")
    db.execute(text("SELECT pg_sleep(2)"))
    logger.info("simulacion_db_fin delay_seconds=2")
    return {
        "status": "ok",
        "message": "Consulta lenta simulada correctamente",
        "delay_seconds": 2,
    }


@app.get("/api/simulate/error", tags=["simulación"])
def simular_error() -> dict:
    """Simula un fallo interno del servidor (HTTP 500)."""
    trace.get_current_span().add_event(
        "error.simulado",
        {"error.type": "SimulatedError", "error.message": "Error interno simulado"},
    )
    logger.error("simulacion_error_forzada status=500")
    raise HTTPException(status_code=500, detail="Error interno simulado")
