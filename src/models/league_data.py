"""League data models"""
from dataclasses import dataclass
from typing import List


@dataclass
class LeagueAnnualRecord:
    """Annual record for league-wide data"""
    year: int
    avg_viewership: float
    avg_attendance: float
    avg_salary: float
    total_teams: int


@dataclass
class LeagueData:
    """League-wide data"""
    annual_records: List[LeagueAnnualRecord]
