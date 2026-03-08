"""WEHOOP R package adapter for WNBA statistics"""
from typing import Optional, List
import time

from src.models import PlayerData, TeamData, PlayerAnnualRecord, TeamAnnualRecord


class WEHOOPAdapter:
    """
    Adapter for wehoop R package to fetch WNBA statistics
    
    The wehoop package provides WNBA game and player statistics including:
    - Play-by-play data (2002-2024)
    - Team box scores (2003-2024)
    - Player box scores (2002-2024)
    
    Note: wehoop provides on-court performance data but does not include
    financial metrics (revenue, valuations, sponsorships).
    
    Installation (R):
        if (!requireNamespace('pacman', quietly = TRUE)){   
            install.packages('pacman') 
        }  
        pacman::p_load(wehoop, dplyr, glue, tictoc, progressr)
    
    Python Requirements:
        pip install rpy2
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize WEHOOP adapter
        
        Args:
            max_retries: Maximum number of retry attempts for API calls (default: 3)
        """
        self.max_retries = max_retries
        self._rpy2_available = False
        self._robjects = None
        self._importr = None
        
        # Try to import rpy2
        try:
            import rpy2.robjects as robjects
            from rpy2.robjects.packages import importr
            self._robjects = robjects
            self._importr = importr
            self._rpy2_available = True
        except ImportError:
            pass
    
    def fetch_player_stats(
        self,
        player_id: str,
        start_year: int,
        end_year: int
    ) -> PlayerData:
        """
        Fetch player statistics from wehoop package
        
        Args:
            player_id: Unique player identifier
            start_year: Starting year for data
            end_year: Ending year for data
            
        Returns:
            PlayerData object with career statistics
            
        Raises:
            RuntimeError: If rpy2 or wehoop is not available
            ValueError: If API call fails after retries
        """
        if not self._rpy2_available:
            raise RuntimeError("rpy2 package not available. Install with: pip install rpy2")
        
        for attempt in range(self.max_retries):
            try:
                # Load wehoop package
                wehoop = self._importr('wehoop')
                
                # Fetch player box scores
                # This is a stub - actual implementation would call wehoop functions
                # For now, return mock data structure
                annual_records = []
                for year in range(start_year, end_year + 1):
                    record = PlayerAnnualRecord(
                        year=year,
                        team_id=f"TEAM_{year}",
                        points_per_game=20.0,
                        games_played=40,
                        minutes_per_game=35.0,
                        salary=100000.0,
                        scoring_percentile=0.85
                    )
                    annual_records.append(record)
                
                return PlayerData(
                    player_id=player_id,
                    player_name=f"Player {player_id}",
                    annual_records=annual_records
                )
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(f"Failed to fetch player stats after {self.max_retries} attempts: {e}")
        
        raise ValueError(f"Failed to fetch player stats after {self.max_retries} attempts")
    
    def fetch_team_stats(
        self,
        team_id: str,
        start_year: int,
        end_year: int
    ) -> TeamData:
        """
        Fetch team statistics from wehoop package
        
        Args:
            team_id: Unique team identifier
            start_year: Starting year for data
            end_year: Ending year for data
            
        Returns:
            TeamData object with team statistics
            
        Raises:
            RuntimeError: If rpy2 or wehoop is not available
            ValueError: If API call fails after retries
        """
        if not self._rpy2_available:
            raise RuntimeError("rpy2 package not available. Install with: pip install rpy2")
        
        for attempt in range(self.max_retries):
            try:
                # Load wehoop package
                wehoop = self._importr('wehoop')
                
                # Fetch team box scores
                # This is a stub - actual implementation would call wehoop functions
                annual_records = []
                for year in range(start_year, end_year + 1):
                    record = TeamAnnualRecord(
                        year=year,
                        valuation=100_000_000.0,
                        revenue=20_000_000.0,
                        attendance_avg=8000.0,
                        points_per_game=85.0
                    )
                    annual_records.append(record)
                
                return TeamData(
                    team_id=team_id,
                    team_name=f"Team {team_id}",
                    market_tier=2,
                    dma_ranking=10,
                    annual_records=annual_records
                )
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(f"Failed to fetch team stats after {self.max_retries} attempts: {e}")
        
        raise ValueError(f"Failed to fetch team stats after {self.max_retries} attempts")
