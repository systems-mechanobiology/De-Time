from __future__ import annotations

import json
import sys
from typing import Any, Dict

import numpy as np

from ..core import DecompResult, DecompositionConfig
from ..io import read_series
from ..recommend import recommend_methods
from ..registry import MethodRegistry, decompose
from ..schemas import available_schemas, get_schema
from ..serialization import normalize_fields, serialize_result


def _json_default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "list_methods",
            "description": "List registered De-Time methods and their machine-readable metadata.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "include_optional_backends": {"type": "boolean", "default": True},
                },
            },
        },
        {
            "name": "get_schema",
            "description": "Return a packaged JSON schema for config, result, meta, or method-registry.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "enum": available_schemas(),
                    }
                },
                "required": ["name"],
            },
        },
        {
            "name": "recommend_method",
            "description": "Recommend decomposition methods from input size, channels, and speed/accuracy preferences.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "length": {"type": "integer", "minimum": 1},
                    "channels": {"type": "integer", "minimum": 1, "default": 1},
                    "prefer": {"type": "string", "enum": ["speed", "balanced", "accuracy"], "default": "balanced"},
                    "allow_optional_backends": {"type": "boolean", "default": False},
                    "require_native": {"type": "boolean", "default": False},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                },
                "required": ["length"],
            },
        },
        {
            "name": "run_decomposition",
            "description": "Run a decomposition and return a full, summary, or meta payload.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "series": {"type": "array"},
                    "series_path": {"type": "string"},
                    "col": {"type": "string"},
                    "cols": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                    "config": {"type": "object"},
                    "output_mode": {"type": "string", "enum": ["full", "summary", "meta"], "default": "summary"},
                    "fields": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                },
                "required": ["config"],
            },
        },
        {
            "name": "summarize_result",
            "description": "Summarize an existing result payload without rerunning decomposition.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "result": {"type": "object"},
                    "output_mode": {"type": "string", "enum": ["summary", "meta"], "default": "summary"},
                    "fields": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                },
                "required": ["result"],
            },
        },
    ]


def _structured_response(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, indent=2, sort_keys=True, default=_json_default),
            }
        ],
        "structuredContent": payload,
    }


def _load_series(arguments: Dict[str, Any], method: str) -> tuple[np.ndarray, dict[str, Any]]:
    if "series" in arguments and arguments["series"] is not None:
        arr = np.asarray(arguments["series"], dtype=float)
        info = {
            "channel_names": None,
            "multivariate": arr.ndim > 1,
        }
        return arr, info
    if "series_path" in arguments and arguments["series_path"]:
        return read_series(
            arguments["series_path"],
            col=arguments.get("col"),
            cols=arguments.get("cols"),
            method=method,
            return_info=True,
        )
    raise ValueError("Provide either 'series' or 'series_path'.")


def _result_from_payload(payload: Dict[str, Any]) -> DecompResult:
    components = {
        str(name): np.asarray(value, dtype=float)
        for name, value in dict(payload.get("components", {})).items()
    }
    return DecompResult(
        trend=np.asarray(payload["trend"], dtype=float),
        season=np.asarray(payload["season"], dtype=float),
        residual=np.asarray(payload["residual"], dtype=float),
        components=components,
        meta=dict(payload.get("meta", {})),
    )


def call_tool(name: str, arguments: Dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    if name == "list_methods":
        include_optional = bool(arguments.get("include_optional_backends", True))
        catalog = MethodRegistry.list_catalog()
        if not include_optional:
            catalog = [
                entry for entry in catalog
                if entry.get("dependency_tier") != "optional-backend"
            ]
        return _structured_response({"methods": catalog})

    if name == "get_schema":
        schema_name = arguments["name"]
        return _structured_response({"name": schema_name, "schema": get_schema(schema_name)})

    if name == "recommend_method":
        response = recommend_methods(arguments)
        return _structured_response(response.model_dump(mode="json"))

    if name == "run_decomposition":
        config_data = dict(arguments.get("config", {}))
        if "method" not in config_data:
            raise ValueError("'config.method' is required.")
        series, info = _load_series(arguments, config_data["method"])
        if info.get("channel_names") and not config_data.get("channel_names"):
            config_data["channel_names"] = info["channel_names"]
        config = DecompositionConfig.model_validate(config_data)
        result = decompose(series, config)
        payload = serialize_result(
            result,
            mode=arguments.get("output_mode", "summary"),
            fields=normalize_fields(arguments.get("fields")),
        )
        return _structured_response(payload)

    if name == "summarize_result":
        result = _result_from_payload(dict(arguments["result"]))
        output_mode = arguments.get("output_mode", "summary")
        if output_mode == "full":
            raise ValueError("summarize_result only supports summary or meta output.")
        payload = serialize_result(
            result,
            mode=output_mode,
            fields=normalize_fields(arguments.get("fields")),
        )
        return _structured_response(payload)

    raise ValueError(f"Unknown MCP tool: {name}")


def _read_message(stdin: Any) -> dict[str, Any] | None:
    content_length: int | None = None
    while True:
        line = stdin.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        header = line.decode("utf-8").strip()
        if header.lower().startswith("content-length:"):
            content_length = int(header.split(":", 1)[1].strip())

    if content_length is None:
        raise RuntimeError("Missing Content-Length header.")
    body = stdin.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8"))


def _write_message(stdout: Any, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, default=_json_default).encode("utf-8")
    stdout.write(f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8"))
    stdout.write(body)
    stdout.flush()


def _success(message_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {"code": code, "message": message},
    }


def serve_stdio() -> int:
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    while True:
        message = _read_message(stdin)
        if message is None:
            return 0

        message_id = message.get("id")
        method = message.get("method")
        params = dict(message.get("params", {}))

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "detime-mcp", "version": "0.1.0"},
                    "capabilities": {"tools": {}},
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": _tool_definitions()}
            elif method == "tools/call":
                result = call_tool(params["name"], params.get("arguments"))
            elif method == "notifications/initialized":
                continue
            else:
                _write_message(stdout, _error(message_id, -32601, f"Method not found: {method}"))
                continue
            _write_message(stdout, _success(message_id, result))
        except Exception as exc:  # pragma: no cover - transport failures are integration-level
            _write_message(stdout, _error(message_id, -32000, str(exc)))


def main() -> int:
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
