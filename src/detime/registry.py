from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Literal

import numpy as np

from .backends import inject_runtime_params, runtime_options_from_config
from .core import DecompResult, DecompositionConfig

InputMode = Literal["univariate", "multivariate", "channelwise"]
MethodSignature = Callable[[np.ndarray, Dict[str, Any]], DecompResult]

REMOVED_METHOD_HINTS: Dict[str, str] = {
    "DR_TS_REG": (
        "DR_TS_REG moved to the separate 'de-time-bench' repository. "
        "Install that package and use 'detime_bench' instead."
    ),
    "DR_TS_AE": (
        "DR_TS_AE moved to the separate 'de-time-bench' repository. "
        "Install that package and use 'detime_bench' instead."
    ),
    "SL_LIB": (
        "SL_LIB moved to the separate 'de-time-bench' repository. "
        "Install that package and use 'detime_bench' instead."
    ),
}

METHOD_METADATA: Dict[str, Dict[str, Any]] = {
    "SSA": {
        "family": "SSA",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": True,
        "min_length": 24,
        "summary": "Singular spectrum analysis for structured univariate decomposition.",
        "recommended_for": [
            "accuracy-first univariate decomposition",
            "component recovery",
            "season-trend separation with structured signals",
        ],
        "typical_failure_modes": [
            "window too small for the dominant period",
            "rank or grouping chosen inconsistently with the signal structure",
        ],
    },
    "STD": {
        "family": "SeasonalTrend",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "channelwise",
        "native_backed": True,
        "min_length": 8,
        "summary": "Fast seasonal-trend decomposition with dispersion-aware diagnostics.",
        "recommended_for": [
            "fast seasonal-trend baselines",
            "channelwise multivariate workflows",
            "native-backed production paths",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "shared seasonal structure changing too quickly across cycles",
        ],
    },
    "STDR": {
        "family": "SeasonalTrend",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "channelwise",
        "native_backed": True,
        "min_length": 8,
        "summary": "Robust seasonal-trend decomposition for noisier periodic signals.",
        "recommended_for": [
            "robust seasonal-trend decomposition",
            "channelwise multivariate workflows",
            "native-backed seasonal structure recovery",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "heavy structural breaks that violate shared seasonal assumptions",
        ],
    },
    "MSSA": {
        "family": "SSA",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "shared-model",
        "native_backed": True,
        "min_length": 24,
        "summary": "Multivariate SSA for shared-structure decomposition across channels.",
        "recommended_for": [
            "multivariate component recovery",
            "shared seasonal structure across channels",
            "accuracy-first multivariate workflows",
        ],
        "typical_failure_modes": [
            "too few channels for MSSA",
            "window or rank too small for the shared structure",
        ],
    },
    "STL": {
        "family": "SeasonalTrend",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 12,
        "summary": "Classical STL wrapped into the DeTime workflow contract.",
        "recommended_for": [
            "classical seasonal-trend baselines",
            "statsmodels-compatible workflows",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "multiple seasonalities outside STL's basic assumptions",
        ],
    },
    "MSTL": {
        "family": "SeasonalTrend",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 24,
        "summary": "Statsmodels MSTL wrapped into the DeTime workflow surface.",
        "recommended_for": [
            "multiple seasonalities in univariate data",
            "classical decomposition baselines",
        ],
        "typical_failure_modes": [
            "seasonal periods not provided",
            "nonstationary structure beyond classical assumptions",
        ],
    },
    "ROBUST_STL": {
        "family": "SeasonalTrend",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 12,
        "summary": "Robust STL-style decomposition wrapped for reproducible workflows.",
        "recommended_for": [
            "outlier-prone seasonal-trend baselines",
            "classical robust decomposition",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "multiple strong seasonalities beyond the model assumptions",
        ],
    },
    "EMD": {
        "family": "EMD",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "Empirical mode decomposition under the DeTime result contract.",
        "recommended_for": [
            "adaptive decomposition of nonlinear signals",
            "IMF-oriented exploratory analysis",
        ],
        "typical_failure_modes": [
            "mode mixing",
            "short or heavily noisy series that destabilize IMF extraction",
        ],
    },
    "CEEMDAN": {
        "family": "EMD",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 24,
        "summary": "Noise-assisted EMD variant for more stable IMF extraction.",
        "recommended_for": [
            "noise-assisted EMD workflows",
            "adaptive decomposition with improved IMF stability",
        ],
        "typical_failure_modes": [
            "high runtime on long series",
            "parameter choices that over-fragment signal modes",
        ],
    },
    "VMD": {
        "family": "Variational",
        "maturity": "stable",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": True,
        "min_length": 24,
        "summary": "Variational mode decomposition integrated into the common workflow layer.",
        "recommended_for": [
            "band-limited mode separation",
            "frequency-structured univariate workflows",
        ],
        "typical_failure_modes": [
            "number of modes chosen poorly",
            "penalty parameters not aligned with the signal bandwidth",
        ],
    },
    "WAVELET": {
        "family": "Wavelet",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "Wavelet-based decomposition exposed through the common output contract.",
        "recommended_for": [
            "multiscale exploratory analysis",
            "wavelet-style trend and detail separation",
        ],
        "typical_failure_modes": [
            "wavelet family mismatch",
            "boundary artifacts on short series",
        ],
    },
    "MA_BASELINE": {
        "family": "Baseline",
        "maturity": "stable",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": True,
        "min_length": 4,
        "summary": "Simple moving-average baseline for smoke tests and lightweight workflows.",
        "recommended_for": [
            "sanity checks",
            "lightweight baseline decomposition",
        ],
        "typical_failure_modes": [
            "window too large for the series length",
            "oversmoothing when fine seasonal structure matters",
        ],
    },
    "GABOR_CLUSTER": {
        "family": "Experimental",
        "maturity": "experimental",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": True,
        "min_length": 16,
        "summary": "Experimental clustering-based decomposition path.",
        "recommended_for": [
            "research prototypes",
            "exploratory clustering-style decomposition",
        ],
        "typical_failure_modes": [
            "unstable clustering assignments",
            "parameter sensitivity on short series",
        ],
    },
    "MVMD": {
        "family": "Variational",
        "maturity": "optional-backend",
        "implementation": "optional-backend",
        "dependency_tier": "optional-backend",
        "multivariate_support": "shared-model",
        "native_backed": False,
        "min_length": 24,
        "summary": "Optional multivariate VMD backend for shared frequency structure.",
        "recommended_for": [
            "multivariate variational decomposition",
            "shared frequency structure across channels",
        ],
        "typical_failure_modes": [
            "optional backend unavailable",
            "mode count or penalties not tuned to the signal family",
        ],
    },
    "MEMD": {
        "family": "EMD",
        "maturity": "optional-backend",
        "implementation": "optional-backend",
        "dependency_tier": "optional-backend",
        "multivariate_support": "shared-model",
        "native_backed": False,
        "min_length": 24,
        "summary": "Optional multivariate EMD backend for shared oscillatory structure.",
        "recommended_for": [
            "multivariate adaptive decomposition",
            "shared oscillatory modes across channels",
        ],
        "typical_failure_modes": [
            "optional backend unavailable",
            "high runtime or unstable mode alignment across channels",
        ],
    },
}

_NEURAL_BLOCK_METHOD_METADATA: Dict[str, Dict[str, Any]] = {
    "AUTOFORMER_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "Standalone moving-average decomposition head extracted from the Autoformer architecture.",
        "recommended_for": [
            "neural-architecture-inspired seasonal-trend baselines",
            "Autoformer-style decomposition ablations",
        ],
        "typical_failure_modes": [
            "moving-average window misaligned with the dominant period",
            "oversmoothing sharp changes or regime shifts",
        ],
    },
    "DLINEAR_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "Standalone moving-average decomposition head extracted from DLinear-style forecasting blocks.",
        "recommended_for": [
            "DLinear-style trend/season split baselines",
            "fast neural decomposition head comparisons",
        ],
        "typical_failure_modes": [
            "moving-average window too short or too long",
            "weak separation when trend and seasonal energy overlap",
        ],
    },
    "MOVING_AVERAGE_DECOMPOSITION_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "Generic neural forecasting moving-average decomposition block exposed as a DeTime method.",
        "recommended_for": [
            "generic decomposition-block smoke tests",
            "fast moving-average neural head baselines",
        ],
        "typical_failure_modes": [
            "oversmoothing short local events",
            "period hints that do not match the actual seasonal scale",
        ],
    },
    "NBEATS_INTERPRETABLE": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "Torch-backed interpretable N-BEATS trend and seasonality stacks used as a learned decomposition prior.",
        "recommended_for": [
            "learned-basis decomposition experiments",
            "N-BEATS interpretable-stack ablations",
        ],
        "typical_failure_modes": [
            "torch unavailable in the runtime environment",
            "slow fitting or unstable small-sample optimization",
        ],
        "optional_dependencies": ["torch"],
    },
    "XPATCH_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "xPatch-inspired exponential smoothing head for standalone trend and local-season decomposition.",
        "recommended_for": [
            "exponential smoothing neural head comparisons",
            "fast local seasonal-trend decomposition",
        ],
        "typical_failure_modes": [
            "alpha or beta choices that lag rapid trend shifts",
            "season smoothing that removes high-frequency structure",
        ],
    },
    "LEDDAM_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "LEDDAM LD smoothing block exposed as a Gaussian-kernel decomposition operator.",
        "recommended_for": [
            "LEDDAM-style decomposition ablations",
            "kernel smoothing neural head comparisons",
        ],
        "typical_failure_modes": [
            "kernel size too wide for short series",
            "sigma choices that blur local changes",
        ],
    },
    "INPARFORMER_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "InParformer-inspired moving-average trend plus periodic-template seasonal decomposition head.",
        "recommended_for": [
            "periodic-template neural decomposition baselines",
            "prefix/full-scope ablation experiments",
        ],
        "typical_failure_modes": [
            "primary period mis-specified",
            "template fit scope inconsistent with the intended forecasting protocol",
        ],
    },
    "DELELSTM_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "DeLELSTM-inspired Holt trend plus periodic-template seasonal decomposition head.",
        "recommended_for": [
            "LSTM decomposition-head ablations",
            "signals with smooth level and slope structure",
        ],
        "typical_failure_modes": [
            "alpha or beta values that underfit sharp changes",
            "periodic template mismatch on drifting seasonality",
        ],
    },
    "AMD_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "AMD-inspired multiscale smoothing head with periodic-template seasonal reconstruction.",
        "recommended_for": [
            "multiscale neural decomposition comparisons",
            "seasonal signals where multiple smoothing scales are informative",
        ],
        "typical_failure_modes": [
            "multiscale windows poorly matched to the series length",
            "averaged trend erasing localized events",
        ],
    },
    "ST_MTM_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "ST-MTM-inspired smoothing head combining trend smoothing and smoothed periodic seasonality.",
        "recommended_for": [
            "seasonal-trend pretraining block ablations",
            "smooth periodic decomposition baselines",
        ],
        "typical_failure_modes": [
            "season smoother removing useful high-frequency seasonal content",
            "period mismatch in periodic-template fitting",
        ],
    },
    "PARSIMONY_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "Parsimony-inspired trend head with compact harmonic seasonal projection.",
        "recommended_for": [
            "compact harmonic decomposition baselines",
            "low-parameter neural head comparisons",
        ],
        "typical_failure_modes": [
            "too few harmonics for complex seasonality",
            "trend window absorbing seasonal variation",
        ],
    },
    "TIMES2D_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "Times2D-inspired multi-period harmonic decomposition head.",
        "recommended_for": [
            "multi-period neural decomposition baselines",
            "FFT-selected seasonal period comparisons",
        ],
        "typical_failure_modes": [
            "dominant FFT periods tracking noise",
            "top-k period choices that over-average incompatible seasonalities",
        ],
    },
    "FREQMOE_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "FreqMoE-inspired frequency mixture head for trend plus multi-band seasonal reconstruction.",
        "recommended_for": [
            "frequency-mixture neural head ablations",
            "multi-band seasonal decomposition experiments",
        ],
        "typical_failure_modes": [
            "frequency bands dominated by noise",
            "expert width or band count too large for short series",
        ],
    },
    "TIMEKAN_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "TimeKAN-inspired decomposition head blending template and harmonic seasonal estimates.",
        "recommended_for": [
            "KAN-inspired neural decomposition ablations",
            "frequency-template hybrid seasonal baselines",
        ],
        "typical_failure_modes": [
            "dominant period inference locking onto noisy bands",
            "trend smoothing that masks short transients",
        ],
    },
    "WAVEFORM_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "WaveForM-inspired wavelet multiresolution decomposition head.",
        "recommended_for": [
            "wavelet neural-head ablations",
            "multiresolution trend/detail comparisons",
        ],
        "typical_failure_modes": [
            "wavelet family mismatch",
            "boundary artifacts on short series",
        ],
        "optional_dependencies": ["PyWavelets"],
    },
    "WAVELETMIXER_BLOCK": {
        "family": "NeuralBlock",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "WaveletMixer-inspired multiresolution decomposition head using mixed wavelet detail levels.",
        "recommended_for": [
            "wavelet-mixer neural decomposition baselines",
            "multi-level detail seasonal reconstruction",
        ],
        "typical_failure_modes": [
            "season detail levels chosen inconsistently with the signal scale",
            "edge effects from short or nonperiodic series",
        ],
        "optional_dependencies": ["PyWavelets"],
    },
}
METHOD_METADATA.update(_NEURAL_BLOCK_METHOD_METADATA)

METHOD_REFERENCE_LINKS: Dict[str, list[Dict[str, str]]] = {
    "SSA": [
        {
            "title": "Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series",
            "url": "https://link.springer.com/book/10.1007/978-3-662-62436-4",
            "note": "Primary SSA reference; the second edition also covers multivariate SSA (MSSA).",
        }
    ],
    "MSSA": [
        {
            "title": "Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series",
            "url": "https://link.springer.com/book/10.1007/978-3-662-62436-4",
            "note": "Primary SSA/MSSA reference used for the multivariate extension.",
        }
    ],
    "STD": [
        {
            "title": "Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series",
            "url": "https://doi.org/10.48550/arXiv.2204.10398",
            "note": "Primary reference for STD and the robust seasonal-trend-dispersion family.",
        }
    ],
    "STDR": [
        {
            "title": "Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series",
            "url": "https://doi.org/10.48550/arXiv.2204.10398",
            "note": "Primary reference for STD and the robust seasonal-trend-dispersion family.",
        }
    ],
    "STL": [
        {
            "title": "Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS",
            "url": "https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html",
            "note": "Statsmodels STL docs cite the original Journal of Official Statistics paper.",
        }
    ],
    "ROBUST_STL": [
        {
            "title": "Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS",
            "url": "https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html",
            "note": "Robust STL in DeTime builds on the same STL literature and upstream implementation family.",
        }
    ],
    "MSTL": [
        {
            "title": "Bandara, Hyndman, and Bergmeir (2021), MSTL: A Seasonal-Trend Decomposition Algorithm for Time Series with Multiple Seasonal Patterns",
            "url": "https://arxiv.org/abs/2107.13462",
            "note": "Primary MSTL reference used by the statsmodels implementation.",
        }
    ],
    "EMD": [
        {
            "title": "Huang et al. (1998), The empirical mode decomposition and the Hilbert spectrum for nonlinear and non-stationary time series analysis",
            "url": "https://doi.org/10.1098/rspa.1998.0193",
            "note": "Primary empirical mode decomposition reference.",
        }
    ],
    "CEEMDAN": [
        {
            "title": "Torres et al. (2011), A complete ensemble empirical mode decomposition with adaptive noise",
            "url": "https://pyemd.readthedocs.io/en/latest/ceemdan.html",
            "note": "PyEMD CEEMDAN docs cite the original ICASSP 2011 paper.",
        },
        {
            "title": "Colominas, Schlotthauer, and Torres (2014), Improved complete ensemble EMD: A suitable tool for biomedical signal processing",
            "url": "https://pyemd.readthedocs.io/en/latest/ceemdan.html",
            "note": "Improved CEEMDAN variant adopted by the PyEMD implementation used by DeTime.",
        },
    ],
    "VMD": [
        {
            "title": "Dragomiretskiy and Zosso (2014), Variational Mode Decomposition",
            "url": "https://doi.org/10.1109/TSP.2013.2288675",
            "note": "Primary variational mode decomposition reference.",
        }
    ],
    "WAVELET": [
        {
            "title": "Mallat (1989), A theory for multiresolution signal decomposition: the wavelet representation",
            "url": "https://ieeexplore.ieee.org/document/192463",
            "note": "Foundational wavelet multiresolution reference.",
        },
        {
            "title": "Lee et al. (2019), PyWavelets: A Python package for wavelet analysis",
            "url": "https://doi.org/10.21105/joss.01237",
            "note": "Package citation for the upstream wavelet implementation used by DeTime.",
        },
    ],
    "MVMD": [
        {
            "title": "Rehman and Aftab (2019), Multivariate Variational Mode Decomposition",
            "url": "https://arxiv.org/abs/1907.04509",
            "note": "Primary MVMD reference for the multivariate VMD extension.",
        }
    ],
    "MEMD": [
        {
            "title": "Rehman and Mandic (2010), Multivariate empirical mode decomposition",
            "url": "https://doi.org/10.1098/rspa.2009.0502",
            "note": "Primary MEMD reference for the multivariate EMD extension.",
        }
    ],
    "GABOR_CLUSTER": [
        {
            "title": "Gabor (1946), Theory of Communication",
            "url": "https://www.rctn.org/w/images/b/b6/Gabor.pdf",
            "note": "Historical reference for the Gabor time-frequency representation family.",
        },
        {
            "title": "Douze et al. (2024), The Faiss library",
            "url": "https://arxiv.org/abs/2401.08281",
            "note": "Reference for the similarity-search backend used by the experimental clustering path.",
        },
    ],
}

_NEURAL_BLOCK_REFERENCE_LINKS: Dict[str, list[Dict[str, str]]] = {
    "AUTOFORMER_BLOCK": [
        {
            "title": "Wu et al. (2021), Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting",
            "url": "https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html",
            "note": "Source architecture for the moving-average decomposition block exposed by AUTOFORMER_BLOCK.",
        }
    ],
    "DLINEAR_BLOCK": [
        {
            "title": "Zeng et al. (2023), Are Transformers Effective for Time Series Forecasting?",
            "url": "https://ojs.aaai.org/index.php/AAAI/article/view/26317",
            "note": "Introduces the LTSF-Linear family, including the DLinear decomposition-based linear model.",
        }
    ],
    "MOVING_AVERAGE_DECOMPOSITION_BLOCK": [
        {
            "title": "Wu et al. (2021), Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting",
            "url": "https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html",
            "note": "Primary source for treating moving-average series decomposition as an internal neural forecasting block.",
        },
        {
            "title": "Zeng et al. (2023), Are Transformers Effective for Time Series Forecasting?",
            "url": "https://ojs.aaai.org/index.php/AAAI/article/view/26317",
            "note": "Uses decomposition-based linear forecasting as a simple long-term forecasting baseline.",
        },
    ],
    "NBEATS_INTERPRETABLE": [
        {
            "title": "Oreshkin et al. (2020), N-BEATS: Neural basis expansion analysis for interpretable time series forecasting",
            "url": "https://openreview.net/forum?id=r1ecqn4YwB",
            "note": "Source for interpretable trend and seasonality basis stacks.",
        }
    ],
    "XPATCH_BLOCK": [
        {
            "title": "Stitsyuk and Choi (2024), xPatch: Dual-Stream Time Series Forecasting with Exponential Seasonal-Trend Decomposition",
            "url": "https://arxiv.org/abs/2412.17323",
            "note": "Source architecture for exponential seasonal-trend decomposition.",
        }
    ],
    "LEDDAM_BLOCK": [
        {
            "title": "Yu et al. (2024), Revitalizing Multivariate Time Series Forecasting: Learnable Decomposition with Inter-Series Dependencies and Intra-Series Variations Modeling",
            "url": "https://arxiv.org/abs/2402.12694",
            "note": "Introduces LEDDAM, the learnable decomposition and dual-attention module.",
        }
    ],
    "INPARFORMER_BLOCK": [
        {
            "title": "Cao et al. (2023), InParformer: Evolutionary Decomposition Transformers with Interactive Parallel Attention for Long-Term Time Series Forecasting",
            "url": "https://ojs.aaai.org/index.php/AAAI/article/view/25845",
            "note": "Source architecture for evolutionary seasonal-trend decomposition in a transformer forecaster.",
        }
    ],
    "DELELSTM_BLOCK": [
        {
            "title": "Wang et al. (2023), DeLELSTM: Decomposition-based Linear Explainable LSTM to Capture Instantaneous and Long-term Effects in Time Series",
            "url": "https://arxiv.org/abs/2308.13797",
            "note": "Source model for decomposition-based explainable LSTM effects.",
        }
    ],
    "AMD_BLOCK": [
        {
            "title": "Hu et al. (2024), Adaptive Multi-Scale Decomposition Framework for Time Series Forecasting",
            "url": "https://arxiv.org/abs/2406.03751",
            "note": "Source framework for adaptive multiscale decomposition.",
        }
    ],
    "ST_MTM_BLOCK": [
        {
            "title": "Seo and Lim (2025), ST-MTM: Masked Time Series Modeling with Seasonal-Trend Decomposition for Time Series Forecasting",
            "url": "https://arxiv.org/abs/2507.00013",
            "note": "Source method for seasonal-trend masked time-series modeling.",
        }
    ],
    "PARSIMONY_BLOCK": [
        {
            "title": "Deng et al. (2024), Parsimony or Capability? Decomposition Delivers Both in Long-term Time Series Forecasting",
            "url": "https://arxiv.org/abs/2401.11929",
            "note": "Source paper for parameter-efficient decomposition in long-term forecasting.",
        }
    ],
    "TIMES2D_BLOCK": [
        {
            "title": "Nematirad, Pahwa, and Natarajan (2025), Times2D: Multi-Period Decomposition and Derivative Mapping for General Time Series Forecasting",
            "url": "https://arxiv.org/abs/2504.00118",
            "note": "Source method for multi-period decomposition and 2D time-series mapping.",
        }
    ],
    "FREQMOE_BLOCK": [
        {
            "title": "Liu (2025), FreqMoE: Enhancing Time Series Forecasting through Frequency Decomposition Mixture of Experts",
            "url": "https://arxiv.org/abs/2501.15125",
            "note": "Source architecture for frequency decomposition mixture-of-experts forecasting.",
        }
    ],
    "TIMEKAN_BLOCK": [
        {
            "title": "Huang et al. (2025), TimeKAN: KAN-based Frequency Decomposition Learning Architecture for Long-term Time Series Forecasting",
            "url": "https://arxiv.org/abs/2502.06910",
            "note": "Source method for KAN-based frequency decomposition learning.",
        }
    ],
    "WAVEFORM_BLOCK": [
        {
            "title": "Yang et al. (2023), WaveForM: Graph Enhanced Wavelet Learning for Long Sequence Forecasting of Multivariate Time Series",
            "url": "https://ojs.aaai.org/index.php/AAAI/article/view/26276",
            "note": "Source architecture for graph-enhanced wavelet learning.",
        }
    ],
    "WAVELETMIXER_BLOCK": [
        {
            "title": "Zhang et al. (2025), WaveletMixer: A Multi-Resolution Wavelets Based MLP-Mixer for Multivariate Long-Term Time Series Forecasting",
            "url": "https://ojs.aaai.org/index.php/AAAI/article/view/34434",
            "note": "Source method for multi-resolution wavelet mixer forecasting.",
        }
    ],
}
METHOD_REFERENCE_LINKS.update(_NEURAL_BLOCK_REFERENCE_LINKS)

METHOD_PACKAGE_LINKS: Dict[str, list[Dict[str, str]]] = {
    "SSA": [
        {
            "title": "SSALib",
            "url": "https://github.com/ADSCIAN/ssalib",
            "note": "Specialist SSA package used as an external comparison point.",
        }
    ],
    "MSSA": [
        {
            "title": "SSALib",
            "url": "https://github.com/ADSCIAN/ssalib",
            "note": "SSA-focused package; useful comparison point for SSA-family workflows.",
        }
    ],
    "STL": [
        {
            "title": "statsmodels",
            "url": "https://www.statsmodels.org/",
            "note": "Official project site for the upstream STL implementation.",
        }
    ],
    "ROBUST_STL": [
        {
            "title": "statsmodels",
            "url": "https://www.statsmodels.org/",
            "note": "Official project site for the upstream STL implementation family.",
        }
    ],
    "MSTL": [
        {
            "title": "statsmodels",
            "url": "https://www.statsmodels.org/",
            "note": "Official project site for the upstream MSTL implementation.",
        }
    ],
    "EMD": [
        {
            "title": "PyEMD",
            "url": "https://github.com/laszukdawid/PyEMD",
            "note": "Upstream Python package wrapped by DeTime for EMD-family methods.",
        }
    ],
    "CEEMDAN": [
        {
            "title": "PyEMD",
            "url": "https://github.com/laszukdawid/PyEMD",
            "note": "Upstream Python package wrapped by DeTime for EMD-family methods.",
        }
    ],
    "VMD": [
        {
            "title": "sktime",
            "url": "https://www.sktime.net/en/stable/",
            "note": "Current maintained ecosystem for `vmdpy`, which the archived project directs users toward.",
        },
        {
            "title": "vmdpy",
            "url": "https://github.com/vrcarva/vmdpy",
            "note": "Archived Python VMD package used by the current DeTime wrapper.",
        },
    ],
    "WAVELET": [
        {
            "title": "PyWavelets",
            "url": "https://pywavelets.readthedocs.io/en/latest/",
            "note": "Official documentation for the upstream wavelet package.",
        }
    ],
    "MVMD": [
        {
            "title": "PySDKit",
            "url": "https://pysdkit.readthedocs.io/en/latest/",
            "note": "Optional multivariate backend used by DeTime for MVMD.",
        }
    ],
    "MEMD": [
        {
            "title": "PySDKit",
            "url": "https://pysdkit.readthedocs.io/en/latest/",
            "note": "Optional multivariate backend used by DeTime for MEMD.",
        }
    ],
    "GABOR_CLUSTER": [
        {
            "title": "Faiss",
            "url": "https://github.com/facebookresearch/faiss",
            "note": "Vector similarity search library required by the experimental clustering backend.",
        }
    ],
}


def _param_doc(
    name: str,
    type_: str,
    description: str,
    *,
    default: Any = None,
    required: bool = False,
    common: bool = True,
) -> Dict[str, Any]:
    return {
        "name": name,
        "type": type_,
        "required": required,
        "default": default,
        "description": description,
        "common": common,
    }


METHOD_PARAMETER_GUIDE: Dict[str, list[Dict[str, Any]]] = {
    "SSA": [
        _param_doc("window", "int", "Embedding window length for trajectory-matrix construction.", required=True),
        _param_doc("rank", "int | None", "Number of elementary components to retain before grouping.", default=None),
        _param_doc("primary_period", "int | None", "Dominant seasonal period used by automatic grouping.", default=None),
        _param_doc("fs", "float", "Sampling frequency used by frequency-based grouping.", default=1.0, common=False),
        _param_doc("trend_components", "list[int] | None", "Explicit component indexes assigned to trend.", default=None, common=False),
        _param_doc("season_components", "list[int] | None", "Explicit component indexes assigned to season.", default=None, common=False),
        _param_doc("power_iterations", "int", "Fast native mode iteration count when speed_mode='fast'.", default=4, common=False),
    ],
    "STD": [
        _param_doc("period", "int", "Seasonal period in samples.", required=True),
        _param_doc("max_period_search", "int | None", "Optional search horizon when period inference is enabled.", default=None, common=False),
        _param_doc("eps", "float", "Small numerical guard for dispersion calculations.", default=1e-8, common=False),
    ],
    "STDR": [
        _param_doc("period", "int", "Seasonal period in samples.", required=True),
        _param_doc("max_period_search", "int | None", "Optional search horizon when period inference is enabled.", default=None, common=False),
        _param_doc("eps", "float", "Small numerical guard for robust dispersion calculations.", default=1e-8, common=False),
    ],
    "MSSA": [
        _param_doc("window", "int", "Shared embedding window length for aligned channels.", required=True),
        _param_doc("rank", "int | None", "Number of shared elementary components to retain.", default=None),
        _param_doc("primary_period", "int | None", "Dominant shared period used by automatic grouping.", default=None),
        _param_doc("fs", "float", "Sampling frequency used by frequency-based grouping.", default=1.0, common=False),
        _param_doc("trend_components", "list[int] | None", "Explicit component indexes assigned to trend.", default=None, common=False),
        _param_doc("season_components", "list[int] | None", "Explicit component indexes assigned to season.", default=None, common=False),
    ],
    "STL": [
        _param_doc("period", "int", "Seasonal period passed to statsmodels STL.", required=True),
        _param_doc("seasonal", "int | None", "Odd LOESS seasonal smoother length.", default=None, common=False),
        _param_doc("trend", "int | None", "Odd LOESS trend smoother length.", default=None, common=False),
        _param_doc("robust", "bool", "Whether to use robust LOESS fitting.", default=False, common=False),
    ],
    "MSTL": [
        _param_doc("periods", "list[int]", "One or more seasonal periods passed to statsmodels MSTL.", required=True),
        _param_doc("windows", "list[int] | None", "Optional smoother windows aligned with periods.", default=None, common=False),
        _param_doc("stl_kwargs", "dict | None", "Additional statsmodels STL keyword arguments.", default=None, common=False),
    ],
    "ROBUST_STL": [
        _param_doc("period", "int", "Seasonal period passed to robust statsmodels STL.", required=True),
        _param_doc("seasonal", "int | None", "Odd LOESS seasonal smoother length.", default=None, common=False),
        _param_doc("trend", "int | None", "Odd LOESS trend smoother length.", default=None, common=False),
    ],
    "EMD": [
        _param_doc("n_imfs", "int | None", "Maximum number of intrinsic mode functions to retain.", default=None),
        _param_doc("primary_period", "int | None", "Period hint for grouping IMFs into season and trend.", default=None),
        _param_doc("trend_imfs", "list[int] | None", "Explicit IMF indexes assigned to trend.", default=None, common=False),
        _param_doc("season_imfs", "list[int] | None", "Explicit IMF indexes assigned to season.", default=None, common=False),
        _param_doc("fs", "float", "Sampling frequency used by grouping heuristics.", default=1.0, common=False),
    ],
    "CEEMDAN": [
        _param_doc("trials", "int", "Number of noise-assisted ensemble trials.", default=50),
        _param_doc("noise_width", "float", "Relative width of the injected noise.", default=0.05),
        _param_doc("primary_period", "int | None", "Period hint for grouping IMFs into season and trend.", default=None),
        _param_doc("fs", "float", "Sampling frequency used by grouping heuristics.", default=1.0, common=False),
    ],
    "VMD": [
        _param_doc("K", "int", "Number of variational modes.", default=4),
        _param_doc("alpha", "float", "Bandwidth penalty parameter.", default=2000.0),
        _param_doc("tau", "float", "Dual ascent time step.", default=0.0, common=False),
        _param_doc("DC", "bool", "Keep the first mode at zero frequency.", default=False, common=False),
        _param_doc("init", "int", "Initialization policy used by the VMD backend.", default=1, common=False),
        _param_doc("tol", "float", "Convergence tolerance.", default=1e-7, common=False),
        _param_doc("primary_period", "int | None", "Period hint for grouping modes into season and trend.", default=None),
    ],
    "WAVELET": [
        _param_doc("wavelet", "str", "PyWavelets wavelet family name.", default="db4"),
        _param_doc("level", "int | None", "Decomposition depth. Defaults to PyWavelets maximum usable level.", default=None),
        _param_doc("trend_levels", "list[int] | None", "Detail levels assigned to trend reconstruction.", default=None, common=False),
        _param_doc("season_levels", "list[int] | None", "Detail levels assigned to seasonal reconstruction.", default=None, common=False),
    ],
    "MA_BASELINE": [
        _param_doc("trend_window", "int", "Moving-average window used for the trend estimate.", default=7),
        _param_doc("season_period", "int | None", "Optional period for a simple seasonal average.", default=None),
    ],
    "MVMD": [
        _param_doc("K", "int", "Number of shared variational modes requested from PySDKit.", default=4),
        _param_doc("alpha", "float", "Bandwidth penalty parameter for the MVMD backend.", default=2000.0),
        _param_doc("primary_period", "int | None", "Shared period hint for grouping modes.", default=None),
        _param_doc("fs", "float", "Sampling frequency used by grouping heuristics.", default=1.0, common=False),
    ],
    "MEMD": [
        _param_doc("primary_period", "int | None", "Shared period hint for grouping multivariate IMFs.", default=None),
        _param_doc("trend_modes", "list[int] | None", "Explicit mode indexes assigned to trend.", default=None, common=False),
        _param_doc("season_modes", "list[int] | None", "Explicit mode indexes assigned to season.", default=None, common=False),
        _param_doc("fs", "float", "Sampling frequency used by grouping heuristics.", default=1.0, common=False),
    ],
    "GABOR_CLUSTER": [
        _param_doc("model", "GaborClusterModel | None", "In-memory trained clustering model.", default=None),
        _param_doc("model_path", "str | None", "Path to a serialized trained clustering model.", default=None),
        _param_doc("max_clusters", "int | None", "Optional cap on clusters used during reconstruction.", default=None, common=False),
        _param_doc("trend_freq_thr", "float | None", "Frequency threshold used for trend-like atoms.", default=None, common=False),
    ],
}

METHOD_OUTPUT_COMPONENTS: Dict[str, list[str]] = {
    "SSA": ["trend", "season", "residual", "components.elementary"],
    "STD": ["trend", "season", "residual", "components.dispersion", "components.seasonal_shape"],
    "STDR": ["trend", "season", "residual", "components.dispersion", "components.seasonal_shape"],
    "MSSA": ["trend", "season", "residual", "components.elementary"],
    "STL": ["trend", "season", "residual"],
    "MSTL": ["trend", "season", "residual", "components.seasonal_terms"],
    "ROBUST_STL": ["trend", "season", "residual"],
    "EMD": ["trend", "season", "residual", "components.imfs"],
    "CEEMDAN": ["trend", "season", "residual", "components.imfs"],
    "VMD": ["trend", "season", "residual", "components.modes"],
    "WAVELET": ["trend", "season", "residual", "components.coefficients"],
    "MA_BASELINE": ["trend", "season", "residual"],
    "MVMD": ["trend", "season", "residual", "components.modes"],
    "MEMD": ["trend", "season", "residual", "components.imfs"],
    "GABOR_CLUSTER": ["trend", "season", "residual", "components.clusters"],
}

METHOD_EXAMPLE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "SSA": {
        "method": "SSA",
        "params": {"window": 24, "rank": 6, "primary_period": 12},
        "backend": "auto",
        "speed_mode": "exact",
        "seed": 42,
    },
    "STD": {
        "method": "STD",
        "params": {"period": 12},
        "backend": "auto",
        "speed_mode": "exact",
    },
    "STDR": {
        "method": "STDR",
        "params": {"period": 12},
        "backend": "auto",
        "speed_mode": "exact",
    },
    "MSSA": {
        "method": "MSSA",
        "params": {"window": 24, "rank": 6, "primary_period": 12},
        "backend": "auto",
        "speed_mode": "exact",
        "channel_names": ["channel_a", "channel_b", "channel_c"],
    },
    "STL": {"method": "STL", "params": {"period": 12}},
    "MSTL": {"method": "MSTL", "params": {"periods": [12, 24]}},
    "ROBUST_STL": {"method": "ROBUST_STL", "params": {"period": 12}},
    "EMD": {"method": "EMD", "params": {"primary_period": 12, "n_imfs": 4}},
    "CEEMDAN": {"method": "CEEMDAN", "params": {"primary_period": 12, "trials": 20, "noise_width": 0.05}},
    "VMD": {"method": "VMD", "params": {"K": 4, "alpha": 2000.0, "primary_period": 12}},
    "WAVELET": {"method": "WAVELET", "params": {"wavelet": "db4", "level": 3}},
    "MA_BASELINE": {"method": "MA_BASELINE", "params": {"trend_window": 7, "season_period": 12}},
    "MVMD": {"method": "MVMD", "params": {"K": 4, "alpha": 2000.0, "primary_period": 12}},
    "MEMD": {"method": "MEMD", "params": {"primary_period": 12}},
    "GABOR_CLUSTER": {"method": "GABOR_CLUSTER", "params": {"model_path": "path/to/trained-gabor-model.pkl"}},
}

_NEURAL_FIT_SCOPE_PARAMS = [
    _param_doc("primary_period", "int | None", "Dominant period hint used by neural block heuristics.", default=None),
    _param_doc("fit_scope", "str", "Whether to fit templates on the full series or a prefix window.", default="full"),
    _param_doc("train_fraction", "float", "Prefix fraction used when fit_scope='prefix'.", default=0.6, common=False),
]

_NEURAL_MOVING_AVG_PARAMS = [
    _param_doc("moving_avg", "int | None", "Moving-average window used by the extracted forecasting block.", default=None),
    _param_doc("window", "int | None", "Alias for moving_avg.", default=None, common=False),
    _param_doc("primary_period", "int | None", "Period hint used to derive the moving-average window.", default=None),
]

METHOD_PARAMETER_GUIDE.update(
    {
        "AUTOFORMER_BLOCK": list(_NEURAL_MOVING_AVG_PARAMS),
        "DLINEAR_BLOCK": list(_NEURAL_MOVING_AVG_PARAMS),
        "MOVING_AVERAGE_DECOMPOSITION_BLOCK": list(_NEURAL_MOVING_AVG_PARAMS),
        "NBEATS_INTERPRETABLE": [
            _param_doc("degree_of_polynomial", "int", "Polynomial trend basis degree.", default=3),
            _param_doc("num_harmonics", "int", "Number of Fourier harmonics in the seasonality stack.", default=8),
            _param_doc("trend_blocks", "int", "Number of interpretable trend blocks.", default=2, common=False),
            _param_doc("seasonality_blocks", "int", "Number of interpretable seasonality blocks.", default=2, common=False),
            _param_doc("layers", "int", "Fully connected layers per block.", default=6, common=False),
            _param_doc("layer_size", "int", "Hidden width for each block.", default=128, common=False),
            _param_doc("fit_scope", "str", "Whether to fit on the full series or prefix window.", default="full"),
            _param_doc("train_fraction", "float", "Prefix fraction used when fit_scope='prefix'.", default=0.6, common=False),
            _param_doc("n_epochs", "int", "Maximum torch optimization epochs.", default=200),
            _param_doc("patience", "int", "Early-stopping patience.", default=40, common=False),
            _param_doc("restarts", "int", "Number of random restarts.", default=2, common=False),
            _param_doc("learning_rate", "float", "Adam learning rate.", default=1e-3, common=False),
            _param_doc("weight_decay", "float", "Adam weight decay.", default=1e-4, common=False),
            _param_doc("device", "str", "Torch device: auto, cpu, cuda, or gpu.", default="auto", common=False),
            _param_doc("seed", "int", "Base random seed for torch restarts.", default=0, common=False),
        ],
        "XPATCH_BLOCK": [
            _param_doc("ma_type", "str", "Smoothing type, either 'ema' or 'dema'.", default="ema"),
            _param_doc("trend_window", "int | None", "Window used to derive the EMA alpha.", default=None),
            _param_doc("season_smooth", "int | None", "Optional moving-average smoother for the seasonal residual.", default=None),
            _param_doc("alpha", "float | None", "EMA or DEMA level smoothing coefficient.", default=None, common=False),
            _param_doc("beta", "float | None", "DEMA slope smoothing coefficient.", default=None, common=False),
        ],
        "LEDDAM_BLOCK": [
            _param_doc("kernel_size", "int", "Odd Gaussian smoothing kernel size.", default=25),
            _param_doc("sigma", "float", "Gaussian smoothing kernel sigma.", default=1.0),
        ],
        "INPARFORMER_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("trend_window", "int | None", "Moving-average trend window.", default=None),
        ],
        "DELELSTM_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("alpha", "float", "Holt level smoothing coefficient.", default=0.4),
            _param_doc("beta", "float", "Holt slope smoothing coefficient.", default=0.2),
        ],
        "AMD_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("multiscale_windows", "list[int] | None", "Smoothing windows averaged into the multiscale trend.", default=None),
        ],
        "PARSIMONY_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("trend_window", "int | None", "Moving-average trend window.", default=None),
            _param_doc("num_harmonics", "int", "Number of harmonic seasonal terms.", default=2),
        ],
        "ST_MTM_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("trend_window", "int | None", "Moving-average trend window.", default=None),
            _param_doc("season_smooth_window", "int | None", "Smoother applied to the periodic seasonal template.", default=None),
        ],
        "TIMES2D_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("top_k_periods", "int", "Number of dominant FFT periods to retain.", default=2),
            _param_doc("num_harmonics", "int", "Number of harmonics per selected period.", default=1),
            _param_doc("trend_window", "int | None", "Moving-average trend window.", default=None),
        ],
        "FREQMOE_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("trend_window", "int | None", "Moving-average trend window.", default=None),
            _param_doc("num_bands", "int", "Number of frequency bands in the mixture.", default=4),
            _param_doc("expert_width", "int", "Frequency expert width used by the scaffold.", default=64, common=False),
        ],
        "TIMEKAN_BLOCK": [
            *_NEURAL_FIT_SCOPE_PARAMS,
            _param_doc("trend_window", "int | None", "Moving-average trend window.", default=None),
            _param_doc("num_bands", "int", "Number of dominant periods/templates to blend.", default=2),
            _param_doc("kan_width", "int", "KAN-inspired width used to choose harmonic capacity.", default=32, common=False),
        ],
        "WAVEFORM_BLOCK": [
            _param_doc("wavelet", "str", "PyWavelets wavelet family name.", default="db4"),
            _param_doc("level", "int", "Wavelet decomposition depth.", default=3),
            _param_doc("season_levels", "list[int]", "Detail coefficient levels assigned to the seasonal component.", default=[1, 2]),
        ],
        "WAVELETMIXER_BLOCK": [
            _param_doc("wavelet", "str", "PyWavelets wavelet family name.", default="sym4"),
            _param_doc("level", "int", "Wavelet decomposition depth.", default=4),
            _param_doc("season_levels", "list[int]", "Detail coefficient levels assigned to the seasonal component.", default=[1, 2, 3]),
        ],
    }
)

_NEURAL_TREND_SEASON_OUTPUTS = [
    "trend",
    "season",
    "residual",
    "components.trend",
    "components.season",
]

METHOD_OUTPUT_COMPONENTS.update(
    {
        "AUTOFORMER_BLOCK": ["trend", "season", "residual", "components.moving_mean"],
        "DLINEAR_BLOCK": ["trend", "season", "residual", "components.moving_mean"],
        "MOVING_AVERAGE_DECOMPOSITION_BLOCK": ["trend", "season", "residual", "components.moving_mean"],
        "NBEATS_INTERPRETABLE": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "XPATCH_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "LEDDAM_BLOCK": ["trend", "season", "residual", "components.ld_trend", "components.kernel"],
        "INPARFORMER_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "DELELSTM_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "AMD_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "ST_MTM_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "PARSIMONY_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "TIMES2D_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "FREQMOE_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "TIMEKAN_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "WAVEFORM_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
        "WAVELETMIXER_BLOCK": list(_NEURAL_TREND_SEASON_OUTPUTS),
    }
)

METHOD_EXAMPLE_CONFIGS.update(
    {
        "AUTOFORMER_BLOCK": {"method": "AUTOFORMER_BLOCK", "params": {"primary_period": 12, "moving_avg": 25}},
        "DLINEAR_BLOCK": {"method": "DLINEAR_BLOCK", "params": {"primary_period": 12, "moving_avg": 25}},
        "MOVING_AVERAGE_DECOMPOSITION_BLOCK": {
            "method": "MOVING_AVERAGE_DECOMPOSITION_BLOCK",
            "params": {"primary_period": 12, "moving_avg": 25},
        },
        "NBEATS_INTERPRETABLE": {
            "method": "NBEATS_INTERPRETABLE",
            "params": {"num_harmonics": 8, "n_epochs": 200, "restarts": 2, "fit_scope": "full"},
        },
        "XPATCH_BLOCK": {"method": "XPATCH_BLOCK", "params": {"trend_window": 25, "season_smooth": 7}},
        "LEDDAM_BLOCK": {"method": "LEDDAM_BLOCK", "params": {"kernel_size": 25, "sigma": 1.0}},
        "INPARFORMER_BLOCK": {
            "method": "INPARFORMER_BLOCK",
            "params": {"primary_period": 12, "trend_window": 25, "fit_scope": "full"},
        },
        "DELELSTM_BLOCK": {
            "method": "DELELSTM_BLOCK",
            "params": {"primary_period": 12, "alpha": 0.2, "beta": 0.1, "fit_scope": "full"},
        },
        "AMD_BLOCK": {
            "method": "AMD_BLOCK",
            "params": {"primary_period": 12, "multiscale_windows": [13, 25, 49], "fit_scope": "full"},
        },
        "ST_MTM_BLOCK": {
            "method": "ST_MTM_BLOCK",
            "params": {"primary_period": 12, "trend_window": 13, "season_smooth_window": 7, "fit_scope": "full"},
        },
        "PARSIMONY_BLOCK": {
            "method": "PARSIMONY_BLOCK",
            "params": {"primary_period": 12, "trend_window": 13, "num_harmonics": 2, "fit_scope": "full"},
        },
        "TIMES2D_BLOCK": {
            "method": "TIMES2D_BLOCK",
            "params": {"primary_period": 12, "top_k_periods": 2, "num_harmonics": 1, "fit_scope": "full"},
        },
        "FREQMOE_BLOCK": {
            "method": "FREQMOE_BLOCK",
            "params": {"primary_period": 12, "num_bands": 4, "expert_width": 64, "fit_scope": "full"},
        },
        "TIMEKAN_BLOCK": {
            "method": "TIMEKAN_BLOCK",
            "params": {"primary_period": 12, "num_bands": 2, "kan_width": 32, "fit_scope": "full"},
        },
        "WAVEFORM_BLOCK": {
            "method": "WAVEFORM_BLOCK",
            "params": {"wavelet": "sym4", "level": 3, "season_levels": [1, 2]},
        },
        "WAVELETMIXER_BLOCK": {
            "method": "WAVELETMIXER_BLOCK",
            "params": {"wavelet": "coif1", "level": 3, "season_levels": [1, 2, 3]},
        },
    }
)


def _default_assumptions(name: str, family: str, input_mode: InputMode) -> list[str]:
    assumptions: list[str] = []
    if input_mode == "univariate":
        assumptions.append("expects one decomposed series at a time")
    elif input_mode == "channelwise":
        assumptions.append("treats each channel independently under one shared method surface")
    else:
        assumptions.append("expects a 2D array with at least two aligned channels")

    family_assumptions = {
        "SSA": "works best when window and rank reflect the dominant temporal structure",
        "SeasonalTrend": "works best when one seasonal period or block structure is reasonably stable",
        "EMD": "assumes oscillatory modes are meaningful enough to separate adaptively",
        "Wavelet": "assumes a wavelet family and decomposition depth can be chosen sensibly",
        "Variational": "assumes the number of modes and bandwidth penalties can be tuned to the signal family",
        "Baseline": "assumes a coarse baseline is acceptable as a sanity check",
        "Experimental": "assumes exploratory use is acceptable and output should be validated against a stable baseline",
        "NeuralBlock": "uses an extracted neural-architecture decomposition head as a standalone operator",
    }
    if family in family_assumptions:
        assumptions.append(family_assumptions[family])
    assumptions.append(f"{name} should be evaluated against residual diagnostics rather than used as a black box")
    return assumptions


def _default_not_recommended(name: str, maturity: str, input_mode: InputMode) -> list[str]:
    discouraged: list[str] = []
    if input_mode == "univariate":
        discouraged.append("shared-model multivariate decomposition problems")
    elif input_mode == "multivariate":
        discouraged.append("single-series workflows where a univariate flagship method is sufficient")
    else:
        discouraged.append("problems that require one shared latent model across channels")

    if maturity == "optional-backend":
        discouraged.append("environments where optional backend dependencies cannot be installed")
    if maturity == "experimental":
        discouraged.append("first-pass baselines or high-trust production workflows")
    if name in {"SSA", "MSSA"}:
        discouraged.append("very short series that cannot support a sensible window length")
    if name in {"STD", "STDR", "STL", "MSTL", "ROBUST_STL"}:
        discouraged.append("series where the dominant period is unknown and cannot be inferred reliably")
    return discouraged


def _default_optional_dependencies(name: str, dependency_tier: str) -> list[str]:
    if dependency_tier == "optional-backend":
        return ["PySDKit"]
    if name in {"STL", "MSTL", "ROBUST_STL"}:
        return ["statsmodels"]
    if name in {"EMD", "CEEMDAN"}:
        return ["PyEMD"]
    if name == "VMD":
        return ["vmdpy", "sktime"]
    if name == "WAVELET":
        return ["PyWavelets"]
    if name == "GABOR_CLUSTER":
        return ["faiss"]
    return []


def _default_references(name: str) -> list[Dict[str, str]]:
    return [dict(item) for item in METHOD_REFERENCE_LINKS.get(name, [])]


def _default_package_links(name: str) -> list[Dict[str, str]]:
    return [dict(item) for item in METHOD_PACKAGE_LINKS.get(name, [])]


def _default_parameter_docs(name: str) -> list[Dict[str, Any]]:
    return [dict(item) for item in METHOD_PARAMETER_GUIDE.get(name, [])]


def _default_output_components(name: str) -> list[str]:
    return list(METHOD_OUTPUT_COMPONENTS.get(name, ["trend", "season", "residual"]))


def _default_example_config(name: str) -> Dict[str, Any]:
    return dict(METHOD_EXAMPLE_CONFIGS.get(name, {"method": name, "params": {}}))


def _fallback_metadata(name: str, input_mode: InputMode) -> Dict[str, Any]:
    multivariate_support = "univariate"
    if input_mode == "multivariate":
        multivariate_support = "shared-model"
    elif input_mode == "channelwise":
        multivariate_support = "channelwise"
    return {
        "family": "Other",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": multivariate_support,
        "native_backed": False,
        "min_length": 8,
        "summary": f"{name} decomposition exposed through the DeTime workflow surface.",
        "recommended_for": ["general decomposition workflows"],
        "typical_failure_modes": ["parameter choices misaligned with the signal structure"],
    }


def _metadata_for_method(name: str, input_mode: InputMode) -> Dict[str, Any]:
    base = dict(METHOD_METADATA.get(name, _fallback_metadata(name, input_mode)))
    base["input_mode"] = input_mode
    base.setdefault(
        "assumptions",
        _default_assumptions(name, str(base.get("family", "Other")), input_mode),
    )
    base.setdefault(
        "not_recommended_for",
        _default_not_recommended(name, str(base.get("maturity", "stable")), input_mode),
    )
    base.setdefault(
        "optional_dependencies",
        _default_optional_dependencies(name, str(base.get("dependency_tier", "core"))),
    )
    base.setdefault("references", _default_references(name))
    base.setdefault("package_links", _default_package_links(name))
    base.setdefault("parameter_docs", _default_parameter_docs(name))
    base.setdefault("output_components", _default_output_components(name))
    base.setdefault("example_config", _default_example_config(name))
    return base


@dataclass(frozen=True)
class MethodSpec:
    func: MethodSignature
    input_mode: InputMode = "univariate"
    metadata: Dict[str, Any] = field(default_factory=dict)


class MethodRegistry:
    _methods: Dict[str, MethodSpec] = {}

    @classmethod
    def register(cls, name: str, *, input_mode: InputMode = "univariate"):
        normalized = name.upper()
        if normalized in REMOVED_METHOD_HINTS:
            raise RuntimeError(REMOVED_METHOD_HINTS[normalized])

        def decorator(func: MethodSignature):
            cls._methods[normalized] = MethodSpec(
                func=func,
                input_mode=input_mode,
                metadata=_metadata_for_method(normalized, input_mode),
            )
            return func

        return decorator

    @classmethod
    def get_spec(cls, name: str) -> MethodSpec:
        name = name.upper()
        if name in REMOVED_METHOD_HINTS:
            raise ValueError(REMOVED_METHOD_HINTS[name])
        if name not in cls._methods:
            raise ValueError(
                f"Unknown decomposition method: {name}. Available: {list(cls._methods.keys())}"
            )
        return cls._methods[name]

    @classmethod
    def get(cls, name: str) -> MethodSignature:
        return cls.get_spec(name).func

    @classmethod
    def get_input_mode(cls, name: str) -> InputMode:
        return cls.get_spec(name).input_mode

    @classmethod
    def is_multivariate_method(cls, name: str) -> bool:
        return cls.get_input_mode(name) != "univariate"

    @classmethod
    def list_methods(cls):
        return sorted(name for name in cls._methods.keys() if name not in REMOVED_METHOD_HINTS)

    @classmethod
    def get_metadata(cls, name: str) -> Dict[str, Any]:
        return dict(cls.get_spec(name).metadata)

    @classmethod
    def list_catalog(cls) -> list[Dict[str, Any]]:
        catalog: list[Dict[str, Any]] = []
        for name in cls.list_methods():
            spec = cls.get_spec(name)
            entry = {"name": name}
            entry.update(spec.metadata)
            catalog.append(entry)
        return catalog


def _normalize_input(series: np.ndarray) -> np.ndarray:
    arr = np.asarray(series, dtype=float)
    if arr.ndim == 0:
        return arr.reshape(1)
    if arr.ndim > 2:
        raise ValueError(f"detime expects a 1D or 2D array, got shape {arr.shape}.")
    return arr


def _validate_input_mode(method: str, x: np.ndarray, input_mode: InputMode) -> None:
    if x.ndim == 1:
        if input_mode == "multivariate":
            raise ValueError(
                f"{method} requires 2D input with shape (T, C). Received 1D input with shape {x.shape}."
            )
        return
    if input_mode in {"multivariate", "channelwise"}:
        return
    raise ValueError(
        f"{method} only supports 1D input. Received 2D input with shape {x.shape}. "
        "Use a multivariate method such as MSSA/MVMD/MEMD or a channelwise-capable method."
    )


def _annotate_result_layout(
    result: DecompResult,
    x: np.ndarray,
    channel_names: list[str] | None,
) -> DecompResult:
    meta = dict(result.meta or {})
    meta.setdefault("input_shape", [int(v) for v in x.shape])
    if x.ndim == 1:
        meta.setdefault("result_layout", "univariate")
        meta.setdefault("n_channels", 1)
        if channel_names:
            meta.setdefault("channel_names", channel_names[:1])
    else:
        meta.setdefault("result_layout", "multivariate")
        meta.setdefault("n_channels", int(x.shape[1]))
        if channel_names:
            meta.setdefault("channel_names", channel_names)
    result.meta = meta
    return result


def decompose(series: np.ndarray, config: DecompositionConfig) -> DecompResult:
    """Main entry point for decomposition."""
    spec = MethodRegistry.get_spec(config.method)
    x = _normalize_input(series)
    _validate_input_mode(config.method, x, spec.input_mode)
    runtime = runtime_options_from_config(config)
    params = inject_runtime_params(config.params, runtime)
    result = spec.func(x, params)
    channel_names = list(config.channel_names or [])
    return _annotate_result_layout(result, x, channel_names or None)
