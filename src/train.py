"""Entrenamiento reproducible con evaluación temporal fuera de muestra."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hashlib
import json
from datetime import datetime, timezone
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.paths import DATA, MODELS
from app.rag import cargar_datos


def entrenar():
    datos = cargar_datos()
    corte = max(4, int(len(datos) * 0.8))
    train, test = datos.iloc[:corte], datos.iloc[corte:]
    MODELS.mkdir(exist_ok=True)
    metadata = {'entrenado_en': datetime.now(timezone.utc).isoformat(),
                'dataset_sha256': hashlib.sha256(DATA.read_bytes()).hexdigest(),
                'registros': len(datos), 'evaluacion': 'Temporal: primeros 80% entrenan, últimos 20% evalúan; después se ajusta con todos los datos.',
                'dias_evaluacion': test.dia.astype(int).tolist(), 'modelos': {}}
    for color, modelo, filename in [
        ('BLUE', LinearRegression(), 'modelo.pkl'),
        ('GREEN', DecisionTreeRegressor(max_depth=3, random_state=42), 'modelo_nuevo.pkl')]:
        modelo.fit(train[['dia']], train.ventas)
        pred = modelo.predict(test[['dia']])
        scores = {'mae': float(mean_absolute_error(test.ventas, pred)),
                  'rmse': float(mean_squared_error(test.ventas, pred) ** 0.5)}
        modelo.fit(datos[['dia']], datos.ventas)
        joblib.dump(modelo, MODELS / filename)
        metadata['modelos'][color] = {'algoritmo': type(modelo).__name__, 'archivo': filename, **scores}
    (MODELS / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return metadata


if __name__ == '__main__':
    entrenar()
