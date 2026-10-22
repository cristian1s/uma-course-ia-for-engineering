# Verificación de acceso, validación y registros

Fecha: 21 de octubre de 2026.

Se ejecutó `python -m unittest discover -s tests -v`: nueve pruebas correctas. Cubren autenticación, estructura de datos, evaluación de modelos, consultas, entradas inválidas, CSV inválidos, monitoreo, recursos web y predicción con cambio/recarga de modelo.

La comprobación con Git confirmó que el .gitignore excluye .env, claves en .secrets, logs reales y copias rotadas, y modelos generados. Permite versionar .env.example, el código, README y archivos .gitkeep.

Se comprobó el panel con Chrome sin interfaz y un perfil temporal: clave incorrecta rechazada, clave local aceptada, campo de clave vaciado después de conectar, predicción y consulta correctas, diálogo de controles y desconexión. Se verificó ausencia de desbordamiento horizontal a 390 píxeles. No hubo errores JavaScript durante esa comprobación. La referencia visual está en acceso_protegido.png; no incluye la clave.

Los registros de pruebas y de navegador están en logs, excluidos de Git. No se subió el repositorio, no se ejecutó Docker y no se implementó todavía generación RAG con LLM.
