"""JSON file operations and presentation of the matrix analysis result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_message(path: str | Path) -> dict[str, Any]:
    """Read a UTF-8 JSON object from a file."""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Содержимое JSON-файла должно быть объектом")
    return value


def write_message(path: str | Path, message: dict[str, Any]) -> None:
    """Write a JSON object in a stable, readable UTF-8 representation."""
    Path(path).write_text(
        json.dumps(message, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def format_result(response: dict[str, Any]) -> str:
    """Format an accepted worker response for a console user."""
    data = response["data"]
    return (
        f"Размер матрицы: {data['rows']} x {data['columns']}\n"
        f"Положительных элементов: {data['positive_count']}"
    )
