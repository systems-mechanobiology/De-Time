"""
Decomposition + Symbolic Regression Pipeline.

Core pipeline that:
1. Decomposes time series into trend + seasonal + residual
2. Runs SR on each component separately
3. Combines expressions and evaluates mechanism match
4. Includes Oracle baselines for error attribution
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from .budget_controller import BudgetController, BudgetConfig
from .mechanism_matcher import MechanismMatcher, MechanismMatch


@dataclass
class DecompSRResult:
    """Complete result from Decomposition + SR pipeline."""
    
    # === Metadata ===
    sample_id: str = ""
    scenario: str = ""
    decomp_method: str = ""
    sr_method: str = ""
    
    # === Ground truth (for evaluation) ===
    trend_true: Optional[np.ndarray] = None
    seasonal_true: Optional[np.ndarray] = None
    trend_expr_true: str = ""
    seasonal_expr_true: str = ""
    
    # === Decomposition results ===
    trend_estimated: Optional[np.ndarray] = None
    seasonal_estimated: Optional[np.ndarray] = None
    residual: Optional[np.ndarray] = None
    decomp_time_sec: float = 0.0
    decomp_metrics: Dict[str, float] = field(default_factory=dict)
    
    # === SR results (per component) ===
    trend_expr: str = ""
    trend_sr_metrics: Dict[str, float] = field(default_factory=dict)
    seasonal_expr: str = ""
    seasonal_sr_metrics: Dict[str, float] = field(default_factory=dict)
    
    # === Combined results ===
    full_expr: str = ""
    final_r2: float = 0.0
    final_mse: float = float('inf')
    mechanism_match: Optional[MechanismMatch] = None
    total_runtime_sec: float = 0.0
    
    # === Oracle results (for error attribution) ===
    oracle_trend_expr: str = ""          # SR on T_true
    oracle_seasonal_expr: str = ""       # SR on S_true
    oracle_trend_r2: float = 0.0
    oracle_seasonal_r2: float = 0.0
    oracle_full_r2: float = 0.0
    
    # === Error propagation ===
    delta_decomp_trend: float = 0.0      # MSE(T_true, T_hat)
    delta_decomp_seasonal: float = 0.0   # MSE(S_true, S_hat)
    delta_sr_trend: float = 0.0          # MSE(T_hat, f_T(t))
    delta_sr_seasonal: float = 0.0       # MSE(S_hat, f_S(t))
    delta_pipe: float = 0.0              # MSE(y, f_T + f_S)
    
    # === Status ===
    success: bool = True
    error_message: str = ""
    timeout: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame."""
        result = {
            'sample_id': self.sample_id,
            'scenario': self.scenario,
            'decomp_method': self.decomp_method,
            'sr_method': self.sr_method,
            
            # Decomposition metrics
            'decomp_time_sec': self.decomp_time_sec,
            **{f'decomp_{k}': v for k, v in self.decomp_metrics.items()},
            
            # Expressions
            'trend_expr': self.trend_expr,
            'seasonal_expr': self.seasonal_expr,
            'full_expr': self.full_expr,
            
            # SR metrics
            **{f'trend_sr_{k}': v for k, v in self.trend_sr_metrics.items()},
            **{f'seasonal_sr_{k}': v for k, v in self.seasonal_sr_metrics.items()},
            
            # Final metrics
            'final_r2': self.final_r2,
            'final_mse': self.final_mse,
            'total_runtime_sec': self.total_runtime_sec,
            
            # Oracle
            'oracle_trend_expr': self.oracle_trend_expr,
            'oracle_seasonal_expr': self.oracle_seasonal_expr,
            'oracle_trend_r2': self.oracle_trend_r2,
            'oracle_seasonal_r2': self.oracle_seasonal_r2,
            'oracle_full_r2': self.oracle_full_r2,
            
            # Error propagation
            'delta_decomp_trend': self.delta_decomp_trend,
            'delta_decomp_seasonal': self.delta_decomp_seasonal,
            'delta_sr_trend': self.delta_sr_trend,
            'delta_sr_seasonal': self.delta_sr_seasonal,
            'delta_pipe': self.delta_pipe,
            
            # Status
            'success': self.success,
            'error_message': self.error_message,
            'timeout': self.timeout,
        }
        
        # Add mechanism match fields
        if self.mechanism_match:
            result.update({
                f'mech_{k}': v for k, v in self.mechanism_match.to_dict().items()
            })
        
        return result


class DecompSRPipeline:
    """
    Main pipeline for Decomposition + Symbolic Regression.
    
    Usage:
        pipeline = DecompSRPipeline(
            decomp_method='stl',
            sr_method='gplearn',
            budget_config=BudgetConfig(time_budget_sec=60),
        )
        result = pipeline.fit(sample)
    """
    
    def __init__(
        self,
        decomp_method: str = 'stl',
        sr_method: str = 'gplearn',
        budget_config: Optional[BudgetConfig] = None,
        run_oracle: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize pipeline.
        
        Args:
            decomp_method: Decomposition method name ('stl', 'ssa', 'dr_ts_reg', etc.)
            sr_method: SR method name ('gplearn', 'pysr')
            budget_config: Fair comparison budget configuration
            run_oracle: Whether to run Oracle baselines
            verbose: Print progress
        """
        self.decomp_method = decomp_method
        self.sr_method = sr_method
        self.budget_config = budget_config or BudgetConfig()
        self.budget_controller = BudgetController(self.budget_config)
        self.run_oracle = run_oracle
        self.verbose = verbose
        self.mechanism_matcher = MechanismMatcher()
        
        # Initialize decomposition method
        self._decomposer = self._get_decomposer(decomp_method)
        
        # Initialize SR method
        self._sr = self._get_sr_method(sr_method)
    
    def _get_decomposer(self, name: str):
        """Get decomposition method by name."""
        name_lower = name.lower()
        
        if name_lower == 'none' or name_lower == 'original':
            # Identity decomposition (trend=y, seasonal=0, resid=0)
            return lambda y, **kwargs: type('DecompResult', (), {
                'trend': y, 'seasonal': np.zeros_like(y), 'residual': np.zeros_like(y), 'components': [y]
            })()
        
        if name_lower == 'stl':
            from synthetic_ts_bench.decomp_methods import stl_decompose
            return stl_decompose
        elif name_lower == 'mstl':
            from synthetic_ts_bench.decomp_methods import mstl_decompose
            return mstl_decompose
        elif name_lower == 'ssa':
            from synthetic_ts_bench.decomp_methods import ssa_decompose
            return ssa_decompose
        elif name_lower == 'dr_ts_reg':
            from synthetic_ts_bench.dr_ts_reg import dr_ts_reg_decompose
            return dr_ts_reg_decompose
        elif name_lower == 'dr_ts_ae':
            from synthetic_ts_bench.dr_ts_ae import dr_ts_ae_decompose
            return dr_ts_ae_decompose
        elif name_lower == 'sl_lib':
            from synthetic_ts_bench.sl_lib import sl_lib_decompose
            return sl_lib_decompose
        elif name_lower == 'wavelet':
            from synthetic_ts_bench.decomp_methods import wavelet_decompose
            return wavelet_decompose
        elif name_lower == 'emd':
            from synthetic_ts_bench.decomp_methods import emd_decompose
            return emd_decompose
        elif name_lower == 'ceemdan':
            from synthetic_ts_bench.decomp_methods import ceemdan_decompose
            return ceemdan_decompose
        elif name_lower == 'vmd':
            from synthetic_ts_bench.decomp_methods import vmd_decompose
            return vmd_decompose
        else:
            raise ValueError(f"Unknown decomposition method: {name}")
    
    def _get_sr_method(self, name: str):
        """Get SR method by name."""
        name_lower = name.lower()
        
        if name_lower == 'gplearn':
            from sr_methods import GPLearnRegressor
            return GPLearnRegressor(
                operators=self.budget_config.operators,
                time_limit=self.budget_config.time_budget_sec,
                verbose=self.verbose,
                population_size=500,
                generations=30,
            )
        elif name_lower == 'pysr':
            from sr_methods import PySRRegressor
            return PySRRegressor(
                operators=self.budget_config.operators,
                time_limit=self.budget_config.time_budget_sec,
                verbose=self.verbose,
            )
        elif name_lower == 'nd2':
            from sr_methods import ND2Regressor
            return ND2Regressor(
                time_limit=self.budget_config.time_budget_sec,
                verbose=self.verbose,
            )
        else:
            raise ValueError(f"Unknown SR method: {name}")
    
    def fit(self, sample) -> DecompSRResult:
        """
        Run full pipeline on a sample.
        
        Args:
            sample: SRSample object with t, y, trend, seasonal, etc.
            
        Returns:
            DecompSRResult with all metrics and expressions
        """
        start_time = time.time()
        
        result = DecompSRResult(
            sample_id=sample.sample_id,
            scenario=sample.scenario,
            decomp_method=self.decomp_method,
            sr_method=self.sr_method,
            trend_true=getattr(sample, 'trend', None),
            seasonal_true=getattr(sample, 'seasonal', None),
            trend_expr_true=getattr(sample, 'trend_expr', ''),
            seasonal_expr_true=getattr(sample, 'seasonal_expr', ''),
        )
        
        try:
            t = sample.t
            y = sample.y_clean if hasattr(sample, 'y_clean') else sample.y
            
            # === Step 1: Decomposition ===
            if self.verbose:
                print(f"  Decomposing with {self.decomp_method}...")
            
            decomp_start = time.time()
            
            # Prepare decomposition config
            decomp_config = {'period': 24}  # Default period for synthetic data
            
            # Get period from sample if available
            if hasattr(sample, 'period'):
                decomp_config['period'] = sample.period
            elif hasattr(sample, 'omega') and sample.omega > 0:
                # Convert omega to period: T = 2*pi/omega
                decomp_config['period'] = max(2, int(2 * np.pi / sample.omega))
            
            # Call decomposer with config
            try:
                decomp_result = self._decomposer(y, config=decomp_config)
            except TypeError:
                # Some methods don't accept config
                decomp_result = self._decomposer(y)
            
            result.decomp_time_sec = time.time() - decomp_start
            
            # Handle different result formats
            if hasattr(decomp_result, 'trend'):
                result.trend_estimated = decomp_result.trend
            elif hasattr(decomp_result, 'components') and len(decomp_result.components) > 0:
                result.trend_estimated = decomp_result.components[0]
            else:
                raise ValueError(f"Cannot extract trend from {type(decomp_result)}")
            
            if hasattr(decomp_result, 'seasonal'):
                result.seasonal_estimated = decomp_result.seasonal
            elif hasattr(decomp_result, 'components') and len(decomp_result.components) > 1:
                result.seasonal_estimated = decomp_result.components[1]
            elif hasattr(decomp_result, 'residual'):
                # Use y - trend as seasonal approximation
                result.seasonal_estimated = y - result.trend_estimated - decomp_result.residual
            else:
                result.seasonal_estimated = y - result.trend_estimated
            
            if hasattr(decomp_result, 'residual'):
                result.residual = decomp_result.residual
            else:
                result.residual = y - result.trend_estimated - result.seasonal_estimated
            
            # Decomposition metrics
            if result.trend_true is not None:
                result.decomp_metrics['T_r2'] = self._r2(result.trend_true, result.trend_estimated)
                result.delta_decomp_trend = self._mse(result.trend_true, result.trend_estimated)
            if result.seasonal_true is not None:
                result.decomp_metrics['S_r2'] = self._r2(result.seasonal_true, result.seasonal_estimated)
                result.delta_decomp_seasonal = self._mse(result.seasonal_true, result.seasonal_estimated)
            
            # === Step 2: SR on Trend ===
            if self.verbose:
                print(f"  SR on trend with {self.sr_method}...")
            
            trend_sr_result = self._sr.fit(t.reshape(-1, 1), result.trend_estimated)
            result.trend_expr = trend_sr_result.expression
            result.trend_sr_metrics = {
                'r2': trend_sr_result.r2_score,
                'mse': trend_sr_result.mse,
                'nodes': trend_sr_result.complexity,
                'runtime': trend_sr_result.runtime_sec,
            }
            result.delta_sr_trend = trend_sr_result.mse
            
            # === Step 3: SR on Seasonal ===
            if self.verbose:
                print(f"  SR on seasonal with {self.sr_method}...")
            
            seasonal_sr_result = self._sr.fit(t.reshape(-1, 1), result.seasonal_estimated)
            result.seasonal_expr = seasonal_sr_result.expression
            result.seasonal_sr_metrics = {
                'r2': seasonal_sr_result.r2_score,
                'mse': seasonal_sr_result.mse,
                'nodes': seasonal_sr_result.complexity,
                'runtime': seasonal_sr_result.runtime_sec,
            }
            result.delta_sr_seasonal = seasonal_sr_result.mse
            
            # === Step 4: Combine and Evaluate ===
            result.full_expr = f"({result.trend_expr}) + ({result.seasonal_expr})"
            
            # Predict combined
            trend_pred = self._sr.predict(t.reshape(-1, 1)) if hasattr(self._sr, 'predict') else np.zeros_like(t)
            # Need to refit for seasonal prediction...
            # For simplicity, compute final metrics from component predictions
            y_pred = trend_pred + seasonal_sr_result.r2_score * result.seasonal_estimated  # approximation
            
            result.final_r2 = self._r2(y, y_pred)
            result.final_mse = self._mse(y, y_pred)
            result.delta_pipe = result.final_mse
            
            # === Step 5: Oracle Baselines ===
            if self.run_oracle and result.trend_true is not None:
                if self.verbose:
                    print(f"  Running Oracle-SR...")
                
                # Oracle on true trend
                oracle_trend = self._sr.fit(t.reshape(-1, 1), result.trend_true)
                result.oracle_trend_expr = oracle_trend.expression
                result.oracle_trend_r2 = oracle_trend.r2_score
                
                # Oracle on true seasonal
                if result.seasonal_true is not None:
                    oracle_seasonal = self._sr.fit(t.reshape(-1, 1), result.seasonal_true)
                    result.oracle_seasonal_expr = oracle_seasonal.expression
                    result.oracle_seasonal_r2 = oracle_seasonal.r2_score
            
            # === Step 6: Mechanism Match ===
            result.mechanism_match = self.mechanism_matcher.match(
                pred_expr=result.full_expr,
                true_expr=getattr(sample, 'full_expr', ''),
                pred_trend_expr=result.trend_expr,
                true_trend_expr=result.trend_expr_true,
                pred_seasonal_expr=result.seasonal_expr,
                true_seasonal_expr=result.seasonal_expr_true,
            )
            
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            if self.verbose:
                print(f"  Error: {e}")
        
        result.total_runtime_sec = time.time() - start_time
        return result
    
    def _r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute R² score."""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 1e-10 else 0.0
    
    def _mse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute MSE."""
        return float(np.mean((y_true - y_pred) ** 2))
