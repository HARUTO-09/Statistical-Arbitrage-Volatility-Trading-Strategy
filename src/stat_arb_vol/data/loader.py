"""Data loading utilities with real-data first and simulated fallback."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "LTC": "litecoin",
    "XRP": "ripple",
    "BNB": "binancecoin",
    "SOL": "solana",
}


@dataclass
class DataLoader:
    symbols: tuple[str, ...]
    start_date: str
    end_date: str

    def load_prices(self) -> pd.DataFrame:
        """Load close prices indexed by daily date."""
        real = self._download_coingecko()
        if real is not None and not real.empty:
            return real.ffill().dropna(how="all")

        LOGGER.warning("Falling back to simulated GBM + latent factor data.")
        return self._simulate_prices()

    def _download_coingecko(self) -> pd.DataFrame | None:
        start = pd.Timestamp(self.start_date)
        end = pd.Timestamp(self.end_date)
        days = max((end - start).days, 365)
        out: dict[str, pd.Series] = {}

        for symbol in self.symbols:
            cg_id = COINGECKO_IDS.get(symbol)
            if cg_id is None:
                continue
            url = (
                f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart"
                f"?vs_currency=usd&days={days}&interval=daily"
            )
            try:
                frame = pd.read_json(url)
                prices = pd.DataFrame(frame["prices"].tolist(), columns=["ts", "close"])
                prices["date"] = pd.to_datetime(prices["ts"], unit="ms").dt.date
                series = prices.groupby("date")["close"].last()
                series.index = pd.to_datetime(series.index)
                series = series.loc[(series.index >= start) & (series.index <= end)]
                if not series.empty:
                    out[symbol] = series
            except Exception as exc:  # pragma: no cover - network-dependent
                LOGGER.warning("Could not download %s from CoinGecko: %s", symbol, exc)

        if not out:
            return None
        return pd.DataFrame(out).sort_index()

    def _simulate_prices(self, seed: int = 7) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        dates = pd.date_range(self.start_date, self.end_date, freq="D")
        latent = rng.normal(0, 0.015, len(dates)).cumsum()
        out = {}

        for i, symbol in enumerate(self.symbols):
            drift = 0.0001 + i * 0.00002
            vol = 0.008 + i * 0.0005
            idio = rng.normal(0, vol, len(dates)).cumsum()
            log_price = np.log(100 + i * 20) + drift * np.arange(len(dates)) + 0.95 * latent + 0.05 * idio
            out[symbol] = np.exp(log_price)

        return pd.DataFrame(out, index=dates)
