from contextlib import asynccontextmanager
import json
import math
from threading import RLock
from time import perf_counter
from typing import Annotated, Literal
from uuid import uuid4
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request, Path, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from app.paths import ROOT, MODELS
from app.rag import cargar_datos, generar_respuesta_natural, obtener_maxima_venta, obtener_promedio_ventas
from app.audit import registrar_evento, leer_eventos, preparar_logs
from app.security import obtener_clave, validar_clave

lock = RLock()
state = {'activo': 'BLUE', 'total': 0, 'latencia_total': 0.0, 'modelos': {}, 'metadata': {}}


def cargar_modelos():
    # Sólo cargar artefactos locales generados por src/train.py.
    modelos = {'BLUE': joblib.load(MODELS / 'modelo.pkl'),
               'GREEN': joblib.load(MODELS / 'modelo_nuevo.pkl')}
    metadata = json.loads((MODELS / 'metadata.json').read_text(encoding='utf-8'))
    with lock:
        state.update(modelos=modelos, metadata=metadata)


@asynccontextmanager
async def lifespan(app):
    preparar_logs()
    app.state.api_key = obtener_clave()
    cargar_modelos()
    registrar_evento('INICIO', 'Servicio local iniciado')
    yield


app = FastAPI(title='Ventas IA · Semana 13', version='1.0.0', lifespan=lifespan)
router = APIRouter(dependencies=[Depends(validar_clave)])
app.mount('/static', StaticFiles(directory=ROOT / 'app' / 'static'), name='static')


@app.middleware('http')
async def monitorear(request: Request, call_next):
    inicio = perf_counter()
    request_id = uuid4().hex
    try:
        response = await call_next(request)
    except Exception as exc:
        # No registrar mensajes de excepción, cuerpos ni cabeceras: pueden contener secretos.
        registrar_evento('ERROR_SERVIDOR', {'tipo': type(exc).__name__, 'request_id': request_id}, 'errores.log')
        response = JSONResponse(status_code=500, content={'detail': 'Error interno. Consulta errores.log.', 'request_id': request_id})
    ruta = getattr(request.scope.get('route'), 'path', 'recurso_estatico_o_desconocido')
    registrar_evento('SOLICITUD_HTTP', {'request_id': request_id, 'metodo': request.method,
                     'ruta': ruta, 'estado': response.status_code,
                     'duracion_ms': round((perf_counter() - inicio) * 1000, 3)}, 'monitoreo.log')
    response.headers['X-Request-ID'] = request_id
    response.headers['Cache-Control'] = 'no-store'
    if response.status_code >= 400:
        registrar_evento('RESPUESTA_ERROR', {'request_id': request_id, 'estado': response.status_code, 'ruta': ruta}, 'errores.log')
    return response


@app.exception_handler(RequestValidationError)
async def entrada_invalida(request: Request, exc: RequestValidationError):
    # Evitar devolver el contenido recibido en los errores de validación.
    errores = [{'campo': '.'.join(map(str, e['loc'])), 'tipo': e['type']} for e in exc.errors()]
    registrar_evento('VALIDACION_RECHAZADA', {'errores': errores})
    return JSONResponse(status_code=422, content={'detail': 'Datos inválidos. Revisa los campos y sus límites.', 'errores': errores})


class Entrada(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dia: int = Field(gt=0, le=10000, strict=True)


@app.get('/')
def inicio():
    with lock:
        return {'estado': 'activo', 'modelo_activo': state['activo']}


@app.get('/panel', include_in_schema=False)
def panel():
    return FileResponse(ROOT / 'app' / 'static' / 'index.html')


@router.post('/predict')
def predict(datos: Entrada):
    start = perf_counter()
    with lock:
        color = state['activo']
        modelo = state['modelos'][color]
    value = float(modelo.predict(pd.DataFrame({'dia': [datos.dia]}))[0])
    if not math.isfinite(value):
        raise HTTPException(500, 'El modelo produjo una salida no finita.')
    latency = perf_counter() - start
    result = {'modelo': color, 'dia': datos.dia, 'prediccion': value, 'latencia': latency}
    registrar_evento('PREDICCION', result, 'predicciones.log')
    registrar_evento('PREDICCION', result)
    with lock:
        state['total'] += 1
        state['latencia_total'] += latency
    return result


@router.get('/consulta/{dia}')
def consulta(dia: Annotated[int, Path(gt=0, le=10000)]):
    registrar_evento('CONSULTA_RAG', {'dia': dia})
    return {'respuesta': generar_respuesta_natural(dia)}


@router.get('/max-ventas')
def max_ventas():
    result = obtener_maxima_venta()
    registrar_evento('CONSULTA_MAX_VENTAS', result)
    return {'mensaje': f"El día con mayores ventas fue {result['dia']}", **result}


@router.get('/promedio-ventas')
def promedio_ventas():
    result = {'promedio': obtener_promedio_ventas()}
    registrar_evento('CONSULTA_PROMEDIO', result)
    return result


@router.get('/datos')
def datos():
    return {'registros': cargar_datos().to_dict(orient='records')}


@router.put('/switch/{color}')
def switch_model(color: str):
    color = color.upper()
    if color not in ('BLUE', 'GREEN'):
        raise HTTPException(422, 'Debe elegir BLUE o GREEN.')
    with lock:
        anterior = state['activo']
        state['activo'] = color
    detail = {'anterior': anterior, 'nuevo': color}
    registrar_evento('CAMBIO_MODELO', detail, 'deployment.log')
    registrar_evento('CAMBIO_MODELO', detail)
    return {'mensaje': f'Producción ahora usa {color}', 'modelo_activo': color}


@router.put('/reload-model')
def reload_model():
    cargar_modelos()
    registrar_evento('RELOAD_MODELOS', 'Modelos locales recargados')
    return {'mensaje': 'Modelos recargados exitosamente'}


@router.get('/metrics')
def metrics():
    with lock:
        return {'estado': 'ok', 'modelo_activo': state['activo'], 'total_predicciones': state['total'],
                'latencia_promedio_ms': round(state['latencia_total'] * 1000 / state['total'], 3) if state['total'] else 0}


@router.get('/modelo-info')
def modelo_info():
    with lock:
        result = {'modelo_activo': state['activo'], **state['metadata']}
    registrar_evento('CONSULTA_MODELO', result['modelo_activo'])
    return result


@router.get('/governance')
def governance():
    registrar_evento('CONSULTA_GOVERNANCE', 'Estado de controles del prototipo')
    return {'logging': True, 'trazabilidad': True, 'validacion_entradas': True, 'autenticacion_api_key': True,
            'evaluacion_temporal': True, 'cumplimiento_certificado': False,
            'alcance': 'Prototipo académico local. Consultas CSV con respuestas fijas; sin LLM.',
            'limitaciones': ['Dataset didáctico de 20 días.', 'Clave de servicio compartida: sin roles ni identificación individual. Uso local sin HTTPS.',
                            'Cambio Blue/Green dentro de un proceso; no representa dos entornos de producción.',
                            'El árbol no extrapola tendencias fuera de los días entrenados.']}


@router.get('/audit')
def audit():
    return {'eventos': leer_eventos()}


@router.get('/logs/{tipo}')
def logs(tipo: Literal['audit', 'predicciones', 'deployment', 'monitoreo', 'errores', 'seguridad'],
         limite: Annotated[int, Query(ge=1, le=100)] = 30):
    return {'archivo': f'{tipo}.log', 'eventos': leer_eventos(limite, f'{tipo}.log')}


@router.delete('/reset')
def reset_service():
    with lock:
        state.update(total=0, latencia_total=0.0)
    registrar_evento('RESET', 'Contadores reiniciados; historial preservado')
    return {'mensaje': 'Contadores reiniciados correctamente'}


app.include_router(router)
