from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np

from ...core import DecompResult
from ...registry import MethodRegistry

try:
    import torch
    from torch import nn
    _TORCH_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # pragma: no cover - optional dependency
    torch = None
    nn = None
    _TORCH_IMPORT_ERROR = exc


if torch is not None:

    class _TrendBasis(nn.Module):
        def __init__(self, degree: int, length: int):
            super().__init__()
            degree = max(0, int(degree))
            t = torch.linspace(0.0, 1.0, int(length), dtype=torch.float32)
            basis = torch.stack([t**power for power in range(degree + 1)], dim=0)
            self.degree = degree
            self.register_buffer("basis", basis)

        def forward(self, theta: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
            n = self.degree + 1
            backcast = torch.einsum("bp,pt->bt", theta[:, n:], self.basis)
            forecast = torch.einsum("bp,pt->bt", theta[:, :n], self.basis)
            return backcast, forecast


    class _SeasonalityBasis(nn.Module):
        def __init__(self, harmonics: int, length: int):
            super().__init__()
            harmonics = max(1, int(harmonics))
            t = torch.linspace(0.0, 1.0, int(length), dtype=torch.float32)
            freqs = torch.arange(1, harmonics + 1, dtype=torch.float32)[:, None]
            angles = 2.0 * np.pi * freqs * t[None, :]
            self.harmonics = harmonics
            self.register_buffer("cos_basis", torch.cos(angles))
            self.register_buffer("sin_basis", torch.sin(angles))

        def forward(self, theta: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
            h = self.harmonics
            backcast_cos = torch.einsum("bp,pt->bt", theta[:, 2 * h:3 * h], self.cos_basis)
            backcast_sin = torch.einsum("bp,pt->bt", theta[:, 3 * h:], self.sin_basis)
            forecast_cos = torch.einsum("bp,pt->bt", theta[:, :h], self.cos_basis)
            forecast_sin = torch.einsum("bp,pt->bt", theta[:, h:2 * h], self.sin_basis)
            return backcast_cos + backcast_sin, forecast_cos + forecast_sin


    class _NBeatsBlock(nn.Module):
        def __init__(self, input_size: int, theta_size: int, basis: nn.Module, layers: int, layer_size: int):
            super().__init__()
            layers = max(1, int(layers))
            layer_size = max(8, int(layer_size))
            seq = []
            in_features = int(input_size)
            for _ in range(layers):
                seq.append(nn.Linear(in_features, layer_size))
                seq.append(nn.ReLU())
                in_features = layer_size
            self.backbone = nn.Sequential(*seq)
            self.theta = nn.Linear(in_features, int(theta_size))
            self.basis = basis

        def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
            h = self.backbone(x)
            theta = self.theta(h)
            return self.basis(theta)


    class _InterpretableNBeatsDecomposer(nn.Module):
        def __init__(
            self,
            length: int,
            trend_blocks: int,
            seasonality_blocks: int,
            layers: int,
            layer_size: int,
            degree_of_polynomial: int,
            num_harmonics: int,
        ):
            super().__init__()
            length = int(length)
            degree_of_polynomial = max(0, int(degree_of_polynomial))
            num_harmonics = max(1, int(num_harmonics))
            self.trend_blocks = nn.ModuleList(
                [
                    _NBeatsBlock(
                        input_size=length,
                        theta_size=2 * (degree_of_polynomial + 1),
                        basis=_TrendBasis(degree_of_polynomial, length),
                        layers=layers,
                        layer_size=layer_size,
                    )
                    for _ in range(max(1, int(trend_blocks)))
                ]
            )
            self.seasonality_blocks = nn.ModuleList(
                [
                    _NBeatsBlock(
                        input_size=length,
                        theta_size=4 * num_harmonics,
                        basis=_SeasonalityBasis(num_harmonics, length),
                        layers=layers,
                        layer_size=layer_size,
                    )
                    for _ in range(max(1, int(seasonality_blocks)))
                ]
            )

        def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            residual = x
            trend = torch.zeros_like(x)
            season = torch.zeros_like(x)

            for block in self.trend_blocks:
                backcast, forecast = block(residual)
                residual = residual - backcast
                trend = trend + forecast

            for block in self.seasonality_blocks:
                backcast, forecast = block(residual)
                residual = residual - backcast
                season = season + forecast

            return trend, season, residual


@dataclass
class _FitResult:
    trend: np.ndarray
    season: np.ndarray
    residual: np.ndarray
    meta: Dict[str, Any]


def _require_torch() -> None:
    if torch is None:
        raise ImportError(
            "NBEATS_INTERPRETABLE requires the optional dependency 'torch'. "
            "Install 'de-time[neural]' or torch before running this method in DeTime. "
            f"Original import error: {_TORCH_IMPORT_ERROR!r}"
        )


def _resolve_device(device: Any) -> "torch.device":
    _require_torch()
    requested = str(device or "auto").strip().lower()
    if requested in {"cuda", "gpu"} and torch.cuda.is_available():
        return torch.device("cuda")
    if requested == "auto" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _standardize_series(y: np.ndarray) -> Tuple[np.ndarray, float, float]:
    arr = np.asarray(y, dtype=float).reshape(-1)
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    if not np.isfinite(std) or std < 1e-8:
        std = 1.0
    return (arr - mean) / std, mean, std


def _fit_interpretable_nbeats(y: np.ndarray, params: Dict[str, Any]) -> _FitResult:
    _require_torch()
    series = np.asarray(y, dtype=float).reshape(-1)
    length = int(series.size)
    fit_scope = str(params.get("fit_scope", "full")).strip().lower()
    train_fraction = float(params.get("train_fraction", 0.6))
    train_end = max(8, min(length, int(round(length * train_fraction))))

    series_norm, mean, std = _standardize_series(series)
    observed = series_norm.copy()
    loss_mask = np.ones(length, dtype=np.float32)
    if fit_scope == "prefix":
        observed[train_end:] = 0.0
        loss_mask[train_end:] = 0.0

    learning_rate = float(params.get("learning_rate", 1e-3))
    weight_decay = float(params.get("weight_decay", 1e-4))
    n_epochs = int(params.get("n_epochs", 200))
    patience = int(params.get("patience", 40))
    restarts = int(params.get("restarts", 2))
    layers = int(params.get("layers", 4))
    layer_size = int(params.get("layer_size", 128))
    trend_blocks = int(params.get("trend_blocks", 3))
    seasonality_blocks = int(params.get("seasonality_blocks", 3))
    degree_of_polynomial = int(params.get("degree_of_polynomial", 2))
    num_harmonics = int(params.get("num_harmonics", 8))
    base_seed = int(params.get("seed", 42))

    device = _resolve_device(params.get("device", "auto"))
    x = torch.tensor(observed, dtype=torch.float32, device=device).unsqueeze(0)
    target = torch.tensor(series_norm, dtype=torch.float32, device=device).unsqueeze(0)
    mask = torch.tensor(loss_mask, dtype=torch.float32, device=device).unsqueeze(0)

    best_loss = float("inf")
    best_payload: Dict[str, Any] | None = None

    for restart in range(max(1, restarts)):
        torch.manual_seed(base_seed + restart)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(base_seed + restart)

        model = _InterpretableNBeatsDecomposer(
            length=length,
            trend_blocks=trend_blocks,
            seasonality_blocks=seasonality_blocks,
            layers=layers,
            layer_size=layer_size,
            degree_of_polynomial=degree_of_polynomial,
            num_harmonics=num_harmonics,
        ).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

        best_restart_loss = float("inf")
        best_restart_state: Dict[str, Any] | None = None
        stale = 0

        for epoch in range(max(1, n_epochs)):
            model.train()
            optimizer.zero_grad(set_to_none=True)
            trend_pred, season_pred, _ = model(x)
            recon = trend_pred + season_pred
            denom = torch.clamp(mask.sum(), min=1.0)
            loss = (((recon - target) ** 2) * mask).sum() / denom
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            loss_value = float(loss.detach().cpu().item())
            if loss_value + 1e-8 < best_restart_loss:
                best_restart_loss = loss_value
                best_restart_state = {
                    "model": {key: value.detach().cpu().clone() for key, value in model.state_dict().items()},
                    "epoch": epoch + 1,
                }
                stale = 0
            else:
                stale += 1
                if stale >= max(1, patience):
                    break

        if best_restart_state is None:
            continue

        model.load_state_dict(best_restart_state["model"])
        model.eval()
        with torch.no_grad():
            trend_pred, season_pred, _ = model(x)
        trend_np = trend_pred.squeeze(0).detach().cpu().numpy().astype(float)
        season_np = season_pred.squeeze(0).detach().cpu().numpy().astype(float)
        trend_out = trend_np * std + mean
        season_out = season_np * std
        residual_out = series - trend_out - season_out

        if best_restart_loss < best_loss:
            best_loss = best_restart_loss
            best_payload = {
                "trend": trend_out,
                "season": season_out,
                "residual": residual_out,
                "epoch": int(best_restart_state["epoch"]),
                "restart": restart,
                "device": str(device),
            }

    if best_payload is None:
        raise RuntimeError("N-BEATS interpretable fitting failed to produce a valid model state.")

    return _FitResult(
        trend=np.asarray(best_payload["trend"], dtype=float),
        season=np.asarray(best_payload["season"], dtype=float),
        residual=np.asarray(best_payload["residual"], dtype=float),
        meta={
            "method": "NBEATS_INTERPRETABLE",
            "block_family": "backprop_learned_decomposition_prior",
            "fit_scope": fit_scope,
            "train_fraction": train_fraction,
            "best_loss": float(best_loss),
            "best_epoch": int(best_payload["epoch"]),
            "best_restart": int(best_payload["restart"]),
            "device_used": str(best_payload["device"]),
            "trend_blocks": trend_blocks,
            "seasonality_blocks": seasonality_blocks,
            "layers": layers,
            "layer_size": layer_size,
            "degree_of_polynomial": degree_of_polynomial,
            "num_harmonics": num_harmonics,
        },
    )


@MethodRegistry.register("NBEATS_INTERPRETABLE")
def nbeats_interpretable_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    fit = _fit_interpretable_nbeats(y, params or {})
    return DecompResult(
        trend=fit.trend,
        season=fit.season,
        residual=fit.residual,
        components={
            "trend": fit.trend.copy(),
            "season": fit.season.copy(),
        },
        meta=dict(fit.meta),
    )
