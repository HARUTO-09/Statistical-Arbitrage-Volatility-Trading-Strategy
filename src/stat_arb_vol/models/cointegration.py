"""Cointegration utilities based on Engle-Granger tests."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from statsmodels.tsa.stattools import coint


@dataclass
class PairCandidate:
    asset_x: str
    asset_y: str
    pvalue: float
    score: float


class CointegrationSelector:
    def __init__(self, significance: float = 0.05) -> None:
        self.significance = significance

    def select_pairs(self, prices: pd.DataFrame) -> list[PairCandidate]:
        symbols = prices.columns.tolist()
        selected: list[PairCandidate] = []

        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                x, y = symbols[i], symbols[j]
                pair = prices[[x, y]].dropna()
                if len(pair) < 120:
                    continue
                score, pvalue, _ = coint(pair[x], pair[y])
                if pvalue <= self.significance:
                    selected.append(PairCandidate(x, y, pvalue, score))

        selected.sort(key=lambda p: p.pvalue)
        return selected
