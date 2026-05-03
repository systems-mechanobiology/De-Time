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
  "backend": "python",
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
  "backend": "python",
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
