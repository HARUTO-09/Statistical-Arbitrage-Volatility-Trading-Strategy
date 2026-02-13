# Statistical Arbitrage & Volatility Trading Strategy

Research-grade, modular Python implementation for **pairs trading/statistical arbitrage** with an **OU mean-reversion spread model**, **event-driven backtester**, and **Kelly-based risk management**.

## Project Structure

```text
.
├── data/
│   └── sample_schema.json            # generated schema example
├── reports/
│   ├── equity_curve.png              # generated visualization
│   ├── performance_report.md          # generated report
│   └── summary.json                  # key metrics + target check
├── scripts/
│   └── run_backtest.py               # end-to-end execution pipeline
├── src/stat_arb_vol/
│   ├── analytics/
│   │   ├── metrics.py
│   │   └── report.py
│   ├── backtest/
│   │   ├── engine.py
│   │   └── events.py
│   ├── data/
│   │   └── loader.py
│   ├── models/
│   │   ├── cointegration.py
│   │   └── ou.py
│   ├── risk/
│   │   └── kelly.py
│   ├── strategy/
│   │   └── pairs_ou_strategy.py
│   ├── web/
│   │   └── app.py
│   └── config.py
└── requirements.txt
```

## Core Features

- **Pair Selection:** Engle-Granger two-step cointegration screening.
- **Spread Modeling:** Ornstein-Uhlenbeck inspired mean-reversion dynamics + rolling z-score signals.
- **Backtesting:** Event-driven flow with latency, transaction costs, and variable slippage.
- **Risk Management:** Kelly sizing with drawdown-based exposure throttling.
- **Evaluation:** Out-of-sample backtest metrics (Sharpe, max drawdown, CAGR, win rate).
- **Web App:** Modern interactive dashboard with performance cards, equity visualization, and artifact drill-down links.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
```

## Run End-to-End Backtest

Prefer real data (CoinGecko); automatically falls back to simulated data if unavailable:

```bash
python scripts/run_backtest.py
```

Mock-only mode:

```bash
python scripts/run_backtest.py --mock-only
```

## Launch Interactive Web Dashboard

```bash
python -m stat_arb_vol.web.app
```

Then open: `http://localhost:8000`

## Sample Backtesting Workflow

1. Load crypto close-price universe (real or simulated).
2. Split into train / 24-month out-of-sample test windows.
3. Select statistically significant cointegrated pairs via Engle-Granger.
4. Estimate hedge ratio and run event-driven OU/z-score strategy.
5. Apply latency, slippage, and cost model at execution layer.
6. Size positions with Kelly + drawdown limit.
7. Export metrics, report, and equity visualization.

## Notes

- Strategy research code is deterministic in mock mode and network-dependent in real-data mode.
- This is a baseline research architecture suitable for extension (multi-pair portfolio, walk-forward re-fit, volatility surface overlays, etc.).
