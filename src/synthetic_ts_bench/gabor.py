# synthetic_ts_bench/gabor.py
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class GaborConfig:
    fs: float = 1.0                 # 采样频率
    win_len: int = 256              # 窗长 L
    hop: int = 64                   # 帧移 a
    n_fft: Optional[int] = None     # FFT 点数（默认下一次幂 >= win_len）
    window_type: str = "gaussian"   # "gaussian" | "hann"
    gaussian_sigma: Optional[float] = None  # 高斯窗的 sigma；None 用 L/6 经验值
    bands: Optional[List[Tuple[float,float]]] = None # [(f_low, f_high)] Hz，若 None 用默认三段：trend/seasonal/noise
    ridge: bool = False             # 是否启用简单 ridge 重构（优先 bands）
    ridge_max_peaks: int = 2        # 每帧最多保留的峰（ridge 模式）
    tight_frame: bool = True        # 近似 tight：分析窗=合成窗

@dataclass
class DecompResult:
    components: Dict[str, np.ndarray]
    residual: np.ndarray
    meta: Dict

def _make_window(L:int, wtype:str, sigma:Optional[float])->np.ndarray:
    if wtype == "gaussian":
        if sigma is None:
            sigma = L/6.0
        n = np.arange(L) - (L-1)/2
        w = np.exp(-0.5*(n/sigma)**2)
        return (w / np.sqrt((w**2).sum()))
    elif wtype == "hann":
        w = np.hanning(L)
        return w / np.sqrt((w**2).sum())
    else:
        raise ValueError(f"Unsupported window_type={wtype}")

def _stft(x:np.ndarray, L:int, hop:int, n_fft:Optional[int], window:np.ndarray)->np.ndarray:
    N = len(x)
    if n_fft is None:
        n_fft = 1<<(int(np.ceil(np.log2(L))))
    n_frames = 1 + (N - L) // hop if N >= L else 1
    n_bins = n_fft // 2 + 1
    Z = np.empty((n_frames, n_bins), dtype=np.complex64)
    for m in range(n_frames):
        start = m*hop
        seg = np.zeros(L, dtype=float)
        if start+L <= N:
            seg[:] = x[start:start+L]
        else:
            tail = N - start
            if tail > 0:
                seg[:tail] = x[start:]
        segw = seg * window
        Z[m,:] = np.fft.rfft(segw, n=n_fft)
    return Z  # shape: (M, K_r), 仅非负频

def _istft(Z:np.ndarray, L:int, hop:int, n_fft:int, window:np.ndarray, length:int)->np.ndarray:
    # 逆变换重叠相加；Z 是 rfft 结果 (M, K_r)
    M, K_r = Z.shape
    x_rec = np.zeros(length + L, dtype=float)
    win_acc = np.zeros(length + L, dtype=float)
    for m in range(M):
        frame = np.fft.irfft(Z[m,:], n=n_fft).real[:L]
        start = m*hop
        x_rec[start:start+L] += frame * window
        win_acc[start:start+L] += window**2
    # 归一化（避免重叠加窗导致能量偏移）
    nz = win_acc > 1e-12
    x_out = np.zeros_like(x_rec)
    x_out[nz] = x_rec[nz] / win_acc[nz]
    return x_out[:length]

def _hz_to_bin(f:float, fs:float, n_fft:int)->int:
    return int(np.clip(round(f*n_fft/fs), 0, n_fft//2))

def _default_bands(fs:float)->List[Tuple[float,float]]:
    # 经验三段：趋势(超低频)、主季节(低中频)、高频噪声
    return [(0.0, 0.02*fs), (0.02*fs, 0.15*fs), (0.15*fs, 0.5*fs)]

def _apply_band_masks(Z:np.ndarray, fs:float, n_fft:int, bands:List[Tuple[float,float]])->List[np.ndarray]:
    M, K_r = Z.shape
    outs = []
    for (f0, f1) in bands:
        b0 = _hz_to_bin(max(0.0,f0), fs, n_fft)
        b1 = _hz_to_bin(min(fs/2,f1), fs, n_fft)
        mask = np.zeros_like(Z, dtype=np.float32)
        mask[:, b0:b1+1] = 1.0
        outs.append(Z * mask)
    return outs

def _simple_ridge_mask(Z:np.ndarray, max_peaks:int)->np.ndarray:
    # 非学习、贪心：每帧在幅度谱上保留若干峰值频点及其一阶邻域
    M, K_r = Z.shape
    A = np.abs(Z)
    mask = np.zeros_like(Z, dtype=np.float32)
    for m in range(M):
        amp = A[m]
        # 粗略峰：top-k
        idx = np.argsort(amp)[-max_peaks:]
        for k in idx:
            mask[m, max(0,k-1):min(K_r, k+2)] = 1.0
    return Z * mask

def gabor_decompose(
    x: np.ndarray,
    cfg: GaborConfig
) -> DecompResult:
    x = np.asarray(x, dtype=float).ravel()
    N = len(x)
    L = cfg.win_len
    hop = cfg.hop
    n_fft = cfg.n_fft or (1<<(int(np.ceil(np.log2(L)))))
    window = _make_window(L, cfg.window_type, cfg.gaussian_sigma)

    Z = _stft(x, L, hop, n_fft, window)         # (M, K_r)
    fs = cfg.fs

    components: Dict[str, np.ndarray] = {}
    masks_meta = {}

    if cfg.bands is None and not cfg.ridge:
        bands = _default_bands(fs)
    else:
        bands = cfg.bands

    if bands is not None:
        band_Zs = _apply_band_masks(Z, fs, n_fft, bands)
        names = ["Trend_LF", "Seasonal_MF", "Noise_HF"] if len(bands)==3 else [f"Band_{i}" for i in range(len(bands))]
        for name, Zb in zip(names, band_Zs):
            xr = _istft(Zb, L, hop, n_fft, window, N)
            components[name] = xr
        masks_meta["mode"] = "bands"
        masks_meta["bands"] = bands

    if cfg.ridge:
        Zr = _simple_ridge_mask(Z, cfg.ridge_max_peaks)
        xr = _istft(Zr, L, hop, n_fft, window, N)
        components["Ridge_AMFM"] = xr
        masks_meta["ridge_max_peaks"] = cfg.ridge_max_peaks
        masks_meta["mode"] = "ridge" if bands is None else "bands+ridge"

    # 残差 = 原信号 - 所有分量之和
    if components:
        s = np.zeros(N)
        for v in components.values():
            s += v
        residual = x - s
    else:
        residual = x.copy()

    meta = dict(
        fs=fs, win_len=L, hop=hop, n_fft=n_fft, window_type=cfg.window_type,
        gaussian_sigma=cfg.gaussian_sigma, tight_frame=cfg.tight_frame,
        masks=masks_meta, stft_shape=Z.shape
    )
    return DecompResult(components=components, residual=residual, meta=meta)
