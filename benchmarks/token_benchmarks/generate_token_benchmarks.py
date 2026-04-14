from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tiktoken

from detime import DecompResult, __version__
from detime.serialization import serialize_result


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "assets" / "generated" / "evidence"
ENCODING_NAME = "cl100k_base"


def _sample_result(length: int, channels: int) -> DecompResult:
    t = np.arange(length, dtype=float)
    trend = 0.01 * t
    season = np.sin(2.0 * np.pi * t / max(length // 8, 8))
    residual = 0.1 * np.cos(2.0 * np.pi * t / max(length // 12, 6))

    if channels == 1:
        components = {
            "detail": 0.5 * season,
            "modes": np.column_stack([trend, season]),
        }
        return DecompResult(
            trend=trend,
            season=season,
            residual=residual,
            components=components,
            meta={"method": "SSA", "result_layout": "univariate", "n_channels": 1},
        )

    trend_2d = np.column_stack([trend + 0.01 * idx for idx in range(channels)])
    season_2d = np.column_stack([season + 0.05 * idx for idx in range(channels)])
    residual_2d = np.column_stack([residual for _ in range(channels)])
    modes = np.stack([trend_2d, season_2d, residual_2d], axis=0)
    return DecompResult(
        trend=trend_2d,
        season=season_2d,
        residual=residual_2d,
        components={"modes": modes, "channelwise_detail": season_2d},
        meta={
            "method": "MSSA",
            "result_layout": "multivariate",
            "n_channels": channels,
            "channel_names": [f"x{idx}" for idx in range(channels)],
        },
    )


def _count_tokens(encoder: tiktoken.Encoding, payload: dict[str, object]) -> int:
    text = json.dumps(payload, sort_keys=True)
    return len(encoder.encode(text))


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    encoder = tiktoken.get_encoding(ENCODING_NAME)

    scenarios = [
        ("univariate-short", 64, 1),
        ("univariate-medium", 256, 1),
        ("univariate-long", 1024, 1),
        ("multivariate-short", 64, 3),
        ("multivariate-medium", 256, 3),
        ("multivariate-long", 1024, 3),
    ]

    rows: list[dict[str, object]] = []
    for scenario, length, channels in scenarios:
        result = _sample_result(length, channels)
        full_tokens: int | None = None
        for mode in ("full", "summary", "meta"):
            payload = serialize_result(result, mode=mode)
            token_count = _count_tokens(encoder, payload)
            if mode == "full":
                full_tokens = token_count
            rows.append(
                {
                    "scenario": scenario,
                    "length": length,
                    "channels": channels,
                    "mode": mode,
                    "encoding": ENCODING_NAME,
                    "tokens": token_count,
                    "relative_to_full": round(token_count / max(full_tokens or token_count, 1), 4),
                }
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_version": __version__,
        "encoding": ENCODING_NAME,
        "rows": rows,
    }

    json_path = OUTPUT_DIR / "token_benchmarks.json"
    csv_path = OUTPUT_DIR / "token_benchmarks.csv"
    figure_path = OUTPUT_DIR / "token_benchmarks.svg"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    labels = [row["scenario"] for row in rows if row["mode"] == "full"]
    full_vals = [row["tokens"] for row in rows if row["mode"] == "full"]
    summary_vals = [row["tokens"] for row in rows if row["mode"] == "summary"]
    meta_vals = [row["tokens"] for row in rows if row["mode"] == "meta"]
    positions = np.arange(len(labels))
    width = 0.25

    plt.figure(figsize=(12, 5))
    plt.bar(positions - width, full_vals, width=width, label="full")
    plt.bar(positions, summary_vals, width=width, label="summary")
    plt.bar(positions + width, meta_vals, width=width, label="meta")
    plt.xticks(positions, labels, rotation=20, ha="right")
    plt.ylabel(f"Approximate tokens ({ENCODING_NAME})")
    plt.title("De-Time payload token budget by scenario and serialization mode")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_path)
    plt.close()

    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
