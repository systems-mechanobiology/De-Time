import numpy as np
import pickle
from time import perf_counter
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Sequence, Tuple
from .._native import has_native_method, invoke_native
from ..backends import finalize_result, resolve_backend, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry

try:
    import faiss
    _HAS_FAISS = True
    _FAISS_IMPORT_ERROR = None
except Exception as exc:
    _HAS_FAISS = False
    _FAISS_IMPORT_ERROR = exc

@dataclass
class GaborClusterConfig:
    fs: float = 1.0
    win_len: int = 256
    hop: int = 64
    n_fft: Optional[int] = None
    window_type: str = "gaussian"
    gaussian_sigma: Optional[float] = None
    n_clusters: int = 8
    max_atoms: int = 200_000
    use_log_amp: bool = True
    random_state: int = 42
    n_iter: int = 20
    verbose: bool = False

@dataclass
class GaborClusterModel:
    centroids: np.ndarray
    mu: np.ndarray
    sigma: np.ndarray
    cfg: GaborClusterConfig

    def save(self, path: str) -> None:
        np.savez_compressed(
            path,
            centroids=self.centroids.astype(np.float32),
            mu=self.mu.astype(np.float32),
            sigma=self.sigma.astype(np.float32),
            cfg=np.array([self.cfg], dtype=object),
        )

    @staticmethod
    def load(path: str) -> "GaborClusterModel":
        data = np.load(path, allow_pickle=True)
        centroids = data["centroids"]
        mu = data["mu"]
        sigma = data["sigma"]
        cfg = data["cfg"][0]
        return GaborClusterModel(centroids=centroids, mu=mu, sigma=sigma, cfg=cfg)

def _make_window(L: int, wtype: str, sigma: Optional[float]) -> np.ndarray:
    if wtype == "gaussian":
        if sigma is None:
            sigma = L / 6.0
        n = np.arange(L) - (L - 1) / 2.0
        w = np.exp(-0.5 * (n / sigma) ** 2)
        return w / np.sqrt((w ** 2).sum())
    elif wtype == "hann":
        w = np.hanning(L)
        return w / np.sqrt((w ** 2).sum())
    else:
        raise ValueError(f"Unsupported window_type={wtype}")

def _stft_rfft(x: np.ndarray, L: int, hop: int, n_fft: Optional[int], window: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float).ravel()
    N = len(x)
    if n_fft is None:
        n_fft = 1 << int(np.ceil(np.log2(L)))
    if N < L:
        n_frames = 1
    else:
        n_frames = 1 + (N - L) // hop
    Z = np.empty((n_frames, n_fft // 2 + 1), dtype=np.complex64)
    for m in range(n_frames):
        start = m * hop
        seg = np.zeros(L, dtype=float)
        if start + L <= N:
            seg[:] = x[start:start + L]
        else:
            tail = N - start
            if tail > 0:
                seg[:tail] = x[start:]
        segw = seg * window
        Z[m, :] = np.fft.rfft(segw, n=n_fft)
    return Z

def _istft_rfft(Z: np.ndarray, L: int, hop: int, n_fft: int, window: np.ndarray, length: int) -> np.ndarray:
    M, K_r = Z.shape
    x_rec = np.zeros(length + L, dtype=float)
    win_acc = np.zeros(length + L, dtype=float)
    for m in range(M):
        frame = np.fft.irfft(Z[m, :], n=n_fft).real[:L]
        start = m * hop
        x_rec[start:start + L] += frame * window
        win_acc[start:start + L] += window ** 2
    nz = win_acc > 1e-12
    x_out = np.zeros_like(x_rec)
    x_out[nz] = x_rec[nz] / win_acc[nz]
    return x_out[:length]

def _extract_gabor_features(x: np.ndarray, cfg: GaborClusterConfig, window: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float).ravel()
    L = cfg.win_len
    hop = cfg.hop
    n_fft = cfg.n_fft or (1 << int(np.ceil(np.log2(L))))
    Z = _stft_rfft(x, L, hop, n_fft, window)
    M, K_r = Z.shape
    amp = np.abs(Z)
    if cfg.use_log_amp:
        amp_feat = np.log1p(amp)
    else:
        amp_feat = amp
    if M > 1:
        t_idx = np.linspace(0.0, 1.0, M)
    else:
        t_idx = np.array([0.0])
    if K_r > 1:
        f_idx = np.linspace(0.0, 1.0, K_r)
    else:
        f_idx = np.array([0.0])
    T, F = np.meshgrid(t_idx, f_idx, indexing="ij")
    feats = np.stack([T.ravel().astype(np.float32), F.ravel().astype(np.float32), amp_feat.ravel().astype(np.float32)], axis=1)
    return feats, Z


def _extract_gabor_features_backend(
    x: np.ndarray,
    cfg: GaborClusterConfig,
    window: np.ndarray,
    *,
    backend: str,
) -> Tuple[np.ndarray, np.ndarray]:
    if backend == "native":
        n_fft = cfg.n_fft or (1 << int(np.ceil(np.log2(cfg.win_len))))
        Z = invoke_native(
            "gabor_stft_rfft",
            np.asarray(x, dtype=float).ravel(),
            win_len=int(cfg.win_len),
            hop=int(cfg.hop),
            n_fft=int(n_fft),
            window=np.asarray(window, dtype=float),
        )
        Z = np.asarray(Z, dtype=np.complex64)
        M, K_r = Z.shape
        amp = np.abs(Z)
        amp_feat = np.log1p(amp) if cfg.use_log_amp else amp
        t_idx = np.linspace(0.0, 1.0, M) if M > 1 else np.array([0.0])
        f_idx = np.linspace(0.0, 1.0, K_r) if K_r > 1 else np.array([0.0])
        T, F = np.meshgrid(t_idx, f_idx, indexing="ij")
        feats = np.stack(
            [T.ravel().astype(np.float32), F.ravel().astype(np.float32), amp_feat.ravel().astype(np.float32)],
            axis=1,
        )
        return feats, Z
    return _extract_gabor_features(x, cfg, window)

def _assign_clusters_faiss(feats: np.ndarray, model: GaborClusterModel) -> np.ndarray:
    if not _HAS_FAISS:
        raise ImportError("faiss is required for GABOR_CLUSTER.")
    X = (feats - model.mu) / model.sigma
    X = X.astype(np.float32)
    d = X.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(model.centroids.astype(np.float32))
    D, I = index.search(X, 1)
    return I.ravel()

@MethodRegistry.register("GABOR_CLUSTER")
def gabor_cluster_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    started_at = perf_counter()
    if not _HAS_FAISS:
        raise ImportError("faiss is required for GABOR_CLUSTER.") from _FAISS_IMPORT_ERROR

    cfg_dict, runtime = split_runtime_params(params)
    model_path = cfg_dict.get("model_path")
    model = cfg_dict.get("model")
    max_clusters = cfg_dict.get("max_clusters")
    
    if model is None:
        if model_path:
            model = GaborClusterModel.load(model_path)
        else:
            raise ValueError("GABOR_CLUSTER requires 'model_path' or 'model' in params.")
            
    cfg = model.cfg
    x = np.asarray(y, dtype=float).ravel()
    N = len(x)
    L = cfg.win_len
    hop = cfg.hop
    n_fft = cfg.n_fft or (1 << int(np.ceil(np.log2(L))))
    window = _make_window(L, cfg.window_type, cfg.gaussian_sigma)

    native_methods = ("gabor_stft_rfft", "gabor_istft_rfft")
    if runtime.backend == "native" and not all(has_native_method(name) for name in native_methods):
        raise RuntimeError(
            "GABOR_CLUSTER requested backend='native' but the native STFT helpers are unavailable."
        )
    backend = resolve_backend("GABOR_CLUSTER", runtime, native_methods=native_methods)

    feats, Z = _extract_gabor_features_backend(x, cfg, window, backend=backend)
    labels = _assign_clusters_faiss(feats, model)
    
    M, K_r = Z.shape
    K = model.centroids.shape[0]
    labels_2d = labels.reshape(M, K_r)
    
    amp = np.abs(Z)
    energy_per_cluster = np.zeros(K, dtype=float)
    for j in range(K):
        mask = (labels_2d == j)
        if np.any(mask):
            energy_per_cluster[j] = (amp[mask] ** 2).sum()
            
    if max_clusters is not None and max_clusters < K:
        keep_idx = np.argsort(energy_per_cluster)[-max_clusters:]
        keep_mask = np.zeros(K, dtype=bool)
        keep_mask[keep_idx] = True
    else:
        keep_mask = np.ones(K, dtype=bool)
        
    components: Dict[str, np.ndarray] = {}
    used_clusters = []
    
    for j in range(K):
        if not keep_mask[j]:
            continue
        mask = (labels_2d == j).astype(np.float32)
        if not np.any(mask):
            continue
        Zj = Z * mask
        if backend == "native":
            xj = np.asarray(
                invoke_native(
                    "gabor_istft_rfft",
                    np.asarray(Zj, dtype=np.complex64),
                    win_len=int(L),
                    hop=int(hop),
                    n_fft=int(n_fft),
                    window=np.asarray(window, dtype=float),
                    length=int(N),
                ),
                dtype=float,
            )
        else:
            xj = _istft_rfft(Zj, L, hop, n_fft, window, N)
        components[f"Cluster_{j}"] = xj
        used_clusters.append(j)
        
    if components:
        sum_comp = np.zeros_like(x)
        for v in components.values():
            sum_comp += v
        residual = x - sum_comp
    else:
        residual = x.copy()
        
    # Map to trend/season if possible (heuristic)
    trend_freq_thr = float(cfg_dict.get("trend_freq_thr", 0.08))
    trend = np.zeros_like(x)
    season = np.zeros_like(x)
    
    for key, val in components.items():
        cluster_idx = int(key.split("_")[1])
        # Centroid freq is at index 1 (normalized freq)
        f_norm = float(model.centroids[cluster_idx, 1])
        if f_norm <= trend_freq_thr:
            trend += val
        else:
            season += val
            
    return finalize_result(
        DecompResult(
            trend=trend,
            season=season,
            residual=residual,
            components=components,
            meta={
                "method": "GABOR_CLUSTER",
                "n_clusters": K,
                "used_clusters": used_clusters,
                "max_clusters": max_clusters
            }
        ),
        method="GABOR_CLUSTER",
        runtime=runtime,
        backend_used=backend,
        started_at=started_at,
    )
