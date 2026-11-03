"""Validation for the versioned JSON request used by the matrix worker."""

from __future__ import annotations

from typing import Any


PROTOCOL_VERSION = 1


class InputDataError(ValueError):
    """Raised when a request does not satisfy the input contract."""


def validate_request(request: Any) -> dict[str, Any]:
    """Validate an envelope and return a normalized request."""
    if not isinstance(request, dict):
        raise InputDataError("Запрос должен быть JSON-объектом")
    version = request.get("protocol_version")
    if not isinstance(version, int) or isinstance(version, bool) or version != PROTOCOL_VERSION:
        raise InputDataError("Несовместимая версия протокола")
    payload = request.get("payload")
    if not isinstance(payload, dict):
        raise InputDataError("Поле payload должно быть JSON-объектом")

    rows = payload.get("rows")
    columns = payload.get("columns")
    for name, value in (("rows", rows), ("columns", columns)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise InputDataError(f"Размер матрицы {name} должен быть целым числом")
        if value <= 0:
            raise InputDataError(f"Размер матрицы {name} должен быть положительным")

    return {
        "protocol_version": PROTOCOL_VERSION,
        "payload": {"rows": rows, "columns": columns},
    }
