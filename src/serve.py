"""Inicia el servidor y abre el navegador cuando el panel está disponible."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import socket
from threading import Thread
import time
from urllib.request import urlopen
import webbrowser
import uvicorn

URL = 'http://127.0.0.1:8000'


def abrir_cuando_listo():
    for _ in range(100):
        try:
            with urlopen(URL + '/', timeout=1) as response:
                if json.load(response).get('estado') == 'activo':
                    webbrowser.open(URL + '/panel')
                    return
        except Exception:
            time.sleep(0.2)


if __name__ == '__main__':
    with socket.socket() as sock:
        ocupado = sock.connect_ex(('127.0.0.1', 8000)) == 0
    if ocupado:
        try:
            with urlopen(URL + '/openapi.json', timeout=2) as response:
                title = json.load(response)['info']['title']
            if title == 'Ventas IA · Semana 13':
                print('Ventas IA ya está ejecutándose. Abriendo el panel existente.')
                webbrowser.open(URL + '/panel')
                sys.exit(0)
        except Exception:
            pass
        sys.exit('El puerto 8000 está ocupado por otro servicio. Libéralo e intenta de nuevo.')
    Thread(target=abrir_cuando_listo, daemon=True).start()
    uvicorn.run('app.api:app', host='127.0.0.1', port=8000)
