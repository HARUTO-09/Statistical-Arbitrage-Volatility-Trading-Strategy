"""Run end-to-end strategy research workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import statsmodels.api as sm

from stat_arb_vol.analytics.metrics import compute_metrics
from stat_arb_vol.analytics.report import create_performance_plot, write_markdown_report
from stat_arb_vol.backtest.engine import EventDrivenBacktester
from stat_arb_vol.config import BacktestConfig, UniverseConfig
from stat_arb_vol.data.loader import DataLoader
from stat_arb_vol.models.cointegration import CointegrationSelector


def split_train_test(prices: pd.DataFrame, out_of_sample_months: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = prices.index.max() - pd.DateOffset(months=out_of_sample_months)
    train = prices.loc[prices.index < cutoff]
    test = prices.loc[prices.index >= cutoff]
    return train, test


def estimate_spread_params(train: pd.DataFrame, pair: tuple[str, str]) -> tuple[float, pd.Series]:
    x, y = pair
    model = sm.OLS(train[x], sm.add_constant(train[y])).fit()
    beta = float(model.params.iloc[1])
    spread = train[x] - beta * train[y]
    return beta, spread


def main(use_mock_only: bool = False) -> None:
    universe = UniverseConfig()
    config = BacktestConfig()

    loader = DataLoader(universe.symbols, universe.start_date, universe.end_date)
    prices = loader._simulate_prices() if use_mock_only else loader.load_prices()

    prices = prices.asfreq("D").ffill().dropna()
    train, test = split_train_test(prices, config.out_of_sample_months)

    selector = CointegrationSelector(significance=0.05)
    candidates = selector.select_pairs(train)
    if not candidates:
        raise RuntimeError("No cointegrated pairs found. Try mock mode or broader universe.")

    pair = (candidates[0].asset_x, candidates[0].asset_y)
    hedge_ratio, _ = estimate_spread_params(train, pair)
    backtester = EventDrivenBacktester(test, pair, config, hedge_ratio=hedge_ratio)
    result = backtester.run()
    metrics = compute_metrics(result.equity_curve, result.trade_returns, annualization=config.annualization)

    Path("reports").mkdir(exist_ok=True)
    create_performance_plot(result.equity_curve, "reports/equity_curve.png")
    write_markdown_report(metrics, pair, "reports/performance_report.md")

    data_schema = {
        "index": "datetime64[ns] daily",
        "columns": [{"symbol": col, "type": "float close price"} for col in prices.columns],
    }
    Path("data/sample_schema.json").write_text(json.dumps(data_schema, indent=2), encoding="utf-8")

    summary = {
        "selected_pair": pair,
        "hedge_ratio": result.hedge_ratio,
        "metrics": metrics,
        "target_sharpe_ratio": 2.1,
        "target_achieved": metrics["Sharpe Ratio"] >= 2.1,
    }
    Path("reports/summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run stat-arb volatility strategy backtest")
    parser.add_argument("--mock-only", action="store_true", help="use simulated data only")
    args = parser.parse_args()
    main(use_mock_only=args.mock_only)
