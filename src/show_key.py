"""Mostrar la clave al dueño del equipo sin publicarla ni registrarla."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.security import obtener_clave

if __name__ == '__main__':
    print('Clave local para el panel y Authorize en /docs:')
    print(obtener_clave())
    print('\nNo publiques esta clave ni la incluyas en capturas.')
