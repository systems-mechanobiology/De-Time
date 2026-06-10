# Config Reference

`DecompositionConfig` is the single runtime contract shared by Python, CLI,
docs examples, and machine-facing schema exports.

Current package version target: `0.1.1`.

## Top-level fields

| Field | Type | Default | Semantics |
|---|---|---|---|
| `method` | `str` | required | Registered method name such as `SSA`, `STD`, `STDR`, or `MSSA`. |
| `params` | `dict[str, Any]` | `{}` | Method-specific parameters documented below. |
| `return_components` | `list[str] \| None` | `None` | Compatibility field; retained methods return the normalized result object. |
| `backend` | `auto \| native \| python \| gpu` | `auto` | Backend preference. `native` requires an available native kernel. |
| `speed_mode` | `exact \| fast` | `exact` | Accuracy policy. Native `SSA` uses exact SVD in `exact` and an iterative approximation in `fast`. |
| `profile` | `bool` | `False` | Attach runtime metadata or produce profile reports when routed through the profiler. |
| `device` | `str \| None` | `cpu` | Reserved device selector; retained methods are CPU workflows unless a wrapper says otherwise. |
| `n_jobs` | `int` | `1` | Parallelism hint for wrappers that support it. |
| `seed` | `int \| None` | `42` | Seed used by approximate or randomized paths where relevant. |
| `channel_names` | `list[str] \| None` | `None` | Optional labels for aligned multivariate channels. |

## Complete examples

### Univariate SSA

```json
{
  "backend": "auto",
  "method": "SSA",
  "params": {
    "primary_period": 12,
    "rank": 6,
    "window": 24
  },
  "seed": 42,
  "speed_mode": "exact"
}
```

### Seasonal STD

```json
{
  "backend": "auto",
  "method": "STD",
  "params": {
    "period": 12
  },
  "speed_mode": "exact"
}
```

### Multivariate MSSA

```json
{
  "backend": "auto",
  "channel_names": [
    "channel_a",
    "channel_b",
    "channel_c"
  ],
  "method": "MSSA",
  "params": {
    "primary_period": 12,
    "rank": 6,
    "window": 24
  },
  "speed_mode": "exact"
}
```

## Method-specific parameters

### `AMD_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `multiscale_windows` | list[int] \| None | no | `None` | Smoothing windows averaged into the multiscale trend. |

Example config:

```json
{
  "method": "AMD_BLOCK",
  "params": {
    "fit_scope": "full",
    "multiscale_windows": [
      13,
      25,
      49
    ],
    "primary_period": 12
  }
}
```

### `AUTOFORMER_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.moving_mean`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `moving_avg` | int \| None | no | `None` | Moving-average window used by the extracted forecasting block. |
| `window` | int \| None | no | `None` | Alias for moving_avg. |
| `primary_period` | int \| None | no | `None` | Period hint used to derive the moving-average window. |

Example config:

```json
{
  "method": "AUTOFORMER_BLOCK",
  "params": {
    "moving_avg": 25,
    "primary_period": 12
  }
}
```

### `CEEMDAN`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`, `components.imfs`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `trials` | int | no | `50` | Number of noise-assisted ensemble trials. |
| `noise_width` | float | no | `0.05` | Relative width of the injected noise. |
| `primary_period` | int \| None | no | `None` | Period hint for grouping IMFs into season and trend. |
| `fs` | float | no | `1.0` | Sampling frequency used by grouping heuristics. |

Example config:

```json
{
  "method": "CEEMDAN",
  "params": {
    "noise_width": 0.05,
    "primary_period": 12,
    "trials": 20
  }
}
```

### `DELELSTM_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `alpha` | float | no | `0.4` | Holt level smoothing coefficient. |
| `beta` | float | no | `0.2` | Holt slope smoothing coefficient. |

Example config:

```json
{
  "method": "DELELSTM_BLOCK",
  "params": {
    "alpha": 0.2,
    "beta": 0.1,
    "fit_scope": "full",
    "primary_period": 12
  }
}
```

### `DLINEAR_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.moving_mean`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `moving_avg` | int \| None | no | `None` | Moving-average window used by the extracted forecasting block. |
| `window` | int \| None | no | `None` | Alias for moving_avg. |
| `primary_period` | int \| None | no | `None` | Period hint used to derive the moving-average window. |

Example config:

```json
{
  "method": "DLINEAR_BLOCK",
  "params": {
    "moving_avg": 25,
    "primary_period": 12
  }
}
```

### `EMD`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`, `components.imfs`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `n_imfs` | int \| None | no | `None` | Maximum number of intrinsic mode functions to retain. |
| `primary_period` | int \| None | no | `None` | Period hint for grouping IMFs into season and trend. |
| `trend_imfs` | list[int] \| None | no | `None` | Explicit IMF indexes assigned to trend. |
| `season_imfs` | list[int] \| None | no | `None` | Explicit IMF indexes assigned to season. |
| `fs` | float | no | `1.0` | Sampling frequency used by grouping heuristics. |

Example config:

```json
{
  "method": "EMD",
  "params": {
    "n_imfs": 4,
    "primary_period": 12
  }
}
```

### `FREQMOE_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `trend_window` | int \| None | no | `None` | Moving-average trend window. |
| `num_bands` | int | no | `4` | Number of frequency bands in the mixture. |
| `expert_width` | int | no | `64` | Frequency expert width used by the scaffold. |

Example config:

```json
{
  "method": "FREQMOE_BLOCK",
  "params": {
    "expert_width": 64,
    "fit_scope": "full",
    "num_bands": 4,
    "primary_period": 12
  }
}
```

### `GABOR_CLUSTER`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.clusters`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `model` | GaborClusterModel \| None | no | `None` | In-memory trained clustering model. |
| `model_path` | str \| None | no | `None` | Path to a serialized trained clustering model. |
| `max_clusters` | int \| None | no | `None` | Optional cap on clusters used during reconstruction. |
| `trend_freq_thr` | float \| None | no | `None` | Frequency threshold used for trend-like atoms. |

Example config:

```json
{
  "method": "GABOR_CLUSTER",
  "params": {
    "model_path": "path/to/trained-gabor-model.pkl"
  }
}
```

### `INPARFORMER_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `trend_window` | int \| None | no | `None` | Moving-average trend window. |

Example config:

```json
{
  "method": "INPARFORMER_BLOCK",
  "params": {
    "fit_scope": "full",
    "primary_period": 12,
    "trend_window": 25
  }
}
```

### `LEDDAM_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.ld_trend`, `components.kernel`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `kernel_size` | int | no | `25` | Odd Gaussian smoothing kernel size. |
| `sigma` | float | no | `1.0` | Gaussian smoothing kernel sigma. |

Example config:

```json
{
  "method": "LEDDAM_BLOCK",
  "params": {
    "kernel_size": 25,
    "sigma": 1.0
  }
}
```

### `MA_BASELINE`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `trend_window` | int | no | `7` | Moving-average window used for the trend estimate. |
| `season_period` | int \| None | no | `None` | Optional period for a simple seasonal average. |

Example config:

```json
{
  "method": "MA_BASELINE",
  "params": {
    "season_period": 12,
    "trend_window": 7
  }
}
```

### `MEMD`

- Input mode: `multivariate`
- Maturity: `optional-backend`
- Output components: `trend`, `season`, `residual`, `components.imfs`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Shared period hint for grouping multivariate IMFs. |
| `trend_modes` | list[int] \| None | no | `None` | Explicit mode indexes assigned to trend. |
| `season_modes` | list[int] \| None | no | `None` | Explicit mode indexes assigned to season. |
| `fs` | float | no | `1.0` | Sampling frequency used by grouping heuristics. |

Example config:

```json
{
  "method": "MEMD",
  "params": {
    "primary_period": 12
  }
}
```

### `MOVING_AVERAGE_DECOMPOSITION_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.moving_mean`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `moving_avg` | int \| None | no | `None` | Moving-average window used by the extracted forecasting block. |
| `window` | int \| None | no | `None` | Alias for moving_avg. |
| `primary_period` | int \| None | no | `None` | Period hint used to derive the moving-average window. |

Example config:

```json
{
  "method": "MOVING_AVERAGE_DECOMPOSITION_BLOCK",
  "params": {
    "moving_avg": 25,
    "primary_period": 12
  }
}
```

### `MSSA`

- Input mode: `multivariate`
- Maturity: `flagship`
- Output components: `trend`, `season`, `residual`, `components.elementary`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `window` | int | yes | required | Shared embedding window length for aligned channels. |
| `rank` | int \| None | no | `None` | Number of shared elementary components to retain. |
| `primary_period` | int \| None | no | `None` | Dominant shared period used by automatic grouping. |
| `fs` | float | no | `1.0` | Sampling frequency used by frequency-based grouping. |
| `trend_components` | list[int] \| None | no | `None` | Explicit component indexes assigned to trend. |
| `season_components` | list[int] \| None | no | `None` | Explicit component indexes assigned to season. |

Example config:

```json
{
  "backend": "auto",
  "channel_names": [
    "channel_a",
    "channel_b",
    "channel_c"
  ],
  "method": "MSSA",
  "params": {
    "primary_period": 12,
    "rank": 6,
    "window": 24
  },
  "speed_mode": "exact"
}
```

### `MSTL`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`, `components.seasonal_terms`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `periods` | list[int] | yes | required | One or more seasonal periods passed to statsmodels MSTL. |
| `windows` | list[int] \| None | no | `None` | Optional smoother windows aligned with periods. |
| `stl_kwargs` | dict \| None | no | `None` | Additional statsmodels STL keyword arguments. |

Example config:

```json
{
  "method": "MSTL",
  "params": {
    "periods": [
      12,
      24
    ]
  }
}
```

### `MVMD`

- Input mode: `multivariate`
- Maturity: `optional-backend`
- Output components: `trend`, `season`, `residual`, `components.modes`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `K` | int | no | `4` | Number of shared variational modes requested from PySDKit. |
| `alpha` | float | no | `2000.0` | Bandwidth penalty parameter for the MVMD backend. |
| `primary_period` | int \| None | no | `None` | Shared period hint for grouping modes. |
| `fs` | float | no | `1.0` | Sampling frequency used by grouping heuristics. |

Example config:

```json
{
  "method": "MVMD",
  "params": {
    "K": 4,
    "alpha": 2000.0,
    "primary_period": 12
  }
}
```

### `NBEATS_INTERPRETABLE`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `degree_of_polynomial` | int | no | `3` | Polynomial trend basis degree. |
| `num_harmonics` | int | no | `8` | Number of Fourier harmonics in the seasonality stack. |
| `trend_blocks` | int | no | `2` | Number of interpretable trend blocks. |
| `seasonality_blocks` | int | no | `2` | Number of interpretable seasonality blocks. |
| `layers` | int | no | `6` | Fully connected layers per block. |
| `layer_size` | int | no | `128` | Hidden width for each block. |
| `fit_scope` | str | no | `"full"` | Whether to fit on the full series or prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `n_epochs` | int | no | `200` | Maximum torch optimization epochs. |
| `patience` | int | no | `40` | Early-stopping patience. |
| `restarts` | int | no | `2` | Number of random restarts. |
| `learning_rate` | float | no | `0.001` | Adam learning rate. |
| `weight_decay` | float | no | `0.0001` | Adam weight decay. |
| `device` | str | no | `"auto"` | Torch device: auto, cpu, cuda, or gpu. |
| `seed` | int | no | `0` | Base random seed for torch restarts. |

Example config:

```json
{
  "method": "NBEATS_INTERPRETABLE",
  "params": {
    "fit_scope": "full",
    "n_epochs": 200,
    "num_harmonics": 8,
    "restarts": 2
  }
}
```

### `PARSIMONY_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `trend_window` | int \| None | no | `None` | Moving-average trend window. |
| `num_harmonics` | int | no | `2` | Number of harmonic seasonal terms. |

Example config:

```json
{
  "method": "PARSIMONY_BLOCK",
  "params": {
    "fit_scope": "full",
    "num_harmonics": 2,
    "primary_period": 12,
    "trend_window": 13
  }
}
```

### `ROBUST_STL`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `period` | int | yes | required | Seasonal period passed to robust statsmodels STL. |
| `seasonal` | int \| None | no | `None` | Odd LOESS seasonal smoother length. |
| `trend` | int \| None | no | `None` | Odd LOESS trend smoother length. |

Example config:

```json
{
  "method": "ROBUST_STL",
  "params": {
    "period": 12
  }
}
```

### `SSA`

- Input mode: `univariate`
- Maturity: `flagship`
- Output components: `trend`, `season`, `residual`, `components.elementary`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `window` | int | yes | required | Embedding window length for trajectory-matrix construction. |
| `rank` | int \| None | no | `None` | Number of elementary components to retain before grouping. |
| `primary_period` | int \| None | no | `None` | Dominant seasonal period used by automatic grouping. |
| `fs` | float | no | `1.0` | Sampling frequency used by frequency-based grouping. |
| `trend_components` | list[int] \| None | no | `None` | Explicit component indexes assigned to trend. |
| `season_components` | list[int] \| None | no | `None` | Explicit component indexes assigned to season. |
| `power_iterations` | int | no | `4` | Fast native mode iteration count when speed_mode='fast'. |

Example config:

```json
{
  "backend": "auto",
  "method": "SSA",
  "params": {
    "primary_period": 12,
    "rank": 6,
    "window": 24
  },
  "seed": 42,
  "speed_mode": "exact"
}
```

### `STD`

- Input mode: `channelwise`
- Maturity: `flagship`
- Output components: `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `period` | int | yes | required | Seasonal period in samples. |
| `max_period_search` | int \| None | no | `None` | Optional search horizon when period inference is enabled. |
| `eps` | float | no | `1e-08` | Small numerical guard for dispersion calculations. |

Example config:

```json
{
  "backend": "auto",
  "method": "STD",
  "params": {
    "period": 12
  },
  "speed_mode": "exact"
}
```

### `STDR`

- Input mode: `channelwise`
- Maturity: `flagship`
- Output components: `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `period` | int | yes | required | Seasonal period in samples. |
| `max_period_search` | int \| None | no | `None` | Optional search horizon when period inference is enabled. |
| `eps` | float | no | `1e-08` | Small numerical guard for robust dispersion calculations. |

Example config:

```json
{
  "backend": "auto",
  "method": "STDR",
  "params": {
    "period": 12
  },
  "speed_mode": "exact"
}
```

### `STL`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `period` | int | yes | required | Seasonal period passed to statsmodels STL. |
| `seasonal` | int \| None | no | `None` | Odd LOESS seasonal smoother length. |
| `trend` | int \| None | no | `None` | Odd LOESS trend smoother length. |
| `robust` | bool | no | `false` | Whether to use robust LOESS fitting. |

Example config:

```json
{
  "method": "STL",
  "params": {
    "period": 12
  }
}
```

### `ST_MTM_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `trend_window` | int \| None | no | `None` | Moving-average trend window. |
| `season_smooth_window` | int \| None | no | `None` | Smoother applied to the periodic seasonal template. |

Example config:

```json
{
  "method": "ST_MTM_BLOCK",
  "params": {
    "fit_scope": "full",
    "primary_period": 12,
    "season_smooth_window": 7,
    "trend_window": 13
  }
}
```

### `TIMEKAN_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `trend_window` | int \| None | no | `None` | Moving-average trend window. |
| `num_bands` | int | no | `2` | Number of dominant periods/templates to blend. |
| `kan_width` | int | no | `32` | KAN-inspired width used to choose harmonic capacity. |

Example config:

```json
{
  "method": "TIMEKAN_BLOCK",
  "params": {
    "fit_scope": "full",
    "kan_width": 32,
    "num_bands": 2,
    "primary_period": 12
  }
}
```

### `TIMES2D_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `primary_period` | int \| None | no | `None` | Dominant period hint used by neural block heuristics. |
| `fit_scope` | str | no | `"full"` | Whether to fit templates on the full series or a prefix window. |
| `train_fraction` | float | no | `0.6` | Prefix fraction used when fit_scope='prefix'. |
| `top_k_periods` | int | no | `2` | Number of dominant FFT periods to retain. |
| `num_harmonics` | int | no | `1` | Number of harmonics per selected period. |
| `trend_window` | int \| None | no | `None` | Moving-average trend window. |

Example config:

```json
{
  "method": "TIMES2D_BLOCK",
  "params": {
    "fit_scope": "full",
    "num_harmonics": 1,
    "primary_period": 12,
    "top_k_periods": 2
  }
}
```

### `VMD`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`, `components.modes`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `K` | int | no | `4` | Number of variational modes. |
| `alpha` | float | no | `2000.0` | Bandwidth penalty parameter. |
| `tau` | float | no | `0.0` | Dual ascent time step. |
| `DC` | bool | no | `false` | Keep the first mode at zero frequency. |
| `init` | int | no | `1` | Initialization policy used by the VMD backend. |
| `tol` | float | no | `1e-07` | Convergence tolerance. |
| `primary_period` | int \| None | no | `None` | Period hint for grouping modes into season and trend. |

Example config:

```json
{
  "method": "VMD",
  "params": {
    "K": 4,
    "alpha": 2000.0,
    "primary_period": 12
  }
}
```

### `WAVEFORM_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `wavelet` | str | no | `"db4"` | PyWavelets wavelet family name. |
| `level` | int | no | `3` | Wavelet decomposition depth. |
| `season_levels` | list[int] | no | `[1, 2]` | Detail coefficient levels assigned to the seasonal component. |

Example config:

```json
{
  "method": "WAVEFORM_BLOCK",
  "params": {
    "level": 3,
    "season_levels": [
      1,
      2
    ],
    "wavelet": "sym4"
  }
}
```

### `WAVELET`

- Input mode: `univariate`
- Maturity: `stable`
- Output components: `trend`, `season`, `residual`, `components.coefficients`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `wavelet` | str | no | `"db4"` | PyWavelets wavelet family name. |
| `level` | int \| None | no | `None` | Decomposition depth. Defaults to PyWavelets maximum usable level. |
| `trend_levels` | list[int] \| None | no | `None` | Detail levels assigned to trend reconstruction. |
| `season_levels` | list[int] \| None | no | `None` | Detail levels assigned to seasonal reconstruction. |

Example config:

```json
{
  "method": "WAVELET",
  "params": {
    "level": 3,
    "wavelet": "db4"
  }
}
```

### `WAVELETMIXER_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `wavelet` | str | no | `"sym4"` | PyWavelets wavelet family name. |
| `level` | int | no | `4` | Wavelet decomposition depth. |
| `season_levels` | list[int] | no | `[1, 2, 3]` | Detail coefficient levels assigned to the seasonal component. |

Example config:

```json
{
  "method": "WAVELETMIXER_BLOCK",
  "params": {
    "level": 3,
    "season_levels": [
      1,
      2,
      3
    ],
    "wavelet": "coif1"
  }
}
```

### `XPATCH_BLOCK`

- Input mode: `univariate`
- Maturity: `experimental`
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `ma_type` | str | no | `"ema"` | Smoothing type, either 'ema' or 'dema'. |
| `trend_window` | int \| None | no | `None` | Window used to derive the EMA alpha. |
| `season_smooth` | int \| None | no | `None` | Optional moving-average smoother for the seasonal residual. |
| `alpha` | float \| None | no | `None` | EMA or DEMA level smoothing coefficient. |
| `beta` | float \| None | no | `None` | DEMA slope smoothing coefficient. |

Example config:

```json
{
  "method": "XPATCH_BLOCK",
  "params": {
    "season_smooth": 7,
    "trend_window": 25
  }
}
```
