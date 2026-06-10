# Import all methods to trigger @MethodRegistry.register decorators.
from . import ceemdan
from . import emd
from . import gabor_cluster
from . import ma_baseline
from . import memd
from . import mssa
from . import mvmd
from . import neural_blocks
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
from .neural_blocks.forecasting_blocks import (
    autoformer_block_decompose,
    dlinear_block_decompose,
    moving_average_decomposition_block,
)
from .neural_blocks.learned_priors import nbeats_interpretable_decompose
from .neural_blocks.leddam_block import leddam_block_decompose
from .neural_blocks.neural_block_portfolio import (
    amd_block_decompose,
    delelstm_block_decompose,
    freqmoe_block_decompose,
    inparformer_block_decompose,
    parsimony_block_decompose,
    stmtm_block_decompose,
    timekan_block_decompose,
    times2d_block_decompose,
    waveform_block_decompose,
    waveletmixer_block_decompose,
)
from .neural_blocks.xpatch_block import xpatch_block_decompose
from .ssa import ssa_decompose
from .std import std_decompose, stdr_decompose
from .stl import mstl_decompose, robuststl_decompose, stl_decompose
from .vmd import vmd_decompose
from .wavelet import wavelet_decompose

__all__ = [
    "ceemdan_decompose",
    "amd_block_decompose",
    "autoformer_block_decompose",
    "delelstm_block_decompose",
    "emd_decompose",
    "dlinear_block_decompose",
    "freqmoe_block_decompose",
    "gabor_cluster_decompose",
    "inparformer_block_decompose",
    "leddam_block_decompose",
    "ma_decompose",
    "memd_decompose",
    "moving_average_decomposition_block",
    "mssa_decompose",
    "mstl_decompose",
    "mvmd_decompose",
    "nbeats_interpretable_decompose",
    "parsimony_block_decompose",
    "robuststl_decompose",
    "ssa_decompose",
    "std_decompose",
    "stdr_decompose",
    "stmtm_block_decompose",
    "stl_decompose",
    "timekan_block_decompose",
    "times2d_block_decompose",
    "vmd_decompose",
    "waveform_block_decompose",
    "wavelet_decompose",
    "waveletmixer_block_decompose",
    "xpatch_block_decompose",
]
