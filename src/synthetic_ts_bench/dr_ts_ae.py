"""DR-TS-AE: Structured Autoencoder for Time Series Decomposition.

This module implements a neural network approach to decompose time series into
trend, seasonal, and residual components using specialized decoder branches.

Architecture:
    - 1D Conv Encoder → Latent embeddings (z_T for trend, z_S for seasonal)
    - Trend Decoder: Low-pass / smooth reconstruction branch
    - Seasonal Decoder: Periodic / narrow-band reconstruction branch
    - Residual is computed as: r = x - trend - seasonal

Training Objective:
    L = ReconstructionLoss + α_T*TrendSmoothness + α_S*SeasonalPeriodicity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False
    torch = None
    nn = None


@dataclass
class DRTSAEConfig:
    """Configuration for DR-TS-AE model.
    
    Attributes
    ----------
    latent_dim : int
        Dimension of latent space for each branch.
    hidden_channels : List[int]
        Channel sizes for encoder conv layers.
    kernel_size : int
        Kernel size for conv layers.
    alpha_T : float
        Weight for trend smoothness regularization.
    alpha_S : float
        Weight for seasonal periodicity regularization.
    period : int
        Expected seasonal period (for regularization).
    learning_rate : float
        Learning rate for training.
    n_epochs : int
        Number of training epochs.
    batch_size : int
        Batch size for training.
    """
    latent_dim: int = 16
    hidden_channels: List[int] = field(default_factory=lambda: [32, 64])
    kernel_size: int = 7
    alpha_T: float = 10.0
    alpha_S: float = 5.0
    period: int = 32
    learning_rate: float = 1e-3
    n_epochs: int = 100
    batch_size: int = 32


if _HAS_TORCH:
    class StructuredAE(nn.Module):
        """Structured Autoencoder for time series decomposition.
        
        The model has:
        - Shared 1D conv encoder
        - Two latent vectors: z_trend and z_seasonal
        - Two decoder branches producing trend and seasonal components
        """
        
        def __init__(
            self,
            input_length: int,
            latent_dim: int = 16,
            hidden_channels: Optional[List[int]] = None,
            kernel_size: int = 7,
        ):
            super().__init__()
            
            if hidden_channels is None:
                hidden_channels = [32, 64]
            
            self.input_length = input_length
            self.latent_dim = latent_dim
            self.hidden_channels = hidden_channels
            
            # Encoder layers
            enc_layers = []
            in_ch = 1
            for out_ch in hidden_channels:
                enc_layers.extend([
                    nn.Conv1d(in_ch, out_ch, kernel_size, padding=kernel_size // 2),
                    nn.BatchNorm1d(out_ch),
                    nn.ReLU(),
                    nn.MaxPool1d(2),
                ])
                in_ch = out_ch
            
            self.encoder = nn.Sequential(*enc_layers)
            
            # Calculate encoded length after pooling
            self.encoded_length = input_length // (2 ** len(hidden_channels))
            self.flat_dim = hidden_channels[-1] * self.encoded_length
            
            # Latent projections
            self.fc_trend = nn.Linear(self.flat_dim, latent_dim)
            self.fc_seasonal = nn.Linear(self.flat_dim, latent_dim)
            
            # Trend decoder (smooth, low-pass)
            self.trend_fc = nn.Linear(latent_dim, self.flat_dim)
            trend_dec = []
            in_ch = hidden_channels[-1]
            for i, out_ch in enumerate(reversed(hidden_channels[:-1])):
                trend_dec.extend([
                    nn.Upsample(scale_factor=2, mode='linear', align_corners=False),
                    nn.Conv1d(in_ch, out_ch, kernel_size, padding=kernel_size // 2),
                    nn.BatchNorm1d(out_ch),
                    nn.ReLU(),
                ])
                in_ch = out_ch
            # Final layer
            trend_dec.extend([
                nn.Upsample(scale_factor=2, mode='linear', align_corners=False),
                nn.Conv1d(in_ch, 1, kernel_size * 2 - 1, padding=(kernel_size * 2 - 1) // 2),
            ])
            self.trend_decoder = nn.Sequential(*trend_dec)
            
            # Seasonal decoder (periodic-aware)
            self.seasonal_fc = nn.Linear(latent_dim, self.flat_dim)
            seasonal_dec = []
            in_ch = hidden_channels[-1]
            for i, out_ch in enumerate(reversed(hidden_channels[:-1])):
                seasonal_dec.extend([
                    nn.Upsample(scale_factor=2, mode='linear', align_corners=False),
                    nn.Conv1d(in_ch, out_ch, kernel_size, padding=kernel_size // 2),
                    nn.BatchNorm1d(out_ch),
                    nn.ReLU(),
                ])
                in_ch = out_ch
            seasonal_dec.extend([
                nn.Upsample(scale_factor=2, mode='linear', align_corners=False),
                nn.Conv1d(in_ch, 1, kernel_size, padding=kernel_size // 2),
            ])
            self.seasonal_decoder = nn.Sequential(*seasonal_dec)
        
        def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
            """Encode input to latent representations."""
            # x: (batch, 1, length)
            h = self.encoder(x)
            h_flat = h.view(h.size(0), -1)
            z_trend = self.fc_trend(h_flat)
            z_seasonal = self.fc_seasonal(h_flat)
            return z_trend, z_seasonal
        
        def decode_trend(self, z: torch.Tensor) -> torch.Tensor:
            """Decode trend latent to trend component."""
            h = self.trend_fc(z)
            h = h.view(h.size(0), self.hidden_channels[-1], self.encoded_length)
            trend = self.trend_decoder(h)
            # Ensure output matches input length
            if trend.size(-1) != self.input_length:
                trend = F.interpolate(trend, size=self.input_length, mode='linear', align_corners=False)
            return trend
        
        def decode_seasonal(self, z: torch.Tensor) -> torch.Tensor:
            """Decode seasonal latent to seasonal component."""
            h = self.seasonal_fc(z)
            h = h.view(h.size(0), self.hidden_channels[-1], self.encoded_length)
            seasonal = self.seasonal_decoder(h)
            if seasonal.size(-1) != self.input_length:
                seasonal = F.interpolate(seasonal, size=self.input_length, mode='linear', align_corners=False)
            return seasonal
        
        def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            """Forward pass returning trend, seasonal, and reconstruction."""
            z_trend, z_seasonal = self.encode(x)
            trend = self.decode_trend(z_trend)
            seasonal = self.decode_seasonal(z_seasonal)
            recon = trend + seasonal
            return trend, seasonal, recon


def _second_diff_loss(x: "torch.Tensor") -> "torch.Tensor":
    """Compute second-order difference penalty for smoothness."""
    if x.size(-1) < 3:
        return torch.tensor(0.0, device=x.device)
    diff2 = x[..., 2:] - 2 * x[..., 1:-1] + x[..., :-2]
    return torch.mean(diff2 ** 2)


def _seasonal_lag_loss(x: "torch.Tensor", period: int) -> "torch.Tensor":
    """Compute seasonal periodicity penalty."""
    if period >= x.size(-1) or period < 1:
        return torch.tensor(0.0, device=x.device)
    diff = x[..., period:] - x[..., :-period]
    return torch.mean(diff ** 2)


def train_structured_ae(
    series_list: List[np.ndarray],
    config: Optional[DRTSAEConfig] = None,
    device: str = 'cpu',
    verbose: bool = False,
) -> "StructuredAE":
    """Train a StructuredAE model on a list of time series.
    
    Parameters
    ----------
    series_list : List[np.ndarray]
        List of 1D numpy arrays (training data).
    config : DRTSAEConfig, optional
        Model and training configuration.
    device : str
        Device to train on ('cpu' or 'cuda').
    verbose : bool
        Whether to print training progress.
        
    Returns
    -------
    StructuredAE
        Trained model.
    """
    if not _HAS_TORCH:
        raise ImportError("PyTorch is required for DR-TS-AE.")
    
    cfg = config or DRTSAEConfig()
    
    # Determine input length (use most common length or pad)
    lengths = [len(s) for s in series_list]
    input_length = max(lengths)
    
    # Pad/truncate series to same length
    data = []
    for s in series_list:
        s = np.asarray(s, dtype=np.float32).ravel()
        if len(s) < input_length:
            s = np.pad(s, (0, input_length - len(s)), mode='edge')
        elif len(s) > input_length:
            s = s[:input_length]
        # Normalize
        s_mean, s_std = s.mean(), s.std() + 1e-8
        s = (s - s_mean) / s_std
        data.append(s)
    
    X = np.stack(data, axis=0)[:, np.newaxis, :]  # (N, 1, L)
    X_tensor = torch.tensor(X, dtype=torch.float32)
    
    dataset = TensorDataset(X_tensor)
    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True)
    
    # Build model
    model = StructuredAE(
        input_length=input_length,
        latent_dim=cfg.latent_dim,
        hidden_channels=cfg.hidden_channels,
        kernel_size=cfg.kernel_size,
    ).to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate)
    
    model.train()
    for epoch in range(cfg.n_epochs):
        total_loss = 0.0
        for (batch,) in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            
            trend, seasonal, recon = model(batch)
            
            # Reconstruction loss
            recon_loss = F.mse_loss(recon, batch)
            
            # Regularization
            trend_smooth_loss = _second_diff_loss(trend)
            seasonal_period_loss = _seasonal_lag_loss(seasonal, cfg.period)
            
            loss = recon_loss + cfg.alpha_T * trend_smooth_loss + cfg.alpha_S * seasonal_period_loss
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * batch.size(0)
        
        if verbose and (epoch + 1) % 20 == 0:
            avg_loss = total_loss / len(X)
            print(f"Epoch {epoch+1}/{cfg.n_epochs}, Loss: {avg_loss:.6f}")
    
    model.eval()
    return model


def decompose_with_ae(
    y: np.ndarray,
    model: "StructuredAE",
    device: str = 'cpu',
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Decompose a single series using a trained StructuredAE.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series.
    model : StructuredAE
        Trained model.
    device : str
        Device to run inference on.
        
    Returns
    -------
    trend : np.ndarray
    seasonal : np.ndarray
    residual : np.ndarray
    """
    if not _HAS_TORCH:
        raise ImportError("PyTorch is required for DR-TS-AE.")
    
    y_arr = np.asarray(y, dtype=np.float32).ravel()
    n = len(y_arr)
    input_length = model.input_length
    
    # Store normalization params
    y_mean, y_std = y_arr.mean(), y_arr.std() + 1e-8
    y_norm = (y_arr - y_mean) / y_std
    
    # Pad/truncate
    if n < input_length:
        y_padded = np.pad(y_norm, (0, input_length - n), mode='edge')
    elif n > input_length:
        y_padded = y_norm[:input_length]
    else:
        y_padded = y_norm
    
    x_tensor = torch.tensor(y_padded[np.newaxis, np.newaxis, :], dtype=torch.float32).to(device)
    
    model.eval()
    with torch.no_grad():
        trend_t, seasonal_t, _ = model(x_tensor)
    
    trend = trend_t.cpu().numpy().squeeze()
    seasonal = seasonal_t.cpu().numpy().squeeze()
    
    # Truncate/pad back to original length
    if n < input_length:
        trend = trend[:n]
        seasonal = seasonal[:n]
    elif n > input_length:
        # Extrapolate by repeating edge
        trend = np.pad(trend, (0, n - input_length), mode='edge')
        seasonal = np.pad(seasonal, (0, n - input_length), mode='edge')
    
    # Denormalize
    trend = trend * y_std + y_mean * (trend.mean() / (trend.mean() + 1e-8) if abs(trend.mean()) > 1e-8 else 0)
    # Keep seasonal zero-mean
    seasonal = seasonal * y_std
    
    # Adjust to ensure reconstruction
    # trend should capture the mean/level, seasonal should be zero-mean
    trend_offset = y_arr.mean() - (trend + seasonal).mean()
    trend = trend + trend_offset
    
    residual = y_arr - trend - seasonal
    
    return trend, seasonal, residual


# Global model cache
_MODEL_CACHE: Dict[str, "StructuredAE"] = {}


def dr_ts_ae_decompose(
    y: np.ndarray,
    config: Optional[Dict[str, Any]] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> "DecompResult":
    """DR-TS-AE decomposition using a structured autoencoder.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series.
    config : dict, optional
        Configuration with keys: model_path, latent_dim, period, etc.
    fs : float
        Sampling frequency (not directly used).
    meta : dict, optional
        Metadata from scenario.
        
    Returns
    -------
    DecompResult
        Decomposition result.
    """
    from .decomp_methods import DecompResult
    
    if not _HAS_TORCH:
        # Fallback to simple decomposition
        y_arr = np.asarray(y, dtype=float).ravel()
        n = len(y_arr)
        window = max(3, n // 10)
        trend = np.convolve(y_arr, np.ones(window) / window, mode='same')
        residual = y_arr - trend
        seasonal = np.zeros(n)
        return DecompResult(
            trend=trend,
            season=seasonal,
            residual=residual,
            extra={'method': 'dr_ts_ae', 'fallback': 'no_torch'},
        )
    
    y_arr = np.asarray(y, dtype=float).ravel()
    cfg = dict(config or {})
    
    model_path = cfg.get('model_path')
    device = cfg.get('device', 'cpu')
    cache_model = bool(cfg.get('cache_model', True))
    cache_key = cfg.get('cache_key')
    
    # Check if we have a pre-trained model
    model = None
    if model_path and Path(model_path).exists():
        path_key = str(model_path)
        if path_key not in _MODEL_CACHE:
            _MODEL_CACHE[path_key] = torch.load(model_path, map_location=device)
        model = _MODEL_CACHE[path_key]

    if model is None and cache_model:
        if cache_key is None:
            period_val = cfg.get('period')
            if period_val is None and meta:
                period_val = meta.get('primary_period')
            period_val = int(period_val) if period_val not in (None, 0) else 32
            hidden = cfg.get('hidden_channels', [32, 64])
            cache_key = (
                f"auto_len{len(y_arr)}_latent{cfg.get('latent_dim', 16)}"
                f"_period{period_val}_epochs{cfg.get('n_epochs', 50)}"
                f"_kernel{cfg.get('kernel_size', 7)}"
                f"_hidden{','.join(str(v) for v in hidden)}"
                f"_device{device}"
            )
        if cache_key in _MODEL_CACHE:
            model = _MODEL_CACHE[cache_key]
    
    if model is None:
        # Train a quick model on just this series (not ideal but works for single inference)
        # In practice, should use a pre-trained model
        ae_config = DRTSAEConfig(
            latent_dim=int(cfg.get('latent_dim', 16)),
            period=int(cfg.get('period', meta.get('primary_period', 32) if meta else 32)),
            n_epochs=int(cfg.get('n_epochs', 50)),  # Quick training
            alpha_T=float(cfg.get('alpha_T', 10.0)),
            alpha_S=float(cfg.get('alpha_S', 5.0)),
        )
        # Train on just this series (multiple copies for batch diversity)
        model = train_structured_ae(
            [y_arr] * 10,  # Replicate for training
            config=ae_config,
            device=device,
            verbose=False,
        )
        if cache_model and cache_key:
            _MODEL_CACHE[cache_key] = model
    
    trend, seasonal, residual = decompose_with_ae(y_arr, model, device=device)
    
    extra = {
        'method': 'dr_ts_ae',
        'params': cfg,
    }
    
    return DecompResult(
        trend=trend,
        season=seasonal,
        residual=residual,
        extra=extra,
    )
