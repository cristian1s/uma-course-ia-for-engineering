import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import joblib
import pandas as pd
from app.paths import MODELS

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dia', type=int, default=21)
    args = parser.parse_args()
    if args.dia <= 0:
        parser.error('El día debe ser positivo.')
    modelo = joblib.load(MODELS / 'modelo.pkl')
    print(float(modelo.predict(pd.DataFrame({'dia': [args.dia]}))[0]))
