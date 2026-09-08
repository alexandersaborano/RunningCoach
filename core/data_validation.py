"""Validação leve dos documentos JSON persistidos pela aplicação."""

from collections.abc import Mapping
from typing import Any


class DataValidationError(ValueError):
    """Indica que um documento local não respeita o formato mínimo esperado."""


def _document(data: Any, name: str) -> dict:
    if not isinstance(data, Mapping):
        raise DataValidationError(f"{name} deve ser um objeto JSON.")
    return dict(data)


def validate_memory(data: Any) -> dict:
    result = _document(data, "Memória")
    for key in ("padroes_atleta", "regras_estilo", "historico_feedback"):
        if key in result and not isinstance(result[key], list):
            raise DataValidationError(f"{name_for(key)} deve ser uma lista.")
    return result


def validate_recovery(data: Any) -> dict:
    result = _document(data, "Recuperação")
    for day, value in result.items():
        if not isinstance(value, Mapping):
            raise DataValidationError(f"Recuperação de {day} deve ser um objeto.")
    return result


def validate_wellness_records(data: Any) -> list[dict]:
    """Validate the minimal shape required for imported wellness records."""
    if not isinstance(data, list):
        raise DataValidationError("Bem-estar deve ser uma lista.")
    result = []
    for record in data:
        if not isinstance(record, Mapping):
            raise DataValidationError("Cada registo de bem-estar deve ser um objeto.")
        item = dict(record)
        if not str(item.get("data", "")).strip():
            raise DataValidationError("Cada registo de bem-estar precisa de data.")
        result.append(item)
    return result


def validate_session(data: Any) -> dict:
    result = _document(data, "Sessão")
    if not str(result.get("atividade_id", "")).strip():
        raise DataValidationError("Sessão precisa de atividade_id.")
    return result


def validate_profile(data: Any) -> dict:
    return _document(data, "Perfil")


def validate_global_analysis(data: Any) -> dict:
    return _document(data, "Análise global")


def name_for(key: str) -> str:
    return {
        "padroes_atleta": "Padrões do atleta",
        "regras_estilo": "Regras de análise",
        "historico_feedback": "Histórico de feedback",
    }.get(key, key)
