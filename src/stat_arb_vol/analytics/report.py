"""Generate visual reports and markdown summaries."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_performance_plot(equity: pd.Series, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    equity.plot(ax=ax, color="navy", lw=1.6)
    ax.set_title("Portfolio Equity Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def write_markdown_report(metrics: dict[str, float], selected_pair: tuple[str, str], out_file: str) -> None:
    lines = [
        "# Backtest Performance Report",
        "",
        f"Selected Pair: **{selected_pair[0]} / {selected_pair[1]}**",
        "",
        "## Metrics",
    ]
    for key, value in metrics.items():
        lines.append(f"- **{key}:** {value:.4f}")

    lines.extend(
        [
            "",
            "## Notes",
            "- Event-driven simulation with latency, costs, and slippage.",
            "- Pair selected via Engle-Granger cointegration test.",
            "- Position sizing uses Kelly criterion plus drawdown scaling.",
        ]
    )

    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text("\n".join(lines), encoding="utf-8")
