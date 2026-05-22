from __future__ import annotations

"""Optional adapters to established backtesting and reporting libraries."""

from pathlib import Path
from typing import Any

import pandas as pd


def run_vectorbt_from_signals(
    close: pd.DataFrame,
    entries: pd.DataFrame,
    exits: pd.DataFrame,
    *,
    fees: float = 0.0005,
    slippage: float = 0.0002,
    init_cash: float = 100_000.0,
) -> Any:
    """Run `vectorbt.Portfolio.from_signals` when vectorbt is installed."""

    try:
        import vectorbt as vbt  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install vectorbt to use this adapter: python -m pip install vectorbt") from exc
    return vbt.Portfolio.from_signals(
        close,
        entries=entries.reindex_like(close).fillna(False),
        exits=exits.reindex_like(close).fillna(False),
        init_cash=init_cash,
        fees=fees,
        slippage=slippage,
        freq="1D",
    )


def run_bt_target_weights(close: pd.DataFrame, weights: pd.DataFrame, *, name: str = "detime_rotation") -> Any:
    """Run the `bt` framework from a target-weight matrix."""

    try:
        import bt  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install bt to use this adapter: python -m pip install bt") from exc
    aligned = weights.reindex(index=close.index, columns=close.columns).fillna(0.0)
    strategy = bt.Strategy(
        name,
        [bt.algos.RunDaily(), bt.algos.SelectAll(), bt.algos.WeighTarget(aligned), bt.algos.Rebalance()],
    )
    test = bt.Backtest(strategy, close)
    return bt.run(test)


def run_backtestingpy_signal(
    ohlcv: pd.DataFrame,
    signal: pd.Series,
    *,
    cash: float = 100_000.0,
    commission: float = 0.0005,
) -> Any:
    """Run backtesting.py from a precomputed side signal.

    The signal should be 1 for long, -1 for short, and 0 for flat.
    """

    try:
        from backtesting import Backtest, Strategy  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install backtesting.py to use this adapter: python -m pip install backtesting") from exc

    data = ohlcv.copy()
    sig = signal.reindex(data.index).fillna(0.0).astype(float)

    class PrecomputedDeTimeSignal(Strategy):
        def init(self):
            self.signal = self.I(lambda: sig.to_numpy(), name="detime_signal")

        def next(self):
            value = self.signal[-1]
            if value > 0 and not self.position.is_long:
                self.position.close()
                self.buy()
            elif value < 0 and not self.position.is_short:
                self.position.close()
                self.sell()
            elif value == 0 and self.position:
                self.position.close()

    bt = Backtest(data, PrecomputedDeTimeSignal, cash=cash, commission=commission, exclusive_orders=True)
    return bt.run()


BACKTRADER_TEMPLATE = """
import backtrader as bt

class DeTimeSignalData(bt.feeds.PandasData):
    lines = ('detime_signal',)
    params = (('detime_signal', -1),)

class DeTimeSignalStrategy(bt.Strategy):
    params = dict(stake=10)

    def next(self):
        sig = self.data.detime_signal[0]
        if sig > 0 and not self.position:
            self.buy(size=self.params.stake)
        elif sig <= 0 and self.position:
            self.sell(size=self.params.stake)

# cerebro = bt.Cerebro()
# cerebro.addstrategy(DeTimeSignalStrategy)
# cerebro.adddata(DeTimeSignalData(dataname=your_ohlcv_with_detime_signal))
# cerebro.broker.setcash(100000.0)
# cerebro.broker.setcommission(commission=0.0005)
# result = cerebro.run()
""".strip()


ZIPLINE_RELOADED_TEMPLATE = """
from zipline.api import order_target_percent, record, symbol

# Precompute De-Time signals outside Zipline, store them in a calendar-safe
# bundle/CSV/Pipeline field, and align them to the Zipline trading calendar.

def initialize(context):
    context.asset = symbol('AAPL')


def handle_data(context, data):
    sig = 0  # Replace with a date-indexed De-Time signal lookup.
    if sig > 0:
        order_target_percent(context.asset, 1.0)
    elif sig < 0:
        order_target_percent(context.asset, -1.0)
    else:
        order_target_percent(context.asset, 0.0)
    record(detime_signal=sig)
""".strip()


def write_framework_templates(output_dir: str | Path) -> list[Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    payloads = {
        "backtrader_detime_signal_template.py": BACKTRADER_TEMPLATE,
        "zipline_reloaded_detime_signal_template.py": ZIPLINE_RELOADED_TEMPLATE,
    }
    paths: list[Path] = []
    for filename, text in payloads.items():
        path = out / filename
        path.write_text(text + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def quantstats_html_report(returns: pd.Series, output_path: str | Path, *, benchmark: pd.Series | None = None) -> Path:
    """Create a QuantStats HTML report when quantstats is installed."""

    try:
        import quantstats as qs  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install quantstats to create tear sheets: python -m pip install quantstats") from exc
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    qs.reports.html(returns.dropna(), benchmark=benchmark, output=str(out))
    return out
