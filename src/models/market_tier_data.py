"""Market tier data models"""
from dataclasses import dataclass
from typing import List


@dataclass
class MarketTierData:
    """Market tier classification"""
    tier: int  # 1, 2, or 3
    adjustment_factor: float  # 1.25, 1.0, or 0.85
    teams: List[str]
