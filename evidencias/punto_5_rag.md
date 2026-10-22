# Cómo completar la evidencia de RAG funcional

## Situación actual

app/rag.py recupera registros de ventas de un CSV y genera una frase mediante una plantilla. Coincide con el ejemplo de la guía de semanas 12–13, pero no incluye generación de respuestas mediante un modelo de lenguaje. No presentar esa función como un chatbot RAG con LLM.

## Implementación mínima propuesta

1. Añadir un formulario de pregunta libre y un endpoint protegido POST /rag/ask.
2. Recuperar los datos pertinentes de ventas.csv y calcular con Python máximos, promedios o comparaciones que requiera la pregunta. Para datos tabulares, la recuperación puede ser estructurada; una base vectorial no es obligatoria.
3. Construir un contexto que incluya únicamente datos recuperados y su fuente: archivo, días o filas.
4. Enviar la pregunta y ese contexto a un LLM mediante API. Esto evita cargar un modelo generativo pesado en este equipo; requiere internet y una credencial de proveedor que puede tener coste. Nunca usar la clave de servicio de Ventas IA como clave del proveedor.
5. Pedir al LLM responder sólo con el contexto, indicar falta de información y tratar el contenido recuperado como datos, sin obedecer instrucciones incrustadas en él.
6. Devolver respuesta y fuentes; registrar latencia y estado, sin claves ni datos sensibles. Verificar números y afirmaciones contra el contexto; las instrucciones al LLM no garantizan por sí solas respuestas correctas.

No es necesario entrenar un LLM. Para este MVP podemos mantener la recuperación simple. Si se amplía a documentos extensos, se puede añadir fragmentación, embeddings y búsqueda semántica.

## Evidencias a capturar cuando se implemente

- Pregunta sobre ventas existentes, contexto recuperado, respuesta generada y fuentes visibles.
- Pregunta fuera de los datos, con respuesta de información insuficiente.
- Prueba con una instrucción maliciosa incrustada en el contenido y comprobación de que no cambia las reglas del servicio.
- Solicitud sin clave rechazada y log del evento de consulta sin secretos.
- Pruebas de respuestas numéricas, fuente correcta y fallo del proveedor manejado sin inventar una respuesta.

Ejemplos: ¿Cuánto se vendió el día 10? ¿Qué día tuvo la mayor venta? ¿Hay datos de ventas del día 50?

Referencia técnica: https://docs.langchain.com/oss/python/deepagents/retrieval

Esta es una guía de implementación pendiente. No se ha conectado ningún proveedor ni se ha generado evidencia de RAG con LLM.
