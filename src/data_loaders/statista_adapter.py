"""Statista data adapter for WNBA statistics

Note: Statista data requires manual entry from source as it's behind a paywall.
This adapter provides stub methods for data entry.
"""
from typing import Optional


class StatistaAdapter:
    """
    Adapter for Statista WNBA data
    
    Note: Statista data must be manually entered from source.
    These methods serve as stubs for manual data entry.
    """
    
    def __init__(self):
        """Initialize Statista adapter with empty data store"""
        self._viewership_data = {}
        self._attendance_data = {}
        self._salary_data = {}
    
    def get_viewership_data(self, year: int) -> float:
        """
        Get league viewership for a given year
        
        Args:
            year: Year to get viewership data for
            
        Returns:
            Average viewership in millions
            
        Raises:
            ValueError: If data for the year is not available
            
        Note:
            Data must be manually entered from Statista source:
            https://www.statista.com/statistics/1236723/wnba-regular-season-viewers/
        """
        if year not in self._viewership_data:
            raise ValueError(
                f"Viewership data for year {year} not available. "
                "Please manually enter data from Statista source."
            )
        return self._viewership_data[year]
    
    def set_viewership_data(self, year: int, viewership: float) -> None:
        """
        Manually set viewership data for a year
        
        Args:
            year: Year to set data for
            viewership: Average viewership in millions
        """
        if viewership < 0:
            raise ValueError("Viewership must be non-negative")
        self._viewership_data[year] = viewership
    
    def get_attendance_data(self, team_id: str, year: int) -> float:
        """
        Get team attendance for a given year
        
        Args:
            team_id: Team identifier
            year: Year to get attendance data for
            
        Returns:
            Average home attendance per game
            
        Raises:
            ValueError: If data for the team/year is not available
            
        Note:
            Data must be manually entered from Statista source:
            https://www.statista.com/statistics/1236749/wnba-team-attendance/
        """
        key = (team_id, year)
        if key not in self._attendance_data:
            raise ValueError(
                f"Attendance data for team {team_id} in year {year} not available. "
                "Please manually enter data from Statista source."
            )
        return self._attendance_data[key]
    
    def set_attendance_data(self, team_id: str, year: int, attendance: float) -> None:
        """
        Manually set attendance data for a team/year
        
        Args:
            team_id: Team identifier
            year: Year to set data for
            attendance: Average home attendance per game
        """
        if attendance < 0:
            raise ValueError("Attendance must be non-negative")
        key = (team_id, year)
        self._attendance_data[key] = attendance
    
    def get_salary_data(self, player_id: str, year: int) -> float:
        """
        Get player salary for a given year
        
        Args:
            player_id: Player identifier
            year: Year to get salary data for
            
        Returns:
            Player annual salary in dollars
            
        Raises:
            ValueError: If data for the player/year is not available
            
        Note:
            Data must be manually entered from Statista source:
            https://www.statista.com/statistics/1120680/annual-salaries-nba-wnba/
        """
        key = (player_id, year)
        if key not in self._salary_data:
            raise ValueError(
                f"Salary data for player {player_id} in year {year} not available. "
                "Please manually enter data from Statista source."
            )
        return self._salary_data[key]
    
    def set_salary_data(self, player_id: str, year: int, salary: float) -> None:
        """
        Manually set salary data for a player/year
        
        Args:
            player_id: Player identifier
            year: Year to set data for
            salary: Player annual salary in dollars
        """
        if salary < 0:
            raise ValueError("Salary must be non-negative")
        key = (player_id, year)
        self._salary_data[key] = salary
