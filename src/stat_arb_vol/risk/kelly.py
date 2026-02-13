"""Kelly-criterion based position sizing with drawdown controls."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class KellySizer:
    max_fraction: float = 0.25
    min_fraction: float = 0.01

    def fraction(self, trade_returns: list[float]) -> float:
        if len(trade_returns) < 10:
            return self.min_fraction

        wins = [r for r in trade_returns if r > 0]
        losses = [abs(r) for r in trade_returns if r <= 0]
        if not wins or not losses:
            return self.min_fraction

        p = len(wins) / len(trade_returns)
        b = np.mean(wins) / max(np.mean(losses), 1e-8)
        f = p - (1 - p) / b
        return float(np.clip(f, self.min_fraction, self.max_fraction))

    @staticmethod
    def apply_drawdown_limit(current_drawdown: float, raw_fraction: float, max_drawdown: float) -> float:
        if current_drawdown <= 0:
            return raw_fraction
        if current_drawdown >= max_drawdown:
            return 0.0
        scale = 1 - (current_drawdown / max_drawdown)
        return raw_fraction * max(scale, 0.1)
