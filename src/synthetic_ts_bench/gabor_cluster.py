# gabor_cluster.py
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Sequence, Tuple

try:
    import faiss  # faiss-cpu or faiss-gpu
except ImportError as e:
    faiss = None


@dataclass
class GaborClusterConfig:
    fs: float = 1.0            # sampling freq
    win_len: int = 256         # window length L
    hop: int = 64              # hop size a
    n_fft: Optional[int] = None
    window_type: str = "gaussian"  # "gaussian" | "hann"
    gaussian_sigma: Optional[float] = None

    n_clusters: int = 8        # K
    max_atoms: int = 200_000   # max TF points to use in training
    use_log_amp: bool = True   # log(1+|Z|)
    random_state: int = 42     # seed for reproducibility

    # training iterations for faiss KMeans
    n_iter: int = 20
    verbose: bool = False


@dataclass
class GaborClusterModel:
    """
    Global clustering model learned from many series.
    """
    centroids: np.ndarray      # (K, d)
    mu: np.ndarray             # (d,)
    sigma: np.ndarray          # (d,)
    cfg: GaborClusterConfig    # Gabor & feature config

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


@dataclass
class DecompResult:
    components: Dict[str, np.ndarray]
    residual: np.ndarray
    meta: Dict


def gabor_components_to_TS(
    components: Dict[str, np.ndarray],
    model: GaborClusterModel,
    trend_freq_thr: float = 0.08,
) -> Dict[str, Optional[np.ndarray]]:
    """
    Collapse per-cluster components into trend / seasonal buckets based on centroid frequency.
    """

    import re

    trend = None
    seasonal = None
    for key, value in components.items():
        match = re.match(r"Cluster_(\d+)$", key)
        if not match:
            continue
        cluster_idx = int(match.group(1))
        f_norm = float(model.centroids[cluster_idx, 1])
        if f_norm <= trend_freq_thr:
            trend = value if trend is None else trend + value
        else:
            seasonal = value if seasonal is None else seasonal + value
    return {"trend": trend, "seasonal": seasonal}


# ---------------- STFT / ISTFT utilities ---------------- #

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


def _stft_rfft(x: np.ndarray, L: int, hop: int, n_fft: Optional[int],
               window: np.ndarray) -> np.ndarray:
    """
    Real-input STFT using rfft. Output shape: (M, K_r), where K_r = n_fft//2 + 1
    """
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


def _istft_rfft(Z: np.ndarray, L: int, hop: int, n_fft: int,
                window: np.ndarray, length: int) -> np.ndarray:
    """
    Overlap-add ISTFT for rfft coefficients.
    Z: (M, K_r), K_r = n_fft//2 + 1
    """
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


# ---------------- Feature extraction ---------------- #

def _extract_gabor_features(
    x: np.ndarray,
    cfg: GaborClusterConfig,
    window: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    For a single series x, compute STFT and return:
    - features: (N_atoms, d) matrix
    - Z: complex STFT matrix (M, K_r)

    Feature: [t_norm, f_norm, log_amp or amp]
    """
    x = np.asarray(x, dtype=float).ravel()
    N = len(x)
    L = cfg.win_len
    hop = cfg.hop
    n_fft = cfg.n_fft or (1 << int(np.ceil(np.log2(L))))
    Z = _stft_rfft(x, L, hop, n_fft, window)  # (M, K_r)
    M, K_r = Z.shape

    amp = np.abs(Z)
    if cfg.use_log_amp:
        amp_feat = np.log1p(amp)
    else:
        amp_feat = amp

    # normalized time/freq coordinates
    if M > 1:
        t_idx = np.linspace(0.0, 1.0, M)
    else:
        t_idx = np.array([0.0])
    if K_r > 1:
        f_idx = np.linspace(0.0, 1.0, K_r)
    else:
        f_idx = np.array([0.0])

    T, F = np.meshgrid(t_idx, f_idx, indexing="ij")  # (M,K_r)
    feats = np.stack(
        [
            T.ravel().astype(np.float32),
            F.ravel().astype(np.float32),
            amp_feat.ravel().astype(np.float32),
        ],
        axis=1,
    )  # (M*K_r, 3)
    return feats, Z


# ---------------- FAISS K-means training ---------------- #

def train_gabor_clusters(
    series_list: Sequence[np.ndarray],
    cfg: GaborClusterConfig,
) -> GaborClusterModel:
    """
    Learn global Gabor-atom clusters from a list of 1D series.

    Steps:
        - For each series: STFT -> [t_norm, f_norm, log_amp] features
        - Concatenate across all series
        - Subsample up to cfg.max_atoms
        - Standardize features
        - Run FAISS k-means to get centroids

    Returns:
        GaborClusterModel
    """
    if faiss is None:
        raise ImportError(
            "faiss is not installed. Please install faiss-cpu or faiss-gpu before "
            "using train_gabor_clusters."
        )

    if len(series_list) == 0:
        raise ValueError("series_list is empty.")

    L = cfg.win_len
    window = _make_window(L, cfg.window_type, cfg.gaussian_sigma)

    feat_list = []
    for x in series_list:
        feats, _ = _extract_gabor_features(x, cfg, window)
        feat_list.append(feats)

    X = np.concatenate(feat_list, axis=0)  # (N_atoms, d)
    N_atoms, d = X.shape

    if cfg.max_atoms is not None and N_atoms > cfg.max_atoms:
        rng = np.random.default_rng(cfg.random_state)
        idx = rng.choice(N_atoms, cfg.max_atoms, replace=False)
        X = X[idx]
        N_atoms = X.shape[0]

    # standardize
    mu = X.mean(axis=0)
    sigma = X.std(axis=0) + 1e-8
    X_norm = (X - mu) / sigma
    X_norm = X_norm.astype(np.float32)

    # FAISS KMeans
    k = cfg.n_clusters
    if cfg.verbose:
        print(f"[GaborCluster] Training FAISS KMeans with K={k}, N={N_atoms}, d={d}")

    km = faiss.Kmeans(
        d=d,
        k=k,
        niter=cfg.n_iter,
        verbose=cfg.verbose,
        seed=cfg.random_state,
    )
    km.train(X_norm)

    centroids = km.centroids  # (k, d)
    return GaborClusterModel(
        centroids=centroids,
        mu=mu,
        sigma=sigma,
        cfg=cfg,
    )


# ---------------- Per-series decomposition ---------------- #

def _assign_clusters_faiss(
    feats: np.ndarray,
    model: GaborClusterModel
) -> np.ndarray:
    """
    Assign each feature vector to nearest centroid using FAISS IndexFlatL2.
    feats: (N_atoms, d)
    Returns: labels (N_atoms,) in [0, K-1]
    """
    if faiss is None:
        raise ImportError(
            "faiss is not installed. Please install faiss-cpu or faiss-gpu before "
            "using gabor_cluster_decompose."
        )

    X = (feats - model.mu) / model.sigma
    X = X.astype(np.float32)

    d = X.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(model.centroids.astype(np.float32))
    D, I = index.search(X, 1)
    labels = I.ravel()
    return labels


def gabor_cluster_decompose(
    x: np.ndarray,
    model: GaborClusterModel,
    max_clusters: Optional[int] = None,
) -> DecompResult:
    """
    Decompose a single series x by:
        - computing Gabor STFT
        - assigning each TF atom to nearest global centroid
        - reconstructing each cluster as one component via ISTFT

    If max_clusters is not None, only keep the largest-energy clusters and
    merge the rest into the residual.
    """
    cfg = model.cfg
    x = np.asarray(x, dtype=float).ravel()
    N = len(x)

    L = cfg.win_len
    hop = cfg.hop
    n_fft = cfg.n_fft or (1 << int(np.ceil(np.log2(L))))
    window = _make_window(L, cfg.window_type, cfg.gaussian_sigma)

    feats, Z = _extract_gabor_features(x, cfg, window)
    labels = _assign_clusters_faiss(feats, model)

    M, K_r = Z.shape
    K = model.centroids.shape[0]
    labels_2d = labels.reshape(M, K_r)

    # optional: select top clusters by total energy to keep as components
    amp = np.abs(Z)
    energy_per_cluster = np.zeros(K, dtype=float)
    for j in range(K):
        mask = (labels_2d == j)
        if np.any(mask):
            energy_per_cluster[j] = (amp[mask] ** 2).sum()

    if max_clusters is not None and max_clusters < K:
        # indices of clusters to keep
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
        xj = _istft_rfft(Zj, L, hop, n_fft, window, N)
        components[f"Cluster_{j}"] = xj
        used_clusters.append(j)

    # residual = x - sum_kept_components
    if components:
        sum_comp = np.zeros_like(x)
        for v in components.values():
            sum_comp += v
        residual = x - sum_comp
    else:
        residual = x.copy()

    meta = dict(
        fs=cfg.fs,
        win_len=L,
        hop=hop,
        n_fft=n_fft,
        window_type=cfg.window_type,
        gaussian_sigma=cfg.gaussian_sigma,
        n_clusters=model.centroids.shape[0],
        used_clusters=used_clusters,
        max_clusters=max_clusters,
        feature_dim=model.centroids.shape[1],
    )
    return DecompResult(components=components, residual=residual, meta=meta)
