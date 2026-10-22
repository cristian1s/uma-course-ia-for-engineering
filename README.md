# Sistema de predicción de ventas

Proyecto académico con panel web, API FastAPI, dos modelos, consultas CSV, autenticación por clave, monitoreo y auditoría. No requiere Docker para funcionar localmente. Este README corresponde a la carpeta que debes subir a GitHub.

## Ejecutar en Windows

1. Si faltan dependencias, ejecutar preparar.bat (Python 3.13 e internet).
2. Ejecutar iniciar.bat y mantener abierta la ventana. Panel: http://127.0.0.1:8000/panel.
3. Ejecutar ver_clave.bat. Copiar la clave al campo Clave de acceso del panel y presionar Conectar.
4. En http://127.0.0.1:8000/docs, usar Authorize e ingresar la misma clave para probar la API.

La clave se genera en .secrets/api_key.txt la primera vez, salvo que se defina VENTAS_API_KEY en el entorno. Debe contener al menos 32 caracteres ASCII sin espacios. El archivo .env.example es sólo una referencia; no se carga automáticamente. La clave del panel permanece en memoria de la pestaña, no se guarda en localStorage y se pierde al recargar. Desconectar limpia la página. No publiques la clave ni la captures en pantalla.

El estado básico GET /, el panel vacío, sus archivos estáticos y la documentación son públicos; los datos, predicciones, cambios de modelo, logs y auditoría requieren X-API-Key. La protección es de servicio con clave compartida, sin usuarios o roles. El servidor local usa HTTP; no exponerlo a internet sin HTTPS y otros controles.

## Archivos principales

- app/api.py: rutas, autenticación, validación, monitoreo y manejo de errores.
- app/security.py: generación y comprobación de clave.
- app/audit.py: logs JSON Lines, rotación y lectura de eventos.
- app/rag.py: validación de datos y consultas estructuradas del CSV.
- app/static/: panel HTML/CSS/JavaScript.
- src/train.py: entrenamiento, evaluación temporal y modelos guardados.
- tests/test_model.py: pruebas HTTP y validación de datos.
- logs/README.md: significado de los seis archivos de registros.
- evidencias/punto_5_rag.md: alcance actual y pasos para completar RAG con LLM.

## Validación y registros

POST /predict acepta únicamente {"dia":21}, con día entero de 1 a 10000 y sin campos extra. GET /consulta/{dia} aplica el mismo rango. GET /logs/{tipo} admite sólo los seis tipos documentados y limite de 1 a 100. Los colores de modelo permitidos son BLUE y GREEN. El CSV requiere días únicos positivos, ventas no negativas, valores finitos y al menos ocho registros.

Las solicitudes sin clave o con clave incorrecta reciben 401; los datos inválidos reciben 422. Se registran métodos, estados HTTP y tiempos sin incluir claves, cabeceras, cuerpos ni mensajes internos sensibles. El identificador X-Request-ID permite vincular la respuesta con sus registros de monitoreo y errores. Los logs rotan aproximadamente a 1 MB con tres copias. Los contadores viven en memoria; los registros permanecen en disco.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

También se pueden ejecutar con probar.bat. Las pruebas usan una clave aleatoria de proceso que no se guarda en el repositorio. Levantan un servidor en un puerto libre. Verifican protección, datos inválidos, modelos, predicción, consultas, métricas, recarga y auditoría. Los eventos resultantes son reales y quedan en logs.

## GitHub

Publicar esta carpeta como raíz del repositorio. El .gitignore excluye .secrets, .env, entornos, cachés, modelos generados y logs reales. Conserva .env.example, models/.gitkeep y logs/.gitkeep para permitir reproducir el proyecto. Evitar arrastrar archivos a la web de GitHub: usar Git para que aplique .gitignore.

Desde esta carpeta, una vez creado tu repositorio remoto:

```powershell
git init
git add .
git status
git commit -m "Proyecto de ventas con API protegida y auditoria"
git branch -M main
# Agregar TU URL real antes de subir:
# git remote add origin URL_DE_TU_REPOSITORIO
git push -u origin main
```

Revisar git status antes del commit. .gitignore no elimina archivos que ya estaban versionados. No se ha creado ni publicado un repositorio remoto desde esta tarea.

El workflow instala dependencias, entrena, prueba, conserva modelos como artefactos y construye la imagen Docker. El Dockerfile se mantiene preparado, sin ejecución local verificada. Para obtener evidencia de Docker operativo aún falta arrancar y consultar un contenedor en un equipo compatible o en CI.

## Alcance de la demostración

Dataset didáctico de 20 días. Blue: regresión lineal; Green: árbol de decisión. Evaluación en días 17–20 tras entrenar con 1–16; posteriormente ambos se ajustan con todo el historial. El árbol no extrapola tendencias. Cambiar de modelo es una selección dentro de un proceso, no dos entornos de producción. Editar el CSV no reentrena automáticamente: ejecutar src/train.py y recargar modelos.

Las consultas históricas tienen respuestas fijas y no usan LLM. El punto 5 con generación basada en recuperación sigue pendiente. El informe final será elaborado por el usuario. El panel y la API funcionan sin internet tras instalar dependencias; /docs utiliza Swagger desde un CDN.
