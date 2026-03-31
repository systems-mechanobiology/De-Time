"""Utility helpers for decomposition methods."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def extract_primary_period(meta: Optional[Dict[str, Any]]) -> Optional[float]:
    """
    Inspect ``series['meta']`` for the first available primary period.
    """

    if not isinstance(meta, dict):
        return None
    cycles = meta.get("cycles")
    if not isinstance(cycles, list):
        return None

    for entry in cycles:
        if not isinstance(entry, dict):
            continue
        params = entry.get("params", {})
        if not isinstance(params, dict):
            continue
        period = params.get("period")
        if period is not None:
            try:
                return float(period)
            except (TypeError, ValueError):
                continue
        periods = params.get("periods")
        if periods:
            try:
                return float(periods[0])
            except (TypeError, ValueError, IndexError):
                continue
    return None


def extract_periods_from_meta(
    meta: Optional[Dict[str, Any]],
    fallback: Optional[float] = None,
) -> List[int]:
    """
    Extract a list of integer seasonal periods from metadata.
    """

    periods: List[int] = []
    if isinstance(meta, dict):
        cycles = meta.get("cycles")
        if isinstance(cycles, list):
            for entry in cycles:
                if not isinstance(entry, dict):
                    continue
                params = entry.get("params", {})
                if not isinstance(params, dict):
                    continue
                period = params.get("period")
                if period:
                    try:
                        p_int = int(round(float(period)))
                        if p_int >= 2:
                            periods.append(p_int)
                    except (TypeError, ValueError):
                        pass
                multi = params.get("periods")
                if multi:
                    for val in multi:
                        try:
                            p_int = int(round(float(val)))
                            if p_int >= 2:
                                periods.append(p_int)
                        except (TypeError, ValueError):
                            continue

    if not periods and fallback:
        try:
            p_int = int(round(float(fallback)))
            if p_int >= 2:
                periods.append(p_int)
        except (TypeError, ValueError):
            pass

    # remove duplicates while preserving order
    seen = set()
    unique_periods: List[int] = []
    for p in periods:
        if p not in seen:
            seen.add(p)
            unique_periods.append(p)
    return unique_periods
