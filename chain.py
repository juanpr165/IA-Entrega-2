"""Cadena LCEL resiliente para extraer entidades técnicas con un LLM."""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from schemas import EntidadesTecnicas

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

FORMAT_INSTRUCTIONS = """Extrae únicamente información respaldada por el texto.
Incluye al menos una tecnología, usa criticidad baja/media/alta y redacta un resumen
técnico de 20 caracteres o más. No inventes datos ni agregues texto fuera del objeto."""

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un analista de operaciones de software. {format_instructions}",
        ),
        ("human", "Texto sin procesar:\n{input_text}"),
    ]
)


class IncompleteOutputError(RuntimeError):
    """La respuesta se truncó o no pudo convertirse al contrato Pydantic."""


def _build_model() -> Any:
    """Crea el cliente según LLM_PROVIDER, sin leer ni mostrar secretos."""
    provider = os.getenv("LLM_PROVIDER", "").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            temperature=0,
        )

    raise ValueError(
        "LLM_PROVIDER debe ser 'openai' o 'groq'."
    )


def _validate_structured_response(response: dict[str, Any]) -> EntidadesTecnicas:
    """Falla para activar el reintento si la salida fue truncada o inválida."""
    raw = response.get("raw")
    metadata = getattr(raw, "response_metadata", {}) or {}
    finish_reason = metadata.get("finish_reason")
    if finish_reason in {"length", "max_tokens"}:
        raise IncompleteOutputError(f"Respuesta incompleta del modelo: {finish_reason}")

    parsing_error = response.get("parsing_error")
    parsed = response.get("parsed")
    if parsing_error or parsed is None:
        raise IncompleteOutputError(
            f"El modelo no devolvió un objeto válido: {parsing_error or 'objeto ausente'}"
        )

    # La validación se vuelve a aplicar como evidencia explícita del contrato Pydantic.
    return EntidadesTecnicas.model_validate(parsed)


def build_chain() -> Any:
    """Compone Prompt + salida estructurada + validador con LCEL y dos intentos."""
    model = _build_model()
    structured_model = model.with_structured_output(EntidadesTecnicas, include_raw=True)

    return (
        PROMPT.partial(format_instructions=FORMAT_INSTRUCTIONS)
        | structured_model
        | RunnableLambda(_validate_structured_response)
    ).with_retry(stop_after_attempt=2, retry_if_exception_type=(Exception,))


async def process_text(input_text: str) -> EntidadesTecnicas:
    """Procesa texto de manera asíncrona y devuelve sólo un objeto validado."""
    if not input_text or not input_text.strip():
        raise ValueError("input_text no puede estar vacío")

    logger.info("Iniciando extracción técnica (%s caracteres)", len(input_text))
    try:
        result = await build_chain().ainvoke({"input_text": input_text})
        logger.info("Extracción completada con %s tecnologías", len(result.tecnologias))
        return result
    except Exception:
        logger.exception("Falló la extracción tras aplicar la estrategia de reintento")
        raise
