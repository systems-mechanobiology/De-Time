# Import all methods to trigger @MethodRegistry.register decorators
from . import stl
from . import ssa
from . import ma_baseline
from . import wavelet
from . import emd
from . import ceemdan
from . import vmd
from . import std
from . import mssa
from . import mvmd
from . import memd
from . import std_multi
from . import gabor_cluster
from . import dr_ts_reg
from . import dr_ts_ae
from . import sl_lib

# Re-export for convenience
from .stl import stl_decompose, mstl_decompose, robuststl_decompose
from .ssa import ssa_decompose
from .ma_baseline import ma_decompose
from .wavelet import wavelet_decompose
from .emd import emd_decompose
from .ceemdan import ceemdan_decompose
from .vmd import vmd_decompose
from .std import std_decompose, stdr_decompose
from .mssa import mssa_decompose
from .mvmd import mvmd_decompose
from .memd import memd_decompose
from .gabor_cluster import gabor_cluster_decompose
from .dr_ts_reg import dr_ts_reg_wrapper
from .dr_ts_ae import dr_ts_ae_wrapper
from .sl_lib import sl_lib_wrapper

__all__ = [
    "stl_decompose", "mstl_decompose", "robuststl_decompose",
    "ssa_decompose",
    "ma_decompose",
    "wavelet_decompose",
    "emd_decompose",
    "ceemdan_decompose",
    "vmd_decompose",
    "std_decompose",
    "stdr_decompose",
    "mssa_decompose",
    "mvmd_decompose",
    "memd_decompose",
    "gabor_cluster_decompose",
    "dr_ts_reg_wrapper",
    "dr_ts_ae_wrapper",
    "sl_lib_wrapper",
]
