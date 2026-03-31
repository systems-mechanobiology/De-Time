"""
Budget Controller for fair comparison in Decomp+SR pipeline.

Ensures all SR methods use identical:
- Time budget (wall-clock limit)
- Complexity budget (max nodes, max depth)
- Operator set
"""

from __future__ import annotations

import time
import signal
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from contextlib import contextmanager


@dataclass
class BudgetConfig:
    """Configuration for fair comparison budgets."""
    
    # Time budget
    time_budget_sec: float = 60.0
    
    # Complexity budget
    max_nodes: int = 50
    max_depth: int = 10
    
    # Operator set (must be identical for all methods)
    operators: List[str] = field(default_factory=lambda: [
        'add', 'sub', 'mul', 'div', 'sin', 'cos', 'exp'
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time_budget_sec': self.time_budget_sec,
            'max_nodes': self.max_nodes,
            'max_depth': self.max_depth,
            'operators': self.operators.copy(),
        }


class TimeoutError(Exception):
    """Raised when operation exceeds time budget."""
    pass


class BudgetController:
    """
    Controls time and complexity budgets for fair comparison.
    
    Usage:
        controller = BudgetController(config)
        with controller.time_limit():
            result = sr_method.fit(t, y)
        controller.check_complexity(result.expression)
    """
    
    def __init__(self, config: Optional[BudgetConfig] = None):
        self.config = config or BudgetConfig()
        self._start_time: Optional[float] = None
        self._timed_out: bool = False
    
    @contextmanager
    def time_limit(self):
        """Context manager for time-limited execution."""
        self._start_time = time.time()
        self._timed_out = False
        
        def handler(signum, frame):
            self._timed_out = True
            raise TimeoutError(f"Exceeded time budget of {self.config.time_budget_sec}s")
        
        # Set alarm (Unix only)
        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(int(self.config.time_budget_sec) + 1)
        
        try:
            yield
        except TimeoutError:
            self._timed_out = True
            raise
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def elapsed_time(self) -> float:
        """Get elapsed time since time_limit started."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    def check_complexity(self, expression: str) -> Dict[str, Any]:
        """
        Check if expression meets complexity budget.
        
        Returns:
            Dict with 'nodes', 'depth', 'within_budget' fields.
        """
        nodes = self._count_nodes(expression)
        depth = self._count_depth(expression)
        
        return {
            'nodes': nodes,
            'depth': depth,
            'within_budget': (nodes <= self.config.max_nodes and 
                            depth <= self.config.max_depth),
            'max_nodes': self.config.max_nodes,
            'max_depth': self.config.max_depth,
        }
    
    def _count_nodes(self, expr: str) -> int:
        """Count nodes in expression (simple approximation)."""
        if not expr:
            return 0
        # Count operators and operands
        import re
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[+\-*/()]', expr)
        return len([t for t in tokens if t not in '()'])
    
    def _count_depth(self, expr: str) -> int:
        """Count max nesting depth in expression."""
        if not expr:
            return 0
        max_depth = 0
        current = 0
        for c in expr:
            if c == '(':
                current += 1
                max_depth = max(max_depth, current)
            elif c == ')':
                current -= 1
        return max_depth
    
    def get_gplearn_params(self) -> Dict[str, Any]:
        """Get GPlearn-compatible parameters from budget."""
        return {
            'function_set': self._convert_operators_gplearn(),
            'init_depth': (2, min(6, self.config.max_depth)),
            'max_samples': 1.0,
        }
    
    def get_pysr_params(self) -> Dict[str, Any]:
        """Get PySR-compatible parameters from budget."""
        return {
            'binary_operators': ['+', '-', '*', '/'],
            'unary_operators': ['sin', 'cos', 'exp'],
            'maxsize': self.config.max_nodes,
            'timeout_in_seconds': int(self.config.time_budget_sec),
        }
    
    def _convert_operators_gplearn(self) -> List[str]:
        """Convert operator names to GPlearn format."""
        mapping = {
            'add': 'add', '+': 'add',
            'sub': 'sub', '-': 'sub',
            'mul': 'mul', '*': 'mul',
            'div': 'div', '/': 'div',
            'sin': 'sin', 'cos': 'cos',
            'exp': 'exp', 'log': 'log',
            'sqrt': 'sqrt', 'abs': 'abs',
        }
        result = []
        for op in self.config.operators:
            if op.lower() in mapping:
                gp_op = mapping[op.lower()]
                if gp_op not in result:
                    result.append(gp_op)
        return result
    
    @property
    def timed_out(self) -> bool:
        return self._timed_out
