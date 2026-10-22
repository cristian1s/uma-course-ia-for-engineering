"""Clave de servicio local; nunca se incorpora al HTML ni a los logs."""
import os
from pathlib import Path
import secrets
from fastapi import Request, Security, HTTPException
from fastapi.security import APIKeyHeader
from app.paths import ROOT
from app.audit import registrar_evento

header_clave = APIKeyHeader(name='X-API-Key', auto_error=False, scheme_name='ClaveDeAPI')


def obtener_clave():
    configurada = os.environ.get('VENTAS_API_KEY')
    if configurada is not None:
        if len(configurada) < 32 or not configurada.isascii() or any(c.isspace() for c in configurada):
            raise ValueError('VENTAS_API_KEY debe tener al menos 32 caracteres ASCII sin espacios.')
        return configurada
    carpeta = Path(os.environ.get('VENTAS_SECRETS_DIR', str(ROOT / '.secrets')))
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / 'api_key.txt'
    try:
        with archivo.open('x', encoding='ascii') as f:
            f.write(secrets.token_urlsafe(32))
        archivo.chmod(0o600)
    except FileExistsError:
        pass
    clave = archivo.read_text(encoding='ascii').strip()
    if len(clave) < 32:
        raise ValueError('La clave local no es válida. Usa una clave de al menos 32 caracteres.')
    return clave


def validar_clave(request: Request, clave: str | None = Security(header_clave)):
    esperada = request.app.state.api_key
    if clave is None or not secrets.compare_digest(clave.encode('utf-8'), esperada.encode('utf-8')):
        registrar_evento('ACCESO_RECHAZADO', {'motivo': 'clave_ausente_o_incorrecta'}, 'seguridad.log')
        registrar_evento('ACCESO_RECHAZADO', {'motivo': 'clave_ausente_o_incorrecta'})
        raise HTTPException(401, 'Clave de API ausente o incorrecta.', headers={'WWW-Authenticate':'ApiKey'})
