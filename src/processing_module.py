"""Numerical processing for the matrix analysis project."""

from __future__ import annotations

import math


def count_positive_elements(rows: int, columns: int) -> int:
    """Count matrix elements sin(i + j / 2) greater than zero."""
    return sum(
        1
        for i in range(rows)
        for j in range(columns)
        if math.sin(i + j / 2) > 0
    )


def process(rows: int, columns: int) -> dict[str, int]:
    """Return a result record for the specified matrix dimensions."""
    return {
        "rows": rows,
        "columns": columns,
        "positive_count": count_positive_elements(rows, columns),
    }
