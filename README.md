# Prueba de concepto: Observabilidad

Stack de ejemplo con frontend Angular, API en Python/FastAPI, PostgreSQL y un stack
de observabilidad completo (OpenTelemetry Collector, Prometheus, Loki, Jaeger y Grafana).

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) con Docker Compose v2

## Cómo arrancar

1. Copia el archivo de variables de entorno:

   ```bash
   cp backend-poc/.env.example backend-poc/.env
   ```

2. Levanta todo el stack:

   ```bash
   docker compose up --build
   ```

La primera vez tarda unos minutos porque compila las imágenes.

## Servicios

| Servicio                 | URL                          |
| ------------------------ | ---------------------------- |
| Frontend                 | http://localhost:4200        |
| API (FastAPI, docs)      | http://localhost:8000/docs   |
| Grafana (admin/admin)    | http://localhost:3000        |
| Prometheus               | http://localhost:9090        |
| Jaeger                   | http://localhost:16686       |
| Loki                     | http://localhost:3100        |

## Parar el stack

```bash
docker compose down
```

Para borrar también los datos guardados (Postgres, Prometheus, Loki y Grafana):

```bash
docker compose down -v
```

## Estructura

- `backend-poc/` — API FastAPI + PostgreSQL
- `frontend-poc/` — Frontend Angular (servido con Nginx)
- `observabilidad/` — Configuración de Collector, Prometheus, Loki y Grafana
- `docker-compose.yml` — Orquestación de todos los servicios
