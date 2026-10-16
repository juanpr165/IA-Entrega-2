# Entregable 2 — Pipeline de procesamiento validado

Pipeline de extracción de entidades técnicas construido con LangChain, LCEL y Pydantic. Recibe un texto libre (por ejemplo, un log o una descripción de arquitectura) y retorna un objeto validado.

## Qué demuestra

- **Contrato Pydantic:** `EntidadesTecnicas` exige tecnologías no vacías, criticidad limitada a `baja`, `media` o `alta`, y un resumen técnico útil.
- **Prompt modular:** `ChatPromptTemplate` recibe el texto y las instrucciones de formato sin f-strings dentro de la cadena.
- **LCEL y salida estructurada:** `PROMPT | model.with_structured_output(EntidadesTecnicas) | validador`.
- **Resiliencia:** `.with_retry(stop_after_attempt=2)` se activa ante JSON/objeto inválido, validación fallida o respuesta truncada (`finish_reason`).
- **Asincronía y observabilidad:** `process_text()` usa `await chain.ainvoke(...)` y registra inicio, éxito y errores.

## Requisitos

Windows 11, Python 3.10 o superior, VS Code y una clave de Groq u OpenAI. 



## Ejemplo de salida

```json
{
  "tecnologias": ["Python", "FastAPI", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "El servicio de pagos falla por rechazos de conexión en PostgreSQL y afecta el checkout."
}
```



## Estructura

```text
schemas.py     # contrato Pydantic
chain.py       # prompt, LCEL, reintentos, .ainvoke y logging
test_async.py  # prueba asíncrona manual
```
