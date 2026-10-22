# Verificación local de semana 13

Verificación realizada el 7 de octubre de 2026.

## Pruebas automatizadas

Comando ejecutado con Python 3.13:

```text
python -m unittest discover -s tests -v
```

Resultado: seis pruebas completadas correctamente.

- Estadísticas del dataset: 20 registros, promedio 299.5 y máximo 540 en el día 20.
- Modelos de clases diferentes y evaluación temporal en días 17 a 20.
- Consultas históricas existentes y ausentes.
- Rechazo HTTP 422 de entradas inválidas y colores no permitidos.
- Acceso HTTP al panel, JavaScript y documentación Swagger.
- Predicción, cambio de modelo, recarga, contadores y trazabilidad.

## Comprobación en navegador

- Panel cargado con gráfico y estadísticas.
- Predicción Blue para día 21: 540.6842105263158 unidades.
- Cambio a Green desde el botón: predicción para día 21 de 525 unidades.
- Consulta del día 10 desde el formulario: 270 unidades.
- Retorno a Blue para dejar el panel listo para la demostración.
- Vista completa guardada en vista_panel.png como referencia de la verificación.

## Configuraciones sin ejecución

Dockerfile y workflow GitHub Actions incluidos. No se ejecutó Docker ni se subió el proyecto a GitHub. No se atribuye una ejecución remota a las pruebas locales.

Los archivos de logs contienen los eventos reales de estas comprobaciones. El usuario puede realizar sus propias capturas para la entrega.
