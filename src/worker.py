"""Worker that validates a JSON request and runs the matrix algorithm."""

from __future__ import annotations

import argparse
import json
import sys

if __package__:
    from .input_module import InputDataError, PROTOCOL_VERSION, validate_request
    from .output_module import read_message, write_message
    from .processing_module import process
else:
    from input_module import InputDataError, PROTOCOL_VERSION, validate_request
    from output_module import read_message, write_message
    from processing_module import process


def handle(request: dict) -> dict:
    """Validate and process one request envelope."""
    normalized = validate_request(request)
    payload = normalized["payload"]
    return {
        "protocol_version": PROTOCOL_VERSION,
        "status": "ok",
        "data": process(payload["rows"], payload["columns"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Обработка запроса анализа матрицы")
    parser.add_argument("--request", required=True)
    parser.add_argument("--response", required=True)
    args = parser.parse_args()
    try:
        response = handle(read_message(args.request))
    except (OSError, json.JSONDecodeError, InputDataError, ValueError) as error:
        write_message(
            args.response,
            {"protocol_version": PROTOCOL_VERSION, "status": "error", "error": str(error)},
        )
        print(f"Ошибка worker: {error}", file=sys.stderr)
        return 1
    write_message(args.response, response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
