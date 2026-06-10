from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping
from urllib.parse import quote
from urllib.request import Request, urlopen


TSDECOMPOSE_BENCHMARK_DATASET = "Zipeng365/TSDecompose-Benchmark"
TSDECOMPOSE_BENCHMARK_CODE_PREFIX = "code/TSDecompose"
TSDECOMPOSE_BENCHMARK_REVISION = "main"


class BenchmarkSourceError(RuntimeError):
    """Raised when the external benchmark source cannot be resolved."""


class BenchmarkRunError(RuntimeError):
    """Raised when the external benchmark runner exits unsuccessfully."""

    def __init__(self, message: str, result: "BenchmarkRunResult") -> None:
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class BenchmarkRunResult:
    """Result metadata for an external TSDecompose benchmark run."""

    benchmark_dir: Path
    output_dir: Path
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    leaderboard_path: Path
    summary_dir: Path

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "benchmark_dir": str(self.benchmark_dir),
            "output_dir": str(self.output_dir),
            "command": list(self.command),
            "returncode": self.returncode,
            "leaderboard_path": str(self.leaderboard_path),
            "summary_dir": str(self.summary_dir),
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def default_benchmark_cache_dir() -> Path:
    """Return the cache directory used for external benchmark snapshots."""

    env_value = os.environ.get("DETIME_BENCHMARK_CACHE")
    if env_value:
        return Path(env_value).expanduser()
    return Path.home() / ".cache" / "detime" / "benchmarks"


def _repo_tree_url(dataset: str, revision: str) -> str:
    repo = quote(dataset, safe="/")
    rev = quote(revision, safe="")
    return f"https://huggingface.co/api/datasets/{repo}/tree/{rev}?recursive=true"


def _resolve_url(dataset: str, revision: str, path: str) -> str:
    repo = quote(dataset, safe="/")
    rev = quote(revision, safe="")
    resolved_path = quote(path, safe="/")
    return f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{resolved_path}"


def _request_headers() -> dict[str, str]:
    headers = {"User-Agent": "de-time-benchmark-runner"}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _read_json_url(url: str) -> Any:
    request = Request(url, headers=_request_headers())
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _download_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers=_request_headers())
    with urlopen(request, timeout=120) as response:
        target.write_bytes(response.read())


def _tree_entries(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        for key in ("siblings", "value", "files"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, Mapping)]
    raise BenchmarkSourceError("Unexpected Hugging Face tree API response.")


def _cache_subdir(dataset: str, revision: str, code_prefix: str) -> Path:
    safe_dataset = dataset.replace("/", "__")
    safe_revision = revision.replace("/", "_")
    safe_prefix = code_prefix.replace("/", "__")
    return Path(safe_dataset) / safe_revision / safe_prefix


def download_tsdecompose_benchmark(
    *,
    cache_dir: str | Path | None = None,
    dataset: str = TSDECOMPOSE_BENCHMARK_DATASET,
    revision: str = TSDECOMPOSE_BENCHMARK_REVISION,
    code_prefix: str = TSDECOMPOSE_BENCHMARK_CODE_PREFIX,
    force: bool = False,
) -> Path:
    """Download the TSDecompose benchmark source snapshot from Hugging Face.

    The DeTime package does not vendor the benchmark. This helper only caches
    the benchmark source bundle so users can run the published runner locally.
    """

    root = (
        Path(cache_dir).expanduser()
        if cache_dir is not None
        else default_benchmark_cache_dir()
    )
    benchmark_dir = root / _cache_subdir(dataset, revision, code_prefix)
    runner = benchmark_dir / "scripts" / "run_paper_benchmark.py"
    if runner.exists() and not force:
        return benchmark_dir

    payload = _read_json_url(_repo_tree_url(dataset, revision))
    prefix = code_prefix.rstrip("/") + "/"
    files = [
        str(item["path"])
        for item in _tree_entries(payload)
        if item.get("type") == "file" and str(item.get("path", "")).startswith(prefix)
    ]
    if not files:
        raise BenchmarkSourceError(
            f"No files found under '{code_prefix}' in Hugging Face dataset '{dataset}'."
        )

    for remote_path in files:
        relative = Path(remote_path).relative_to(code_prefix)
        _download_file(_resolve_url(dataset, revision, remote_path), benchmark_dir / relative)

    metadata = {
        "dataset": dataset,
        "revision": revision,
        "code_prefix": code_prefix,
        "file_count": len(files),
        "runner": "scripts/run_paper_benchmark.py",
    }
    (benchmark_dir / ".detime_benchmark_source.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not runner.exists():
        raise BenchmarkSourceError(f"Downloaded benchmark is missing runner: {runner}")
    return benchmark_dir


def ensure_tsdecompose_benchmark(
    benchmark_dir: str | Path | None = None,
    *,
    cache_dir: str | Path | None = None,
    dataset: str = TSDECOMPOSE_BENCHMARK_DATASET,
    revision: str = TSDECOMPOSE_BENCHMARK_REVISION,
    force_download: bool = False,
) -> Path:
    """Resolve a local benchmark directory or download the HF source snapshot."""

    if benchmark_dir is not None:
        resolved = Path(benchmark_dir).expanduser()
        runner = resolved / "scripts" / "run_paper_benchmark.py"
        if not runner.exists():
            raise BenchmarkSourceError(f"Cannot find benchmark runner at {runner}")
        return resolved
    return download_tsdecompose_benchmark(
        cache_dir=cache_dir,
        dataset=dataset,
        revision=revision,
        force=force_download,
    )


def run_tsdecompose_benchmark(
    *,
    benchmark_dir: str | Path | None = None,
    cache_dir: str | Path | None = None,
    dataset: str = TSDECOMPOSE_BENCHMARK_DATASET,
    revision: str = TSDECOMPOSE_BENCHMARK_REVISION,
    force_download: bool = False,
    smoke: bool = True,
    methods: str | None = None,
    seeds: str = "0",
    n_samples: int | None = None,
    length: int = 512,
    dt: float = 1.0,
    out_dir: str | Path | None = None,
    plots: bool = False,
    no_aggregate: bool = False,
    python_executable: str | Path | None = None,
    timeout: float | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
) -> BenchmarkRunResult:
    """Run the TSDecompose paper benchmark through its published runner.

    By default this executes the benchmark bundle's smoke run. Pass
    ``smoke=False`` for the full paper-core run.
    """

    source_dir = ensure_tsdecompose_benchmark(
        benchmark_dir,
        cache_dir=cache_dir,
        dataset=dataset,
        revision=revision,
        force_download=force_download,
    )
    runner = source_dir / "scripts" / "run_paper_benchmark.py"
    output_dir = (
        Path(out_dir).expanduser()
        if out_dir is not None
        else source_dir / "artifacts" / ("paper_core_smoke" if smoke else "paper_core_benchmark")
    )

    executable = str(python_executable or sys.executable)
    command: list[str] = [executable, str(runner)]
    if smoke:
        command.append("--smoke")
    if methods:
        command.extend(["--methods", methods])
    if seeds:
        command.extend(["--seeds", seeds])
    if n_samples is not None:
        command.extend(["--n-samples", str(n_samples)])
    command.extend(["--length", str(length), "--dt", str(dt), "--out", str(output_dir)])
    if plots:
        command.append("--plots")
    if no_aggregate:
        command.append("--no-aggregate")

    run_env = os.environ.copy()
    if env is not None:
        run_env.update(env)

    completed = subprocess.run(
        command,
        cwd=source_dir,
        env=run_env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    result = BenchmarkRunResult(
        benchmark_dir=source_dir,
        output_dir=output_dir,
        command=tuple(command),
        returncode=int(completed.returncode),
        stdout=completed.stdout,
        stderr=completed.stderr,
        leaderboard_path=output_dir / "leaderboard.csv",
        summary_dir=output_dir / "summary",
    )
    if check and not result.ok:
        message = (
            "TSDecompose benchmark runner failed with exit code "
            f"{result.returncode}. See the attached stdout/stderr on the result object."
        )
        raise BenchmarkRunError(message, result)
    return result


__all__ = [
    "BenchmarkRunError",
    "BenchmarkRunResult",
    "BenchmarkSourceError",
    "TSDECOMPOSE_BENCHMARK_DATASET",
    "download_tsdecompose_benchmark",
    "ensure_tsdecompose_benchmark",
    "run_tsdecompose_benchmark",
]
