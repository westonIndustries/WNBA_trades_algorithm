"""Brand Portability Formula calculator - main application layer"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.models import PlayerData, TeamData, LeagueData, MarketTierData
from src.calculators.revenue_delta_calculator import (
    RevenueDeltaCalculator,
    RevenueDeltaResult
)
from src.calculators.team_value_lift_calculator import (
    TeamValueLiftCalculator,
    TeamValueLiftResult
)
from src.calculators.career_baseline_calculator import (
    CareerBaselineCalculator,
    CareerBaselineResult
)
from src.calculators.market_adjustment_calculator import (
    MarketAdjustmentCalculator,
    MarketAdjustmentResult
)


@dataclass
class ComponentBreakdown:
    """Breakdown of all formula components"""
    career_baseline: CareerBaselineResult
    market_adjustment: MarketAdjustmentResult
    revenue_delta: RevenueDeltaResult
    team_value_lift: TeamValueLiftResult


@dataclass
class BrandPortabilityResult:
    """Result of brand portability calculation"""
    chi: float
    components: ComponentBreakdown
    formula: str
    interpretation: str
    warnings: List[str]


class BrandPortabilityCalculator:
    """
    Calculate brand portability score χ (chi)
    
    The brand portability formula measures a player's potential impact on team value
    and revenue when traded to a new market.
    
    Formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt)
    
    Where:
    - Ch = Career Historical Baseline (control variable)
    - Ma = Market Adjustment Factor
    - ΔRm = Revenue Delta (new city vs career average)
    - ΔVt = Team Value Lift (team growth minus league average)
    
    Higher χ values indicate greater potential impact on team value/revenue.
    """
    
    def __init__(
        self,
        revenue_delta_calc: RevenueDeltaCalculator,
        team_value_lift_calc: TeamValueLiftCalculator,
        career_baseline_calc: CareerBaselineCalculator,
        market_adjustment_calc: MarketAdjustmentCalculator
    ):
        """
        Initialize BrandPortabilityCalculator with all calculator dependencies
        
        Args:
            revenue_delta_calc: Calculator for ΔRm (revenue delta)
            team_value_lift_calc: Calculator for ΔVt (team value lift)
            career_baseline_calc: Calculator for Ch (career baseline)
            market_adjustment_calc: Calculator for Ma (market adjustment)
        """
        self.revenue_delta_calc = revenue_delta_calc
        self.team_value_lift_calc = team_value_lift_calc
        self.career_baseline_calc = career_baseline_calc
        self.market_adjustment_calc = market_adjustment_calc
    
    def calculate_portability(
        self,
        player_data: PlayerData,
        new_team_data: TeamData,
        league_data: LeagueData,
        market_tier_data: MarketTierData,
        team_data_history: List[TeamData],
        prior_year: int,
        current_year: int,
        player_contribution_weight: float = 0.35
    ) -> BrandPortabilityResult:
        """
        Calculate brand portability score χ
        
        Formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt)
        
        Steps:
        1. Calculate all component variables (Ch, Ma, ΔRm, ΔVt)
        2. Apply formula
        3. Handle edge cases (division by zero, negative values)
        4. Return structured result with all intermediate values
        
        Args:
            player_data: Player career statistics and performance
            new_team_data: New team's market and performance data
            league_data: League-wide averages and trends
            market_tier_data: Market tier classification for new team
            team_data_history: Historical data for all teams player has been on
            prior_year: Starting year for team value lift calculation
            current_year: Ending year for team value lift calculation
            player_contribution_weight: Player's contribution weight (0.0 to 1.0)
            
        Returns:
            BrandPortabilityResult with full breakdown
            
        Raises:
            ValueError: If career baseline is zero or inputs are invalid
        """
        warnings = []
        
        # Calculate Ch (Career Historical Baseline)
        try:
            career_baseline_result = self.career_baseline_calc.calculate(
                player_data=player_data,
                team_data_history=team_data_history
            )
            ch = career_baseline_result.avg_annual_output
        except ValueError as e:
            # Zero career baseline should raise exception
            raise ValueError(f"Cannot calculate brand portability: {str(e)}")
        
        # Calculate Ma (Market Adjustment Factor)
        market_adjustment_result = self.market_adjustment_calc.calculate(
            team_data=new_team_data,
            market_tier_data=market_tier_data,
            player_contribution_weight=player_contribution_weight
        )
        ma = market_adjustment_result.adjustment_factor
        
        # Calculate ΔRm (Revenue Delta)
        revenue_delta_result = self.revenue_delta_calc.calculate(
            player_data=player_data,
            new_team_data=new_team_data,
            league_data=league_data
        )
        delta_rm = revenue_delta_result.total_delta
        
        # Calculate ΔVt (Team Value Lift)
        team_value_lift_result = self.team_value_lift_calc.calculate(
            team_data=new_team_data,
            league_data=league_data,
            prior_year=prior_year,
            current_year=current_year
        )
        delta_vt = team_value_lift_result.net_lift
        
        # Apply formula with edge case handling
        chi, warning = self._handle_edge_cases(ch, ma, delta_rm, delta_vt)
        
        if warning:
            warnings.append(warning)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(chi)
        
        # Build component breakdown
        components = ComponentBreakdown(
            career_baseline=career_baseline_result,
            market_adjustment=market_adjustment_result,
            revenue_delta=revenue_delta_result,
            team_value_lift=team_value_lift_result
        )
        
        return BrandPortabilityResult(
            chi=chi,
            components=components,
            formula="χ = Ch ⋅ Ma / (ΔRm + ΔVt)",
            interpretation=interpretation,
            warnings=warnings
        )
    
    def _handle_edge_cases(
        self,
        ch: float,
        ma: float,
        delta_rm: float,
        delta_vt: float
    ) -> Tuple[float, Optional[str]]:
        """
        Handle edge cases in formula calculation
        
        Cases:
        - Division by zero: If ΔRm + ΔVt = 0, apply epsilon (0.01)
        - Negative denominator: If ΔRm + ΔVt < 0, return warning
        - Zero career baseline: If Ch = 0, this should have been caught earlier
        
        Args:
            ch: Career baseline value
            ma: Market adjustment factor
            delta_rm: Revenue delta
            delta_vt: Team value lift
            
        Returns:
            Tuple of (calculated_chi, warning_message)
        """
        denominator = delta_rm + delta_vt
        warning = None
        
        # Handle division by zero
        if abs(denominator) < 1e-6:  # Effectively zero
            denominator = 0.01  # Apply epsilon
            warning = (
                "Denominator near zero (ΔRm + ΔVt ≈ 0), applied epsilon adjustment (0.01). "
                "This indicates the revenue delta and team value lift are offsetting each other."
            )
        
        # Handle negative denominator
        elif denominator < 0:
            warning = (
                "Negative denominator detected (ΔRm + ΔVt < 0): "
                "Both revenue delta and team value lift are negative, indicating "
                "the player may have negative impact or the market conditions are unfavorable. "
                "Interpret χ value with caution."
            )
        
        # Calculate chi
        chi = (ch * ma) / denominator
        
        return chi, warning
    
    def _generate_interpretation(self, chi: float) -> str:
        """
        Generate interpretation based on chi value
        
        Ranges:
        - χ > 3.0: Exceptional portability - star player with massive market impact
        - 2.0 < χ ≤ 3.0: High portability - significant impact expected
        - 1.0 < χ ≤ 2.0: Moderate portability - average impact
        - 0.5 < χ ≤ 1.0: Low portability - limited impact
        - χ ≤ 0.5: Minimal portability - negligible impact
        
        Args:
            chi: Brand portability score
            
        Returns:
            Human-readable interpretation string
        """
        if chi > 3.0:
            return (
                "Exceptional portability - star player with massive market impact. "
                "This player is expected to significantly boost team value and revenue "
                "in the new market."
            )
        elif chi > 2.0:
            return (
                "High portability - significant impact expected. "
                "This player should have a strong positive effect on team value and revenue."
            )
        elif chi > 1.0:
            return (
                "Moderate portability - average impact. "
                "This player will likely contribute positively to team value and revenue, "
                "but not dramatically."
            )
        elif chi > 0.5:
            return (
                "Low portability - limited impact. "
                "This player may have minimal effect on team value and revenue in the new market."
            )
        else:
            return (
                "Minimal portability - negligible impact. "
                "This player is unlikely to significantly affect team value or revenue."
            )
