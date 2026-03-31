from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union
import numpy as np
from pydantic import BaseModel, ConfigDict, Field

@dataclass
class DecompResult:
    """
    Unified container for time-series decomposition results.
    """
    trend: np.ndarray
    season: np.ndarray
    residual: np.ndarray
    components: Dict[str, np.ndarray] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure basic consistency if components are provided but trend/season are not explicitly set?
        # For now, we assume the creator of DecompResult populates everything correctly.
        pass

class DecompositionConfig(BaseModel):
    """
    Configuration for a decomposition method.
    """
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    return_components: Optional[List[str]] = None
    backend: Literal["auto", "native", "python", "gpu"] = "auto"
    speed_mode: Literal["exact", "fast"] = "exact"
    profile: bool = False
    device: Optional[str] = "cpu"
    n_jobs: int = 1
    seed: Optional[int] = 42
    channel_names: Optional[List[str]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
