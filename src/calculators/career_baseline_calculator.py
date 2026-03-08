"""Career Historical Baseline (Ch) calculator for brand portability formula"""
from dataclasses import dataclass
from typing import List, Tuple

from src.models import PlayerData, TeamData
from src.estimators import PlayerRevenueAttributor


@dataclass
class CareerBaselineResult:
    """Result of career baseline calculation"""
    avg_annual_output: float
    total_years: int
    annual_breakdown: List[Tuple[int, float]]  # (year, output)


class CareerBaselineCalculator:
    """
    Calculate player's career historical baseline (Ch)
    
    Ch represents the player's average annual commercial output from their career data.
    This acts as the control variable in the brand portability formula.
    
    Formula: Ch = Σ(Annual Commercial Output) / Number of Years
    
    Annual Commercial Output is calculated using the PlayerRevenueAttributor to estimate
    the player's revenue contribution for each year of their career.
    """
    
    def __init__(self, revenue_attributor: PlayerRevenueAttributor):
        """
        Initialize CareerBaselineCalculator with revenue attributor dependency
        
        Args:
            revenue_attributor: Estimator for player revenue attribution
        """
        self.revenue_attributor = revenue_attributor
    
    def calculate(
        self,
        player_data: PlayerData,
        team_data_history: List[TeamData]
    ) -> CareerBaselineResult:
        """
        Calculate player's career historical baseline
        
        Steps:
        1. Aggregate player career data across all teams
        2. Calculate annual commercial output for each year
        3. Compute arithmetic mean of all annual outputs
        
        Args:
            player_data: Player career statistics and performance
            team_data_history: Historical data for all teams player has been on
            
        Returns:
            CareerBaselineResult with year-by-year breakdown
            
        Raises:
            ValueError: If player has no career data or career baseline is zero
        """
        if not player_data.annual_records:
            raise ValueError("Player must have at least one year of career data")
        
        if not team_data_history:
            raise ValueError("Team data history must be provided")
        
        # Build team data lookup by team_id and year
        team_lookup = self._build_team_lookup(team_data_history)
        
        # Calculate annual commercial output for each year
        annual_breakdown = []
        total_output = 0.0
        
        for record in player_data.annual_records:
            # Get team data for this year
            team_data = self._get_team_data(team_lookup, record.team_id, record.year)
            
            if not team_data:
                # Skip years where team data is not available
                continue
            
            # Calculate annual commercial output
            annual_output = self._calculate_annual_output(record, team_data)
            
            annual_breakdown.append((record.year, annual_output))
            total_output += annual_output
        
        if not annual_breakdown:
            raise ValueError(
                "Cannot calculate career baseline: no valid annual data available"
            )
        
        # Calculate average annual output
        avg_annual_output = total_output / len(annual_breakdown)
        
        # Edge case: zero career baseline should raise exception
        if avg_annual_output <= 0:
            raise ValueError(
                "Cannot calculate portability: player has zero career baseline. "
                "This indicates the player has no measurable commercial output."
            )
        
        return CareerBaselineResult(
            avg_annual_output=avg_annual_output,
            total_years=len(annual_breakdown),
            annual_breakdown=annual_breakdown
        )
    
    def _calculate_annual_output(
        self,
        player_record,
        team_data: TeamData
    ) -> float:
        """
        Calculate annual commercial output for a single year
        
        Uses PlayerRevenueAttributor to estimate the player's contribution
        to team revenue for that year.
        
        Args:
            player_record: PlayerAnnualRecord for the year
            team_data: TeamData for the team in that year
            
        Returns:
            Estimated annual commercial output
        """
        # Find team records for this year and prior year
        team_record_current = None
        team_record_prior = None
        
        for record in team_data.annual_records:
            if record.year == player_record.year:
                team_record_current = record
            elif record.year == player_record.year - 1:
                team_record_prior = record
        
        if not team_record_current:
            # No team data for this year, return zero
            return 0.0
        
        # Calculate team revenue change
        if team_record_prior and team_record_prior.revenue > 0:
            team_revenue_change = team_record_current.revenue - team_record_prior.revenue
        else:
            # If no prior year data, assume player contributed to current revenue
            # Use a conservative estimate (10% of current revenue)
            team_revenue_change = team_record_current.revenue * 0.1
        
        # Get team PPG for this year
        team_ppg = team_record_current.points_per_game
        if team_ppg <= 0:
            # Default to league average if not available
            team_ppg = 80.0
        
        # Estimate team salary cap (WNBA cap is around $1.46M in 2024)
        # Scale based on year if needed
        team_salary_cap = 1_460_000
        
        # Total games in WNBA season (40 regular season games)
        total_games = 40
        
        # Use revenue attributor to calculate player's contribution
        try:
            annual_output = self.revenue_attributor.calculate_attribution(
                team_revenue_change=team_revenue_change,
                player_ppg=player_record.points_per_game,
                team_ppg=team_ppg,
                player_salary=player_record.salary,
                team_salary_cap=team_salary_cap,
                games_played=player_record.games_played,
                total_games=total_games,
                minutes_per_game=player_record.minutes_per_game
            )
            
            # Ensure non-negative output
            return max(0.0, annual_output)
            
        except ValueError:
            # If attribution calculation fails, return zero
            return 0.0
    
    def _build_team_lookup(self, team_data_history: List[TeamData]) -> dict:
        """
        Build lookup dictionary for team data by team_id
        
        Args:
            team_data_history: List of TeamData objects
            
        Returns:
            Dictionary mapping team_id to TeamData
        """
        return {team.team_id: team for team in team_data_history}
    
    def _get_team_data(
        self,
        team_lookup: dict,
        team_id: str,
        year: int
    ) -> TeamData:
        """
        Get team data for a specific team and year
        
        Args:
            team_lookup: Dictionary mapping team_id to TeamData
            team_id: Team identifier
            year: Year to look up
            
        Returns:
            TeamData if found, None otherwise
        """
        return team_lookup.get(team_id)
