from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path
import subprocess
import sys

import pytest

from detime.mcp import server


def _subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    root = Path(__file__).resolve().parents[2]
    src_root = str(root / "src")
    env["PYTHONPATH"] = src_root
    return env


def _write_message_bytes(payload: dict) -> bytes:
    body = json.dumps(payload).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body


def _read_message_bytes(stream) -> dict:
    content_length = None
    while True:
        line = stream.readline()
        if not line:
            raise RuntimeError("unexpected EOF")
        if line in (b"\r\n", b"\n"):
            break
        header = line.decode("utf-8").strip()
        if header.lower().startswith("content-length:"):
            content_length = int(header.split(":", 1)[1].strip())
    assert content_length is not None
    body = stream.read(content_length)
    return json.loads(body.decode("utf-8"))


def test_mcp_tool_calls_cover_core_surface() -> None:
    listed = server.call_tool("list_methods", {"include_optional_backends": False})
    names = {item["name"] for item in listed["structuredContent"]["methods"]}
    assert "SSA" in names
    assert "MVMD" not in names

    schema = server.call_tool("get_schema", {"name": "config"})
    assert schema["structuredContent"]["schema"]["title"] == "DecompositionConfig"

    registry_schema = server.call_tool("get_schema", {"name": "method-registry"})
    assert "contract_version" in registry_schema["structuredContent"]["schema"]["properties"]

    recommendation = server.call_tool(
        "recommend_method",
        {"length": 128, "channels": 2, "prefer": "accuracy", "top_k": 2},
    )
    assert recommendation["structuredContent"]["recommendations"][0]["method"] == "MSSA"

    result = server.call_tool(
        "run_decomposition",
        {
            "series": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
            "config": {"method": "MA_BASELINE", "params": {"window": 2}},
            "output_mode": "summary",
        },
    )
    assert result["structuredContent"]["mode"] == "summary"

    summarized = server.call_tool(
        "summarize_result",
        {
            "result": {
                "trend": [0.0, 0.5, 0.5],
                "season": [0.0, 0.5, -0.5],
                "residual": [0.0, 0.0, 0.0],
                "components": {},
                "meta": {"method": "TEST"},
            },
            "output_mode": "meta",
        },
    )
    assert summarized["structuredContent"]["mode"] == "meta"


def test_mcp_transport_helpers_roundtrip() -> None:
    payload = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    encoded = _write_message_bytes(payload)
    decoded = server._read_message(BytesIO(encoded))
    assert decoded == payload

    sink = BytesIO()
    server._write_message(sink, {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}})
    sink.seek(0)
    roundtrip = _read_message_bytes(sink)
    assert roundtrip["result"]["ok"] is True


def test_mcp_helpers_cover_errors_and_json_coercion(tmp_path) -> None:
    assert server._json_default(server.np.array([1.0, 2.0])) == [1.0, 2.0]
    assert server._json_default(server.np.int64(3)) == 3
    assert server._json_default(server.np.float64(1.5)) == 1.5
    with pytest.raises(TypeError):
        server._json_default(object())

    assert server._read_message(BytesIO(b"")) is None
    with pytest.raises(RuntimeError):
        server._read_message(BytesIO(b"\r\n"))
    assert server._read_message(BytesIO(b"Content-Length: 0\r\n\r\n")) is None

    success = server._success("1", {"ok": True})
    error = server._error("2", -1, "boom")
    assert success["result"]["ok"] is True
    assert error["error"]["message"] == "boom"

    csv_path = tmp_path / "series.csv"
    csv_path.write_text("value\n1\n2\n3\n4\n", encoding="utf-8")
    loaded = server.call_tool(
        "run_decomposition",
        {
            "series_path": str(csv_path),
            "col": "value",
            "config": {"method": "MA_BASELINE", "params": {"window": 2}},
            "output_mode": "meta",
        },
    )
    assert loaded["structuredContent"]["mode"] == "meta"

    with pytest.raises(ValueError, match="config.method"):
        server.call_tool("run_decomposition", {"config": {}})
    with pytest.raises(ValueError, match="summary or meta"):
        server.call_tool(
            "summarize_result",
            {
                "result": {
                    "trend": [0.0, 0.0],
                    "season": [0.0, 0.0],
                    "residual": [0.0, 0.0],
                    "components": {},
                    "meta": {"method": "TEST"},
                },
                "output_mode": "full",
            },
        )
    with pytest.raises(ValueError, match="Unknown MCP tool"):
        server.call_tool("does_not_exist")


def test_mcp_stdio_server_loop_paths(monkeypatch) -> None:
    class _BufferWrapper:
        def __init__(self, payload: bytes = b"") -> None:
            self.buffer = BytesIO(payload)

    payload = b"".join(
        [
            _write_message_bytes({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}),
            _write_message_bytes({"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}}),
            _write_message_bytes(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "does_not_exist", "arguments": {}},
                }
            ),
            _write_message_bytes({"jsonrpc": "2.0", "id": 3, "method": "bogus", "params": {}}),
        ]
    )
    fake_stdin = _BufferWrapper(payload)
    fake_stdout = _BufferWrapper()
    monkeypatch.setattr(server.sys, "stdin", fake_stdin)
    monkeypatch.setattr(server.sys, "stdout", fake_stdout)

    assert server.serve_stdio() == 0
    fake_stdout.buffer.seek(0)
    first = _read_message_bytes(fake_stdout.buffer)
    second = _read_message_bytes(fake_stdout.buffer)
    third = _read_message_bytes(fake_stdout.buffer)

    assert first["result"] == {}
    assert second["error"]["code"] == -32000
    assert third["error"]["code"] == -32601
    assert server.main() == 0


def test_mcp_server_subprocess_smoke() -> None:
    proc = subprocess.Popen(
        [sys.executable, "-m", "detime.mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_subprocess_env(),
    )
    try:
        assert proc.stdin is not None
        assert proc.stdout is not None

        proc.stdin.write(
            _write_message_bytes(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05"},
                }
            )
        )
        proc.stdin.flush()
        initialize = _read_message_bytes(proc.stdout)
        assert initialize["result"]["serverInfo"]["name"] == "detime-mcp"

        proc.stdin.write(
            _write_message_bytes({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        )
        proc.stdin.flush()
        tools = _read_message_bytes(proc.stdout)
        tool_names = {tool["name"] for tool in tools["result"]["tools"]}
        assert "run_decomposition" in tool_names
    finally:
        proc.terminate()
        proc.wait(timeout=10)
