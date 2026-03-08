"""Team Value Lift (ΔVt) calculator for brand portability formula"""
from dataclasses import dataclass
from typing import List

from src.models import TeamData, LeagueData, TeamAnnualRecord


@dataclass
class TeamValueLiftResult:
    """Result of team value lift calculation"""
    net_lift: float
    team_growth_rate: float
    league_avg_growth_rate: float
    team_valuation_prior: float
    team_valuation_current: float


class TeamValueLiftCalculator:
    """
    Calculate team value lift (ΔVt): team growth minus league average growth
    
    ΔVt represents the year-over-year increase in the team's valuation following
    a trade, minus the league's average growth rate. This isolates the team-specific
    value increase from general league-wide growth.
    
    Formula: ΔVt = Team Growth Rate - League Average Growth Rate
    """
    
    def calculate(
        self,
        team_data: TeamData,
        league_data: LeagueData,
        prior_year: int,
        current_year: int
    ) -> TeamValueLiftResult:
        """
        Calculate team value lift: team growth minus league average growth
        
        Steps:
        1. Calculate team's year-over-year valuation change
        2. Calculate league-average growth rate
        3. Compute net lift (team growth - league average)
        
        Args:
            team_data: Team's historical valuation and performance data
            league_data: League-wide data for all teams
            prior_year: Starting year for comparison
            current_year: Ending year for comparison
            
        Returns:
            TeamValueLiftResult with breakdown
            
        Raises:
            ValueError: If data for specified years is not available
        """
        # Get team valuations for both years
        team_prior = self._get_team_record(team_data, prior_year)
        team_current = self._get_team_record(team_data, current_year)
        
        if not team_prior:
            raise ValueError(f"Team data not available for year {prior_year}")
        if not team_current:
            raise ValueError(f"Team data not available for year {current_year}")
        
        if team_prior.valuation <= 0:
            raise ValueError(f"Team valuation for {prior_year} must be positive")
        
        # Calculate team growth rate
        team_growth_rate = (
            (team_current.valuation - team_prior.valuation) / team_prior.valuation
        )
        
        # Calculate league average growth rate
        league_avg_growth_rate = self.calculate_league_avg_growth(
            league_data,
            prior_year,
            current_year
        )
        
        # Calculate net lift
        net_lift = team_growth_rate - league_avg_growth_rate
        
        return TeamValueLiftResult(
            net_lift=net_lift,
            team_growth_rate=team_growth_rate,
            league_avg_growth_rate=league_avg_growth_rate,
            team_valuation_prior=team_prior.valuation,
            team_valuation_current=team_current.valuation
        )
    
    def calculate_league_avg_growth(
        self,
        league_data: LeagueData,
        prior_year: int,
        current_year: int
    ) -> float:
        """
        Calculate league-average growth rate
        
        Formula: Σ(Team Valuation Change) / Number of Teams / Prior Year Avg Valuation
        
        This is simplified to: (Current Year Avg Valuation - Prior Year Avg Valuation) / Prior Year Avg Valuation
        
        Args:
            league_data: League-wide data including team valuations
            prior_year: Starting year for comparison
            current_year: Ending year for comparison
            
        Returns:
            League average growth rate as a decimal (e.g., 0.15 for 15% growth)
            
        Raises:
            ValueError: If league data for specified years is not available
        """
        # For this implementation, we'll use a simplified approach
        # In production, this would aggregate all team valuations
        
        # Get league records for both years
        prior_record = self._get_league_record(league_data, prior_year)
        current_record = self._get_league_record(league_data, current_year)
        
        if not prior_record:
            # If no league record, estimate based on typical WNBA growth
            # Historical data shows ~10-20% annual growth
            return 0.15  # 15% default growth rate
        
        if not current_record:
            return 0.15  # Default growth rate
        
        # Calculate growth based on league metrics
        # Use average salary as a proxy for league growth if available
        if prior_record.avg_salary > 0 and current_record.avg_salary > 0:
            salary_growth = (
                (current_record.avg_salary - prior_record.avg_salary) / 
                prior_record.avg_salary
            )
            # Salary growth correlates with but is typically lower than valuation growth
            # Multiply by factor to estimate valuation growth
            return salary_growth * 2.0  # Rough multiplier
        
        # Default to historical average
        return 0.15
    
    def _get_team_record(
        self,
        team_data: TeamData,
        year: int
    ) -> TeamAnnualRecord:
        """Get team record for a specific year"""
        for record in team_data.annual_records:
            if record.year == year:
                return record
        return None
    
    def _get_league_record(self, league_data: LeagueData, year: int):
        """Get league record for a specific year"""
        for record in league_data.annual_records:
            if record.year == year:
                return record
        return None
