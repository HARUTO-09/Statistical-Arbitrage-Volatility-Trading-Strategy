from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MarketEvent:
    timestamp: object


@dataclass
class SignalEvent:
    timestamp: object
    pair: tuple[str, str]
    side: int  # +1 long spread, -1 short spread, 0 flat
    strength: float


@dataclass
class OrderEvent:
    timestamp: object
    pair: tuple[str, str]
    side: int
    quantity: float


@dataclass
class FillEvent:
    timestamp: object
    pair: tuple[str, str]
    side: int
    quantity: float
    fill_prices: tuple[float, float]
    fee: float
