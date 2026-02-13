"""Event-driven backtest engine for a single selected pair."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm

from stat_arb_vol.backtest.events import FillEvent, OrderEvent
from stat_arb_vol.config import BacktestConfig
from stat_arb_vol.risk.kelly import KellySizer
from stat_arb_vol.strategy.pairs_ou_strategy import PairsOUStrategy


@dataclass
class BacktestResult:
    pair: tuple[str, str]
    hedge_ratio: float
    equity_curve: pd.Series
    positions: pd.Series
    trade_returns: list[float] = field(default_factory=list)


class EventDrivenBacktester:
    def __init__(
        self,
        prices: pd.DataFrame,
        pair: tuple[str, str],
        config: BacktestConfig,
        hedge_ratio: float | None = None,
    ) -> None:
        self.prices = prices
        self.pair = pair
        self.config = config
        self.kelly = KellySizer()
        self.trade_returns: list[float] = []
        self._entry_equity = None

        self.hedge_ratio = float(hedge_ratio) if hedge_ratio is not None else self._estimate_hedge_ratio()
        self.strategy = PairsOUStrategy(prices=prices, pair=pair, hedge_ratio=self.hedge_ratio, config=config)

    def _estimate_hedge_ratio(self) -> float:
        x, y = self.pair
        aligned = self.prices[[x, y]].dropna()
        model = sm.OLS(aligned[x], sm.add_constant(aligned[y])).fit()
        return float(model.params.iloc[1])

    def run(self) -> BacktestResult:
        x, y = self.pair
        idx = self.prices.index
        equity = pd.Series(index=idx, dtype=float)
        position_side = 0
        exposure = 0.0
        current_qty = 0.0
        cash = self.config.initial_capital
        equity.iloc[0] = cash
        positions = pd.Series(index=idx, dtype=float)
        positions.iloc[0] = 0

        pending_order: OrderEvent | None = None
        pending_submit_time = None

        for i, ts in enumerate(idx[1:], start=1):
            prev_ts = idx[i - 1]
            delta_x = self.prices.loc[ts, x] - self.prices.loc[prev_ts, x]
            delta_y = self.prices.loc[ts, y] - self.prices.loc[prev_ts, y]
            pnl_dollars = position_side * current_qty * (delta_x - self.hedge_ratio * delta_y)
            cash += pnl_dollars

            if pending_order and (i - pending_submit_time) >= self.config.latency_bars:
                fill = self._execute_order(pending_order, ts)
                position_side = fill.side
                current_qty = fill.quantity
                cash -= fill.fee
                pending_order = None
                if position_side != 0:
                    self._entry_equity = cash
                elif self._entry_equity is not None and self._entry_equity > 0:
                    self.trade_returns.append(cash / self._entry_equity - 1)
                    self._entry_equity = None

            signal = self.strategy.on_bar(ts)
            if signal is not None and pending_order is None:
                drawdown = self._compute_drawdown(equity.iloc[:i].ffill())
                kelly_fraction = self.kelly.fraction(self.trade_returns)
                size_fraction = self.kelly.apply_drawdown_limit(
                    drawdown, kelly_fraction, self.config.max_drawdown_limit
                )
                exposure = max(size_fraction * cash, 0.0)
                qty = exposure / max(self.prices.loc[ts, x], 1e-8)
                pending_order = OrderEvent(ts, self.pair, signal.side, qty)
                pending_submit_time = i

            equity.iloc[i] = cash
            positions.iloc[i] = position_side

        return BacktestResult(
            pair=self.pair,
            hedge_ratio=self.hedge_ratio,
            equity_curve=equity.ffill(),
            positions=positions.ffill(),
            trade_returns=self.trade_returns,
        )

    def _execute_order(self, order: OrderEvent, ts: pd.Timestamp) -> FillEvent:
        x, y = order.pair
        base_prices = (self.prices.loc[ts, x], self.prices.loc[ts, y])
        slip_bps = np.random.uniform(self.config.slippage_bps_min, self.config.slippage_bps_max)
        slip_mult = 1 + (slip_bps / 10_000) * np.sign(order.side)
        fill_prices = (base_prices[0] * slip_mult, base_prices[1] * slip_mult)
        notional = abs(order.quantity * fill_prices[0])
        fee = notional * (self.config.transaction_cost_bps / 10_000)
        return FillEvent(ts, order.pair, order.side, order.quantity, fill_prices, fee)

    @staticmethod
    def _compute_drawdown(equity: pd.Series) -> float:
        if equity.empty:
            return 0.0
        peak = equity.cummax()
        dd = (peak - equity) / peak.replace(0, np.nan)
        return float(dd.max(skipna=True) if len(dd) else 0.0)
