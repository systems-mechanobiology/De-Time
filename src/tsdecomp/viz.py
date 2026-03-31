import numpy as np
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from .core import DecompResult

def plot_components(
    result: DecompResult,
    series: Optional[np.ndarray] = None,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: str = "Decomposition Result"
):
    """
    Plot trend, season, residual, and original series in a split-panel layout.
    """
    import matplotlib.pyplot as plt
    
    components = [result.trend, result.season, result.residual]
    names = ["Trend", "Season", "Residual"]
    
    if series is not None:
        components.insert(0, series)
        names.insert(0, "Original")
    
    n = len(components)
    fig, axes = plt.subplots(n, 1, figsize=(10, 2 * n), sharex=True)
    if n == 1:
        axes = [axes]
    
    for ax, comp, name in zip(axes, components, names):
        ax.plot(comp, label=name)
        ax.set_ylabel(name)
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        
    axes[-1].set_xlabel("Time")
    fig.suptitle(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        
    if interactive:
        plt.show()
    else:
        plt.close(fig)

def plot_error(
    result: DecompResult,
    series: np.ndarray,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: str = "Reconstruction Error"
):
    """
    Plot sqrt(error^2) per time step.
    """
    import matplotlib.pyplot as plt
    
    recon = result.trend + result.season + result.residual
    error = np.abs(result.residual)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(error, color="red", label="√SquaredError (|Residual|)")
    ax.set_ylabel("Absolute Error")
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        
    if interactive:
        plt.show()
    else:
        plt.close(fig)

def plot_comparison(
    results: Dict[str, DecompResult],
    series: np.ndarray,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False
):
    """
    Compare multiple methods.
    """
    # Implementation of split-panel overlay if needed
    pass
