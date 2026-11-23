"""Coordinate input validation, JSON file exchange, worker and output."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__:
    from .input_module import InputDataError, PROTOCOL_VERSION, validate_request
    from .output_module import format_result, read_message, write_message
else:
    from input_module import InputDataError, PROTOCOL_VERSION, validate_request
    from output_module import format_result, read_message, write_message


class IntegrationError(RuntimeError):
    """Raised when a worker, protocol or file exchange fails."""


def run(request: dict[str, Any], timeout: float = 3.0) -> dict[str, Any]:
    """Run the worker through temporary JSON request and response files."""
    normalized = validate_request(request)
    with tempfile.TemporaryDirectory(prefix="matrix-integration-") as directory:
        request_path = Path(directory) / "request.json"
        response_path = Path(directory) / "response.json"
        write_message(request_path, normalized)
        worker_path = Path(__file__).with_name("worker.py")
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(worker_path),
                    "--request",
                    str(request_path),
                    "--response",
                    str(response_path),
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise IntegrationError(f"Истёк таймаут worker: {timeout} с") from error
        except OSError as error:
            raise IntegrationError(f"Модуль обработки недоступен: {error}") from error

        if not response_path.exists():
            raise IntegrationError(f"Worker не создал файл ответа (код {completed.returncode})")
        try:
            response = read_message(response_path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            raise IntegrationError(f"Ответ worker повреждён: {error}") from error
        version = response.get("protocol_version")
        if type(version) is not int or version != PROTOCOL_VERSION:
            raise IntegrationError(
                "Версия протокола ответа не совпадает с версией клиента"
            )
        if response.get("status") != "ok":
            raise IntegrationError(response.get("error", "Worker вернул неизвестную ошибку"))
        _validate_result(response.get("data"), normalized["payload"])
        return response


def _validate_result(data: Any, dimensions: dict[str, int]) -> None:
    """Check that a successful reply matches the requested matrix."""
    if not isinstance(data, dict):
        raise IntegrationError("Неверный формат данных ответа")
    for field, expected in dimensions.items():
        value = data.get(field)
        if type(value) is not int or value != expected:
            raise IntegrationError(f"Несоответствие данных ответа: {field}")
    count = data.get("positive_count")
    if type(count) is not int or not 0 <= count <= dimensions["rows"] * dimensions["columns"]:
        raise IntegrationError("Некорректный счётчик в составе данных ответа")


def run_file(input_path: str | Path, output_path: str | Path, timeout: float = 3.0) -> dict[str, Any]:
    """Read a request JSON file, integrate modules and save the response."""
    try:
        response = run(read_message(input_path), timeout=timeout)
    except (OSError, json.JSONDecodeError, ValueError, InputDataError) as error:
        raise IntegrationError(f"Не удалось обработать входной файл: {error}") from error
    write_message(output_path, response)
    return response


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Интеграция модулей анализа матрицы")
    parser.add_argument("input", help="путь к JSON-запросу")
    parser.add_argument("--output", default="response.json", help="путь к JSON-ответу")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()
    try:
        response = run_file(args.input, args.output, timeout=args.timeout)
    except (OSError, IntegrationError) as error:
        print(f"Ошибка интеграции: {error}", file=sys.stderr)
        return 1
    print(format_result(response))
    print(f"JSON-ответ сохранён: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
