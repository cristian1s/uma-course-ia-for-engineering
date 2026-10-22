"""Integración real HTTP sin depender de Docker ni httpx."""
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import secrets
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.paths import MODELS
from app.rag import cargar_datos, obtener_promedio_ventas, obtener_maxima_venta


class VentasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, 'src/train.py'], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        cls.base = f'http://127.0.0.1:{port}'
        cls.output = tempfile.TemporaryFile()
        cls.api_key = secrets.token_urlsafe(32)
        cls.server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.api:app', '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT, stdout=cls.output, stderr=cls.output, env={**os.environ, 'PYTHONUTF8':'1', 'VENTAS_API_KEY': cls.api_key})
        cls.addClassCleanup(cls.stop_server)
        for _ in range(100):
            try:
                cls.request('/')
                break
            except Exception:
                if cls.server.poll() is not None:
                    cls.output.seek(0)
                    raise RuntimeError(cls.output.read().decode(errors='replace'))
                time.sleep(0.1)
        else:
            raise RuntimeError('El servidor de prueba no inició.')

    @classmethod
    def stop_server(cls):
        cls.server.terminate()
        try:
            cls.server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cls.server.kill()
            cls.server.wait()
        cls.output.close()

    @classmethod
    def request(cls, path, method='GET', body=None, auth=True):
        data = json.dumps(body).encode() if body is not None else None
        headers = {'Content-Type':'application/json'}
        if auth:
            headers['X-API-Key'] = cls.api_key
        req = Request(cls.base + path, data=data, method=method, headers=headers)
        with urlopen(req, timeout=10) as res:
            return json.loads(res.read())

    def test_dataset_statistics(self):
        self.assertEqual(len(cargar_datos()), 20)
        self.assertEqual(obtener_maxima_venta(), {'dia':20, 'ventas':540.0})
        self.assertEqual(obtener_promedio_ventas(), 299.5)

    def test_distinct_models_and_evaluation(self):
        blue = joblib.load(MODELS / 'modelo.pkl')
        green = joblib.load(MODELS / 'modelo_nuevo.pkl')
        self.assertNotEqual(type(blue), type(green))
        metadata = self.request('/modelo-info')
        self.assertEqual(metadata['dias_evaluacion'], [17,18,19,20])
        self.assertGreater(metadata['modelos']['GREEN']['mae'], 0)
        for model in (blue, green):
            self.assertTrue(math.isfinite(float(model.predict(pd.DataFrame({'dia':[21]}))[0])))

    def test_prediction_switch_reload_and_reset(self):
        self.request('/reset', 'DELETE')
        self.request('/switch/BLUE', 'PUT')
        blue = self.request('/predict', 'POST', {'dia':21})
        self.assertAlmostEqual(blue['prediccion'], 540.6842105263158, places=6)
        self.request('/switch/GREEN', 'PUT')
        green = self.request('/predict', 'POST', {'dia':21})
        self.assertEqual(green['modelo'], 'GREEN')
        self.assertNotEqual(blue['prediccion'], green['prediccion'])
        self.assertGreaterEqual(green['latencia'], 0)
        self.assertEqual(self.request('/metrics')['total_predicciones'], 2)
        self.request('/reload-model', 'PUT')
        self.assertEqual(self.request('/predict', 'POST', {'dia':21})['prediccion'], green['prediccion'])
        self.request('/reset', 'DELETE')
        self.assertEqual(self.request('/metrics')['total_predicciones'], 0)
        actions = [e['accion'] for e in self.request('/audit')['eventos']]
        self.assertIn('PREDICCION', actions)
        self.assertIn('CAMBIO_MODELO', actions)

    def test_input_validation(self):
        for body in ({'dia':0}, {'dia':-1}, {'dia':1.5}, {'dia':'abc'}, {'dia':True}, {'dia':'21'}, {'dia':10001}, {'dia':2,'extra':1}):
            with self.assertRaises(HTTPError) as ctx:
                self.request('/predict', 'POST', body)
            self.assertEqual(ctx.exception.code, 422)
        with self.assertRaises(HTTPError) as ctx:
            self.request('/switch/RED', 'PUT')
        self.assertEqual(ctx.exception.code, 422)

    def test_api_protection(self):
        for path, method, body in [('/datos','GET',None), ('/audit','GET',None),
                                   ('/predict','POST',{'dia':21}), ('/switch/GREEN','PUT',None),
                                   ('/logs/monitoreo','GET',None), ('/reset','DELETE',None)]:
            with self.assertRaises(HTTPError) as ctx:
                self.request(path, method, body, auth=False)
            self.assertEqual(ctx.exception.code, 401)
        req = Request(self.base + '/metrics', headers={'X-API-Key':'incorrecta'})
        with self.assertRaises(HTTPError) as ctx:
            urlopen(req)
        self.assertEqual(ctx.exception.code, 401)
        spec = self.request('/openapi.json', auth=False)
        self.assertIn('ClaveDeAPI', spec['components']['securitySchemes'])
        self.assertIn('security', spec['paths']['/predict']['post'])

    def test_monitoring_and_validation_audit(self):
        for path in ('/consulta/10001', '/logs/errores?limite=0', '/logs/no-permitido'):
            with self.assertRaises(HTTPError) as ctx:
                self.request(path)
            self.assertEqual(ctx.exception.code, 422)
        self.request('/metrics')
        logs = self.request('/logs/monitoreo?limite=100')['eventos']
        self.assertTrue(any(e['detalle'].get('ruta') == '/metrics' and e['detalle']['estado'] == 200 for e in logs))
        self.assertTrue(any(e['detalle']['estado'] == 422 for e in logs))
        for tipo in ('audit', 'monitoreo', 'errores', 'seguridad', 'deployment', 'predicciones'):
            result = self.request('/logs/' + tipo)
            self.assertNotIn(self.api_key, json.dumps(result))

    def test_invalid_datasets(self):
        original = cargar_datos()
        for change in ('negativo', 'duplicado', 'infinito', 'vacio', 'columnas'):
            data = original.copy()
            if change == 'negativo': data.loc[0,'ventas'] = -1
            if change == 'duplicado': data.loc[0,'dia'] = 2
            if change == 'infinito': data['ventas'] = float('inf')
            if change == 'vacio': data = data.iloc[:3]
            if change == 'columnas': data = data.rename(columns={'dia':'fecha'})
            with patch('app.rag.pd.read_csv', return_value=data):
                with self.assertRaises(ValueError): cargar_datos()

    def test_historical_queries(self):
        self.assertIn('270', self.request('/consulta/10')['respuesta'])
        self.assertIn('No existe', self.request('/consulta/99')['respuesta'])
        self.assertEqual(self.request('/max-ventas')['ventas'], 540)
        self.assertEqual(self.request('/promedio-ventas')['promedio'], 299.5)
        self.assertFalse(self.request('/governance')['cumplimiento_certificado'])

    def test_panel_and_documentation(self):
        for path, expected in [('/panel', b'Ventas'), ('/docs', b'Swagger'), ('/static/app.js', b'predict-form')]:
            with urlopen(self.base + path, timeout=10) as res:
                self.assertEqual(res.status, 200)
                self.assertIn(expected, res.read())


if __name__ == '__main__':
    unittest.main()
