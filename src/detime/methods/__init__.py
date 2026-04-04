# Import all methods to trigger @MethodRegistry.register decorators.
from . import ceemdan
from . import emd
from . import gabor_cluster
from . import ma_baseline
from . import memd
from . import mssa
from . import mvmd
from . import ssa
from . import std
from . import std_multi
from . import stl
from . import vmd
from . import wavelet

# Re-export for convenience.
from .ceemdan import ceemdan_decompose
from .emd import emd_decompose
from .gabor_cluster import gabor_cluster_decompose
from .ma_baseline import ma_decompose
from .memd import memd_decompose
from .mssa import mssa_decompose
from .mvmd import mvmd_decompose
from .ssa import ssa_decompose
from .std import std_decompose, stdr_decompose
from .stl import mstl_decompose, robuststl_decompose, stl_decompose
from .vmd import vmd_decompose
from .wavelet import wavelet_decompose

__all__ = [
    "ceemdan_decompose",
    "emd_decompose",
    "gabor_cluster_decompose",
    "ma_decompose",
    "memd_decompose",
    "mssa_decompose",
    "mstl_decompose",
    "mvmd_decompose",
    "robuststl_decompose",
    "ssa_decompose",
    "std_decompose",
    "stdr_decompose",
    "stl_decompose",
    "vmd_decompose",
    "wavelet_decompose",
]
