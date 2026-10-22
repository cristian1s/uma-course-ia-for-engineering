# Registros de monitoreo y auditoría

Al iniciar el servidor se crean seis archivos JSON Lines:

| Archivo | Contenido |
|---|---|
| audit.log | Operaciones de negocio, validaciones y accesos rechazados |
| predicciones.log | Día, modelo, predicción y latencia |
| deployment.log | Cambio entre Blue y Green |
| monitoreo.log | Método, ruta de operación, estado HTTP, duración y request_id |
| errores.log | Respuestas 4xx/5xx y tipo de excepciones internas |
| seguridad.log | Accesos sin clave o con clave incorrecta |

Cada archivo rota al llegar aproximadamente a 1 MB y conserva hasta tres copias. Los logs están excluidos de Git; este README y .gitkeep conservan la estructura. No se registran claves, cuerpos de solicitudes ni cabeceras de autenticación. No se guardan identidades individuales: la clave autoriza al servicio y no identifica a una persona.

En /docs, usar Authorize con la clave local y consultar GET /logs/{tipo}. Los tipos permitidos son audit, predicciones, deployment, monitoreo, errores y seguridad. El parámetro limite acepta 1 a 100 eventos. GET /audit conserva la consulta usada por el panel.

Para evidencias reales: hacer una predicción, cambiar de modelo, consultar un día, enviar un día inválido e intentar una llamada sin clave. Mostrar los registros resultantes, sin capturar la clave. No subir registros privados a un repositorio público.
