"""Contrato de datos del pipeline de extracción técnica."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class NivelDeCriticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class EntidadesTecnicas(BaseModel):
    """Resultado válido que el LLM debe devolver para cada texto de entrada."""

    tecnologias: list[str] = Field(
        min_length=1,
        description="Tecnologías, protocolos, servicios o herramientas nombradas en el texto.",
    )
    nivel_de_criticidad: NivelDeCriticidad = Field(
        description="Impacto técnico inferido: baja, media o alta."
    )
    resumen_tecnico: str = Field(
        min_length=20,
        description="Resumen técnico claro de al menos 20 caracteres.",
    )

    @field_validator("tecnologias")
    @classmethod
    def tecnologias_no_vacias(cls, tecnologias: list[str]) -> list[str]:
        normalizadas = [tecnologia.strip() for tecnologia in tecnologias if tecnologia.strip()]
        if not normalizadas:
            raise ValueError("tecnologias debe contener al menos un elemento no vacío")
        return normalizadas

    @field_validator("resumen_tecnico")
    @classmethod
    def resumen_no_vacio(cls, resumen: str) -> str:
        resumen = resumen.strip()
        if len(resumen) < 20:
            raise ValueError("resumen_tecnico debe tener al menos 20 caracteres")
        return resumen
