"""Prueba manual asíncrona del pipeline."""

import asyncio

from chain import process_text

SAMPLE_TEXT = """
El servicio de pagos en Python usa FastAPI y PostgreSQL. Tras un despliegue,
la base de datos empezó a rechazar conexiones y el endpoint /checkout devolvió
errores 500 para clientes activos. Se requiere atención inmediata.
"""


async def main() -> None:
    result = await process_text(SAMPLE_TEXT)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
