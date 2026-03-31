"""
Mechanism Matcher for evaluating symbolic recovery quality.

Replaces simple boolean symbolic_match with structured mechanism equivalence:
- Trend family matching (linear/quadratic/exp/logistic/piecewise)
- Frequency parameter matching (omega error, harmonic coverage)
- Equivalence transforms (phase shifts, scale/translate)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class MechanismMatch:
    """Structured mechanism equivalence result."""
    
    # Trend mechanism
    trend_family_match: bool = False
    trend_family_pred: str = "unknown"
    trend_family_true: str = "unknown"
    trend_param_error: float = float('inf')
    
    # Seasonal mechanism
    omega_error: float = float('inf')  # |ω_pred - ω_true| / ω_true
    harmonic_coverage: float = 0.0     # discovered harmonics / true harmonics
    phase_equiv: bool = False          # sin/cos phase equivalence
    freq_count_match: bool = False     # number of frequencies match
    
    # Overall scores
    mechanism_score: float = 0.0       # weighted composite [0, 1]
    
    # Metadata
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trend_family_match': self.trend_family_match,
            'trend_family_pred': self.trend_family_pred,
            'trend_family_true': self.trend_family_true,
            'trend_param_error': self.trend_param_error,
            'omega_error': self.omega_error,
            'harmonic_coverage': self.harmonic_coverage,
            'phase_equiv': self.phase_equiv,
            'freq_count_match': self.freq_count_match,
            'mechanism_score': self.mechanism_score,
        }


class MechanismMatcher:
    """
    Evaluates mechanism equivalence between predicted and ground truth expressions.
    
    More lenient than exact symbolic match:
    - Allows scale/translation equivalence
    - Allows sin/cos phase shifts
    - Focuses on mechanism family rather than exact parameters
    """
    
    # Trend family patterns
    TREND_FAMILIES = {
        'linear': r'^[\d\.\-\+\*\/\s]*[ut][\d\.\-\+\*\/\s]*$',
        'quadratic': r'\*\*\s*2|u\s*\*\s*u|\^2',
        'cubic': r'\*\*\s*3|u\s*\*\s*u\s*\*\s*u|\^3',
        'exp': r'exp\s*\(',
        'logistic': r'\/\s*\(\s*1\s*\+\s*exp',
        'piecewise': r'if|else|max\(|min\(',
    }
    
    def __init__(self, 
                 omega_tolerance: float = 0.05,
                 param_tolerance: float = 0.1):
        """
        Args:
            omega_tolerance: Relative tolerance for frequency matching (5% default)
            param_tolerance: Relative tolerance for parameter matching
        """
        self.omega_tolerance = omega_tolerance
        self.param_tolerance = param_tolerance
    
    def match(self,
              pred_expr: str,
              true_expr: str,
              pred_trend_expr: Optional[str] = None,
              true_trend_expr: Optional[str] = None,
              pred_seasonal_expr: Optional[str] = None,
              true_seasonal_expr: Optional[str] = None,
              true_omega: Optional[float] = None,
              true_harmonics: Optional[List[int]] = None) -> MechanismMatch:
        """
        Compute mechanism match between predicted and true expressions.
        
        Args:
            pred_expr: Full predicted expression
            true_expr: Full ground truth expression
            pred_trend_expr: Predicted trend expression (optional)
            true_trend_expr: True trend expression (optional)
            pred_seasonal_expr: Predicted seasonal expression (optional)
            true_seasonal_expr: True seasonal expression (optional)
            true_omega: True fundamental frequency (optional)
            true_harmonics: True harmonic indices (optional)
            
        Returns:
            MechanismMatch with all evaluation fields
        """
        result = MechanismMatch()
        
        # === Trend matching ===
        if true_trend_expr:
            result.trend_family_true = self._detect_family(true_trend_expr)
        if pred_trend_expr:
            result.trend_family_pred = self._detect_family(pred_trend_expr)
        
        result.trend_family_match = (
            result.trend_family_pred == result.trend_family_true and
            result.trend_family_true != 'unknown'
        )
        
        # === Seasonal matching ===
        if true_seasonal_expr and pred_seasonal_expr:
            # Extract frequencies from expressions
            pred_omegas = self._extract_frequencies(pred_seasonal_expr)
            true_omegas = self._extract_frequencies(true_seasonal_expr)
            
            if true_omega is None and true_omegas:
                true_omega = true_omegas[0]
            
            # Omega error (relative)
            if pred_omegas and true_omega:
                closest = min(pred_omegas, key=lambda x: abs(x - true_omega))
                result.omega_error = abs(closest - true_omega) / max(true_omega, 1e-6)
            
            # Harmonic coverage
            if true_harmonics and pred_omegas and true_omega:
                discovered = 0
                for h in true_harmonics:
                    target = true_omega * h
                    if any(abs(p - target) / target < self.omega_tolerance for p in pred_omegas):
                        discovered += 1
                result.harmonic_coverage = discovered / len(true_harmonics)
            elif true_omegas and pred_omegas:
                # Simple frequency count match
                matched = sum(1 for t in true_omegas 
                            if any(abs(p - t) / max(t, 1e-6) < self.omega_tolerance 
                                  for p in pred_omegas))
                result.harmonic_coverage = matched / len(true_omegas)
            
            # Frequency count match
            result.freq_count_match = len(pred_omegas) == len(true_omegas)
            
            # Phase equivalence (sin ↔ cos allowed)
            result.phase_equiv = self._check_phase_equiv(pred_seasonal_expr, true_seasonal_expr)
        
        # === Compute overall score ===
        result.mechanism_score = self._compute_score(result)
        
        return result
    
    def _detect_family(self, expr: str) -> str:
        """Detect trend family from expression."""
        expr_lower = expr.lower()
        
        # Check in order of specificity (most specific first)
        if re.search(self.TREND_FAMILIES['logistic'], expr_lower):
            return 'logistic'
        if re.search(self.TREND_FAMILIES['piecewise'], expr_lower):
            return 'piecewise'
        if re.search(self.TREND_FAMILIES['exp'], expr_lower):
            return 'exp'
        if re.search(self.TREND_FAMILIES['cubic'], expr_lower):
            return 'cubic'
        if re.search(self.TREND_FAMILIES['quadratic'], expr_lower):
            return 'quadratic'
        if re.search(self.TREND_FAMILIES['linear'], expr_lower):
            return 'linear'
        
        # Check for polynomial by counting variable powers
        if 'u' in expr_lower or 't' in expr_lower:
            # Simple heuristic: count multiplications of u
            u_muls = len(re.findall(r'u\s*\*\s*u', expr_lower))
            if u_muls >= 2:
                return 'cubic'
            if u_muls >= 1:
                return 'quadratic'
            return 'linear'
        
        return 'unknown'
    
    def _extract_frequencies(self, expr: str) -> List[float]:
        """Extract frequency values from expression."""
        frequencies = []
        
        # Pattern: sin(ω*t) or cos(ω*t) where ω is a number
        # Matches: sin(0.1*t), cos(2*pi*t/50), sin(0.125*t + 0.5)
        patterns = [
            r'(?:sin|cos)\s*\(\s*([\d\.]+)\s*\*\s*[tu]',  # sin(0.1*t)
            r'(?:sin|cos)\s*\(\s*[tu]\s*\*\s*([\d\.]+)',  # sin(t*0.1)
            r'2\s*\*?\s*(?:pi|3\.14\d*)\s*\*?\s*[tu]\s*/\s*([\d\.]+)',  # 2*pi*t/P -> ω = 2π/P
        ]
        
        for pattern in patterns[:2]:
            matches = re.findall(pattern, expr.lower())
            for m in matches:
                try:
                    frequencies.append(float(m))
                except ValueError:
                    pass
        
        # Handle 2*pi*t/P format
        period_pattern = r'2\s*\*?\s*(?:pi|3\.14\d*)\s*\*?\s*[tu]\s*/\s*([\d\.]+)'
        period_matches = re.findall(period_pattern, expr.lower())
        for m in period_matches:
            try:
                period = float(m)
                if period > 0:
                    frequencies.append(2 * np.pi / period)
            except ValueError:
                pass
        
        return sorted(set(frequencies))
    
    def _check_phase_equiv(self, pred: str, true: str) -> bool:
        """Check if expressions are equivalent up to phase shift."""
        # Simple check: both use sin/cos
        pred_has_sin = 'sin' in pred.lower()
        pred_has_cos = 'cos' in pred.lower()
        true_has_sin = 'sin' in true.lower()
        true_has_cos = 'cos' in true.lower()
        
        # If both have trig functions, consider phase equivalent
        if (pred_has_sin or pred_has_cos) and (true_has_sin or true_has_cos):
            return True
        
        return False
    
    def _compute_score(self, result: MechanismMatch) -> float:
        """Compute weighted mechanism score [0, 1]."""
        score = 0.0
        weights_sum = 0.0
        
        # Trend family (weight 0.3)
        if result.trend_family_match:
            score += 0.3
        weights_sum += 0.3
        
        # Omega error (weight 0.3, scaled by tolerance)
        if result.omega_error < float('inf'):
            omega_score = max(0, 1 - result.omega_error / self.omega_tolerance)
            score += 0.3 * omega_score
        weights_sum += 0.3
        
        # Harmonic coverage (weight 0.2)
        score += 0.2 * result.harmonic_coverage
        weights_sum += 0.2
        
        # Frequency count match (weight 0.1)
        if result.freq_count_match:
            score += 0.1
        weights_sum += 0.1
        
        # Phase equivalence (weight 0.1)
        if result.phase_equiv:
            score += 0.1
        weights_sum += 0.1
        
        return score / weights_sum if weights_sum > 0 else 0.0
