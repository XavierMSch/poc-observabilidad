#!/usr/bin/env python3
"""Genera tráfico variable contra la API para poblar los dashboards de Grafana.

Solo usa la librería estándar: funciona igual en Linux, macOS y Windows.

Ejemplos:
    python traffic-generator/generate.py
    python traffic-generator/generate.py --duration 300
    python traffic-generator/generate.py --duration 0   # infinito hasta Ctrl+C
"""

from __future__ import annotations

import argparse
import json
import random
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from urllib import error, request

# Peticiones por segundo de cada fase (10 s por fase, se repiten cada minuto).
FASES = [2, 5, 10, 4, 8, 3]
SEGUNDOS_POR_FASE = 10
MAX_WORKERS = 20
TIMEOUT = 5

NOMBRES = ["Ana", "Luis", "Marta", "Pedro", "Lucía", "Jorge", "Elena", "Raúl"]
MOTIVOS = [
    "Reunión de proyecto",
    "Entrevista",
    "Visita comercial",
    "Soporte técnico",
    "Demostración del producto",
    "Formación",
]

contadores = Counter()
lock = threading.Lock()


def _registrar(clave: str) -> None:
    with lock:
        contadores[clave] += 1


def _snapshot() -> dict[str, int]:
    with lock:
        return dict(contadores)


def _payload_visita() -> dict:
    """Datos aleatorios pero válidos para POST /api/visitas."""
    nombre = random.choice(NOMBRES)
    correo = f"{nombre.lower()}.{random.randint(1, 9999)}@example.com"
    return {
        "nombre": nombre,
        "correo": correo,
        "fecha": date.today().isoformat(),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "motivo": random.choice(MOTIVOS),
    }


def _get(url: str) -> None:
    with request.urlopen(url, timeout=TIMEOUT) as respuesta:
        respuesta.read()


def enviar_peticion(base_url: str) -> None:
    """Elige un endpoint según los pesos y lo invoca."""
    destino = random.choices(
        ["get_visitas", "post_visita", "slow", "slow_db", "error"],
        weights=[85, 5, 4, 3, 3],
    )[0]

    try:
        if destino == "get_visitas":
            _get(f"{base_url}/api/visitas")
        elif destino == "post_visita":
            datos = json.dumps(_payload_visita()).encode("utf-8")
            peticion = request.Request(
                f"{base_url}/api/visitas",
                data=datos,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(peticion, timeout=TIMEOUT) as respuesta:
                respuesta.read()
        elif destino == "slow":
            _get(f"{base_url}/api/simulate/slow")
        elif destino == "slow_db":
            _get(f"{base_url}/api/simulate/slow-db")
        else:
            _get(f"{base_url}/api/simulate/error")
    except error.HTTPError as exc:
        # El 500 de /api/simulate/error es intencionado: se cuenta, no se muestra.
        _registrar(f"{exc.code // 100}xx")
    except (error.URLError, OSError):
        _registrar("red")
    else:
        _registrar("2xx")


def _carga(segundo: int) -> int:
    """Peticiones por segundo del instante dado, con jitter aleatorio."""
    fase = (segundo // SEGUNDOS_POR_FASE) % len(FASES)
    return max(1, FASES[fase] + random.choice([-1, 0, 0, 1]))


def _formatear_resumen(transcurrido: float) -> str:
    datos = _snapshot()
    return (
        f"\nResumen:\n"
        f"  Duración: {transcurrido:.1f} s\n"
        f"  Peticiones: {sum(datos.values())}\n"
        f"  2xx: {datos.get('2xx', 0)}  "
        f"4xx: {datos.get('4xx', 0)}  "
        f"5xx: {datos.get('5xx', 0)}  "
        f"red: {datos.get('red', 0)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera tráfico variable contra la API de visitas."
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="URL base de la API (por defecto http://localhost:8000)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=120,
        help="Segundos de ejecución; 0 = infinito hasta Ctrl+C (por defecto 120)",
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    duracion = args.duration
    modo = "infinito, Ctrl+C para parar" if duracion == 0 else f"{duracion} s"
    print(f"Generando tráfico contra {base_url} ({modo})", flush=True)

    inicio = time.monotonic()
    segundo = 0
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    try:
        while duracion == 0 or segundo < duracion:
            comienzo_segundo = time.monotonic()
            carga = _carga(segundo)

            for _ in range(carga):
                executor.submit(enviar_peticion, base_url)

            if segundo % 10 == 0:
                enviadas = sum(_snapshot().values())
                print(
                    f"  t={segundo:>3}s  carga={carga} p/s  enviadas={enviadas}",
                    flush=True,
                )

            segundo += 1
            pausa = comienzo_segundo + 1 - time.monotonic()
            if pausa > 0:
                time.sleep(pausa)
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.", flush=True)
    finally:
        executor.shutdown(wait=True, cancel_futures=True)

    print(_formatear_resumen(time.monotonic() - inicio), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
