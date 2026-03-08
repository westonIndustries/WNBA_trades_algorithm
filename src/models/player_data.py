"""Player data models"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PlayerAnnualRecord:
    """Annual record for a player"""
    year: int
    team_id: str
    points_per_game: float
    games_played: int
    minutes_per_game: float
    salary: float
    scoring_percentile: Optional[float] = None


@dataclass
class PlayerData:
    """Player career data"""
    player_id: str
    player_name: str
    annual_records: List[PlayerAnnualRecord]
