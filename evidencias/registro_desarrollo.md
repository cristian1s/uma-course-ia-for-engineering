# Registro de desarrollo hasta semana 13

Fecha de solicitud: 7 de octubre de 2026, zona America/Bogota.

## Solicitud real del usuario

> okey me queda claro codex, hagamos primero la version final hasta la semana 13 que es lo que tengo presentar ahora, claro con todo lo que acabamos de indicar y tambien pues que se pueda visualizar creemos una carpeta ques e proyect... y le coloquemos todos los arhcivos ahi, aun no hagamos el documento , solo el proyecto y ya bueno creo que en el entregable de la seman 13 tambien se coloan imagenes de la doc, (revisalo) ya eso yo lo hago , pero el proyecto hasta ahi hagamoslo , dale

## Restricciones expresadas previamente

- Mostrar la aplicación en el navegador.
- No ejecutar Docker: el equipo no lo soporta.
- Incluir archivos de configuración.
- Conservar evidencia real de solicitudes y revisiones.
- Limitar esta etapa a semana 13; no elaborar el informe.

## Decisiones de implementación

- Dos algoritmos distintos para corregir la duplicación de un mismo modelo en la guía.
- Evaluación temporal con datos reservados y métricas guardadas.
- Panel HTML/CSS/JS servido por la misma API, sin Node ni recursos remotos.
- Validación estricta de días y CSV, rutas absolutas del proyecto, auditoría persistente.
- Mantener los endpoints de la guía y su estado JSON en la raíz; panel en /panel.
- Respetar el alcance de las consultas CSV y la selección Blue/Green en un proceso.
- Preparar Docker y CI; no atribuirles ejecuciones no realizadas.

Este archivo es un extracto de la solicitud y un registro de decisiones, no una transcripción completa de la conversación. Las capturas serán realizadas por el usuario.
