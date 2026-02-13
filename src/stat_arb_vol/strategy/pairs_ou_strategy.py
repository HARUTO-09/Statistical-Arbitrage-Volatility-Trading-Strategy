"""Signal generation for OU-based mean reversion pairs strategy."""

from __future__ import annotations

import pandas as pd

from stat_arb_vol.backtest.events import SignalEvent
from stat_arb_vol.config import BacktestConfig
from stat_arb_vol.models.ou import OUModel


class PairsOUStrategy:
    def __init__(
        self,
        prices: pd.DataFrame,
        pair: tuple[str, str],
        hedge_ratio: float,
        config: BacktestConfig,
    ) -> None:
        self.prices = prices
        self.pair = pair
        self.hedge_ratio = hedge_ratio
        self.config = config
        self.ou = OUModel()
        self.position = 0

        x, y = pair
        self.spread = self.prices[x] - hedge_ratio * self.prices[y]
        self.z = self.ou.rolling_zscore(self.spread, lookback=self.config.lookback)

    def on_bar(self, timestamp: pd.Timestamp) -> SignalEvent | None:
        z = float(self.z.loc[timestamp])
        side = None

        if self.position == 0:
            if z > self.config.entry_z:
                self.position = -1
                side = -1
            elif z < -self.config.entry_z:
                self.position = 1
                side = 1
        elif self.position == 1:
            if z >= -self.config.exit_z or z < -self.config.stop_z:
                self.position = 0
                side = 0
        elif self.position == -1:
            if z <= self.config.exit_z or z > self.config.stop_z:
                self.position = 0
                side = 0

        if side is None:
            return None
        return SignalEvent(timestamp=timestamp, pair=self.pair, side=side, strength=abs(z))
