"""Team data models"""
from dataclasses import dataclass
from typing import List


@dataclass
class TeamAnnualRecord:
    """Annual record for a team"""
    year: int
    valuation: float
    revenue: float
    attendance_avg: float
    points_per_game: float


@dataclass
class TeamData:
    """Team data with market information"""
    team_id: str
    team_name: str
    market_tier: int  # 1, 2, or 3
    dma_ranking: int
    annual_records: List[TeamAnnualRecord]
