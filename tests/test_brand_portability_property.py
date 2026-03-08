"""Property-based tests for BrandPortabilityCalculator

Feature: brand-portability-formula
Properties: 1, 14, 15
"""
import pytest
from hypothesis import given, strategies as st, settings, assume

from src.calculators import (
    BrandPortabilityCalculator,
    RevenueDeltaCalculator,
    TeamValueLiftCalculator,
    CareerBaselineCalculator,
    MarketAdjustmentCalculator
)
from src.estimators import (
    MerchandiseEstimator,
    TVRatingEstimator,
    TicketPremiumEstimator,
    PlayerRevenueAttributor
)
from src.models import (
    PlayerData,
    PlayerAnnualRecord,
    TeamData,
    TeamAnnualRecord,
    LeagueData,
    LeagueAnnualRecord,
    MarketTierData
)


# Strategies for generating valid test data
percentiles = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
positive_floats = st.floats(min_value=1.0, max_value=1e8, allow_nan=False, allow_infinity=False)
small_positive_floats = st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False)
years = st.integers(min_value=2020, max_value=2030)
market_tiers = st.integers(min_value=1, max_value=3)
dma_rankings = st.integers(min_value=1, max_value=100)
games = st.integers(min_value=1, max_value=40)
contribution_weights = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


def create_player_data(year: int, scoring_pct: float, ppg: float = 20.0) -> PlayerData:
    """Helper to create player data"""
    return PlayerData(
        player_id="test_player",
        player_name="Test Player",
        annual_records=[
            PlayerAnnualRecord(
                year=year,
                team_id="old_team",
                points_per_game=ppg,
                games_played=40,
                minutes_per_game=35.0,
                salary=100_000,
                scoring_percentile=scoring_pct
            )
        ]
    )


def create_team_data(
    team_id: str,
    year: int,
    market_tier: int,
    dma: int,
    revenue: float,
    valuation: float
) -> TeamData:
    """Helper to create team data"""
    return TeamData(
        team_id=team_id,
        team_name=f"Team {team_id}",
        market_tier=market_tier,
        dma_ranking=dma,
        annual_records=[
            TeamAnnualRecord(
                year=year,
                valuation=valuation,
                revenue=revenue,
                attendance_avg=10000,
                points_per_game=85.0
            )
        ]
    )


def create_league_data(year: int) -> LeagueData:
    """Helper to create league data"""
    return LeagueData(
        annual_records=[
            LeagueAnnualRecord(
                year=year,
                avg_viewership=1.0,
                avg_attendance=9000,
                avg_salary=120_000,
                total_teams=12
            )
        ]
    )


def create_market_tier_data(tier: int) -> MarketTierData:
    """Helper to create market tier data"""
    tier_factors = {1: 1.25, 2: 1.0, 3: 0.85}
    return MarketTierData(
        tier=tier,
        adjustment_factor=tier_factors[tier],
        teams=["test_team"]
    )


def create_calculator() -> BrandPortabilityCalculator:
    """Helper to create BrandPortabilityCalculator with all dependencies"""
    # Create estimators
    merch_est = MerchandiseEstimator()
    tv_est = TVRatingEstimator()
    ticket_est = TicketPremiumEstimator()
    revenue_attr = PlayerRevenueAttributor()
    
    # Create calculators
    revenue_delta_calc = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
    team_value_lift_calc = TeamValueLiftCalculator()
    career_baseline_calc = CareerBaselineCalculator(revenue_attr)
    market_adjustment_calc = MarketAdjustmentCalculator()
    
    # Create main calculator
    return BrandPortabilityCalculator(
        revenue_delta_calc,
        team_value_lift_calc,
        career_baseline_calc,
        market_adjustment_calc
    )


class TestBrandPortabilityCalculatorProperty:
    """Property-based tests for BrandPortabilityCalculator"""
    
    # Feature: brand-portability-formula, Property 1: Formula calculation correctness
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        revenue=small_positive_floats,
        valuation_prior=small_positive_floats,
        valuation_current=small_positive_floats,
        contribution_weight=contribution_weights
    )
    @settings(max_examples=100, deadline=None)
    def test_formula_calculation_correctness(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        revenue,
        valuation_prior,
        valuation_current,
        contribution_weight
    ):
        """
        Property 1: Formula calculation correctness
        
        For any valid career baseline (Ch > 0), market adjustment (Ma > 0),
        revenue delta (ΔRm), and team value lift (ΔVt) where ΔRm + ΔVt ≠ 0,
        the calculated brand portability χ should equal Ch ⋅ Ma / (ΔRm + ΔVt).
        
        Validates: Requirements - Acceptance Criteria 2
        """
        # Create calculator
        calculator = create_calculator()
        
        # Create test data
        player_data = create_player_data(year, scoring_pct)
        new_team_data = create_team_data(
            "new_team", year + 1, market_tier, dma, revenue, valuation_current
        )
        old_team_data = create_team_data(
            "old_team", year, market_tier, dma, revenue * 0.9, valuation_prior
        )
        league_data = create_league_data(year)
        market_tier_data = create_market_tier_data(market_tier)
        
        # Add prior year data for team value lift calculation
        new_team_data.annual_records.insert(
            0,
            TeamAnnualRecord(
                year=year,
                valuation=valuation_prior,
                revenue=revenue * 0.9,
                attendance_avg=9000,
                points_per_game=80.0
            )
        )
        
        try:
            # Calculate brand portability
            result = calculator.calculate_portability(
                player_data=player_data,
                new_team_data=new_team_data,
                league_data=league_data,
                market_tier_data=market_tier_data,
                team_data_history=[old_team_data],
                prior_year=year,
                current_year=year + 1,
                player_contribution_weight=contribution_weight
            )
            
            # Extract component values
            ch = result.components.career_baseline.avg_annual_output
            ma = result.components.market_adjustment.adjustment_factor
            delta_rm = result.components.revenue_delta.total_delta
            delta_vt = result.components.team_value_lift.net_lift
            
            # Calculate expected chi
            denominator = delta_rm + delta_vt
            
            # If denominator is near zero, epsilon was applied
            if abs(denominator) < 1e-6:
                expected_chi = (ch * ma) / 0.01
            else:
                expected_chi = (ch * ma) / denominator
            
            # Verify formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt)
            # Allow small floating point error
            assert abs(result.chi - expected_chi) < 0.01 or abs(result.chi - expected_chi) / abs(expected_chi) < 0.01, \
                f"Formula mismatch: expected {expected_chi}, got {result.chi}, " \
                f"Ch={ch}, Ma={ma}, ΔRm={delta_rm}, ΔVt={delta_vt}"
        
        except ValueError as e:
            # Zero career baseline is expected to raise exception
            if "zero career baseline" in str(e).lower():
                pass  # This is expected behavior
            else:
                raise
    
    # Feature: brand-portability-formula, Property 14: Positive denominator handling
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        contribution_weight=contribution_weights
    )
    @settings(max_examples=100, deadline=None)
    def test_positive_denominator_handling(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        contribution_weight
    ):
        """
        Property 14: Positive denominator handling
        
        For any calculation where ΔRm + ΔVt equals zero, the system should apply
        an epsilon adjustment (0.01) to prevent division by zero, and the result
        should include a warning message.
        
        Validates: Requirements - Edge Cases, Acceptance Criteria 4
        """
        # Create calculator
        calculator = create_calculator()
        
        # Create test data designed to produce near-zero denominator
        # Use same revenue and valuation to minimize delta
        revenue = 10_000_000
        valuation = 100_000_000
        
        player_data = create_player_data(year, scoring_pct, ppg=15.0)
        new_team_data = create_team_data(
            "new_team", year + 1, market_tier, dma, revenue, valuation
        )
        old_team_data = create_team_data(
            "old_team", year, market_tier, dma, revenue, valuation
        )
        league_data = create_league_data(year)
        market_tier_data = create_market_tier_data(market_tier)
        
        # Add prior year data with same valuation (zero growth)
        new_team_data.annual_records.insert(
            0,
            TeamAnnualRecord(
                year=year,
                valuation=valuation,
                revenue=revenue,
                attendance_avg=10000,
                points_per_game=85.0
            )
        )
        
        try:
            # Calculate brand portability
            result = calculator.calculate_portability(
                player_data=player_data,
                new_team_data=new_team_data,
                league_data=league_data,
                market_tier_data=market_tier_data,
                team_data_history=[old_team_data],
                prior_year=year,
                current_year=year + 1,
                player_contribution_weight=contribution_weight
            )
            
            # Extract denominator
            delta_rm = result.components.revenue_delta.total_delta
            delta_vt = result.components.team_value_lift.net_lift
            denominator = delta_rm + delta_vt
            
            # If denominator is near zero, verify epsilon was applied and warning exists
            if abs(denominator) < 1e-6:
                # Should have a warning about epsilon adjustment
                assert len(result.warnings) > 0, \
                    "Expected warning for near-zero denominator"
                assert any("epsilon" in w.lower() for w in result.warnings), \
                    f"Expected epsilon warning, got: {result.warnings}"
                
                # Chi should be calculated with epsilon (0.01)
                ch = result.components.career_baseline.avg_annual_output
                ma = result.components.market_adjustment.adjustment_factor
                expected_chi = (ch * ma) / 0.01
                
                assert abs(result.chi - expected_chi) < 0.01, \
                    f"Expected chi with epsilon: {expected_chi}, got {result.chi}"
        
        except ValueError as e:
            # Zero career baseline is expected to raise exception
            if "zero career baseline" in str(e).lower():
                pass  # This is expected behavior
            else:
                raise
    
    # Feature: brand-portability-formula, Property 15: Output structure completeness
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        revenue=small_positive_floats,
        valuation_prior=small_positive_floats,
        valuation_current=small_positive_floats,
        contribution_weight=contribution_weights
    )
    @settings(max_examples=100, deadline=None)
    def test_output_structure_completeness(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        revenue,
        valuation_prior,
        valuation_current,
        contribution_weight
    ):
        """
        Property 15: Output structure completeness
        
        For any successful brand portability calculation, the output should contain
        all required fields: brandPortability (chi value), components (with all four
        sub-components), formula string, interpretation string, and warnings array.
        
        Validates: Requirements - Output Requirements, Acceptance Criteria 5
        """
        # Create calculator
        calculator = create_calculator()
        
        # Create test data
        player_data = create_player_data(year, scoring_pct)
        new_team_data = create_team_data(
            "new_team", year + 1, market_tier, dma, revenue, valuation_current
        )
        old_team_data = create_team_data(
            "old_team", year, market_tier, dma, revenue * 0.9, valuation_prior
        )
        league_data = create_league_data(year)
        market_tier_data = create_market_tier_data(market_tier)
        
        # Add prior year data for team value lift calculation
        new_team_data.annual_records.insert(
            0,
            TeamAnnualRecord(
                year=year,
                valuation=valuation_prior,
                revenue=revenue * 0.9,
                attendance_avg=9000,
                points_per_game=80.0
            )
        )
        
        try:
            # Calculate brand portability
            result = calculator.calculate_portability(
                player_data=player_data,
                new_team_data=new_team_data,
                league_data=league_data,
                market_tier_data=market_tier_data,
                team_data_history=[old_team_data],
                prior_year=year,
                current_year=year + 1,
                player_contribution_weight=contribution_weight
            )
            
            # Verify all required fields exist
            assert hasattr(result, 'chi'), "Missing chi field"
            assert hasattr(result, 'components'), "Missing components field"
            assert hasattr(result, 'formula'), "Missing formula field"
            assert hasattr(result, 'interpretation'), "Missing interpretation field"
            assert hasattr(result, 'warnings'), "Missing warnings field"
            
            # Verify chi is a number
            assert isinstance(result.chi, (int, float)), \
                f"Chi should be numeric, got {type(result.chi)}"
            
            # Verify components has all four sub-components
            assert hasattr(result.components, 'career_baseline'), \
                "Missing career_baseline component"
            assert hasattr(result.components, 'market_adjustment'), \
                "Missing market_adjustment component"
            assert hasattr(result.components, 'revenue_delta'), \
                "Missing revenue_delta component"
            assert hasattr(result.components, 'team_value_lift'), \
                "Missing team_value_lift component"
            
            # Verify formula is the correct string
            assert result.formula == "χ = Ch ⋅ Ma / (ΔRm + ΔVt)", \
                f"Incorrect formula string: {result.formula}"
            
            # Verify interpretation is a non-empty string
            assert isinstance(result.interpretation, str), \
                "Interpretation should be a string"
            assert len(result.interpretation) > 0, \
                "Interpretation should not be empty"
            
            # Verify warnings is a list
            assert isinstance(result.warnings, list), \
                "Warnings should be a list"
        
        except ValueError as e:
            # Zero career baseline is expected to raise exception
            if "zero career baseline" in str(e).lower():
                pass  # This is expected behavior
            else:
                raise
