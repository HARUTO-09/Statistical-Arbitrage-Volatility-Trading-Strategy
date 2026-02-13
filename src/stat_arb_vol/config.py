from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestConfig:
    initial_capital: float = 100_000.0
    transaction_cost_bps: float = 5.0
    slippage_bps_min: float = 1.0
    slippage_bps_max: float = 8.0
    latency_bars: int = 1
    max_drawdown_limit: float = 0.25
    entry_z: float = 2.0
    exit_z: float = 0.5
    stop_z: float = 3.5
    lookback: int = 60
    annualization: int = 252
    out_of_sample_months: int = 24


@dataclass(frozen=True)
class UniverseConfig:
    symbols: tuple[str, ...] = ("BTC", "ETH", "LTC", "XRP", "BNB", "SOL")
    start_date: str = "2020-01-01"
    end_date: str = "2025-01-01"
