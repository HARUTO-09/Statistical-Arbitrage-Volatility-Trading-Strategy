"""Ornstein-Uhlenbeck parameter estimation and signal helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import zscore


@dataclass
class OUParams:
    theta: float
    mu: float
    sigma: float


class OUModel:
    def estimate(self, spread: pd.Series, dt: float = 1.0) -> OUParams:
        s = spread.dropna().values
        if len(s) < 3:
            return OUParams(theta=0.0, mu=float(np.nanmean(s) if len(s) else 0), sigma=0.0)

        x = s[:-1]
        y = s[1:]
        beta, alpha = np.polyfit(x, y, 1)
        beta = np.clip(beta, 1e-6, 0.999999)
        theta = -np.log(beta) / dt
        mu = alpha / (1 - beta)

        resid = y - (alpha + beta * x)
        sigma_hat = np.std(resid, ddof=1)
        sigma = sigma_hat * np.sqrt(2 * theta / (1 - beta**2)) if theta > 0 else sigma_hat
        return OUParams(theta=float(theta), mu=float(mu), sigma=float(abs(sigma)))

    @staticmethod
    def rolling_zscore(spread: pd.Series, lookback: int) -> pd.Series:
        mean = spread.rolling(lookback).mean()
        std = spread.rolling(lookback).std(ddof=0).replace(0, np.nan)
        return ((spread - mean) / std).fillna(0.0)

    @staticmethod
    def static_zscore(spread: pd.Series) -> pd.Series:
        values = zscore(spread.dropna())
        out = pd.Series(index=spread.dropna().index, data=values)
        return out.reindex(spread.index).fillna(0.0)
