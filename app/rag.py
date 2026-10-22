"""Consultas estructuradas del CSV (denominadas RAG en la guía del curso)."""
import pandas as pd
import numpy as np
from app.paths import DATA


def cargar_datos():
    datos = pd.read_csv(DATA)
    if set(datos.columns) != {'dia', 'ventas'} or len(datos) < 8:
        raise ValueError('El CSV debe contener dia, ventas y al menos 8 registros.')
    for column in ('dia', 'ventas'):
        datos[column] = pd.to_numeric(datos[column], errors='raise')
    if not np.isfinite(datos[['dia', 'ventas']].to_numpy()).all():
        raise ValueError('Los datos deben ser finitos y completos.')
    if (datos.dia <= 0).any() or (datos.dia % 1 != 0).any() or datos.dia.duplicated().any():
        raise ValueError('Los días deben ser enteros positivos únicos.')
    if (datos.ventas < 0).any():
        raise ValueError('Las ventas no pueden ser negativas.')
    return datos.sort_values('dia').reset_index(drop=True)


def buscar_ventas(dia):
    datos = cargar_datos()
    resultado = datos.loc[datos.dia == dia, 'ventas']
    return None if resultado.empty else float(resultado.iloc[0])


def generar_respuesta_natural(dia):
    venta = buscar_ventas(dia)
    return (f'No existe información para el día {dia}.' if venta is None else
            f'Las ventas registradas para el día {dia} fueron {venta:g} unidades.')


def obtener_maxima_venta():
    datos = cargar_datos()
    fila = datos.loc[datos.ventas.idxmax()]
    return {'dia': int(fila.dia), 'ventas': float(fila.ventas)}


def obtener_promedio_ventas():
    return round(float(cargar_datos().ventas.mean()), 2)
