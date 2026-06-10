# Method References

This page is generated from `MethodRegistry.list_catalog()` so citations,
upstream package links, and method metadata stay aligned.

Current package version target: `0.1.1`.

These links cover the method families and upstream packages used or compared
in the public DeTime workflow surface. `MA_BASELINE` is an in-package smoke
baseline and therefore has no separate upstream citation.

## Flagship methods

### `MSSA`

- Summary: Multivariate SSA for shared-structure decomposition across channels.
- Optional/runtime dependencies: none

Primary references:
- [Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series](https://link.springer.com/book/10.1007/978-3-662-62436-4) - Primary SSA/MSSA reference used for the multivariate extension.

Related packages:
- [SSALib](https://github.com/ADSCIAN/ssalib) - SSA-focused package; useful comparison point for SSA-family workflows.

### `SSA`

- Summary: Singular spectrum analysis for structured univariate decomposition.
- Optional/runtime dependencies: none

Primary references:
- [Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series](https://link.springer.com/book/10.1007/978-3-662-62436-4) - Primary SSA reference; the second edition also covers multivariate SSA (MSSA).

Related packages:
- [SSALib](https://github.com/ADSCIAN/ssalib) - Specialist SSA package used as an external comparison point.

### `STD`

- Summary: Fast seasonal-trend decomposition with dispersion-aware diagnostics.
- Optional/runtime dependencies: none

Primary references:
- [Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series](https://doi.org/10.48550/arXiv.2204.10398) - Primary reference for STD and the robust seasonal-trend-dispersion family.

Related packages:
- none declared

### `STDR`

- Summary: Robust seasonal-trend decomposition for noisier periodic signals.
- Optional/runtime dependencies: none

Primary references:
- [Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series](https://doi.org/10.48550/arXiv.2204.10398) - Primary reference for STD and the robust seasonal-trend-dispersion family.

Related packages:
- none declared

## Stable wrappers and retained methods

### `CEEMDAN`

- Summary: Noise-assisted EMD variant for more stable IMF extraction.
- Optional/runtime dependencies: PyEMD

Primary references:
- [Torres et al. (2011), A complete ensemble empirical mode decomposition with adaptive noise](https://pyemd.readthedocs.io/en/latest/ceemdan.html) - PyEMD CEEMDAN docs cite the original ICASSP 2011 paper.
- [Colominas, Schlotthauer, and Torres (2014), Improved complete ensemble EMD: A suitable tool for biomedical signal processing](https://pyemd.readthedocs.io/en/latest/ceemdan.html) - Improved CEEMDAN variant adopted by the PyEMD implementation used by DeTime.

Related packages:
- [PyEMD](https://github.com/laszukdawid/PyEMD) - Upstream Python package wrapped by DeTime for EMD-family methods.

### `EMD`

- Summary: Empirical mode decomposition under the DeTime result contract.
- Optional/runtime dependencies: PyEMD

Primary references:
- [Huang et al. (1998), The empirical mode decomposition and the Hilbert spectrum for nonlinear and non-stationary time series analysis](https://doi.org/10.1098/rspa.1998.0193) - Primary empirical mode decomposition reference.

Related packages:
- [PyEMD](https://github.com/laszukdawid/PyEMD) - Upstream Python package wrapped by DeTime for EMD-family methods.

### `MA_BASELINE`

- Summary: Simple moving-average baseline for smoke tests and lightweight workflows.
- Optional/runtime dependencies: none

Primary references:
- none declared

Related packages:
- none declared

### `MSTL`

- Summary: Statsmodels MSTL wrapped into the DeTime workflow surface.
- Optional/runtime dependencies: statsmodels

Primary references:
- [Bandara, Hyndman, and Bergmeir (2021), MSTL: A Seasonal-Trend Decomposition Algorithm for Time Series with Multiple Seasonal Patterns](https://arxiv.org/abs/2107.13462) - Primary MSTL reference used by the statsmodels implementation.

Related packages:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream MSTL implementation.

### `ROBUST_STL`

- Summary: Robust STL-style decomposition wrapped for reproducible workflows.
- Optional/runtime dependencies: statsmodels

Primary references:
- [Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html) - Robust STL in DeTime builds on the same STL literature and upstream implementation family.

Related packages:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream STL implementation family.

### `STL`

- Summary: Classical STL wrapped into the DeTime workflow contract.
- Optional/runtime dependencies: statsmodels

Primary references:
- [Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html) - Statsmodels STL docs cite the original Journal of Official Statistics paper.

Related packages:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream STL implementation.

### `VMD`

- Summary: Variational mode decomposition integrated into the common workflow layer.
- Optional/runtime dependencies: vmdpy, sktime

Primary references:
- [Dragomiretskiy and Zosso (2014), Variational Mode Decomposition](https://doi.org/10.1109/TSP.2013.2288675) - Primary variational mode decomposition reference.

Related packages:
- [sktime](https://www.sktime.net/en/stable/) - Current maintained ecosystem for `vmdpy`, which the archived project directs users toward.
- [vmdpy](https://github.com/vrcarva/vmdpy) - Archived Python VMD package used by the current DeTime wrapper.

### `WAVELET`

- Summary: Wavelet-based decomposition exposed through the common output contract.
- Optional/runtime dependencies: PyWavelets

Primary references:
- [Mallat (1989), A theory for multiresolution signal decomposition: the wavelet representation](https://ieeexplore.ieee.org/document/192463) - Foundational wavelet multiresolution reference.
- [Lee et al. (2019), PyWavelets: A Python package for wavelet analysis](https://doi.org/10.21105/joss.01237) - Package citation for the upstream wavelet implementation used by DeTime.

Related packages:
- [PyWavelets](https://pywavelets.readthedocs.io/en/latest/) - Official documentation for the upstream wavelet package.

## Optional backend methods

### `MEMD`

- Summary: Optional multivariate EMD backend for shared oscillatory structure.
- Optional/runtime dependencies: PySDKit

Primary references:
- [Rehman and Mandic (2010), Multivariate empirical mode decomposition](https://doi.org/10.1098/rspa.2009.0502) - Primary MEMD reference for the multivariate EMD extension.

Related packages:
- [PySDKit](https://pysdkit.readthedocs.io/en/latest/) - Optional multivariate backend used by DeTime for MEMD.

### `MVMD`

- Summary: Optional multivariate VMD backend for shared frequency structure.
- Optional/runtime dependencies: PySDKit

Primary references:
- [Rehman and Aftab (2019), Multivariate Variational Mode Decomposition](https://arxiv.org/abs/1907.04509) - Primary MVMD reference for the multivariate VMD extension.

Related packages:
- [PySDKit](https://pysdkit.readthedocs.io/en/latest/) - Optional multivariate backend used by DeTime for MVMD.

## Experimental methods

### `AMD_BLOCK`

- Summary: AMD-inspired multiscale smoothing head with periodic-template seasonal reconstruction.
- Optional/runtime dependencies: none

Primary references:
- [Hu et al. (2024), Adaptive Multi-Scale Decomposition Framework for Time Series Forecasting](https://arxiv.org/abs/2406.03751) - Source framework for adaptive multiscale decomposition.

Related packages:
- none declared

### `AUTOFORMER_BLOCK`

- Summary: Standalone moving-average decomposition head extracted from the Autoformer architecture.
- Optional/runtime dependencies: none

Primary references:
- [Wu et al. (2021), Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting](https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html) - Source architecture for the moving-average decomposition block exposed by AUTOFORMER_BLOCK.

Related packages:
- none declared

### `DELELSTM_BLOCK`

- Summary: DeLELSTM-inspired Holt trend plus periodic-template seasonal decomposition head.
- Optional/runtime dependencies: none

Primary references:
- [Wang et al. (2023), DeLELSTM: Decomposition-based Linear Explainable LSTM to Capture Instantaneous and Long-term Effects in Time Series](https://arxiv.org/abs/2308.13797) - Source model for decomposition-based explainable LSTM effects.

Related packages:
- none declared

### `DLINEAR_BLOCK`

- Summary: Standalone moving-average decomposition head extracted from DLinear-style forecasting blocks.
- Optional/runtime dependencies: none

Primary references:
- [Zeng et al. (2023), Are Transformers Effective for Time Series Forecasting?](https://ojs.aaai.org/index.php/AAAI/article/view/26317) - Introduces the LTSF-Linear family, including the DLinear decomposition-based linear model.

Related packages:
- none declared

### `FREQMOE_BLOCK`

- Summary: FreqMoE-inspired frequency mixture head for trend plus multi-band seasonal reconstruction.
- Optional/runtime dependencies: none

Primary references:
- [Liu (2025), FreqMoE: Enhancing Time Series Forecasting through Frequency Decomposition Mixture of Experts](https://arxiv.org/abs/2501.15125) - Source architecture for frequency decomposition mixture-of-experts forecasting.

Related packages:
- none declared

### `GABOR_CLUSTER`

- Summary: Experimental clustering-based decomposition path.
- Optional/runtime dependencies: faiss

Primary references:
- [Gabor (1946), Theory of Communication](https://www.rctn.org/w/images/b/b6/Gabor.pdf) - Historical reference for the Gabor time-frequency representation family.
- [Douze et al. (2024), The Faiss library](https://arxiv.org/abs/2401.08281) - Reference for the similarity-search backend used by the experimental clustering path.

Related packages:
- [Faiss](https://github.com/facebookresearch/faiss) - Vector similarity search library required by the experimental clustering backend.

### `INPARFORMER_BLOCK`

- Summary: InParformer-inspired moving-average trend plus periodic-template seasonal decomposition head.
- Optional/runtime dependencies: none

Primary references:
- [Cao et al. (2023), InParformer: Evolutionary Decomposition Transformers with Interactive Parallel Attention for Long-Term Time Series Forecasting](https://ojs.aaai.org/index.php/AAAI/article/view/25845) - Source architecture for evolutionary seasonal-trend decomposition in a transformer forecaster.

Related packages:
- none declared

### `LEDDAM_BLOCK`

- Summary: LEDDAM LD smoothing block exposed as a Gaussian-kernel decomposition operator.
- Optional/runtime dependencies: none

Primary references:
- [Yu et al. (2024), Revitalizing Multivariate Time Series Forecasting: Learnable Decomposition with Inter-Series Dependencies and Intra-Series Variations Modeling](https://arxiv.org/abs/2402.12694) - Introduces LEDDAM, the learnable decomposition and dual-attention module.

Related packages:
- none declared

### `MOVING_AVERAGE_DECOMPOSITION_BLOCK`

- Summary: Generic neural forecasting moving-average decomposition block exposed as a DeTime method.
- Optional/runtime dependencies: none

Primary references:
- [Wu et al. (2021), Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting](https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html) - Primary source for treating moving-average series decomposition as an internal neural forecasting block.
- [Zeng et al. (2023), Are Transformers Effective for Time Series Forecasting?](https://ojs.aaai.org/index.php/AAAI/article/view/26317) - Uses decomposition-based linear forecasting as a simple long-term forecasting baseline.

Related packages:
- none declared

### `NBEATS_INTERPRETABLE`

- Summary: Torch-backed interpretable N-BEATS trend and seasonality stacks used as a learned decomposition prior.
- Optional/runtime dependencies: torch

Primary references:
- [Oreshkin et al. (2020), N-BEATS: Neural basis expansion analysis for interpretable time series forecasting](https://openreview.net/forum?id=r1ecqn4YwB) - Source for interpretable trend and seasonality basis stacks.

Related packages:
- none declared

### `PARSIMONY_BLOCK`

- Summary: Parsimony-inspired trend head with compact harmonic seasonal projection.
- Optional/runtime dependencies: none

Primary references:
- [Deng et al. (2024), Parsimony or Capability? Decomposition Delivers Both in Long-term Time Series Forecasting](https://arxiv.org/abs/2401.11929) - Source paper for parameter-efficient decomposition in long-term forecasting.

Related packages:
- none declared

### `ST_MTM_BLOCK`

- Summary: ST-MTM-inspired smoothing head combining trend smoothing and smoothed periodic seasonality.
- Optional/runtime dependencies: none

Primary references:
- [Seo and Lim (2025), ST-MTM: Masked Time Series Modeling with Seasonal-Trend Decomposition for Time Series Forecasting](https://arxiv.org/abs/2507.00013) - Source method for seasonal-trend masked time-series modeling.

Related packages:
- none declared

### `TIMEKAN_BLOCK`

- Summary: TimeKAN-inspired decomposition head blending template and harmonic seasonal estimates.
- Optional/runtime dependencies: none

Primary references:
- [Huang et al. (2025), TimeKAN: KAN-based Frequency Decomposition Learning Architecture for Long-term Time Series Forecasting](https://arxiv.org/abs/2502.06910) - Source method for KAN-based frequency decomposition learning.

Related packages:
- none declared

### `TIMES2D_BLOCK`

- Summary: Times2D-inspired multi-period harmonic decomposition head.
- Optional/runtime dependencies: none

Primary references:
- [Nematirad, Pahwa, and Natarajan (2025), Times2D: Multi-Period Decomposition and Derivative Mapping for General Time Series Forecasting](https://arxiv.org/abs/2504.00118) - Source method for multi-period decomposition and 2D time-series mapping.

Related packages:
- none declared

### `WAVEFORM_BLOCK`

- Summary: WaveForM-inspired wavelet multiresolution decomposition head.
- Optional/runtime dependencies: PyWavelets

Primary references:
- [Yang et al. (2023), WaveForM: Graph Enhanced Wavelet Learning for Long Sequence Forecasting of Multivariate Time Series](https://ojs.aaai.org/index.php/AAAI/article/view/26276) - Source architecture for graph-enhanced wavelet learning.

Related packages:
- none declared

### `WAVELETMIXER_BLOCK`

- Summary: WaveletMixer-inspired multiresolution decomposition head using mixed wavelet detail levels.
- Optional/runtime dependencies: PyWavelets

Primary references:
- [Zhang et al. (2025), WaveletMixer: A Multi-Resolution Wavelets Based MLP-Mixer for Multivariate Long-Term Time Series Forecasting](https://ojs.aaai.org/index.php/AAAI/article/view/34434) - Source method for multi-resolution wavelet mixer forecasting.

Related packages:
- none declared

### `XPATCH_BLOCK`

- Summary: xPatch-inspired exponential smoothing head for standalone trend and local-season decomposition.
- Optional/runtime dependencies: none

Primary references:
- [Stitsyuk and Choi (2024), xPatch: Dual-Stream Time Series Forecasting with Exponential Seasonal-Trend Decomposition](https://arxiv.org/abs/2412.17323) - Source architecture for exponential seasonal-trend decomposition.

Related packages:
- none declared
