"""Hot Trend Lab utilities for real-data De-Time tutorials."""

from .data import HotTrendDataError
from .decomposition import decompose_table, component_summary, residual_event_table

__all__ = [
    "HotTrendDataError",
    "decompose_table",
    "component_summary",
    "residual_event_table",
]
