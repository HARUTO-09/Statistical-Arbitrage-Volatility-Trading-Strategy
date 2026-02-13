"""Performance metrics for portfolio backtests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(equity: pd.Series, trade_returns: list[float], annualization: int = 252) -> dict[str, float]:
    ret = equity.pct_change().dropna()
    sharpe = np.sqrt(annualization) * ret.mean() / (ret.std(ddof=0) + 1e-12)

    cummax = equity.cummax()
    drawdown = ((equity - cummax) / cummax.replace(0, np.nan)).min()

    total_years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1 / 365.25)
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / total_years) - 1

    win_rate = float(np.mean(np.array(trade_returns) > 0)) if trade_returns else 0.0

    return {
        "Sharpe Ratio": float(sharpe),
        "Maximum Drawdown": float(abs(drawdown)),
        "CAGR": float(cagr),
        "Win Rate": win_rate,
    }
