import json
from collections import deque
from datetime import datetime, timezone
import logging
from logging.handlers import RotatingFileHandler
from threading import Lock
from app.paths import LOGS

_lock = Lock()
ARCHIVOS = ('audit.log', 'predicciones.log', 'deployment.log', 'monitoreo.log', 'errores.log', 'seguridad.log')
_loggers = {}


def preparar_logs():
    with _lock:
        LOGS.mkdir(exist_ok=True)
        for archivo in ARCHIVOS:
            if archivo not in _loggers:
                logger = logging.Logger('ventas.' + archivo, level=logging.INFO)
                handler = RotatingFileHandler(LOGS / archivo, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
                handler.setFormatter(logging.Formatter('%(message)s'))
                logger.addHandler(handler)
                _loggers[archivo] = logger


def registrar_evento(accion, detalle, archivo='audit.log'):
    if archivo not in ARCHIVOS:
        raise ValueError('Archivo de log no permitido.')
    preparar_logs()
    evento = {'fecha': datetime.now(timezone.utc).isoformat(), 'accion': accion, 'detalle': detalle}
    _loggers[archivo].info(json.dumps(evento, ensure_ascii=False))
    return evento


def leer_eventos(limite=30, archivo='audit.log'):
    if archivo not in ARCHIVOS:
        raise ValueError('Archivo de log no permitido.')
    logger = _loggers.get(archivo)
    handler = logger.handlers[0] if logger else None
    if handler:
        handler.acquire()
    try:
        lines = deque(maxlen=limite)
        # Leer también copias rotadas para conservar el historial reciente.
        for path in [LOGS / f'{archivo}.{i}' for i in (3, 2, 1)] + [LOGS / archivo]:
            if path.exists():
                with path.open(encoding='utf-8') as f:
                    lines.extend(f)
        events = []
        for line in reversed(lines):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events
    finally:
        if handler:
            handler.release()
